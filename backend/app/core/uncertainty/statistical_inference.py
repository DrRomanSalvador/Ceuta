"""Rigorous dependency-aware statistical primitives for CeutIA.

No method silently assumes IID data, Gaussian errors, independence or causal
identification. Methods requiring those assumptions state them explicitly.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log, sqrt
from random import Random
from statistics import NormalDist
from typing import Callable, Sequence

EPS = 1e-15


def _validate(values: Sequence[float], minimum: int = 1) -> tuple[float, ...]:
    result = tuple(float(x) for x in values)
    if len(result) < minimum or any(not isfinite(x) for x in result):
        raise ValueError(f"at least {minimum} finite observations are required")
    return result


def _median(values: Sequence[float]) -> float:
    x = sorted(values)
    if not x:
        raise ValueError("median requires observations")
    n = len(x)
    return x[n // 2] if n % 2 else (x[n // 2 - 1] + x[n // 2]) / 2.0


def _symmetric_eigenvalues(matrix: tuple[tuple[float, ...], ...]) -> tuple[float, ...]:
    """Jacobi eigensolver for small symmetric matrices; used only for PSD checks."""
    a = [list(row) for row in matrix]
    n = len(a)
    for _ in range(max(20, 20 * n * n)):
        p, q = 0, 1 if n > 1 else 0
        maximum = 0.0
        for i in range(n):
            for j in range(i + 1, n):
                if abs(a[i][j]) > maximum:
                    maximum, p, q = abs(a[i][j]), i, j
        if maximum <= 1e-12:
            break
        if abs(a[p][p] - a[q][q]) <= EPS:
            angle = 0.7853981633974483
        else:
            angle = 0.5 * __import__("math").atan2(2 * a[p][q], a[p][p] - a[q][q])
        c, s = __import__("math").cos(angle), __import__("math").sin(angle)
        for k in range(n):
            apk, aqk = a[p][k], a[q][k]
            a[p][k], a[q][k] = c * apk + s * aqk, -s * apk + c * aqk
        for k in range(n):
            akp, akq = a[k][p], a[k][q]
            a[k][p], a[k][q] = c * akp + s * akq, -s * akp + c * akq
    return tuple(a[i][i] for i in range(n))


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
            if self.values[i][i] < -1e-10:
                raise ValueError("covariance diagonal cannot be negative")
            for j in range(i + 1, n):
                if abs(self.values[i][j] - self.values[j][i]) > 1e-12:
                    raise ValueError("covariance matrix must be symmetric")
        if min(_symmetric_eigenvalues(self.values)) < -1e-9:
            raise ValueError("covariance matrix must be positive semidefinite")

    @property
    def dimension(self) -> int:
        return len(self.values)

    def quadratic_form(self, vector: Sequence[float]) -> float:
        v = tuple(float(x) for x in vector)
        if len(v) != self.dimension or any(not isfinite(x) for x in v):
            raise ValueError("vector dimension or finiteness is invalid")
        return sum(v[i] * self.values[i][j] * v[j] for i in range(self.dimension) for j in range(self.dimension))

    def linear_variance(self, gradient: Sequence[float]) -> float:
        value = self.quadratic_form(gradient)
        if value < -1e-9:
            raise ValueError("negative propagated variance")
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
class PermutationResult:
    observed: float
    p_value: float
    permutations: int
    alternative: str


class StatisticalInference:
    @staticmethod
    def covariance(samples: Sequence[Sequence[float]], ddof: int = 1) -> CovarianceMatrix:
        rows = [tuple(float(x) for x in row) for row in samples]
        if not rows or len(rows) <= ddof or len({len(row) for row in rows}) != 1 or not rows[0]:
            raise ValueError("covariance requires rectangular data and n > ddof")
        if any(not isfinite(x) for row in rows for x in row):
            raise ValueError("covariance data must be finite")
        n, p = len(rows), len(rows[0])
        means = tuple(sum(row[j] for row in rows) / n for j in range(p))
        return CovarianceMatrix(tuple(tuple(sum((row[i] - means[i]) * (row[j] - means[j]) for row in rows) / (n - ddof) for j in range(p)) for i in range(p)))

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
        deviations = sorted(abs(v - median) for v in x)
        cut = int(len(x) * trim_fraction)
        core = x[cut:len(x) - cut] or x
        return RobustSummary(median, _median(deviations), quantile(0.25), quantile(0.75), quantile(0.75) - quantile(0.25), sum(core) / len(core))

    @staticmethod
    def effective_sample_size(values: Sequence[float]) -> EffectiveSampleSize:
        x = _validate(values, 3)
        mean = sum(x) / len(x)
        centered = [v - mean for v in x]
        denominator = sum(v * v for v in centered)
        rho = sum(centered[i] * centered[i - 1] for i in range(1, len(x))) / denominator if denominator else 0.0
        rho = max(-0.999, min(0.999, rho))
        n_eff = len(x) * (1.0 - rho) / (1.0 + rho)
        return EffectiveSampleSize(len(x), rho, max(1.0, min(float(len(x)), n_eff)), "AR(1)-adjusted ESS; valid as a first-order dependence diagnostic")

    @staticmethod
    def delta_method(estimate: float, gradient: Sequence[float], covariance: CovarianceMatrix) -> tuple[float, float]:
        return estimate, sqrt(covariance.linear_variance(gradient))

    @staticmethod
    def standardize(estimate: float, standard_error: float) -> StandardizedEffect:
        if not isfinite(estimate) or not isfinite(standard_error) or standard_error <= 0:
            raise ValueError("estimate must be finite and standard error positive")
        z = estimate / standard_error
        return StandardizedEffect(estimate, standard_error, z, 2.0 * (1.0 - NormalDist().cdf(abs(z))))

    @staticmethod
    def block_bootstrap(values: Sequence[float], statistic: Callable[[Sequence[float]], float], *, block_size: int, replicates: int = 2000, seed: int = 0) -> tuple[float, ...]:
        x = _validate(values, 2)
        if not 1 <= block_size <= len(x) or replicates < 100:
            raise ValueError("invalid block_size or replicates")
        rng = Random(seed)
        blocks = [x[i:i + block_size] for i in range(len(x) - block_size + 1)]
        out: list[float] = []
        while len(out) < replicates:
            sample: list[float] = []
            while len(sample) < len(x):
                sample.extend(blocks[rng.randrange(len(blocks))])
            out.append(float(statistic(sample[:len(x)])))
        return tuple(out)

    @staticmethod
    def bootstrap_interval(values: Sequence[float], statistic: Callable[[Sequence[float]], float], *, confidence: float = 0.95, replicates: int = 2000, seed: int = 0, block_size: int | None = None) -> BootstrapInterval:
        x = _validate(values, 2)
        if not 0 < confidence < 1 or replicates < 100:
            raise ValueError("invalid confidence or replicates")
        rng = Random(seed)
        samples = list(StatisticalInference.block_bootstrap(x, statistic, block_size=block_size, replicates=replicates, seed=seed)) if block_size else [float(statistic([x[rng.randrange(len(x))] for _ in x])) for _ in range(replicates)]
        samples.sort()
        alpha = (1.0 - confidence) / 2.0
        lo = samples[min(len(samples) - 1, int(alpha * len(samples)))]
        hi = samples[min(len(samples) - 1, max(0, int((1 - alpha) * len(samples)) - 1))]
        return BootstrapInterval(float(statistic(x)), lo, hi, confidence, replicates, "percentile_block_bootstrap" if block_size else "percentile_bootstrap")

    @staticmethod
    def benjamini_hochberg(p_values: Sequence[float], q: float = 0.05) -> MultipleTestingResult:
        p = _validate(p_values)
        if any(x < 0 or x > 1 for x in p) or not 0 < q < 1:
            raise ValueError("p-values must be in [0,1] and q in (0,1)")
        indexed = sorted(enumerate(p), key=lambda pair: pair[1])
        m = len(p)
        adjusted = [1.0] * m
        running = 1.0
        for rank in range(m, 0, -1):
            original, value = indexed[rank - 1]
            running = min(running, value * m / rank)
            adjusted[original] = min(1.0, running)
        cutoff = max((rank for rank, (_, value) in enumerate(indexed, start=1) if value <= q * rank / m), default=0)
        rejected_set = {original for rank, (original, _) in enumerate(indexed, start=1) if rank <= cutoff}
        return MultipleTestingResult(tuple(p), tuple(adjusted), tuple(i in rejected_set for i in range(m)), "Benjamini-Hochberg FDR")

    @staticmethod
    def permutation_test(left: Sequence[float], right: Sequence[float], statistic: Callable[[Sequence[float], Sequence[float]], float], *, permutations: int = 5000, seed: int = 0, alternative: str = "two-sided") -> PermutationResult:
        a, b = _validate(left), _validate(right)
        if permutations < 100 or alternative not in {"two-sided", "greater", "less"}:
            raise ValueError("invalid permutations or alternative")
        observed = float(statistic(a, b))
        pooled = list(a + b)
        rng = Random(seed)
        extreme = 0
        for _ in range(permutations):
            rng.shuffle(pooled)
            candidate = float(statistic(pooled[:len(a)], pooled[len(a):]))
            if alternative == "greater" and candidate >= observed:
                extreme += 1
            elif alternative == "less" and candidate <= observed:
                extreme += 1
            elif alternative == "two-sided" and abs(candidate) >= abs(observed):
                extreme += 1
        return PermutationResult(observed, (extreme + 1) / (permutations + 1), permutations, alternative)

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
