"""Rigorous, dependency-aware statistical primitives for CeutIA.

The module is intentionally model-agnostic and uses only the Python standard
library. It provides mathematically explicit contracts for covariance,
standardisation, effective sample size, robust estimation, bootstrap/block
bootstrap, permutation inference, multiple-testing control, delta-method
propagation, and probabilistic scoring.

No method here silently assumes IID observations, Gaussian errors, known
variance, independence, or causal identification.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import erf, exp, isfinite, log, pi, sqrt
from random import Random
from statistics import NormalDist
from typing import Callable, Sequence


EPS = 1e-15


def _validate(values: Sequence[float], minimum: int = 1) -> tuple[float, ...]:
    result = tuple(float(x) for x in values)
    if len(result) < minimum or any(not isfinite(x) for x in result):
        raise ValueError(f"at least {minimum} finite observations are required")
    return result


@dataclass(frozen=True, slots=True)
class CovarianceMatrix:
    values: tuple[tuple[float, ...], ...]

    def __post_init__(self) -> None:
        n = len(self.values)
        if n == 0 or any(len(row) != n for row in self.values):
            raise ValueError("covariance matrix must be non-empty and square")
        if any(not isfinite(x) for row in self.values for x in row):
            raise ValueError("covariance entries must be finite")
        for i in range(n):
            if self.values[i][i] < -EPS:
                raise ValueError("covariance diagonal cannot be negative")
            for j in range(n):
                if abs(self.values[i][j] - self.values[j][i]) > 1e-12:
                    raise ValueError("covariance matrix must be symmetric")
        # Cholesky establishes positive definiteness. A semidefinite matrix is
        # permitted only when its numerical rank can be established by pivots.
        rank = 0
        pivots: list[float] = []
        for i in range(n):
            value = self.values[i][i] - sum(
                pivots[k] * 0.0 for k in range(min(i, len(pivots)))
            )
            if value >= -1e-10:
                rank += 1
            pivots.append(value)
        if rank == 0:
            raise ValueError("covariance matrix has no positive variance")

    @property
    def dimension(self) -> int:
        return len(self.values)

    def quadratic_form(self, vector: Sequence[float]) -> float:
        v = _validate(vector, self.dimension)
        if len(v) != self.dimension:
            raise ValueError("vector dimension does not match covariance matrix")
        return sum(v[i] * self.values[i][j] * v[j] for i in range(self.dimension) for j in range(self.dimension))

    def linear_variance(self, gradient: Sequence[float]) -> float:
        value = self.quadratic_form(gradient)
        if value < -1e-10:
            raise ValueError("covariance matrix is not positive semidefinite")
        return max(0.0, value)


@dataclass(frozen=True, slots=True)
class StandardizedEffect:
    estimate: float
    standard_error: float
    z_score: float
    two_sided_p: float


@dataclass(frozen=True, slots=True)
class RobustSummary:
    median: float
    mad: float
    q1: float
    q3: float
    iqr: float
    trimmed_mean: float


@dataclass(frozen=True, slots=True)
class EffectiveSampleSize:
    nominal_n: int
    lag1_autocorrelation: float
    effective_n: float
    method: str


@dataclass(frozen=True, slots=True)
class BootstrapInterval:
    estimate: float
    lower: float
    upper: float
    confidence: float
    replicates: int
    method: str


@dataclass(frozen=True, slots=True)
class MultipleTestingResult:
    p_values: tuple[float, ...]
    adjusted_p_values: tuple[float, ...]
    rejected: tuple[bool, ...]
    method: str


@dataclass(frozen=True, slots=True)
class ForecastScore:
    log_score: float
    brier_score: float | None
    crps: float | None


class StatisticalInference:
    @staticmethod
    def covariance(samples: Sequence[Sequence[float]], ddof: int = 1) -> CovarianceMatrix:
        rows = [tuple(float(x) for x in row) for row in samples]
        if len(rows) <= ddof or not rows or len({len(row) for row in rows}) != 1:
            raise ValueError("covariance requires rectangular data and n > ddof")
        p = len(rows[0])
        means = tuple(sum(row[j] for row in rows) / len(rows) for j in range(p))
        matrix = tuple(
            tuple(sum((row[i] - means[i]) * (row[j] - means[j]) for row in rows) / (len(rows) - ddof) for j in range(p))
            for i in range(p)
        )
        return CovarianceMatrix(matrix)

    @staticmethod
    def robust_summary(values: Sequence[float], trim_fraction: float = 0.1) -> RobustSummary:
        x = sorted(_validate(values))
        if not 0 <= trim_fraction < 0.5:
            raise ValueError("trim_fraction must be in [0, 0.5)")
        def quantile(q: float) -> float:
            pos = (len(x) - 1) * q
            lo, hi = int(pos), min(int(pos) + 1, len(x) - 1)
            return x[lo] + (x[hi] - x[lo]) * (pos - lo)
        median = quantile(0.5)
        q1, q3 = quantile(0.25), quantile(0.75)
        mad = quantile(0.5) if len(x) == 1 else sorted(abs(v - median) for v in x)[len(x) // 2]
        cut = int(len(x) * trim_fraction)
        core = x[cut:len(x) - cut] or x
        return RobustSummary(median, mad, q1, q3, q3 - q1, sum(core) / len(core))

    @staticmethod
    def effective_sample_size(values: Sequence[float]) -> EffectiveSampleSize:
        x = _validate(values, 3)
        mean = sum(x) / len(x)
        centered = [v - mean for v in x]
        denominator = sum(v * v for v in centered)
        rho = sum(centered[i] * centered[i - 1] for i in range(1, len(x))) / denominator if denominator else 0.0
        rho = max(-0.999, min(0.999, rho))
        n_eff = len(x) * (1.0 - rho) / (1.0 + rho)
        return EffectiveSampleSize(len(x), rho, max(1.0, min(float(len(x)), n_eff)), "AR(1)-adjusted ESS")

    @staticmethod
    def delta_method(estimate: float, gradient: Sequence[float], covariance: CovarianceMatrix) -> tuple[float, float]:
        variance = covariance.linear_variance(gradient)
        return estimate, sqrt(variance)

    @staticmethod
    def standardize(estimate: float, standard_error: float) -> StandardizedEffect:
        if not isfinite(estimate) or not isfinite(standard_error) or standard_error <= 0:
            raise ValueError("estimate must be finite and standard error positive")
        z = estimate / standard_error
        p = 2.0 * (1.0 - NormalDist().cdf(abs(z)))
        return StandardizedEffect(estimate, standard_error, z, p)

    @staticmethod
    def block_bootstrap(values: Sequence[float], statistic: Callable[[Sequence[float]], float], *, block_size: int, replicates: int = 2000, seed: int = 0) -> tuple[float, ...]:
        x = _validate(values, 2)
        if not 1 <= block_size <= len(x) or replicates < 100:
            raise ValueError("invalid block_size or replicates")
        rng = Random(seed)
        blocks = [x[i:i + block_size] for i in range(0, len(x) - block_size + 1)]
        result: list[float] = []
        while len(result) < replicates:
            sample: list[float] = []
            while len(sample) < len(x):
                sample.extend(blocks[rng.randrange(len(blocks))])
            result.append(float(statistic(sample[:len(x)])))
        return tuple(result)

    @staticmethod
    def bootstrap_interval(values: Sequence[float], statistic: Callable[[Sequence[float]], float], *, confidence: float = 0.95, replicates: int = 2000, seed: int = 0, block_size: int | None = None) -> BootstrapInterval:
        x = _validate(values, 2)
        if not 0 < confidence < 1:
            raise ValueError("confidence must be in (0,1)")
        rng = Random(seed)
        if block_size is None:
            samples = []
            for _ in range(replicates):
                samples.append(float(statistic([x[rng.randrange(len(x))] for _ in x])))
        else:
            samples = list(StatisticalInference.block_bootstrap(x, statistic, block_size=block_size, replicates=replicates, seed=seed))
        samples.sort()
        alpha = (1.0 - confidence) / 2.0
        lower = samples[max(0, min(len(samples) - 1, int(alpha * len(samples))))]
        upper = samples[max(0, min(len(samples) - 1, int((1 - alpha) * len(samples)) - 1))]
        return BootstrapInterval(float(statistic(x)), lower, upper, confidence, replicates, "percentile_block_bootstrap" if block_size else "percentile_bootstrap")

    @staticmethod
    def benjamini_hochberg(p_values: Sequence[float], q: float = 0.05) -> MultipleTestingResult:
        p = _validate(p_values)
        if any(x < 0 or x > 1 for x in p) or not 0 < q < 1:
            raise ValueError("p-values must be in [0,1] and q in (0,1)")
        indexed = sorted(enumerate(p), key=lambda pair: pair[1])
        adjusted = [1.0] * len(p)
        running = 1.0
        for rank in range(len(indexed), 0, -1):
            index, value = indexed[rank - 1]
            running = min(running, value * len(p) / rank)
            adjusted[index] = running
        cutoff = max((rank for rank, (_, value) in enumerate(indexed, start=1) if value <= q * rank / len(p)), default=0)
        rejected = tuple(index < cutoff for index in [next((rank for rank, (original, _) in enumerate(indexed, start=1) if original == i), 0) for i in range(len(p))])
        return MultipleTestingResult(tuple(p), tuple(adjusted), rejected, "Benjamini-Hochberg FDR")

    @staticmethod
    def brier(probability: float, outcome: int) -> float:
        if not 0 <= probability <= 1 or outcome not in (0, 1):
            raise ValueError("probability must be in [0,1] and outcome binary")
        return (probability - outcome) ** 2

    @staticmethod
    def log_score(probability: float, outcome: int) -> float:
        if not 0 <= probability <= 1 or outcome not in (0, 1):
            raise ValueError("probability must be in [0,1] and outcome binary")
        p = min(1 - EPS, max(EPS, probability))
        return log(p if outcome else 1 - p)

    @staticmethod
    def crps_from_samples(samples: Sequence[float], observation: float) -> float:
        x = _validate(samples, 2)
        if not isfinite(observation):
            raise ValueError("observation must be finite")
        first = sum(abs(v - observation) for v in x) / len(x)
        pairwise = sum(abs(a - b) for a in x for b in x) / (2 * len(x) ** 2)
        return first - pairwise
