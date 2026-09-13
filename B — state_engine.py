from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from statistics import fmean
from typing import Final, Iterable, Mapping
from uuid import UUID, uuid4


class StateEngineError(ValueError):
    """Base state-engine validation error."""


class TemporalLeakageError(StateEngineError):
    """Raised when an unavailable observation enters state estimation."""


class InvalidObservationError(StateEngineError):
    """Raised when an observation violates the state contract."""


@dataclass(frozen=True, slots=True)
class StateObservation:
    observation_id: UUID
    variable: str
    domain: str
    value: float
    event_time: datetime
    available_at: datetime
    quality: float
    uncertainty: float

    def __post_init__(self) -> None:
        if not self.variable.strip():
            raise InvalidObservationError("variable cannot be empty")

        if not self.domain.strip():
            raise InvalidObservationError("domain cannot be empty")

        if not isfinite(self.value):
            raise InvalidObservationError("value must be finite")

        if not isfinite(self.quality) or not 0.0 <= self.quality <= 1.0:
            raise InvalidObservationError(
                "quality must be finite and within [0, 1]"
            )

        if not isfinite(self.uncertainty) or self.uncertainty < 0.0:
            raise InvalidObservationError(
                "uncertainty must be finite and non-negative"
            )

        if self.event_time.tzinfo is None:
            raise InvalidObservationError(
                "event_time must be timezone-aware"
            )

        if self.available_at.tzinfo is None:
            raise InvalidObservationError(
                "available_at must be timezone-aware"
            )

        if self.available_at < self.event_time:
            raise TemporalLeakageError(
                "available_at cannot precede event_time"
            )


@dataclass(frozen=True, slots=True)
class VariableEstimate:
    variable: str
    domain: str
    value: float
    velocity: float
    acceleration: float
    uncertainty: float
    observation_count: int
    as_of: datetime


@dataclass(frozen=True, slots=True)
class DomainEstimate:
    domain: str
    variables: tuple[VariableEstimate, ...]
    aggregate_value: float
    aggregate_uncertainty: float


@dataclass(frozen=True, slots=True)
class SystemState:
    state_id: UUID
    as_of: datetime
    variables: tuple[VariableEstimate, ...]
    domains: tuple[DomainEstimate, ...]
    observation_ids: tuple[UUID, ...]


