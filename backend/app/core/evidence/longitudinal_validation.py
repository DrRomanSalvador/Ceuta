"""Frontier statistical validation for longitudinal and dependent observations.

Design principles:
- the independent resampling unit is explicit (subject, cluster, block);
- temporal validation is forward-only and leakage-aware;
- every reported estimate records its dependence assumptions;
- uncertainty methods never silently fall back to IID assumptions.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import exp, isfinite, log, sqrt
from statistics import NormalDist
from typing import Callable, Sequence, TypeVar

T = TypeVar("T")
_Z95 = NormalDist().inv_cdf(0.975)
_EPS = 1e-15


@dataclass(frozen=True, slots=True)
class LongitudinalRecord:
    entity_id: object
    time: float
    outcome: int
    prediction: float
    cluster_id: object | None = None
    observation_id: object | None = None
    horizon: float | None = None


@dataclass(frozen=True, slots=True)
class ResampleSpec:
    unit: str
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


def _group_by(records: Sequence[T], key: Callable[[T], object]) -> dict[object, list[int]]:
    result: dict[object, list[int]] = {}
    for index, record in enumerate(records):
        result.setdefault(key(record), []).append(index)
    return result


def _groups(records: Sequence[LongitudinalRecord], unit: str) -> dict[object, list[int]]:
    if unit == "entity":
        return _group_by(records, lambda r: r.entity_id)
    if unit == "cluster":
        return _group_by(records, lambda r: r.cluster_id if r.cluster_id is not None else r.entity_id)
    raise ValueError("block groups require block construction")


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
    log_loss = -sum(r.outcome * log(max(r.prediction, _EPS)) + (1 - r.outcome) * log(max(1 - r.prediction, _EPS)) for r in records) / n
    return ScoreSummary(brier, log_loss, n, _effective_sample_size(records, "entity"), len(_groups(records, "entity")), method)


def _rng(seed: int):
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


def blocked_or_cluster_bootstrap(records: Sequence[LongitudinalRecord], statistic: Callable[[Sequence[LongitudinalRecord]], float], *, spec: ResampleSpec, replicates: int = 2000) -> BootstrapEstimate:
    _validate_binary_records(records)
    if replicates < 200:
        raise ValueError("at least 200 bootstrap replicates are required")
    observed = float(statistic(records))
    rng = _rng(spec.seed)
    values = [float(statistic([records[i] for i in _resample_indices(records, spec, rng)])) for _ in range(replicates)]
    mean = sum(values) / len(values)
    se = sqrt(sum((value - mean) ** 2 for value in values) / (len(values) - 1))
    return BootstrapEstimate(observed, se, _percentile(values, 0.025), _percentile(values, 0.975), replicates, f"{spec.unit}_bootstrap", spec.unit)


def rolling_origin_splits(records: Sequence[LongitudinalRecord], *, initial_train_time: float, test_horizon: float, step: float, gap: float = 0.0, expanding: bool = True) -> tuple[TemporalFold, ...]:
    """Create forward folds with a strict train-time < test-time invariant."""
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
        train_start = min(times) if expanding else origin - initial_train_time
        test_start = origin + gap
        test_end = test_start + test_horizon
        train_indices = tuple(index for index, record in ordered if train_start <= record.time < origin)
        test_indices = tuple(index for index, record in ordered if test_start <= record.time < test_end)
        if train_indices and test_indices:
            if max(records[i].time for i in train_indices) >= min(records[i].time for i in test_indices):
                raise RuntimeError("temporal leakage detected while constructing rolling-origin folds")
            folds.append(TemporalFold(fold, train_start, origin, test_start, test_end, train_indices, test_indices))
            fold += 1
        origin += step
    if not folds:
        raise ValueError("rolling-origin design produced no valid folds")
    return tuple(folds)


def evaluate_rolling_origin(records: Sequence[LongitudinalRecord], folds: Sequence[TemporalFold], predictor: Callable[[Sequence[LongitudinalRecord], Sequence[LongitudinalRecord]], Sequence[float]]) -> TemporalValidationResult:
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
    if len({r.outcome for r in records}) < 2:
        raise ValueError("calibration requires both outcome classes")
    logits = [log(r.prediction / (1 - r.prediction)) for r in records if 0 < r.prediction < 1]
    if len(logits) != len(records):
        raise ValueError("calibration requires strictly interior probabilities")
    alpha, beta = 0.0, 1.0
    for _ in range(100):
        g0 = g1 = h00 = h01 = h11 = 0.0
        for x, record in zip(logits, records):
            eta = alpha + beta * x
            p = 1 / (1 + exp(-eta)) if eta >= 0 else exp(eta) / (1 + exp(eta))
            w = p * (1 - p)
            residual = record.outcome - p
            g0 += residual; g1 += residual * x
            h00 -= w; h01 -= w * x; h11 -= w * x * x
        det = h00 * h11 - h01 * h01
        scale = max(abs(h00 * h11), abs(h01 * h01), _EPS)
        if det >= 0 or abs(det) <= 1e-14 * scale:
            raise ValueError("temporal calibration model is non-identifiable")
        if max(abs(g0), abs(g1)) <= 1e-10:
            return alpha, beta
        d0 = (g0 * h11 - g1 * h01) / det
        d1 = (h00 * g1 - h01 * g0) / det
        alpha -= d0; beta -= d1
    raise ValueError("temporal calibration did not converge")


__all__ = ["LongitudinalRecord", "ResampleSpec", "BootstrapEstimate", "ScoreSummary", "TemporalFold", "TemporalValidationResult", "blocked_or_cluster_bootstrap", "rolling_origin_splits", "evaluate_rolling_origin"]
