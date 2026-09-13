"""Longitudinal latent-state estimation primitives for CeutIA.

This module implements a deliberately narrow linear-Gaussian state-space model
for one scalar variable. It estimates a latent state from noisy, irregularly
timed observations without treating observations as the state itself.

The implementation is an estimation primitive, not causal inference, anomaly
detection, forecasting, or clinical interpretation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite

from ..errors import ContractViolation, TemporalViolation
from ..pipeline.contracts import ObservationRecord


@dataclass(frozen=True, slots=True)
class StateEstimate:
    """Posterior or prior estimate of a latent scalar state."""

    variable: str
    as_of: datetime
    mean: float
    variance: float
    observation_id: str | None
    prior_mean: float
    prior_variance: float
    innovation: float | None
    innovation_variance: float | None

    def __post_init__(self) -> None:
        if not self.variable:
            raise ContractViolation("variable must not be empty")
        if self.as_of.tzinfo is None or self.as_of.utcoffset() is None:
            raise TemporalViolation("as_of must be timezone-aware")
        for name in (
            "mean", "variance", "prior_mean", "prior_variance",
            "innovation", "innovation_variance",
        ):
            value = getattr(self, name)
            if value is not None and not isfinite(float(value)):
                raise ContractViolation(f"{name} must be finite when provided")
        if self.variance < 0.0 or self.prior_variance < 0.0:
            raise ContractViolation("variances must be non-negative")
        if self.innovation_variance is not None and self.innovation_variance <= 0.0:
            raise ContractViolation("innovation_variance must be positive")


@dataclass(frozen=True, slots=True)
class LongitudinalStateSeries:
    """Ordered immutable sequence of latent-state estimates."""

    estimates: tuple[StateEstimate, ...]

    def __post_init__(self) -> None:
        previous: StateEstimate | None = None
        for estimate in self.estimates:
            if previous is not None:
                if estimate.as_of <= previous.as_of:
                    raise TemporalViolation("estimates must be strictly ordered")
                if estimate.variable != previous.variable:
                    raise ContractViolation("series must contain one variable")
            previous = estimate


class ScalarKalmanFilter:
    """Random-walk Kalman filter with time-scaled process variance.

    State transition: x_t = x_(t-1) + w_t, with
    Var(w_t) = process_variance_per_time * elapsed_time.
    Observation model: y_t = x_t + v_t.

    Observation noise is supplied explicitly by the caller. No causal meaning
    is assigned to innovations or state changes.
    """

    def __init__(
        self,
        variable: str,
        initial_mean: float,
        initial_variance: float,
        process_variance_per_second: float,
    ) -> None:
        if not variable:
            raise ContractViolation("variable must not be empty")
        for name, value in (
            ("initial_mean", initial_mean),
            ("initial_variance", initial_variance),
            ("process_variance_per_second", process_variance_per_second),
        ):
            if not isfinite(float(value)):
                raise ContractViolation(f"{name} must be finite")
        if initial_variance < 0.0 or process_variance_per_second < 0.0:
            raise ContractViolation("variances must be non-negative")
        self.variable = variable
        self._mean = float(initial_mean)
        self._variance = float(initial_variance)
        self._process_variance_per_second = float(process_variance_per_second)
        self._time: datetime | None = None

    def _predict_to(self, as_of: datetime) -> tuple[float, float]:
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise TemporalViolation("as_of must be timezone-aware")
        if self._time is None:
            return self._mean, self._variance
        if as_of <= self._time:
            raise TemporalViolation("prediction time must be strictly forward")
        elapsed = (as_of - self._time).total_seconds()
        return (
            self._mean,
            self._variance + self._process_variance_per_second * elapsed,
        )

    def predict_to(self, as_of: datetime) -> StateEstimate:
        """Advance the latent-state prior without observing a new value."""
        prior_mean, prior_variance = self._predict_to(as_of)
        self._mean = prior_mean
        self._variance = prior_variance
        self._time = as_of
        return StateEstimate(
            variable=self.variable,
            as_of=as_of,
            mean=prior_mean,
            variance=prior_variance,
            observation_id=None,
            prior_mean=prior_mean,
            prior_variance=prior_variance,
            innovation=None,
            innovation_variance=None,
        )

    def update(
        self,
        observation: ObservationRecord,
        observation_variance: float,
    ) -> StateEstimate:
        if observation.variable != self.variable:
            raise ContractViolation("observation variable does not match filter")
        if not isfinite(float(observation_variance)) or observation_variance <= 0.0:
            raise ContractViolation("observation_variance must be finite and positive")

        prior_mean, prior_variance = self._predict_to(observation.event_time)
        innovation = float(observation.value) - prior_mean
        innovation_variance = prior_variance + float(observation_variance)
        gain = prior_variance / innovation_variance
        posterior_mean = prior_mean + gain * innovation
        posterior_variance = max(0.0, (1.0 - gain) * prior_variance)

        self._mean = posterior_mean
        self._variance = posterior_variance
        self._time = observation.event_time
        return StateEstimate(
            variable=self.variable,
            as_of=observation.event_time,
            mean=posterior_mean,
            variance=posterior_variance,
            observation_id=observation.observation_id,
            prior_mean=prior_mean,
            prior_variance=prior_variance,
            innovation=innovation,
            innovation_variance=innovation_variance,
        )

    def filter(
        self,
        observations: tuple[ObservationRecord, ...],
        observation_variances: tuple[float, ...],
    ) -> LongitudinalStateSeries:
        if len(observations) != len(observation_variances):
            raise ContractViolation("observations and variances must have equal length")
        estimates = tuple(
            self.update(observation, variance)
            for observation, variance in zip(observations, observation_variances)
        )
        return LongitudinalStateSeries(estimates)
