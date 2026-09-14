"""Frontier statistical validation for longitudinal and dependent observations.

Design principles:
- the independent resampling unit is explicit (subject, cluster, block, or time);
- temporal validation is forward-only and leakage-aware;
- every reported estimate records its dependence assumptions;
- uncertainty methods never silently fall back to IID assumptions;
- optimism correction and nested model-selection validation keep selection
  inside the resampling loop;
- transport validation separates discrimination, calibration, and score loss;
- prediction horizons are explicit so repeated measurements are not treated as
  independent outcomes by accident.

This module is dependency-light and deterministic. It provides the statistical
infrastructure; model fitting remains an injected callable so CeutIA can use
its deterministic/statistical/ML/LLM model layers without coupling validation
to one estimator implementation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import exp, isfinite, log, sqrt
from statistics import NormalDist
from typing import Callable, Hashable, Iterable, Mapping, Sequence, TypeVar

T = TypeVar("T")
P = TypeVar("P")

_Z95 = NormalDist().inv_cdf(0.975)
_EPS = 1e-15


@dataclass(frozen=True, slots=True)
class LongitudinalRecord:
    """One prediction/evaluation row with explicit dependence structure."""

    entity_id: Hashable
    time: float
    outcome: int
    prediction: float
    cluster_id: Hashable | None = None
    observation_id: Hashable | None = None
    horizon: float | None = None


@dataclass(frozen=True, slots=True)
class ResampleSpec:
    """Defines the unit whose dependence must be preserved during resampling."""

    unit: str  # entity | cluster | block
    block_width: float | None = None
    circular: bool = False
    stratify_by: tuple[str, ...] = ()
    seed: int = 0

    def validate(self) -> None:
        if self.unit not in {"entity", "cluster", "block"}:
            raise ValueError("resampling unit must be entity, cluster, or block")
        if self.unit == "block" and (self.block_width is None or self.block_width <= 0):
            raise ValueError("block bootstrap requires a positive block_width")


@dataclass(frozen=True, slots=True)
class BootstrapEstimate:
    estimate: float
    standard_error: float
    ci_low: float
    ci_high: float
    replicates: int
    method: str
    independent_unit: str
    percentile: tuple[float, float] = (0.025, 0.975)


@dataclass(frozen=True, slots=True)
class ScoreSummary:
    brier: float
    log_loss: float
    n: int
    effective_n: float
    cluster_count: int
    method: str


@dataclass(frozen=True, slots=True)
class TemporalFold:
    fold: int
    train_start: float
    train_end: float
    test_start: float
    test_end: float
    train_indices: tuple[int, ...]
    test_indices: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class TemporalValidationResult:
    folds: tuple[TemporalFold, ...]
    scores: tuple[ScoreSummary, ...]
    pooled_brier: float
    pooled_log_loss: float
    pooled_effective_n: float
    leakage_detected: bool
    minimum_gap: float


@dataclass(frozen=True, slots=True)
class TemporalCalibrationResult:
    folds: tuple[TemporalFold, ...]
    intercepts: tuple[float, ...]
    slopes: tuple[float, ...]
    pooled_intercept: float | None
    pooled_slope: float | None
    drift_detected: bool
    method: str


@dataclass(frozen=True, slots=True)
class OptimismCorrection:
    apparent: float
    optimism: float
    optimism_corrected: float
    bootstrap_replicates: int
    metric: str
    resampling_unit: str


@dataclass(frozen=True, slots=True)
class NestedCVResult:
    outer_scores: tuple[float, ...]
    outer_folds: tuple[tuple[tuple[int, ...], tuple[int, ...]], ...]
    selected_parameters: tuple[Hashable, ...]
    pooled_score: float
    metric: str


@dataclass(frozen=True, slots=True)
class TransportValidationResult:
    source_score: ScoreSummary
    target_score: ScoreSummary
    target_calibration_intercept: float | None
    target_calibration_slope: float | None
    performance_difference: float
    target_entity_count: int
    method: str


def _percentile(values: Sequence[float], q: float) -> float:
    if not values:
        raise ValueError("cannot calculate a percentile from an empty sample")
    if not 0.0 <= q <= 1.0:
        raise ValueError("q must be in [0,1]")
    ordered = sorted(values)
    position = (len(ordered) - 1) * q
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1.0 - weight) + ordered[upper] * weight


def _validate_binary_records(records: Sequence[LongitudinalRecord]) -> None:
    if not records:
        raise ValueError("records must be non-empty")
    for record in records:
        if record.outcome not in (0, 1):
            raise ValueError("outcomes must be binary")
        if not isfinite(record.time) or not isfinite(record.prediction) or not 0.0 <= record.prediction <= 1.0:
            raise ValueError("time and predictions must be finite; predictions must be probabilities in [0,1]")


def _groups(records: Sequence[LongitudinalRecord], unit: str) -> dict[Hashable, list[int]]:
    if unit == "entity":
        return _group_by(records, lambda r: r.entity_id)
    if unit == "cluster":
        return _group_by(records, lambda r: r.cluster_id if r.cluster_id is not None else r.entity_id)
    raise ValueError("block groups require block construction")


def _group_by(records: Sequence[T], key: Callable[[T], Hashable]) -> dict[Hashable, list[int]]:
    result: dict[Hashable, list[int]] = {}
    for index, record in enumerate(records):
        result.setdefault(key(record), []).append(index)
    return result


def _effective_sample_size(records: Sequence[LongitudinalRecord], unit: str) -> float:
    groups = _groups(records, unit)
    if not groups:
        return 0.0
    sizes = [len(v) for v in groups.values()]
    return sum(sizes) ** 2 / sum(size * size for size in sizes)


def _scores(records: Sequence[LongitudinalRecord], method: str) -> ScoreSummary:
    _validate_binary_records(records)
    n = len(records)
    brier = sum((r.prediction - r.outcome) ** 2 for r in records) / n
    log_loss = -sum(
        r.outcome * log(max(r.prediction, _EPS))
        + (1 - r.outcome) * log(max(1 - r.prediction, _EPS))
        for r in records
    ) / n
    return ScoreSummary(
        brier=brier,
        log_loss=log_loss,
        n=n,
        effective_n=_effective_sample_size(records, "entity"),
        cluster_count=len(_groups(records, "entity")),
        method=method,
    )


def _rng(seed: int):
    # Local deterministic generator; avoids mutating process-global RNG state.
    import random
    return random.Random(seed)


def _resample_indices(records: Sequence[LongitudinalRecord], spec: ResampleSpec, rng) -> list[int]:
    spec.validate()
    if spec.unit in {"entity", "cluster"}:
        groups = _groups(records, spec.unit)
        keys = list(groups)
        sampled = [keys[rng.randrange(len(keys))] for _ in keys]
        return [index for key in sampled for index in groups[key]]

    times = sorted(set(record.time for record in records))
    if not times:
        return []
    width = spec.block_width or 1.0
    blocks: dict[int, list[int]] = {}
    for index, record in enumerate(records):
        block = int((record.time - times[0]) // width)
        blocks.setdefault(block, []).append(index)
    keys = list(blocks)
    sampled = [keys[rng.randrange(len(keys))] for _ in keys]
    return [index for key in sampled for index in blocks[key]]


def blocked_or_cluster_bootstrap(
    records: Sequence[LongitudinalRecord],
    statistic: Callable[[Sequence[LongitudinalRecord]], float],
    *,
    spec: ResampleSpec,
    replicates: int = 2000,
) -> BootstrapEstimate:
    """Bootstrap a statistic while preserving the declared dependence unit."""
    _validate_binary_records(records)
    if replicates < 200:
        raise ValueError("at least 200 bootstrap replicates are required")
    observed = float(statistic(records))
    rng = _rng(spec.seed)
    values = [float(statistic([records[i] for i in _resample_indices(records, spec, rng)])) for _ in range(replicates)]
    se = sqrt(sum((value - sum(values) / len(values)) ** 2 for value in values) / (len(values) - 1))
    return BootstrapEstimate(
        estimate=observed,
        standard_error=se,
        ci_low=_percentile(values, 0.025),
        ci_high=_percentile(values, 0.975),
        replicates=replicates,
        method=f"{spec.unit}_bootstrap",
        independent_unit=spec.unit,
    )


def rolling_origin_splits(
    records: Sequence[LongitudinalRecord],
    *,
    initial_train_time: float,
    test_horizon: float,
    step: float,
    gap: float = 0.0,
    expanding: bool = True,
) -> tuple[TemporalFold, ...]:
    """Create leakage-safe forward temporal folds.

    A test observation can never occur at or before the end of the training
    window. ``gap`` is a purge interval for delayed labels/information leakage.
    """
    if initial_train_time <= 0 or test_horizon <= 0 or step <= 0 or gap < 0:
        raise ValueError("initial_train_time, test_horizon and step must be positive; gap cannot be negative")
    ordered = sorted(enumerate(records), key=lambda item: item[1].time)
    times = [record.time for _, record in ordered]
    if not times:
        return ()
    folds: list[TemporalFold] = []
    origin = min(times) + initial_train_time
    fold = 0
    while origin + gap + test_horizon <= max(times):
        train_end = origin
        test_start = origin + gap
        test_end = test_start + test_horizon
        if expanding:
            train_start = min(times)
        else:
            train_start = origin - initial_train_time
        train_indices = tuple(index for index, record in ordered if train_start <= record.time <= train_end)
        test_indices = tuple(index for index, record in ordered if test_start <= record.time < test_end)
        if train_indices and test_indices:
            if max(records[i].time for i in train_indices) >= min(records[i].time for i in test_indices):
                raise RuntimeError("temporal leakage detected while constructing rolling-origin folds")
            folds.append(TemporalFold(fold, train_start, train_end, test_start, test_end, train_indices, test_indices))
            fold += 1
        origin += step
    if not folds:
        raise ValueError("rolling-origin design produced no valid folds")
    return tuple(folds)


def evaluate_rolling_origin(
    records: Sequence[LongitudinalRecord],
    folds: Sequence[TemporalFold],
    predictor: Callable[[Sequence[LongitudinalRecord], Sequence[LongitudinalRecord]], Sequence[float]],
) -> TemporalValidationResult:
    """Evaluate a predictor trained only on each fold's past."""
    scores: list[ScoreSummary] = []
    leakage = False
    for fold in folds:
        train = [records[i] for i in fold.train_indices]
        test = [records[i] for i in fold.test_indices]
        if max(r.time for r in train) >= min(r.time for r in test):
            leakage = True
        predictions = tuple(float(x) for x in predictor(train, test))
        if len(predictions) != len(test):
            raise ValueError("predictor returned a different number of predictions than test observations")
        scored = [LongitudinalRecord(r.entity_id, r.time, r.outcome, p, r.cluster_id, r.observation_id, r.horizon) for r, p in zip(test, predictions)]
        scores.append(_scores(scored, "rolling_origin"))
    all_test = [records[i] for fold in folds for i in fold.test_indices]
    pooled_predictions = [float(x) for fold in folds for x in predictor([records[i] for i in fold.train_indices], [records[i] for i in fold.test_indices])]
    pooled = [LongitudinalRecord(r.entity_id, r.time, r.outcome, p, r.cluster_id, r.observation_id, r.horizon) for r, p in zip(all_test, pooled_predictions)]
    pooled_score = _scores(pooled, "rolling_origin_pooled")
    return TemporalValidationResult(tuple(folds), tuple(scores), pooled_score.brier, pooled_score.log_loss, pooled_score.effective_n, leakage, min(f.test_start - f.train_end for f in folds))


