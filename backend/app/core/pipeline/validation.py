"""Prospective validation contracts and fail-closed calibration ledger."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite

from ..epistemology_p0.advanced import Forecast
from app.validation.circuit_breaker import CalibrationCircuitBreaker


@dataclass(frozen=True, slots=True)
class ValidationReport:
    forecast_id: str
    variable: str
    sample_size: int
    mae: float
    mse: float
    bias: float
    baseline_mse: float | None
    degradation_ratio: float | None
    interval_coverage: float | None
    passed: bool
    evaluated_at: datetime

    def __post_init__(self) -> None:
        if not self.forecast_id or not self.variable:
            raise ValueError("forecast_id and variable are required")
        if self.sample_size < 1:
            raise ValueError("sample_size must be positive")
        if self.evaluated_at.tzinfo is None or self.evaluated_at.utcoffset() is None:
            raise ValueError("evaluated_at must be timezone-aware")
        numeric = (self.mae, self.mse, self.bias)
        if not all(isfinite(value) for value in numeric):
            raise ValueError("validation metrics must be finite")
        if self.mae < 0.0 or self.mse < 0.0:
            raise ValueError("mae and mse must be non-negative")


@dataclass(frozen=True, slots=True)
class CalibrationDecision:
    report: ValidationReport
    promoted: bool
    active_model_version: str


class ClosedLoopCalibrator:
    """Resolve only mature forecasts and promote only through the breaker."""

    def __init__(
        self,
        breaker: CalibrationCircuitBreaker | None = None,
        *,
        active_model_version: str = "baseline-v1",
    ) -> None:
        self.breaker = breaker or CalibrationCircuitBreaker()
        self.active_model_version = active_model_version
        self._pending: dict[str, tuple[Forecast, float]] = {}
        self._reports: list[ValidationReport] = []

    def register(self, forecast: Forecast, *, baseline_prediction: float | None = None) -> None:
        baseline = forecast.point if baseline_prediction is None else float(baseline_prediction)
        if not isfinite(baseline):
            raise ValueError("baseline_prediction must be finite")
        if forecast.forecast_id in self._pending:
            raise ValueError("forecast already registered")
        self._pending[forecast.forecast_id] = (forecast, baseline)

    def resolve(
        self,
        forecast_id: str,
        *,
        realized_value: float,
        resolved_at: datetime,
        sample_size: int = 1,
        interval_coverage: float | None = None,
        candidate_model_version: str | None = None,
    ) -> CalibrationDecision:
        if resolved_at.tzinfo is None or resolved_at.utcoffset() is None:
            raise ValueError("resolved_at must be timezone-aware")
        forecast, baseline = self._pending[forecast_id]
        if resolved_at < forecast.target_time:
            raise ValueError("forecast cannot be resolved before target_time")
        if not isfinite(float(realized_value)):
            raise ValueError("realized_value must be finite")
        if interval_coverage is not None and not 0.0 <= interval_coverage <= 1.0:
            raise ValueError("interval_coverage must be between 0 and 1")
        error = forecast.point - float(realized_value)
        baseline_error = baseline - float(realized_value)
        mse = error * error
        baseline_mse = baseline_error * baseline_error
        report = ValidationReport(
            forecast_id=forecast_id,
            variable=forecast.variable,
            sample_size=sample_size,
            mae=abs(error),
            mse=mse,
            bias=error,
            baseline_mse=baseline_mse,
            degradation_ratio=(mse / baseline_mse) if baseline_mse > 0 else (0.0 if mse == 0 else None),
            interval_coverage=interval_coverage,
            passed=True,
            evaluated_at=resolved_at,
        )
        promoted = self.breaker.evaluate(report)
        if promoted and candidate_model_version:
            self.active_model_version = candidate_model_version
        self._reports.append(report)
        del self._pending[forecast_id]
        return CalibrationDecision(report, promoted, self.active_model_version)

    @property
    def reports(self) -> tuple[ValidationReport, ...]:
        return tuple(self._reports)
