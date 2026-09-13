"""Controlled real-data Shadow Mode.

Shadow Mode executes the same temporal boundary and forecasting path as the
runtime while making production promotion impossible by construction. It can
write forecasts and evaluation metrics, but has no parameter-update capability.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, replace
from datetime import datetime
from math import isfinite
from typing import Protocol

from app.core.epistemology_p0.advanced import Forecast, ForecastLedger, Observation


class ForecastFunction(Protocol):
    def __call__(self, observations: tuple[Observation, ...], *, cutoff_time: datetime) -> Forecast:
        """Produce a forecast from information available at cutoff_time."""


@dataclass(frozen=True, slots=True)
class ShadowEvaluation:
    forecast_id: str
    variable: str
    target_time: datetime
    realized_value: float
    error: float
    squared_error: float
    baseline_squared_error: float
    directional_hit: bool | None
    status: str = "SHADOW_EVALUATION"

    def __post_init__(self) -> None:
        if not self.forecast_id or not self.variable:
            raise ValueError("forecast identity is required")
        if self.target_time.tzinfo is None or self.target_time.utcoffset() is None:
            raise ValueError("target_time must be timezone-aware")
        for name in ("realized_value", "error", "squared_error", "baseline_squared_error"):
            if not isfinite(float(getattr(self, name))):
                raise ValueError(f"{name} must be finite")
        if self.squared_error < 0.0 or self.baseline_squared_error < 0.0:
            raise ValueError("squared errors must be non-negative")


class ShadowModeExecutor:
    """Run prospective forecasts without exposing a production mutation API."""

    def __init__(self, *, ledger: ForecastLedger | None = None, model_version: str = "shadow-v1") -> None:
        if not model_version:
            raise ValueError("model_version must not be empty")
        self.ledger = ledger or ForecastLedger()
        self.model_version = model_version
        self._evaluations: list[ShadowEvaluation] = []

    def forecast(
        self,
        observations: Iterable[Observation],
        *,
        cutoff_time: datetime,
        forecast_fn: ForecastFunction,
    ) -> Forecast:
        """Forecast using only observations whose availability is <= cutoff_time."""
        if cutoff_time.tzinfo is None or cutoff_time.utcoffset() is None:
            raise ValueError("cutoff_time must be timezone-aware")
        eligible = tuple(
            observation for observation in observations if observation.available_at <= cutoff_time
        )
        forecast = forecast_fn(eligible, cutoff_time=cutoff_time)
        if forecast.cutoff_time != cutoff_time:
            raise ValueError("forecast cutoff_time must equal shadow cutoff_time")
        shadow_forecast = replace(forecast, status="SHADOW_EVALUATION")
        self.ledger.record(shadow_forecast, created_at=cutoff_time, model_version=self.model_version)
        return shadow_forecast

    def resolve(
        self,
        forecast_id: str,
        *,
        realized_value: float,
        resolved_at: datetime,
        baseline_prediction: float,
        previous_realized: float | None = None,
        previous_prediction: float | None = None,
    ) -> ShadowEvaluation:
        if resolved_at.tzinfo is None or resolved_at.utcoffset() is None:
            raise ValueError("resolved_at must be timezone-aware")
        if not isfinite(float(realized_value)) or not isfinite(float(baseline_prediction)):
            raise ValueError("realized_value and baseline_prediction must be finite")
        entry = next((item for item in self.ledger.entries if item.forecast.forecast_id == forecast_id), None)
        if entry is None:
            raise KeyError(forecast_id)
        if resolved_at < entry.forecast.target_time:
            raise ValueError("shadow forecast cannot be resolved before target_time")
        error = entry.forecast.point - float(realized_value)
        baseline_error = float(baseline_prediction) - float(realized_value)
        directional_hit: bool | None = None
        if previous_realized is not None and previous_prediction is not None:
            if not isfinite(float(previous_realized)) or not isfinite(float(previous_prediction)):
                raise ValueError("previous values must be finite")
            actual_direction = float(realized_value) - float(previous_realized)
            predicted_direction = entry.forecast.point - float(previous_prediction)
            directional_hit = (actual_direction == 0.0 and predicted_direction == 0.0) or (
                actual_direction > 0.0 and predicted_direction > 0.0
            ) or (actual_direction < 0.0 and predicted_direction < 0.0)
        evaluation = ShadowEvaluation(
            forecast_id=forecast_id,
            variable=entry.forecast.variable,
            target_time=entry.forecast.target_time,
            realized_value=float(realized_value),
            error=error,
            squared_error=error * error,
            baseline_squared_error=baseline_error * baseline_error,
            directional_hit=directional_hit,
        )
        self._evaluations.append(evaluation)
        return evaluation

    @property
    def evaluations(self) -> tuple[ShadowEvaluation, ...]:
        return tuple(self._evaluations)

    @property
    def production_mutation_supported(self) -> bool:
        return False