def _calibration_fit(records: Sequence[LongitudinalRecord]) -> tuple[float, float]:
    """Small self-contained unpenalized logistic recalibration fit."""
    if len({r.outcome for r in records}) < 2:
        raise ValueError("calibration requires both outcome classes")
    logits = [log(r.prediction / (1-r.prediction)) for r in records if 0 < r.prediction < 1]
    filtered = [r for r in records if 0 < r.prediction < 1]
    if len(logits) != len(records):
        raise ValueError("calibration requires strictly interior probabilities")
    alpha, beta = 0.0, 1.0
    for _ in range(100):
        g0=g1=h00=h01=h11=0.0
        for x,r in zip(logits,filtered):
            eta=alpha+beta*x
            p=1/(1+exp(-eta)) if eta>=0 else exp(eta)/(1+exp(eta))
            w=p*(1-p); residual=r.outcome-p
            g0+=residual; g1+=residual*x; h00-=w; h01-=w*x; h11-=w*x*x
        det=h00*h11-h01*h01
        if det >= 0 or abs(det) <= 1e-14*max(abs(h00*h11),abs(h01*h01),1):
            raise ValueError("temporal calibration model is non-identifiable")
        if max(abs(g0),abs(g1)) <= 1e-10:
            return alpha,beta
        d0=(g0*h11-g1*h01)/det; d1=(h00*g1-h01*g0)/det
        alpha-=d0; beta-=d1
    raise ValueError("temporal calibration did not converge")