class MultidomainStateEngine:
    DEFAULT_HISTORY_LIMIT: Final[int] = 128

    def __init__(self, history_limit: int = DEFAULT_HISTORY_LIMIT) -> None:
        if history_limit < 3:
            raise ValueError("history_limit must be at least 3")

        self._history_limit = history_limit
        self._observations: dict[str, list[StateObservation]] = {}

    def ingest(
        self,
        observations: Iterable[StateObservation],
        evaluation_time: datetime,
    ) -> SystemState:
        if evaluation_time.tzinfo is None:
            raise StateEngineError(
                "evaluation_time must be timezone-aware"
            )

        accepted = tuple(observations)

        for observation in accepted:
            if observation.available_at > evaluation_time:
                raise TemporalLeakageError(
                    f"observation {observation.observation_id} is not "
                    "available at evaluation time"
                )

            self._observations.setdefault(observation.variable, []).append(
                observation
            )

        for variable, history in self._observations.items():
            history.sort(
                key=lambda item: (
                    item.event_time,
                    item.available_at,
                    str(item.observation_id),
                )
            )
            if len(history) > self._history_limit:
                del history[:-self._history_limit]

        estimates: list[VariableEstimate] = []

        for variable in sorted(self._observations):
            history = [
                item
                for item in self._observations[variable]
                if item.available_at <= evaluation_time
            ]

            if not history:
                continue

            estimate = self._estimate_variable(
                variable=variable,
                history=history,
                evaluation_time=evaluation_time,
            )
            estimates.append(estimate)

        domains = self._build_domains(estimates)

        observation_ids = tuple(
            sorted(
                {
                    observation.observation_id
                    for observation in accepted
                    if observation.available_at <= evaluation_time
                },
                key=str,
            )
        )

        return SystemState(
            state_id=uuid4(),
            as_of=evaluation_time,
            variables=tuple(estimates),
            domains=domains,
            observation_ids=observation_ids,
        )

    @staticmethod
    def _estimate_variable(
        variable: str,
        history: list[StateObservation],
        evaluation_time: datetime,
    ) -> VariableEstimate:
        latest = history[-1]

        if latest.event_time > evaluation_time:
            raise TemporalLeakageError(
                f"latest observation for {variable} exceeds evaluation time"
            )

        weighted_values = [
            observation.value * max(observation.quality, 0.0)
            for observation in history
        ]
        weights = [
            max(observation.quality, 0.0)
            for observation in history
        ]

        weight_sum = sum(weights)

        if weight_sum <= 0.0:
            raise InvalidObservationError(
                f"no usable quality weight for {variable}"
            )

        value = sum(weighted_values) / weight_sum

        if not isfinite(value):
            raise InvalidObservationError(
                f"estimated value for {variable} is not finite"
            )

        velocity = 0.0
        acceleration = 0.0

        if len(history) >= 2:
            previous = history[-2]
            delta_seconds = (
                latest.event_time - previous.event_time
            ).total_seconds()

            if delta_seconds <= 0.0:
                raise InvalidObservationError(
                    f"non-increasing timestamps for {variable}"
                )

            velocity = (
                latest.value - previous.value
            ) / delta_seconds

        if len(history) >= 3:
            previous = history[-2]
            earlier = history[-3]

            first_delta = (
                previous.event_time - earlier.event_time
            ).total_seconds()
            second_delta = (
                latest.event_time - previous.event_time
            ).total_seconds()

            if first_delta <= 0.0 or second_delta <= 0.0:
                raise InvalidObservationError(
                    f"invalid temporal spacing for {variable}"
                )

            previous_velocity = (
                previous.value - earlier.value
            ) / first_delta

            acceleration = (
                velocity - previous_velocity
            ) / second_delta

        uncertainty = fmean(
            observation.uncertainty
            for observation in history
        )

        if not isfinite(velocity):
            raise InvalidObservationError(
                f"velocity for {variable} is not finite"
            )

        if not isfinite(acceleration):
            raise InvalidObservationError(
                f"acceleration for {variable} is not finite"
            )

        if not isfinite(uncertainty):
            raise InvalidObservationError(
                f"uncertainty for {variable} is not finite"
            )

        return VariableEstimate(
            variable=variable,
            domain=latest.domain,
            value=value,
            velocity=velocity,
            acceleration=acceleration,
            uncertainty=uncertainty,
            observation_count=len(history),
            as_of=evaluation_time,
        )

    @staticmethod
    def _build_domains(
        estimates: list[VariableEstimate],
    ) -> tuple[DomainEstimate, ...]:
        grouped: dict[str, list[VariableEstimate]] = {}

        for estimate in estimates:
            grouped.setdefault(estimate.domain, []).append(estimate)

        domains: list[DomainEstimate] = []

        for domain in sorted(grouped):
            variables = tuple(
                sorted(
                    grouped[domain],
                    key=lambda item: item.variable,
                )
            )

            aggregate_value = fmean(
                variable.value for variable in variables
            )

            aggregate_uncertainty = fmean(
                variable.uncertainty for variable in variables
            )

            if not isfinite(aggregate_value):
                raise InvalidObservationError(
                    f"aggregate value for {domain} is not finite"
                )

            if not isfinite(aggregate_uncertainty):
                raise InvalidObservationError(
                    f"aggregate uncertainty for {domain} is not finite"
                )

            domains.append(
                DomainEstimate(
                    domain=domain,
                    variables=variables,
                    aggregate_value=aggregate_value,
                    aggregate_uncertainty=aggregate_uncertainty,
                )
            )

        return tuple(domains)