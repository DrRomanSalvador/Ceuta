"""Selection, optimism and transport safeguards for dependent validation.

These routines keep model selection inside temporal training data, estimate
optimism within the resampling loop, and evaluate external populations without
silently refitting on the target population.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Hashable, Sequence, TypeVar

from .frontier_longitudinal import RobustInterval, cluster_bootstrap, dependent_proper_score_interval
from .longitudinal_validation import LongitudinalRecord, TemporalFold

Model = TypeVar("Model")
Parameter = TypeVar("Parameter", bound=Hashable)


@dataclass(frozen=True, slots=True)
class OptimismResult:
    apparent: float
    bootstrap_apparent: float
    bootstrap_test: float
    optimism: float
    corrected: float
    metric: str
    direction: str
    unit: str
    replicates: int


@dataclass(frozen=True, slots=True)
class NestedTemporalResult:
    outer_scores: tuple[float, ...]
    selected_parameters: tuple[Hashable, ...]
    outer_folds: tuple[int, ...]
    pooled_score: float
    metric: str


@dataclass(frozen=True, slots=True)
class TransportValidation:
    source_interval: RobustInterval
    target_interval: RobustInterval
    score_difference_target_minus_source: float
    target_refit: bool
    target_calibrated: bool
    target_independent_units: int


def optimism_corrected_bootstrap(
    records: Sequence[LongitudinalRecord],
    *,
    fit: Callable[[Sequence[LongitudinalRecord]], Model],
    score: Callable[[Model, Sequence[LongitudinalRecord]], float],
    unit: str = "entity",
    replicates: int = 1000,
    seed: int = 0,
    direction: str = "higher_is_better",
    metric: str = "user_supplied_metric",
) -> OptimismResult:
    """Estimate resampling optimism with model fitting repeated inside bootstrap.

    For each bootstrap sample the model is fit only on that sample. Performance
    is then measured both on the bootstrap sample and on the original data.
    Their directional difference estimates optimism.
    """
    if direction not in {"higher_is_better", "lower_is_better"}:
        raise ValueError("direction must be higher_is_better or lower_is_better")
    if replicates < 500:
        raise ValueError("at least 500 replicates are required")
    apparent_model = fit(records)
    apparent = float(score(apparent_model, records))
    groups: dict[Hashable, list[int]] = {}
    for i, record in enumerate(records):
        key = record.entity_id if unit == "entity" else record.cluster_id
        if key is None:
            key = record.entity_id
        groups.setdefault(key, []).append(i)
    if len(groups) < 2:
        raise ValueError("at least two independent units are required")
    import random
    rng = random.Random(seed)
    keys = tuple(groups)
    bootstrap_apparent: list[float] = []
    bootstrap_test: list[float] = []
    for _ in range(replicates):
        sampled_keys = [keys[rng.randrange(len(keys))] for _ in keys]
        sample = [records[i] for key in sampled_keys for i in groups[key]]
        model = fit(sample)
        bootstrap_apparent.append(float(score(model, sample)))
        bootstrap_test.append(float(score(model, records)))
    if direction == "higher_is_better":
        optimism = sum(a - t for a, t in zip(bootstrap_apparent, bootstrap_test)) / replicates
    else:
        optimism = sum(t - a for a, t in zip(bootstrap_apparent, bootstrap_test)) / replicates
    return OptimismResult(
        apparent=apparent,
        bootstrap_apparent=sum(bootstrap_apparent) / replicates,
        bootstrap_test=sum(bootstrap_test) / replicates,
        optimism=optimism,
        corrected=apparent - optimism,
        metric=metric,
        direction=direction,
        unit=unit,
        replicates=replicates,
    )


def _inner_folds_for_outer(
    records: Sequence[LongitudinalRecord], outer_train: Sequence[int], template: Sequence[TemporalFold]
) -> tuple[TemporalFold, ...]:
    allowed = set(outer_train)
    result: list[TemporalFold] = []
    for fold in template:
        train = tuple(i for i in fold.train_indices if i in allowed)
        test = tuple(i for i in fold.test_indices if i in allowed)
        if not train or not test:
            continue
        if max(records[i].time for i in train) >= min(records[i].time for i in test):
            raise RuntimeError("inner temporal fold violates chronology")
        result.append(
            TemporalFold(
                fold.fold,
                min(records[i].time for i in train),
                max(records[i].time for i in train),
                min(records[i].time for i in test),
                max(records[i].time for i in test),
                train,
                test,
            )
        )
    return tuple(result)


def nested_temporal_cv(
    records: Sequence[LongitudinalRecord],
    outer_folds: Sequence[TemporalFold],
    inner_template: Sequence[TemporalFold],
    parameters: Sequence[Parameter],
    fit: Callable[[Sequence[LongitudinalRecord], Parameter], Model],
    score: Callable[[Model, Sequence[LongitudinalRecord]], float],
    *,
    direction: str = "higher_is_better",
) -> NestedTemporalResult:
    """Perform parameter selection strictly inside each outer temporal fold."""
    if direction not in {"higher_is_better", "lower_is_better"}:
        raise ValueError("invalid metric direction")
    if not parameters:
        raise ValueError("at least one candidate parameter is required")
    outer_scores: list[float] = []
    selected: list[Hashable] = []
    for outer in outer_folds:
        inner = _inner_folds_for_outer(records, outer.train_indices, inner_template)
        if not inner:
            raise ValueError("outer fold has no valid inner temporal folds")
        candidate_scores: dict[Parameter, list[float]] = {p: [] for p in parameters}
        for parameter in parameters:
            for fold in inner:
                train = [records[i] for i in fold.train_indices]
                test = [records[i] for i in fold.test_indices]
                model = fit(train, parameter)
                candidate_scores[parameter].append(float(score(model, test)))
        mean_scores = {p: sum(v) / len(v) for p, v in candidate_scores.items()}
        chosen = (
            max(mean_scores, key=mean_scores.get)
            if direction == "higher_is_better"
            else min(mean_scores, key=mean_scores.get)
        )
        outer_train = [records[i] for i in outer.train_indices]
        outer_test = [records[i] for i in outer.test_indices]
        model = fit(outer_train, chosen)
        outer_scores.append(float(score(model, outer_test)))
        selected.append(chosen)
    return NestedTemporalResult(
        tuple(outer_scores), tuple(selected), tuple(f.fold for f in outer_folds),
        sum(outer_scores) / len(outer_scores), "user_supplied_metric",
    )


def transport_validate(
    source: Sequence[LongitudinalRecord],
    target: Sequence[LongitudinalRecord],
    predictor: Callable[[Sequence[LongitudinalRecord]], Sequence[float]],
    *,
    metric: str = "brier",
    unit: str = "entity",
    replicates: int = 1000,
    seed: int = 0,
) -> TransportValidation:
    """Evaluate an unchanged source model on a target population.

    ``predictor`` is called once for source and once for target. No target
    refitting is possible through this API; target adaptation must be a
    separate, explicitly named procedure.
    """
    source_predictions = tuple(float(x) for x in predictor(source))
    target_predictions = tuple(float(x) for x in predictor(target))
    if len(source_predictions) != len(source) or len(target_predictions) != len(target):
        raise ValueError("predictor output length mismatch")
    source_scored = tuple(
        LongitudinalRecord(r.entity_id, r.time, r.outcome, p, r.cluster_id, r.observation_id, r.horizon)
        for r, p in zip(source, source_predictions)
    )
    target_scored = tuple(
        LongitudinalRecord(r.entity_id, r.time, r.outcome, p, r.cluster_id, r.observation_id, r.horizon)
        for r, p in zip(target, target_predictions)
    )
    source_interval = dependent_proper_score_interval(
        source_scored, metric=metric, unit=unit, replicates=replicates, seed=seed
    )
    target_interval = dependent_proper_score_interval(
        target_scored, metric=metric, unit=unit, replicates=replicates, seed=seed + 1
    )
    target_units = len({r.entity_id if unit == "entity" else (r.cluster_id or r.entity_id) for r in target})
    return TransportValidation(
        source_interval,
        target_interval,
        target_interval.estimate - source_interval.estimate,
        False,
        False,
        target_units,
    )