def temporal_calibration(records: Sequence[LongitudinalRecord], folds: Sequence[TemporalFold]) -> TemporalCalibrationResult:
    intercepts=[]; slopes=[]
    for fold in folds:
        test=[records[i] for i in fold.test_indices]
        a,b=_calibration_fit(test)
        intercepts.append(a); slopes.append(b)
    return TemporalCalibrationResult(
        folds=tuple(folds), intercepts=tuple(intercepts), slopes=tuple(slopes),
        pooled_intercept=sum(intercepts)/len(intercepts) if intercepts else None,
        pooled_slope=sum(slopes)/len(slopes) if slopes else None,
        drift_detected=(max(intercepts)-min(intercepts) > 0.5 or max(slopes)-min(slopes) > 0.5) if intercepts else False,
        method="fold_specific_temporal_logistic_recalibration",
    )


def dependent_proper_scores(records: Sequence[LongitudinalRecord], *, unit: str = "entity") -> ScoreSummary:
    """Report proper scores with an effective-N correction for repeated units."""
    if unit not in {"entity", "cluster"}:
        raise ValueError("unit must be entity or cluster")
    _validate_binary_records(records)
    groups = _groups(records, unit)
    sizes = [len(v) for v in groups.values()]
    effective_n = sum(sizes) ** 2 / sum(s*s for s in sizes)
    n = len(records)
    brier = sum((r.prediction-r.outcome)**2 for r in records)/n
    log_loss = -sum(r.outcome*log(max(r.prediction,_EPS))+(1-r.outcome)*log(max(1-r.prediction,_EPS)) for r in records)/n
    return ScoreSummary(brier, log_loss, n, effective_n, len(groups), f"proper_scores_dependence_adjusted_{unit}")


