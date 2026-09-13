"""Multivariate, robust and non-linear state estimation for CeutIA.

This module is the higher-rigor state-estimation layer. It is deliberately
system-agnostic: the same mathematics can represent preventive-health
trajectories, epidemiological surveillance, environmental systems, population
signals, industrial telemetry, or other coupled dynamic systems.

Design principles
-----------------
* Separate latent state from measurements and from causal interpretation.
* Preserve irregular time, missing channels, correlated measurement error and
  observation-process metadata instead of silently imputing them.
* Support multivariate covariance, time-varying dynamics, robust innovation
  handling and fixed-interval smoothing.
* Provide an Extended Kalman Filter for differentiable nonlinear systems and a
  bootstrap particle filter for non-Gaussian/nonlinear systems.
* Never turn an innovation, residual or filtered trajectory into causal
  evidence by itself.

The implementation intentionally exposes assumptions and diagnostics. A model
must declare its transition/observation equations and uncertainty rather than
having the estimator invent them.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import exp, isfinite, log, pi, sqrt
from random import Random
from typing import Callable, Sequence

from ..errors import ContractViolation, TemporalViolation

Vector = tuple[float, ...]
Matrix = tuple[tuple[float, ...], ...]

_EPS = 1e-12


def _vector(values: Sequence[float], name: str) -> Vector:
    out = tuple(float(v) for v in values)
    if not out or any(not isfinite(v) for v in out):
        raise ContractViolation(f"{name} must contain finite values")
    return out


def _matrix(values: Sequence[Sequence[float]], rows: int | None = None, cols: int | None = None, name: str = "matrix") -> Matrix:
    out = tuple(tuple(float(v) for v in row) for row in values)
    if not out or not out[0]:
        raise ContractViolation(f"{name} must be non-empty")
    ncols = len(out[0])
    if any(len(row) != ncols for row in out) or any(not isfinite(v) for row in out for v in row):
        raise ContractViolation(f"{name} must be rectangular and finite")
    if rows is not None and len(out) != rows:
        raise ContractViolation(f"{name} has invalid row dimension")
    if cols is not None and ncols != cols:
        raise ContractViolation(f"{name} has invalid column dimension")
    return out


def _zeros(rows: int, cols: int) -> Matrix:
    return tuple(tuple(0.0 for _ in range(cols)) for _ in range(rows))


def _identity(n: int) -> Matrix:
    return tuple(tuple(1.0 if i == j else 0.0 for j in range(n)) for i in range(n))


def _add(a: Matrix, b: Matrix) -> Matrix:
    return tuple(tuple(a[i][j] + b[i][j] for j in range(len(a[0]))) for i in range(len(a)))


def _sub(a: Matrix, b: Matrix) -> Matrix:
    return tuple(tuple(a[i][j] - b[i][j] for j in range(len(a[0]))) for i in range(len(a)))


def _scale(a: Matrix, scalar: float) -> Matrix:
    return tuple(tuple(scalar * v for v in row) for row in a)


def _matmul(a: Matrix, b: Matrix) -> Matrix:
    if len(a[0]) != len(b):
        raise ContractViolation("matrix dimensions are incompatible")
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(len(b))) for j in range(len(b[0]))) for i in range(len(a)))


def _transpose(a: Matrix) -> Matrix:
    return tuple(tuple(a[i][j] for i in range(len(a))) for j in range(len(a[0])))


def _matvec(a: Matrix, x: Vector) -> Vector:
    if len(a[0]) != len(x):
        raise ContractViolation("matrix/vector dimensions are incompatible")
    return tuple(sum(a[i][j] * x[j] for j in range(len(x))) for i in range(len(a)))


def _outer(a: Vector, b: Vector) -> Matrix:
    return tuple(tuple(x * y for y in b) for x in a)


def _symmetrize(a: Matrix) -> Matrix:
    return tuple(tuple((a[i][j] + a[j][i]) / 2.0 for j in range(len(a))) for i in range(len(a)))


def _inverse(a: Matrix) -> Matrix:
    """Gauss-Jordan inverse with partial pivoting for small scientific matrices."""
    n = len(a)
    if n != len(a[0]):
        raise ContractViolation("matrix must be square")
    aug = [list(a[i]) + list(_identity(n)[i]) for i in range(n)]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) <= _EPS:
            raise ContractViolation("singular or numerically singular covariance matrix")
        aug[col], aug[pivot] = aug[pivot], aug[col]
        scale = aug[col][col]
        aug[col] = [v / scale for v in aug[col]]
        for row in range(n):
            if row == col:
                continue
            factor = aug[row][col]
            if factor:
                aug[row] = [aug[row][j] - factor * aug[col][j] for j in range(2 * n)]
    return tuple(tuple(aug[i][n + j] for j in range(n)) for i in range(n))


def _quadratic(x: Vector, covariance: Matrix) -> float:
    inv = _inverse(covariance)
    return sum(x[i] * inv[i][j] * x[j] for i in range(len(x)) for j in range(len(x)))


def _log_gaussian_density(residual: Vector, covariance: Matrix) -> float:
    inv = _inverse(covariance)
    q = sum(residual[i] * inv[i][j] * residual[j] for i in range(len(residual)) for j in range(len(residual)))
    # determinant by elimination; covariance matrices used here are small.
    work = [list(row) for row in covariance]
    determinant = 1.0
    for col in range(len(work)):
        pivot = max(range(col, len(work)), key=lambda r: abs(work[r][col]))
        if abs(work[pivot][col]) <= _EPS:
            return float("-inf")
        if pivot != col:
            work[col], work[pivot] = work[pivot], work[col]
            determinant *= -1.0
        pivot_value = work[col][col]
        determinant *= pivot_value
        for row in range(col + 1, len(work)):
            factor = work[row][col] / pivot_value
            for j in range(col + 1, len(work)):
                work[row][j] -= factor * work[col][j]
    if determinant <= 0.0 or not isfinite(determinant):
        raise ContractViolation("covariance must be positive definite for Gaussian likelihood")
    n = len(residual)
    return -0.5 * (n * log(2.0 * pi) + log(determinant) + q)


def _finite_difference_jacobian(function: Callable[[Vector], Vector], x: Vector, step: float = 1e-5) -> Matrix:
    base = list(x)
    f0 = function(tuple(base))
    cols: list[Vector] = []
    for j in range(len(x)):
        h = step * max(1.0, abs(x[j]))
        xp, xm = base[:], base[:]
        xp[j] += h
        xm[j] -= h
        fp, fm = function(tuple(xp)), function(tuple(xm))
        cols.append(tuple((fp[i] - fm[i]) / (2.0 * h) for i in range(len(f0))))
    return tuple(tuple(cols[j][i] for j in range(len(x))) for i in range(len(f0)))


@dataclass(frozen=True, slots=True)
class ObservationPacket:
    """One multichannel measurement at an exact observation time.

    ``observed`` contains only available channels. ``indices`` maps them back
    to the full observation vector. ``covariance`` is the covariance of those
    available channels, allowing correlated sensors or correlated surveillance
    measurements.
    """

    as_of: datetime
    observed: Vector
    indices: tuple[int, ...]
    covariance: Matrix
    source_ids: tuple[str, ...] = ()
    quality_weight: float = 1.0
    observation_process_version: str | None = None

    def __post_init__(self) -> None:
        if self.as_of.tzinfo is None or self.as_of.utcoffset() is None:
            raise TemporalViolation("observation time must be timezone-aware")
        if len(self.observed) != len(self.indices) or len(self.observed) == 0:
            raise ContractViolation("observed values and indices must have equal non-zero length")
        if len(set(self.indices)) != len(self.indices) or min(self.indices) < 0:
            raise ContractViolation("observation indices must be unique and non-negative")
        _matrix(self.covariance, len(self.observed), len(self.observed), "observation covariance")
        if not 0.0 < self.quality_weight <= 1.0:
            raise ContractViolation("quality_weight must be in (0, 1]")


@dataclass(frozen=True, slots=True)
class StateEstimateVector:
    as_of: datetime
    mean: Vector
    covariance: Matrix
    prior_mean: Vector
    prior_covariance: Matrix
    innovation: Vector | None
    innovation_covariance: Matrix | None
    mahalanobis_distance: float | None
    robust_weight: float
    observation_used: bool


@dataclass(frozen=True, slots=True)
class SmoothingResult:
    filtered: tuple[StateEstimateVector, ...]
    smoothed_means: tuple[Vector, ...]
    smoothed_covariances: tuple[Matrix, ...]
    method: str


@dataclass(frozen=True, slots=True)
class FilterDiagnostics:
    observations: int
    used: int
    missing_updates: int
    robust_downweights: int
    mean_mahalanobis: float | None
    max_mahalanobis: float | None
    assumptions: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class StateSpaceSpecification:
    """Explicit state-space model contract.

    Transition and observation operators may be time-varying. ``process_noise``
    is Q per transition and ``observation_noise`` is R for the corresponding
    observation packet before its quality adjustment.
    """

    state_dimension: int
    observation_dimension: int
    transition: Callable[[datetime, float], Matrix]
    process_noise: Callable[[datetime, float], Matrix]
    observation_matrix: Callable[[datetime], Matrix]
    initial_mean: Vector
    initial_covariance: Matrix

    def __post_init__(self) -> None:
        if self.state_dimension < 1 or self.observation_dimension < 1:
            raise ContractViolation("state and observation dimensions must be positive")
        if len(self.initial_mean) != self.state_dimension:
            raise ContractViolation("initial mean dimension mismatch")
        _matrix(self.initial_covariance, self.state_dimension, self.state_dimension, "initial covariance")


class RobustKalmanFilter:
    """Multivariate Kalman filter with explicit missingness and robust innovations.

    Linear-Gaussian filtering is exact under its stated model. Robust innovation
    weighting is a sensitivity mechanism for contamination/model mismatch; it
    is not a proof that an observation is erroneous. Large innovations may be
    genuine state transitions and therefore remain represented in diagnostics.
    """

    def __init__(self, specification: StateSpaceSpecification, huber_k: float = 3.0) -> None:
        if huber_k <= 0.0 or not isfinite(huber_k):
            raise ContractViolation("huber_k must be positive and finite")
        self.specification = specification
        self.huber_k = float(huber_k)

    def _submatrix(self, matrix: Matrix, indices: tuple[int, ...]) -> Matrix:
        return tuple(tuple(matrix[i][j] for j in indices) for i in indices)

    def _columns(self, matrix: Matrix, indices: tuple[int, ...]) -> Matrix:
        return tuple(tuple(matrix[i][j] for j in indices) for i in range(len(matrix)))

    def _select_rows(self, matrix: Matrix, indices: tuple[int, ...]) -> Matrix:
        return tuple(matrix[i] for i in indices)

    def run(self, packets: Sequence[ObservationPacket]) -> tuple[tuple[StateEstimateVector, ...], FilterDiagnostics]:
        previous_time: datetime | None = None
        mean = self.specification.initial_mean
        covariance = self.specification.initial_covariance
        estimates: list[StateEstimateVector] = []
        distances: list[float] = []
        downweighted = 0
        used = 0
        for packet in packets:
            if previous_time is not None and packet.as_of <= previous_time:
                raise TemporalViolation("observation packets must be strictly time ordered")
            dt = 0.0 if previous_time is None else (packet.as_of - previous_time).total_seconds()
            if dt < 0.0:
                raise TemporalViolation("negative elapsed time")
            transition = _matrix(self.specification.transition(packet.as_of, dt), self.specification.state_dimension, self.specification.state_dimension, "transition")
            q = _matrix(self.specification.process_noise(packet.as_of, dt), self.specification.state_dimension, self.specification.state_dimension, "process covariance")
            prior_mean = _matvec(transition, mean)
            prior_covariance = _symmetrize(_add(_matmul(_matmul(transition, covariance), _transpose(transition)), q))
            if not packet.observed:
                mean, covariance = prior_mean, prior_covariance
                estimates.append(StateEstimateVector(packet.as_of, mean, covariance, prior_mean, prior_covariance, None, None, None, 1.0, False))
                previous_time = packet.as_of
                continue
            h_full = _matrix(self.specification.observation_matrix(packet.as_of), self.specification.observation_dimension, self.specification.state_dimension, "observation matrix")
            h = self._select_rows(h_full, packet.indices)
            predicted = _matvec(h, prior_mean)
            innovation = tuple(packet.observed[i] - predicted[k] for k, i in enumerate(range(len(packet.observed))))
            r = _scale(packet.covariance, 1.0 / packet.quality_weight)
            s = _symmetrize(_add(_matmul(_matmul(h, prior_covariance), _transpose(h)), r))
            distance = max(0.0, _quadratic(innovation, s))
            distances.append(distance)
            dimension = len(innovation)
            # Huber downweighting uses Mahalanobis radius rather than a single
            # coordinate, preserving correlated multichannel structure.
            radius = sqrt(distance)
            weight = 1.0 if radius <= self.huber_k else self.huber_k / max(radius, _EPS)
            if weight < 1.0:
                downweighted += 1
            robust_r = _scale(r, 1.0 / max(weight, _EPS))
            s_robust = _symmetrize(_add(_matmul(_matmul(h, prior_covariance), _transpose(h)), robust_r))
            gain = _matmul(_matmul(prior_covariance, _transpose(h)), _inverse(s_robust))
            mean = tuple(prior_mean[i] + sum(gain[i][j] * innovation[j] for j in range(dimension)) for i in range(self.specification.state_dimension))
            # Joseph form improves numerical covariance integrity.
            identity = _identity(self.specification.state_dimension)
            kh = _matmul(gain, h)
            a = _sub(identity, kh)
            covariance = _symmetrize(_add(_matmul(_matmul(a, prior_covariance), _transpose(a)), _matmul(_matmul(gain, robust_r), _transpose(gain))))
            estimates.append(StateEstimateVector(packet.as_of, mean, covariance, prior_mean, prior_covariance, innovation, s_robust, distance, weight, True))
            used += 1
            previous_time = packet.as_of
        diagnostics = FilterDiagnostics(
            observations=len(packets),
            used=used,
            missing_updates=len(packets) - used,
            robust_downweights=downweighted,
            mean_mahalanobis=(sum(distances) / len(distances)) if distances else None,
            max_mahalanobis=max(distances) if distances else None,
            assumptions=(
                "linear transition and observation operators conditional on supplied matrices",
                "process and measurement errors are represented by supplied covariance matrices",
                "robust Huber weighting is a sensitivity mechanism, not an outlier truth label",
                "missing channels are skipped rather than silently imputed",
                "filtered state is not a causal effect estimate",
            ),
        )
        return tuple(estimates), diagnostics

    def smooth(self, packets: Sequence[ObservationPacket]) -> SmoothingResult:
        filtered, _ = self.run(packets)
        if not filtered:
            return SmoothingResult((), (), (), "Rauch-Tung-Striebel fixed-interval smoother")
        means = [e.mean for e in filtered]
        covariances = [e.covariance for e in filtered]
        for k in range(len(filtered) - 2, -1, -1):
            current = filtered[k]
            future = filtered[k + 1]
            dt = (future.as_of - current.as_of).total_seconds()
            transition = self.specification.transition(future.as_of, dt)
            predicted_covariance = future.prior_covariance
            gain = _matmul(_matmul(current.covariance, _transpose(transition)), _inverse(predicted_covariance))
            delta = tuple(means[k + 1][i] - future.prior_mean[i] for i in range(self.specification.state_dimension))
            means[k] = tuple(current.mean[i] + sum(gain[i][j] * delta[j] for j in range(self.specification.state_dimension)) for i in range(self.specification.state_dimension))
            covariances[k] = _symmetrize(_add(current.covariance, _matmul(_matmul(gain, _sub(covariances[k + 1], predicted_covariance)), _transpose(gain))))
        return SmoothingResult(tuple(filtered), tuple(means), tuple(covariances), "Rauch-Tung-Striebel fixed-interval smoother")


class ExtendedKalmanFilter:
    """First-order nonlinear state-space estimator.

    The caller supplies differentiable transition/observation functions and
    Jacobians. If a Jacobian is omitted, central finite differences are used
    with an explicit numerical-approximation assumption.
    """

    def __init__(self, mean: Vector, covariance: Matrix, process_covariance: Matrix, observation_covariance: Matrix, huber_k: float = 3.0) -> None:
        self.mean = _vector(mean, "mean")
        self.covariance = _matrix(covariance, len(mean), len(mean), "covariance")
        self.process_covariance = _matrix(process_covariance, len(mean), len(mean), "process covariance")
        self.observation_covariance = observation_covariance
        self.huber_k = float(huber_k)

    def step(
        self,
        transition: Callable[[Vector, float], Vector],
        observation: Vector,
        observation_function: Callable[[Vector], Vector],
        *,
        dt: float,
        transition_jacobian: Callable[[Vector, float], Matrix] | None = None,
        observation_jacobian: Callable[[Vector], Matrix] | None = None,
    ) -> StateEstimateVector:
        if dt < 0.0 or not isfinite(dt):
            raise TemporalViolation("dt must be finite and non-negative")
        prior_mean = _vector(transition(self.mean, dt), "transition output")
        f_j = transition_jacobian(prior_mean, dt) if transition_jacobian else _finite_difference_jacobian(lambda x: transition(x, dt), self.mean)
        prior_covariance = _symmetrize(_add(_matmul(_matmul(f_j, self.covariance), _transpose(f_j)), self.process_covariance))
        y = _vector(observation, "observation")
        predicted = _vector(observation_function(prior_mean), "observation prediction")
        if len(y) != len(predicted):
            raise ContractViolation("observation dimension mismatch")
        h_j = observation_jacobian(prior_mean) if observation_jacobian else _finite_difference_jacobian(observation_function, prior_mean)
        r = _matrix(self.observation_covariance, len(y), len(y), "observation covariance")
        innovation = tuple(y[i] - predicted[i] for i in range(len(y)))
        s = _symmetrize(_add(_matmul(_matmul(h_j, prior_covariance), _transpose(h_j)), r))
        distance = max(0.0, _quadratic(innovation, s))
        weight = min(1.0, self.huber_k / max(sqrt(distance), _EPS))
        r_robust = _scale(r, 1.0 / max(weight, _EPS))
        s_robust = _symmetrize(_add(_matmul(_matmul(h_j, prior_covariance), _transpose(h_j)), r_robust))
        gain = _matmul(_matmul(prior_covariance, _transpose(h_j)), _inverse(s_robust))
        self.mean = tuple(prior_mean[i] + sum(gain[i][j] * innovation[j] for j in range(len(y))) for i in range(len(self.mean)))
        identity = _identity(len(self.mean))
        a = _sub(identity, _matmul(gain, h_j))
        self.covariance = _symmetrize(_add(_matmul(_matmul(a, prior_covariance), _transpose(a)), _matmul(_matmul(gain, r_robust), _transpose(gain))))
        return StateEstimateVector(datetime.now().astimezone(), self.mean, self.covariance, prior_mean, prior_covariance, innovation, s_robust, distance, weight, True)


@dataclass(frozen=True, slots=True)
class Particle:
    state: Vector
    log_weight: float


class BootstrapParticleFilter:
    """Sequential Monte Carlo for nonlinear and non-Gaussian state spaces.

    ``transition_sample`` samples the next latent state from p(x_t|x_{t-1}).
    ``log_observation_likelihood`` evaluates log p(y_t|x_t). Missing
    observations simply propagate particles. Systematic resampling is used
    when effective sample size falls below the configured threshold.
    """

    def __init__(self, particles: Sequence[Particle], *, seed: int = 0, resample_threshold: float = 0.5) -> None:
        if not particles:
            raise ContractViolation("at least one particle is required")
        if not 0.0 < resample_threshold <= 1.0:
            raise ContractViolation("resample_threshold must be in (0,1]")
        self.particles = tuple(particles)
        self.rng = Random(seed)
        self.resample_threshold = resample_threshold

    @property
    def effective_sample_size(self) -> float:
        weights = self._normalized_weights()
        return 1.0 / sum(w * w for w in weights)

    def _normalized_weights(self) -> tuple[float, ...]:
        maximum = max(p.log_weight for p in self.particles)
        weights = [exp(p.log_weight - maximum) for p in self.particles]
        total = sum(weights)
        if total <= 0.0 or not isfinite(total):
            raise ContractViolation("particle weights are numerically degenerate")
        return tuple(w / total for w in weights)

    def _systematic_resample(self, weights: Sequence[float]) -> None:
        n = len(self.particles)
        step = 1.0 / n
        start = self.rng.random() * step
        cumulative = 0.0
        index = 0
        selected: list[Particle] = []
        for j in range(n):
            u = start + j * step
            while index < n - 1 and cumulative + weights[index] < u:
                cumulative += weights[index]
                index += 1
            selected.append(Particle(self.particles[index].state, -log(n)))
        self.particles = tuple(selected)

    def step(
        self,
        transition_sample: Callable[[Vector, float, Random], Vector],
        observation: Vector | None,
        log_observation_likelihood: Callable[[Vector, Vector], float] | None,
        *,
        dt: float,
    ) -> Vector:
        if dt < 0.0 or not isfinite(dt):
            raise TemporalViolation("dt must be finite and non-negative")
        propagated: list[Particle] = []
        for particle in self.particles:
            state = _vector(transition_sample(particle.state, dt, self.rng), "particle state")
            log_weight = particle.log_weight
            if observation is not None:
                if log_observation_likelihood is None:
                    raise ContractViolation("observation likelihood is required when observation is present")
                contribution = float(log_observation_likelihood(observation, state))
                if not isfinite(contribution):
                    raise ContractViolation("observation likelihood must be finite")
                log_weight += contribution
            propagated.append(Particle(state, log_weight))
        self.particles = tuple(propagated)
        if observation is not None and self.effective_sample_size < self.resample_threshold * len(self.particles):
            self._systematic_resample(self._normalized_weights())
        weights = self._normalized_weights()
        dimension = len(self.particles[0].state)
        return tuple(sum(weights[i] * self.particles[i].state[d] for i in range(len(self.particles))) for d in range(dimension))
