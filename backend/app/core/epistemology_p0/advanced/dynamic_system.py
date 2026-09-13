"""Evidence-constrained dynamic monitoring for complex systems.

This module turns temporally eligible observations into an auditable system
state, interaction-aware trajectory and bounded forecast. It is deliberately
model-light: it provides deterministic baselines and early-warning indicators,
not unvalidated claims of causal prediction.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from math import isfinite, sqrt
from statistics import mean
from typing import Iterable, Mapping
import uuid


@dataclass(frozen=True, slots=True)
class Observation:
    variable: str
    value: float
    event_time: datetime
    available_at: datetime
    source_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...] = ()
    quality: float = 1.0

    def __post_init__(self) -> None:
        if not self.variable:
            raise ValueError("variable must not be empty")
        if not isfinite(float(self.value)):
            raise ValueError("value must be finite")
        if self.available_at.tzinfo is None or self.event_time.tzinfo is None:
            raise ValueError("timestamps must be timezone-aware")
        if not self.source_ids:
            raise ValueError("at least one source_id is required")
        if not 0.0 <= self.quality <= 1.0:
            raise ValueError("quality must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class VariableState:
    variable: str
    value: float
    previous_value: float | None
    velocity: float | None
    acceleration: float | None
    observations: int
    updated_at: datetime
    evidence_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Interaction:
    upstream: str
    downstream: str
    coupling: float
    lag_steps: int = 1
    mechanism: str = "association"

    def __post_init__(self) -> None:
        if not self.upstream or not self.downstream:
            raise ValueError("interaction endpoints are required")
        if self.upstream == self.downstream:
            raise ValueError("self-interactions are not supported")
        if not 0.0 <= self.coupling <= 1.0:
            raise ValueError("coupling must be between 0 and 1")
        if self.lag_steps < 1:
            raise ValueError("lag_steps must be >= 1")


@dataclass(frozen=True, slots=True)
class EarlyWarning:
    variable: str
    indicators: tuple[str, ...]
    strength: float
    interpretation: str
    status: str = "UNVERIFIED"


@dataclass(frozen=True, slots=True)
class SystemState:
    as_of: datetime
    variables: tuple[VariableState, ...]
    interactions: tuple[Interaction, ...]
    early_warnings: tuple[EarlyWarning, ...]
    state_id: str = field(default_factory=lambda: f"state-{uuid.uuid4().hex[:12]}")

    def variable(self, name: str) -> VariableState:
        for item in self.variables:
            if item.variable == name:
                return item
        raise KeyError(name)


@dataclass(frozen=True, slots=True)
class Forecast:
    forecast_id: str
    variable: str
    cutoff_time: datetime
    target_time: datetime
    point: float
    lower: float
    upper: float
    method: str
    state_id: str
    evidence_ids: tuple[str, ...]
    status: str = "UNVERIFIED"
    realized_value: float | None = None
    score: float | None = None


class DynamicSystemMonitor:
    """Maintain a temporal state and produce bounded, auditable baselines."""

    def __init__(self, interactions: Iterable[Interaction] = ()) -> None:
        self.interactions = tuple(interactions)
        self._history: dict[str, list[Observation]] = {}
        self._states: list[SystemState] = []
        self._forecasts: list[Forecast] = []

    def ingest(self, observations: Iterable[Observation], *, evaluation_time: datetime) -> int:
        """Ingest only observations available at evaluation_time; fail closed."""
        if evaluation_time.tzinfo is None:
            raise ValueError("evaluation_time must be timezone-aware")
        accepted = 0
        for observation in observations:
            if observation.available_at > evaluation_time:
                raise ValueError(
                    f"future information leak: {observation.variable} available at "
                    f"{observation.available_at.isoformat()} after evaluation time"
                )
            self._history.setdefault(observation.variable, []).append(observation)
            self._history[observation.variable].sort(key=lambda item: item.event_time)
            accepted += 1
        return accepted

    def snapshot(self, *, as_of: datetime) -> SystemState:
        if as_of.tzinfo is None:
            raise ValueError("as_of must be timezone-aware")
        variables: list[VariableState] = []
        for variable, observations in sorted(self._history.items()):
            eligible = [item for item in observations if item.available_at <= as_of]
            if not eligible:
                continue
            current = eligible[-1]
            previous = eligible[-2] if len(eligible) >= 2 else None
            velocity = None
            acceleration = None
            if previous is not None:
                dt = (current.event_time - previous.event_time).total_seconds()
                if dt > 0:
                    velocity = (current.value - previous.value) / dt
            if len(eligible) >= 3:
                prior = eligible[-3]
                dt1 = (previous.event_time - prior.event_time).total_seconds()
                dt2 = (current.event_time - previous.event_time).total_seconds()
                if dt1 > 0 and dt2 > 0:
                    v1 = (previous.value - prior.value) / dt1
                    v2 = (current.value - previous.value) / dt2
                    acceleration = (v2 - v1) / ((dt1 + dt2) / 2.0)
            evidence = tuple(dict.fromkeys(e for item in eligible[-10:] for e in item.evidence_ids))
            variables.append(
                VariableState(
                    variable=variable,
                    value=current.value,
                    previous_value=previous.value if previous else None,
                    velocity=velocity,
                    acceleration=acceleration,
                    observations=len(eligible),
                    updated_at=current.event_time,
                    evidence_ids=evidence,
                )
            )

        warnings = tuple(self._early_warnings(variable) for variable in variables)
        warnings = tuple(item for item in warnings if item is not None)
        state = SystemState(as_of, tuple(variables), self.interactions, warnings)
        self._states.append(state)
        return state

    def forecast(self, *, variable: str, horizon: timedelta, state: SystemState) -> Forecast:
        """Create a persistence+velocity baseline; explicitly uncalibrated."""
        if horizon.total_seconds() <= 0:
            raise ValueError("horizon must be positive")
        current = state.variable(variable)
        velocity = current.velocity or 0.0
        seconds = horizon.total_seconds()
        point = current.value + velocity * seconds
        recent = self._history.get(variable, [])[-5:]
        dispersion = self._dispersion([item.value for item in recent])
        uncertainty = max(dispersion, abs(velocity) * seconds * 0.5, 1e-12)
        target = state.as_of + horizon
        forecast = Forecast(
            forecast_id=f"forecast-{uuid.uuid4().hex[:12]}",
            variable=variable,
            cutoff_time=state.as_of,
            target_time=target,
            point=point,
            lower=point - 1.96 * uncertainty,
            upper=point + 1.96 * uncertainty,
            method="persistence_plus_velocity_baseline",
            state_id=state.state_id,
            evidence_ids=current.evidence_ids,
        )
        self._forecasts.append(forecast)
        return forecast

    def resolve_forecast(self, forecast_id: str, realized_value: float) -> Forecast:
        for index, forecast in enumerate(self._forecasts):
            if forecast.forecast_id == forecast_id:
                error = forecast.point - float(realized_value)
                resolved = Forecast(
                    **{**forecast.__dict__, "realized_value": float(realized_value), "score": error * error}
                )
                self._forecasts[index] = resolved
                return resolved
        raise KeyError(forecast_id)

    @property
    def forecasts(self) -> tuple[Forecast, ...]:
        return tuple(self._forecasts)

    @staticmethod
    def _dispersion(values: list[float]) -> float:
        if len(values) < 2:
            return 0.0
        centre = mean(values)
        return sqrt(mean((value - centre) ** 2 for value in values))

    def _early_warnings(self, state: VariableState) -> EarlyWarning | None:
        observations = self._history[state.variable]
        values = [item.value for item in observations[-8:]]
        indicators: list[str] = []
        strength = 0.0
        if len(values) >= 4:
            early_var = self._dispersion(values[: max(2, len(values) // 2)])
            late_var = self._dispersion(values[-max(2, len(values) // 2) :])
            if late_var > early_var * 1.25 and late_var > 0:
                indicators.append("increasing_variance")
                strength = max(strength, min(1.0, late_var / (late_var + early_var)))
            diffs = [values[i] - values[i - 1] for i in range(1, len(values))]
            if len(diffs) >= 3:
                persistence = self._lag1(diffs)
                if persistence > 0.5:
                    indicators.append("increasing_persistence")
                    strength = max(strength, min(1.0, persistence))
        if not indicators:
            return None
        return EarlyWarning(
            variable=state.variable,
            indicators=tuple(indicators),
            strength=round(strength, 6),
            interpretation="Possible change in system dynamics; this is an early-warning signal, not a tipping-point prediction.",
        )

    @staticmethod
    def _lag1(values: list[float]) -> float:
        if len(values) < 2:
            return 0.0
        x = values[:-1]
        y = values[1:]
        xm = mean(x)
        ym = mean(y)
        numerator = sum((a - xm) * (b - ym) for a, b in zip(x, y))
        denominator = sqrt(sum((a - xm) ** 2 for a in x) * sum((b - ym) ** 2 for b in y))
        return numerator / denominator if denominator else 0.0