def optimism_corrected_bootstrap(
    records: Sequence[LongitudinalRecord],
    fit_and_score: Callable[[Sequence[LongitudinalRecord], Sequence[LongitudinalRecord]], float],
    *,
    spec: ResampleSpec,
    replicates: int = 1000,
) -> OptimismCorrection:
    """Estimate bootstrap optimism as apparent performance minus test performance."""
    if replicates < 200:
        raise ValueError("at least 200 bootstrap replicates are required")
    apparent = float(fit_and_score(records, records))
    rng = _rng(spec.seed)
    optimism_values=[]
    for _ in range(replicates):
        sample_indices=_resample_indices(records,spec,rng)
        bootstrap_sample=[records[i] for i in sample_indices]
        in_boot=float(fit_and_score(bootstrap_sample,bootstrap_sample))
        out_boot=float(fit_and_score(bootstrap_sample,records))
        optimism_values.append(in_boot-out_boot)
    optimism=sum(optimism_values)/len(optimism_values)
    return OptimismCorrection(apparent,optimism,apparent-optimism,replicates,"user_supplied_metric",spec.unit)


def nested_temporal_cv(
    records: Sequence[LongitudinalRecord],
    outer_folds: Sequence[TemporalFold],
    inner_splitter: Callable[[Sequence[LongitudinalRecord]], Sequence[tuple[Sequence[int], Sequence[int]]]],
    parameter_grid: Sequence[P],
    fit_score: Callable[[P, Sequence[LongitudinalRecord], Sequence[LongitudinalRecord]], float],
) -> NestedCVResult:
    """Nested temporal CV; parameter selection occurs strictly inside each outer train set."""
    if not parameter_grid:
        raise ValueError("parameter_grid must be non-empty")
    outer_scores=[]; selected=[]; fold_pairs=[]
    for outer in outer_folds:
        outer_train=[records[i] for i in outer.train_indices]
        outer_test=[records[i] for i in outer.test_indices]
        inner=inner_splitter(outer_train)
        if not inner:
            raise ValueError("inner splitter produced no folds")
        mean_scores=[]
        for parameter in parameter_grid:
            values=[]
            for train_local,test_local in inner:
                train=[outer_train[i] for i in train_local]; test=[outer_train[i] for i in test_local]
                values.append(float(fit_score(parameter,train,test)))
            mean_scores.append(sum(values)/len(values))
        best_index=max(range(len(parameter_grid)), key=lambda i: mean_scores[i])
        best_parameter=parameter_grid[best_index]
        selected.append(best_parameter)
        outer_scores.append(float(fit_score(best_parameter,outer_train,outer_test)))
        fold_pairs.append((tuple(outer.train_indices),tuple(outer.test_indices)))
    return NestedCVResult(tuple(outer_scores),tuple(fold_pairs),tuple(selected),sum(outer_scores)/len(outer_scores),"user_supplied_score_maximized")


