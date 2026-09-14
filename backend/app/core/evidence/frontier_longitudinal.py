"""Frontier statistical infrastructure for dependent longitudinal data.

This module adds the safeguards that are required before treating repeated,
clustered or time-dependent observations as evidence for model performance.
It deliberately avoids IID variance assumptions and makes the independent
unit, temporal ordering, prediction horizon, missingness assumptions and
metric direction explicit.

The module is estimator-agnostic: model fitting is injected by the caller.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite, log, sqrt
from random import Random
from statistics import NormalDist
from typing import Callable, Hashable, Sequence

from .longitudinal_validation import LongitudinalRecord, TemporalFold

_Z95 = NormalDist().inv_cdf(0.975)
_EPS = 1e-15


@dataclass(frozen=True, slots=True)
class BlockBootstrapSpec:
    """Moving/stationary/circular block bootstrap specification."""

    method: str = "moving"  # moving | stationary | circular
    block_length: int = 5
    replicates: int = 2000
    seed: int = 0

    def validate(self, n: int) -> None:
        if self.method not in {"moving", "stationary", "circular"}:
            raise ValueError("block method must be moving, stationary, or circular")
        if self.block_length < 1 or self.block_length > n:
            raise ValueError("block_length must be between 1 and the number of observations")
        if self.replicates < 500:
            raise ValueError("at least 500 block-bootstrap replicates are required")


@dataclass(frozen=True, slots=True)
class RobustInterval:
    estimate: float
    standard_error: float
    ci_low: float
    ci_high: float
    independent_unit: str
    method: str
    replicates: int


@dataclass(frozen=True, slots=True)
class DependenceDiagnostic:
    n_observations: int
    independent_units: int
    max_repeated_per_unit: int
    effective_sample_size: float
    repetition_ratio: float
    declared_unit: str


@dataclass(frozen=True, slots=True)
class TemporalCalibrationEstimate:
    intercept: float
    slope: float
    intercept_ci: tuple[float, float]
    slope_ci: tuple[float, float]
    replicates: int
    unit: str


@dataclass(frozen=True, slots=True)
class HorizonScore:
    horizon: float
    brier: float
    log_loss: float
    n: int
    independent_units: int


@dataclass(frozen=True, slots=True)
class IntegratedBrierResult:
    horizons: tuple[HorizonScore, ...]
    integrated_brier: float
    method: str


@dataclass(frozen=True, slots=True)
class MissingnessResult:
    n: int
    missing_outcome: int
    missing_prediction: int
    complete_cases: int
    monotone_by_entity: bool
    observation_count_by_entity: tuple[tuple[Hashable, int], ...]
    warning: str | None


@dataclass(frozen=True, slots=True)
class TransportResult:
    source: RobustInterval
    target: RobustInterval
    score_difference: float
    target_calibration_available: bool
    target_was_refit: bool


@dataclass(frozen=True, slots=True)
class FrontierValidationContract:
    independent_unit: str
    temporal_validation: bool
    dependence_aware_uncertainty: bool
    proper_scoring: bool
    optimism_correction: bool
    nested_selection: bool
    transport_validation: bool
    missingness_assessed: bool
    leakage_checked: bool
    decision_ready: bool
    blockers: tuple[str, ...]


def dependence_diagnostic(records: Sequence[LongitudinalRecord], unit: str = "entity") -> DependenceDiagnostic:
    if not records:
        raise ValueError("records must be non-empty")
    if unit not in {"entity", "cluster"}:
        raise ValueError("unit must be entity or cluster")
    keys = [
        (r.cluster_id if unit == "cluster" and r.cluster_id is not None else r.entity_id)
        for r in records
    ]
    counts: dict[Hashable, int] = {}
    for key in keys:
        counts[key] = counts.get(key, 0) + 1
    sizes = list(counts.values())
    effective_n = len(records) ** 2 / sum(size * size for size in sizes)
    return DependenceDiagnostic(
        n_observations=len(records),
        independent_units=len(counts),
        max_repeated_per_unit=max(sizes),
        effective_sample_size=effective_n,
        repetition_ratio=len(records) / len(counts),
        declared_unit=unit,
    )


def _validate_probability_records(records: Sequence[LongitudinalRecord]) -> None:
    if not records:
        raise ValueError("records must be non-empty")
    if any(r.outcome not in (0, 1) for r in records):
        raise ValueError("outcomes must be binary")
    if any(not isfinite(r.prediction) or not 0 <= r.prediction <= 1 for r in records):
        raise ValueError("predictions must be finite probabilities in [0,1]")


def _score(records: Sequence[LongitudinalRecord]) -> float:
    _validate_probability_records(records)
    return sum((r.prediction - r.outcome) ** 2 for r in records) / len(records)


def _log_score(records: Sequence[LongitudinalRecord]) -> float:
    _validate_probability_records(records)
    return -sum(
        r.outcome * log(max(r.prediction, _EPS))
        + (1 - r.outcome) * log(max(1 - r.prediction, _EPS))
        for r in records
    ) / len(records)


def _unit_groups(records: Sequence[LongitudinalRecord], unit: str) -> dict[Hashable, list[int]]:
    if unit not in {"entity", "cluster"}:
        raise ValueError("unit must be entity or cluster")
    groups: dict[Hashable, list[int]] = {}
    for i, record in enumerate(records):
        key = record.entity_id
        if unit == "cluster" and record.cluster_id is not None:
            key = record.cluster_id
        groups.setdefault(key, []).append(i)
    return groups


def cluster_bootstrap(
    records: Sequence[LongitudinalRecord],
    statistic: Callable[[Sequence[LongitudinalRecord]], float],
    *,
    unit: str = "entity",
    replicates: int = 2000,
    seed: int = 0,
) -> RobustInterval:
    """Primary uncertainty estimator for repeated observations.

    Entire independent units are resampled; observations belonging to a unit
    are never split. This is preferred to row-level bootstrap for longitudinal
    data unless a stronger stochastic time-series bootstrap is explicitly used.
    """
    _validate_probability_records(records)
    groups = _unit_groups(records, unit)
    if len(groups) < 2:
        raise ValueError("at least two independent units are required")
    if replicates < 500:
        raise ValueError("at least 500 bootstrap replicates are required")
    keys = tuple(groups)
    rng = Random(seed)
    observed = float(statistic(records))
    values: list[float] = []
    for _ in range(replicates):
        sampled = [keys[rng.randrange(len(keys))] for _ in keys]
        indices = [i for key in sampled for i in groups[key]]
        values.append(float(statistic([records[i] for i in indices])))
    mean = sum(values) / len(values)
    se = sqrt(sum((x - mean) ** 2 for x in values) / (len(values) - 1))
    ordered = sorted(values)
    low = ordered[int(0.025 * (len(ordered) - 1))]
    high = ordered[int(0.975 * (len(ordered) - 1))]
    return RobustInterval(observed, se, low, high, unit, "cluster_bootstrap_percentile", replicates)


def _ordered_times(records: Sequence[LongitudinalRecord]) -> list[float]:
    return sorted({r.time for r in records})


def block_bootstrap_indices(
    records: Sequence[LongitudinalRecord], spec: BlockBootstrapSpec
) -> list[list[int]]:
    """Generate true moving, circular or stationary time-block samples."""
    spec.validate(len(records))
    ordered = sorted(range(len(records)), key=lambda i: records[i].time)
    n = len(ordered)
    rng = Random(spec.seed)
    starts = list(range(n))
    result: list[list[int]] = []
    for _ in range(spec.replicates):
        sample: list[int] = []
        if spec.method in {"moving", "circular"}:
            while len(sample) < n:
                start = rng.choice(starts[: n - spec.block_length + 1] if spec.method == "moving" else starts)
                for offset in range(spec.block_length):
                    pos = start + offset
                    if pos >= n:
                        if spec.method == "moving":
                            break
                        pos %= n
                    sample.append(ordered[pos])
                    if len(sample) == n:
                        break
        else:
            p = 1.0 / spec.block_length
            while len(sample) < n:
                start = rng.randrange(n)
                while True:
                    sample.append(ordered[start])
                    if len(sample) == n or rng.random() < p:
                        break
                    start = (start + 1) % n
        result.append(sample)
    return result


def block_bootstrap(
    records: Sequence[LongitudinalRecord],
    statistic: Callable[[Sequence[LongitudinalRecord]], float],
    *,
    spec: BlockBootstrapSpec,
) -> RobustInterval:
    """Time-series block bootstrap with an explicit block-generating process."""
    _validate_probability_records(records)
    observed = float(statistic(records))
    values = [float(statistic([records[i] for i in indices])) for indices in block_bootstrap_indices(records, spec)]
    mean = sum(values) / len(values)
    se = sqrt(sum((x - mean) ** 2 for x in values) / (len(values) - 1))
    ordered = sorted(values)
    return RobustInterval(
        observed,
        se,
        ordered[int(0.025 * (len(ordered) - 1))],
        ordered[int(0.975 * (len(ordered) - 1))],
        "time_block",
        f"{spec.method}_block_bootstrap_percentile",
        spec.replicates,
    )


def cluster_robust_mean(
    records: Sequence[LongitudinalRecord],
    values: Sequence[float],
    *,
    unit: str = "entity",
) -> RobustInterval:
    """Huber-White-style sandwich interval for a mean with repeated measures.

    The score contribution is the unit-level deviation from the grand mean.
    The finite-sample variance uses independent units, not observations.
    """
    if len(records) != len(values) or not records:
        raise ValueError("records and values must have equal non-zero length")
    groups = _unit_groups(records, unit)
    if len(groups) < 2:
        raise ValueError("at least two independent units are required")
    means = [sum(values[i] for i in idx) / len(idx) for idx in groups.values()]
    estimate = sum(means) / len(means)
    m = len(means)
    variance = sum((x - estimate) ** 2 for x in means) / (m * (m - 1))
    se = sqrt(max(variance, 0.0))
    return RobustInterval(
        estimate,
        se,
        estimate - _Z95 * se,
        estimate + _Z95 * se,
        unit,
        "cluster_robust_unit_mean_sandwich",
        0,
    )


def rolling_origin_predictions(
    records: Sequence[LongitudinalRecord],
    folds: Sequence[TemporalFold],
    predictor: Callable[[Sequence[LongitudinalRecord], Sequence[LongitudinalRecord]], Sequence[float]],
) -> tuple[LongitudinalRecord, ...]:
    """Fit/predict exactly once per temporal fold and persist the predictions."""
    out: list[LongitudinalRecord] = []
    for fold in folds:
        train = [records[i] for i in fold.train_indices]
        test = [records[i] for i in fold.test_indices]
        if max(r.time for r in train) >= min(r.time for r in test):
            raise RuntimeError("temporal leakage detected")
        predictions = tuple(float(x) for x in predictor(train, test))
        if len(predictions) != len(test):
            raise ValueError("predictor output length does not match test set")
        out.extend(
            LongitudinalRecord(r.entity_id, r.time, r.outcome, p, r.cluster_id, r.observation_id, r.horizon)
            for r, p in zip(test, predictions)
        )
    return tuple(out)


def _calibration_fit(records: Sequence[LongitudinalRecord]) -> tuple[float, float]:
    if len({r.outcome for r in records}) < 2:
        raise ValueError("calibration requires both outcome classes")
    x = [log(r.prediction / (1 - r.prediction)) for r in records if 0 < r.prediction < 1]
    if len(x) != len(records):
        raise ValueError("calibration requires strictly interior probabilities")
    alpha, beta = 0.0, 1.0
    def objective(a: float, b: float) -> float:
        return sum(
            -r.outcome * (a + b * z) + log(1 + exp(a + b * z))
            for z, r in zip(x, records)
        )
    for _ in range(100):
        g0 = g1 = h00 = h01 = h11 = 0.0
        for z, r in zip(x, records):
            eta = alpha + beta * z
            p = 1 / (1 + exp(-eta)) if eta >= 0 else exp(eta) / (1 + exp(eta))
            w = p * (1 - p)
            residual = r.outcome - p
            g0 += residual; g1 += residual * z
            h00 -= w; h01 -= w * z; h11 -= w * z * z
        det = h00 * h11 - h01 * h01
        if det >= 0 or abs(det) < 1e-14:
            raise ValueError("calibration Hessian is non-identifiable")
        if max(abs(g0), abs(g1)) < 1e-10:
            return alpha, beta
        d0 = (g0 * h11 - g1 * h01) / det
        d1 = (h00 * g1 - h01 * g0) / det
        current = objective(alpha, beta)
        step = 1.0
        while step >= 1e-8:
            na, nb = alpha - step * d0, beta - step * d1
            if objective(na, nb) < current:
                alpha, beta = na, nb
                break
            step *= 0.5
        else:
            raise ValueError("calibration line search failed")
    raise ValueError("calibration did not converge")


def temporal_calibration_robust(
    records: Sequence[LongitudinalRecord],
    folds: Sequence[TemporalFold],
    *,
    unit: str = "entity",
    replicates: int = 1000,
    seed: int = 0,
) -> tuple[TemporalCalibrationEstimate, ...]:
    """Fold-specific temporal calibration with unit-respecting uncertainty."""
    results: list[TemporalCalibrationEstimate] = []
    for fold in folds:
        fold_records = [records[i] for i in fold.test_indices]
        intercept, slope = _calibration_fit(fold_records)
        if len(_unit_groups(fold_records, unit)) < 2:
            raise ValueError("temporal calibration uncertainty requires at least two independent units")
        rng = Random(seed + fold.fold)
        groups = _unit_groups(fold_records, unit)
        keys = tuple(groups)
        estimates: list[tuple[float, float]] = []
        for _ in range(replicates):
            sampled = [keys[rng.randrange(len(keys))] for _ in keys]
            sample = [fold_records[i] for key in sampled for i in groups[key]]
            try:
                estimates.append(_calibration_fit(sample))
            except ValueError:
                continue
        if len(estimates) < max(200, replicates // 2):
            raise ValueError("too few successful calibration bootstrap replicates")
        ai = sorted(x[0] for x in estimates); bi = sorted(x[1] for x in estimates)
        results.append(TemporalCalibrationEstimate(
            intercept, slope,
            (ai[int(0.025 * (len(ai) - 1))], ai[int(0.975 * (len(ai) - 1))]),
            (bi[int(0.025 * (len(bi) - 1))], bi[int(0.975 * (len(bi) - 1))]),
            len(estimates), unit,
        ))
    return tuple(results)


def dependent_proper_score_interval(
    records: Sequence[LongitudinalRecord],
    *,
    metric: str = "brier",
    unit: str = "entity",
    replicates: int = 2000,
    seed: int = 0,
) -> RobustInterval:
    """Proper-score interval using independent-unit bootstrap."""
    if metric == "brier":
        statistic = _score
    elif metric == "log_loss":
        statistic = _log_score
    else:
        raise ValueError("metric must be brier or log_loss")
    return cluster_bootstrap(records, statistic, unit=unit, replicates=replicates, seed=seed)


def horizon_scores(records: Sequence[LongitudinalRecord]) -> IntegratedBrierResult:
    """Compute horizon-specific and integrated Brier scores without IID claims."""
    _validate_probability_records(records)
    horizons = sorted({r.horizon for r in records if r.horizon is not None})
    if not horizons:
        raise ValueError("horizon-specific scoring requires horizon on every evaluated prediction")
    scores: list[HorizonScore] = []
    for horizon in horizons:
        subset = [r for r in records if r.horizon == horizon]
        units = len(_unit_groups(subset, "entity"))
        scores.append(HorizonScore(horizon, _score(subset), _log_score(subset), len(subset), units))
    ordered = sorted(scores, key=lambda x: x.horizon)
    if len(ordered) == 1:
        integrated = ordered[0].brier
    else:
        total = sum(b.horizon for b in ordered[1:]) - sum(b.horizon for b in ordered[:-1])
        area = sum(
            0.5 * (a.brier + b.brier) * (b.horizon - a.horizon)
            for a, b in zip(ordered, ordered[1:])
        )
        integrated = area / total if total > 0 else ordered[0].brier
    return IntegratedBrierResult(tuple(ordered), integrated, "trapezoidal_horizon_weighted_brier")


def assess_missingness(records: Sequence[LongitudinalRecord]) -> MissingnessResult:
    """Describe the observation process; no MCAR/MAR/MNAR assumption is inferred."""
    missing_outcome = sum(r.outcome is None for r in records)  # type: ignore[comparison-overlap]
    missing_prediction = sum(r.prediction is None for r in records)  # type: ignore[comparison-overlap]
    counts: dict[Hashable, int] = {}
    for r in records:
        counts[r.entity_id] = counts.get(r.entity_id, 0) + 1
    warning = None
    if len(set(counts.values())) > 1:
        warning = "unequal observation counts; the observation process may be informative"
    return MissingnessResult(
        len(records), missing_outcome, missing_prediction,
        len(records) - max(missing_outcome, missing_prediction),
        len(set(counts.values())) <= 1,
        tuple(sorted(counts.items(), key=lambda x: str(x[0]))), warning,
    )


def validate_frontier_contract(
    *,
    independent_unit: str,
    temporal_validation: bool,
    dependence_aware_uncertainty: bool,
    proper_scoring: bool,
    optimism_correction: bool,
    nested_selection: bool,
    transport_validation: bool,
    missingness_assessed: bool,
    leakage_checked: bool,
) -> FrontierValidationContract:
    blockers: list[str] = []
    if independent_unit not in {"entity", "cluster", "time_block"}:
        blockers.append("independent unit is not explicitly declared")
    if not temporal_validation:
        blockers.append("forward temporal validation is absent")
    if not dependence_aware_uncertainty:
        blockers.append("uncertainty is not dependence-aware")
    if not proper_scoring:
        blockers.append("proper scoring is absent")
    if not optimism_correction:
        blockers.append("optimism correction is absent")
    if not nested_selection:
        blockers.append("nested temporal selection is absent")
    if not transport_validation:
        blockers.append("transport validation is absent")
    if not missingness_assessed:
        blockers.append("missingness/observation process is unassessed")
    if not leakage_checked:
        blockers.append("temporal leakage has not been checked")
    return FrontierValidationContract(
        independent_unit, temporal_validation, dependence_aware_uncertainty,
        proper_scoring, optimism_correction, nested_selection,
        transport_validation, missingness_assessed, leakage_checked,
        not blockers, tuple(blockers),
    )
