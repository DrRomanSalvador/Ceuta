"""Controlled real-data Shadow Mode with strict temporal isolation.

Shadow Mode executes the same temporal boundary and forecasting path as the
runtime while making production promotion impossible by construction. Shadow
forecasts are persisted only in the dedicated :mod:`shadow_engine` ledger.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Protocol

from app.core.epistemology_p0.advanced import Forecast, Observation
from app.core.pipeline.sources.shadow_engine import ShadowEngine, ShadowLedger


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
    baseline_error: float
    squared_error: float
    baseline_squared_error: float
    directional_hit: bool | None
    status: str = "SHADOW_EVALUATION"

    def __post_init__(self) -> None:
        if not self.forecast_id or not self.variable:
            raise ValueError("forecast identity is required")
        if self.target_time.tzinfo is None or self.target_time.utcoffset() is None:
            raise ValueError("target_time must be timezone-aware")
        for name in (
            "realized_value", "error", "baseline_error",
            "squared_error", "baseline_squared_error",
        ):
            if not isfinite(float(getattr(self, name))):
                raise ValueError(f"{name} must be finite")
        if self.squared_error < 0.0 or self.baseline_squared_error < 0.0:
            raise ValueError("squared errors must be non-negative")
        if self.status != "SHADOW_EVALUATION":
            raise ValueError("shadow evaluations cannot enter production status")


class ShadowModeExecutor:
    """Run prospective forecasts without any production mutation capability."""

    def __init__(
        self,
        *,
        ledger: ShadowLedger | None = None,
        model_version: str = "shadow-v1",
    ) -> None:
        if not model_version:
            raise ValueError("model_version must not be empty")
        self._engine = ShadowEngine(model_version=model_version, ledger=ledger)
        self._evaluations: list[ShadowEvaluation] = []

    @property
    def ledger(self) -> ShadowLedger:
        """Return the isolated shadow ledger, never the production ledger."""
        return self._engine.ledger

    def forecast(
        self,
        observations: Iterable[Observation],
        *,
        cutoff_time: datetime,
        forecast_fn: ForecastFunction,
    ) -> Forecast:
        """Forecast using only observations available by cutoff_time."""
        result = self._engine.execute(
            observations,
            cutoff_time=cutoff_time,
            forecast_fn=forecast_fn,
        )
        # The returned object is reconstructed from the isolated record only;
        # no ForecastLedger or production persistence API is touched.
        record = result.record
        return Forecast(
            forecast_id=record.forecast_id,
            variable=record.variable,
            cutoff_time=record.cutoff_time,
            target_time=record.target_time,
            point=record.point,
            lower=record.point,
            upper=record.point,
            method="shadow",
            state_id="shadow",
            evidence_ids=(),
            status="SHADOW_EVALUATION",
        )

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
        entry = next((item for item in self.ledger.records if item.forecast_id == forecast_id), None)
        if entry is None:
            raise KeyError(forecast_id)
        if resolved_at < entry.target_time:
            raise ValueError("shadow forecast cannot be resolved before target_time")
        error = entry.point - float(realized_value)
        baseline_error = float(baseline_prediction) - float(realized_value)
        directional_hit: bool | None = None
        if previous_realized is not None and previous_prediction is not None:
            if not isfinite(float(previous_realized)) or not isfinite(float(previous_prediction)):
                raise ValueError("previous values must be finite")
            actual_direction = float(realized_value) - float(previous_realized)
            predicted_direction = entry.point - float(previous_prediction)
            directional_hit = (actual_direction == 0.0 and predicted_direction == 0.0) or (
                actual_direction > 0.0 and predicted_direction > 0.0
            ) or (actual_direction < 0.0 and predicted_direction < 0.0)
        evaluation = ShadowEvaluation(
            forecast_id=forecast_id,
            variable=entry.variable,
            target_time=entry.target_time,
            realized_value=float(realized_value),
            error=error,
            baseline_error=baseline_error,
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
        return self._engine.production_mutation_supported