def transport_validation(
    source: Sequence[LongitudinalRecord],
    target: Sequence[LongitudinalRecord],
) -> TransportValidationResult:
    """Evaluate transport without refitting on target data."""
    source_score=dependent_proper_scores(source,unit="entity")
    target_score=dependent_proper_scores(target,unit="entity")
    try:
        target_intercept,target_slope=_calibration_fit(target)
    except ValueError:
        target_intercept,target_slope=None,None
    return TransportValidationResult(
        source_score=source_score,
        target_score=target_score,
        target_calibration_intercept=target_intercept,
        target_calibration_slope=target_slope,
        performance_difference=target_score.brier-source_score.brier,
        target_entity_count=len(_groups(target,"entity")),
        method="external_transport_without_target_refitting",
    )


@dataclass(frozen=True, slots=True)
class StatisticalValidationContract:
    """Decision gate preventing IID claims for dependent data."""

    dependence_structure_declared: bool
    temporal_holdout: bool
    leakage_tested: bool
    independent_unit: str | None
    uncertainty_method: str | None
    missingness_assessed: bool
    optimism_assessed: bool
    nested_selection: bool
    transport_assessed: bool

    @property
    def decision_ready(self) -> bool:
        return all((
            self.dependence_structure_declared,
            self.temporal_holdout,
            self.leakage_tested,
            self.independent_unit is not None,
            self.uncertainty_method is not None,
            self.missingness_assessed,
            self.optimism_assessed,
            self.nested_selection,
            self.transport_assessed,
        ))


__all__ = [
    "BootstrapEstimate", "LongitudinalRecord", "NestedCVResult", "OptimismCorrection",
    "ResampleSpec", "ScoreSummary", "StatisticalValidationContract", "TemporalCalibrationResult",
    "TemporalFold", "TemporalValidationResult", "TransportValidationResult",
    "blocked_or_cluster_bootstrap", "dependent_proper_scores", "evaluate_rolling_origin",
    "nested_temporal_cv", "optimism_corrected_bootstrap", "rolling_origin_splits",
    "temporal_calibration", "transport_validation",
]
