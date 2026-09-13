"""Closed-loop orchestration for evidence-constrained complex-system anticipation.

The engine deliberately separates monitoring, regime assessment, trajectory
construction, forecasting and prospective scoring. It never upgrades an
uncalibrated forecast into a probability or causal claim.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from statistics import mean
from typing import Iterable

from .dynamic_system import DynamicSystemMonitor, Forecast, Observation, SystemState


@dataclass(frozen=True, slots=True)
class RegimeAssessment:
    variable: str
    regime: str
    score: float
    indicators: tuple[str, ...]
    status: str = "UNVERIFIED"


@dataclass(frozen=True, slots=True)
class TrajectoryPoint:
    as_of: datetime
    state_id: str
    values: tuple[tuple[str, float], ...]


@dataclass(frozen=True, slots=True)
class ForecastLedgerEntry:
    forecast: Forecast
    created_at: datetime
    model_version: str
    validation_status: str = "PENDING_PROSPECTIVE_VALIDATION"


class ForecastLedger:
    """Immutable-by-replacement ledger for prospective forecast evaluation."""

    def __init__(self) -> None:
        self._entries: list[ForecastLedgerEntry] = []

    def record(self, forecast: Forecast, *, created_at: datetime, model_version: str) -> ForecastLedgerEntry:
        if created_at.tzinfo is None:
            raise ValueError("created_at must be timezone-aware")
        if forecast.cutoff_time > created_at:
            raise ValueError("forecast cutoff cannot be after forecast creation")
        entry = ForecastLedgerEntry(forecast, created_at, model_version)
        self._entries.append(entry)
        return entry

    def resolve(self, forecast_id: str, *, realized_value: float, resolved_at: datetime) -> ForecastLedgerEntry:
        if resolved_at.tzinfo is None:
            raise ValueError("resolved_at must be timezone-aware")
        for index, entry in enumerate(self._entries):
            if entry.forecast.forecast_id != forecast_id:
                continue
            if resolved_at < entry.forecast.target_time:
                raise ValueError("forecast cannot be resolved before target_time")
            error = entry.forecast.point - float(realized_value)
            resolved = Forecast(
                **{
                    "forecast_id": entry.forecast.forecast_id,
                    "variable": entry.forecast.variable,
                    "cutoff_time": entry.forecast.cutoff_time,
                    "target_time": entry.forecast.target_time,
                    "point": entry.forecast.point,
                    "lower": entry.forecast.lower,
                    "upper": entry.forecast.upper,
                    "method": entry.forecast.method,
                    "state_id": entry.forecast.state_id,
                    "evidence_ids": entry.forecast.evidence_ids,
                    "status": "PROSPECTIVELY_SCORED",
                    "realized_value": float(realized_value),
                    "score": error * error,
                }
            )
            updated = ForecastLedgerEntry(
                resolved,
                entry.created_at,
                entry.model_version,
                "SCORED_NOT_CALIBRATED",
            )
            self._entries[index] = updated
            return updated
        raise KeyError(forecast_id)

    @property
    def entries(self) -> tuple[ForecastLedgerEntry, ...]:
        return tuple(self._entries)

    def mean_squared_error(self, *, variable: str | None = None) -> float | None:
        scores = [
            entry.forecast.score
            for entry in self._entries
            if entry.forecast.score is not None
            and (variable is None or entry.forecast.variable == variable)
        ]
        return mean(scores) if scores else None


class ComplexSystemAnticipationEngine:
    """Execute one reproducible monitor -> state -> trajectory -> forecast cycle."""

    def __init__(
        self,
        monitor: DynamicSystemMonitor,
        *,
        model_version: str = "baseline-v1",
    ) -> None:
        self.monitor = monitor
        self.model_version = model_version
        self.ledger = ForecastLedger()
        self._trajectory: list[TrajectoryPoint] = []

    def cycle(
        self,
        observations: Iterable[Observation],
        *,
        as_of: datetime,
        forecast_horizon: timedelta,
        variables: Iterable[str] | None = None,
    ) -> tuple[SystemState, tuple[Forecast, ...]]:
        """Run one fail-closed cycle using only information available at ``as_of``."""
        self.monitor.ingest(observations, evaluation_time=as_of)
        state = self.monitor.snapshot(as_of=as_of)
        self._trajectory.append(
            TrajectoryPoint(
                as_of=as_of,
                state_id=state.state_id,
                values=tuple((item.variable, item.value) for item in state.variables),
            )
        )
        selected = tuple(variables) if variables is not None else tuple(
            item.variable for item in state.variables
        )
        forecasts: list[Forecast] = []
        for variable in selected:
            forecast = self.monitor.forecast(
                variable=variable,
                horizon=forecast_horizon,
                state=state,
            )
            self.ledger.record(
                forecast,
                created_at=as_of,
                model_version=self.model_version,
            )
            forecasts.append(forecast)
        return state, tuple(forecasts)

    def assess_regimes(self, state: SystemState) -> tuple[RegimeAssessment, ...]:
        """Classify dynamics conservatively; this is not a learned regime model."""
        assessments: list[RegimeAssessment] = []
        for variable in state.variables:
            indicators = [warning for warning in state.early_warnings if warning.variable == variable.variable]
            if indicators:
                score = max(item.strength for item in indicators)
                assessments.append(
                    RegimeAssessment(
                        variable=variable.variable,
                        regime="DYNAMIC_CHANGE_SIGNAL",
                        score=score,
                        indicators=tuple(name for item in indicators for name in item.indicators),
                    )
                )
            else:
                assessments.append(
                    RegimeAssessment(
                        variable=variable.variable,
                        regime="NO_DETECTED_CHANGE_SIGNAL",
                        score=0.0,
                        indicators=(),
                    )
                )
        return tuple(assessments)

    @property
    def trajectory(self) -> tuple[TrajectoryPoint, ...]:
        return tuple(self._trajectory)
