from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Iterable
from uuid import UUID


class CalibrationError(ValueError):
    """Base calibration error."""


class CalibrationDataError(CalibrationError):
    """Raised when forecast/outcome data is incomplete or invalid."""


@dataclass(frozen=True, slots=True)
class ForecastRecord:
    forecast_id: UUID
    model: str
    target_time: datetime
    created_at: datetime
    cutoff_time: datetime
    predicted_value: float
    observed_outcome: float | None
    probability: float | None
    direction: int | None
    resolved: bool

    def __post_init__(self) -> None:
        if self.target_time.tzinfo is None:
            raise CalibrationDataError(
                "target_time must be timezone-aware"
            )

        if self.created_at.tzinfo is None:
            raise CalibrationDataError(
                "created_at must be timezone-aware"
            )

        if self.cutoff_time.tzinfo is None:
            raise CalibrationDataError(
                "cutoff_time must be timezone-aware"
            )

        if self.created_at < self.cutoff_time:
            raise CalibrationDataError(
                "created_at cannot precede cutoff_time"
            )

        if not isfinite(self.predicted_value):
            raise CalibrationDataError(
                "predicted_value must be finite"
            )

        if self.probability is not None:
            if not isfinite(self.probability):
                raise CalibrationDataError(
                    "probability must be finite"
                )
            if not 0.0 <= self.probability <= 1.0:
                raise CalibrationDataError(
                    "probability must be within [0, 1]"
                )

        if self.observed_outcome is not None:
            if not isfinite(self.observed_outcome):
                raise CalibrationDataError(
                    "observed_outcome must be finite"
                )

        if self.direction is not None and self.direction not in (-1, 0, 1):
            raise CalibrationDataError(
                "direction must be -1, 0 or 1"
            )


@dataclass(frozen=True, slots=True)
class CalibrationRecord:
    model: str
    evaluated_at: datetime
    sample_size: int
    mse: float
    brier_score: float | None
    directional_bias: float
    mean_error: float
    status: str
    recommendation: str

    def __post_init__(self) -> None:
        if self.evaluated_at.tzinfo is None:
            raise CalibrationDataError(
                "evaluated_at must be timezone-aware"
            )

        if self.sample_size < 1:
            raise CalibrationDataError(
                "sample_size must be positive"
            )

        for name, value in (
            ("mse", self.mse),
            ("directional_bias", self.directional_bias),
            ("mean_error", self.mean_error),
        ):
            if not isfinite(value):
                raise CalibrationDataError(
                    f"{name} must be finite"
                )

        if self.brier_score is not None:
            if not isfinite(self.brier_score):
                raise CalibrationDataError(
                    "brier_score must be finite"
                )

            if not 0.0 <= self.brier_score <= 1.0:
                raise CalibrationDataError(
                    "brier_score must be within [0, 1]"
                )


class ForecastCalibrationEngine:
    def __init__(
        self,
        max_mse: float,
        max_brier_score: float = 0.25,
        max_absolute_bias: float = 0.20,
        minimum_sample_size: int = 30,
    ) -> None:
        if not isfinite(max_mse) or max_mse <= 0.0:
            raise ValueError("max_mse must be finite and positive")

        if not 0.0 < max_brier_score <= 1.0:
            raise ValueError(
                "max_brier_score must be within (0, 1]"
            )

        if not 0.0 < max_absolute_bias <= 1.0:
            raise ValueError(
                "max_absolute_bias must be within (0, 1]"
            )

        if minimum_sample_size < 1:
            raise ValueError(
                "minimum_sample_size must be positive"
            )

        self._max_mse = max_mse
        self._max_brier_score = max_brier_score
        self._max_absolute_bias = max_absolute_bias
        self._minimum_sample_size = minimum_sample_size

    def calibrate(
        self,
        forecasts: Iterable[ForecastRecord],
        current_time: datetime,
    ) -> CalibrationRecord:
        if current_time.tzinfo is None:
            raise CalibrationDataError(
                "current_time must be timezone-aware"
            )

        eligible = [
            forecast
            for forecast in forecasts
            if forecast.target_time <= current_time
            and forecast.resolved
        ]

        if not eligible:
            raise CalibrationDataError(
                "no resolved forecasts are available"
            )

        unresolved = [
            forecast
            for forecast in eligible
            if forecast.observed_outcome is None
        ]

        if unresolved:
            raise CalibrationDataError(
                "resolved forecasts contain missing outcomes"
            )

        models = {forecast.model for forecast in eligible}

        if len(models) != 1:
            raise CalibrationDataError(
                "calibration requires forecasts from exactly one model"
            )

        model = next(iter(models))

        errors = [
            forecast.observed_outcome - forecast.predicted_value
            for forecast in eligible
            if forecast.observed_outcome is not None
        ]

        mse = sum(error * error for error in errors) / len(errors)
        mean_error = sum(errors) / len(errors)

        directional_bias = self._directional_bias(eligible)

        probabilities = [
            forecast
            for forecast in eligible
            if forecast.probability is not None
        ]

        brier_score = None

        if probabilities:
            brier_components = []

            for forecast in probabilities:
                if forecast.observed_outcome not in (0.0, 1.0):
                    raise CalibrationDataError(
                        "Brier score requires binary outcomes"
                    )

                probability = forecast.probability
                if probability is None:
                    raise CalibrationDataError(
                        "probability unexpectedly missing"
                    )

                brier_components.append(
                    (probability - forecast.observed_outcome) ** 2
                )

            brier_score = (
                sum(brier_components) / len(brier_components)
            )

        status, recommendation = self._decision(
            sample_size=len(eligible),
            mse=mse,
            brier_score=brier_score,
            directional_bias=directional_bias,
        )

        return CalibrationRecord(
            model=model,
            evaluated_at=current_time,
            sample_size=len(eligible),
            mse=mse,
            brier_score=brier_score,
            directional_bias=directional_bias,
            mean_error=mean_error,
            status=status,
            recommendation=recommendation,
        )

    @staticmethod
    def _directional_bias(
        forecasts: list[ForecastRecord],
    ) -> float:
        directional_errors: list[float] = []

        for forecast in forecasts:
            if forecast.direction is None:
                continue

            if forecast.observed_outcome is None:
                raise CalibrationDataError(
                    "directional forecast has no outcome"
                )

            observed_direction = (
                1
                if forecast.observed_outcome > forecast.predicted_value
                else -1
                if forecast.observed_outcome < forecast.predicted_value
                else 0
            )

            directional_errors.append(
                float(observed_direction - forecast.direction)
            )

        if not directional_errors:
            return 0.0

        return sum(directional_errors) / len(directional_errors)

    def _decision(
        self,
        sample_size: int,
        mse: float,
        brier_score: float | None,
        directional_bias: float,
    ) -> tuple[str, str]:
        if sample_size < self._minimum_sample_size:
            return (
                "INSUFFICIENT_SAMPLE",
                "KEEP_WITHOUT_CALIBRATION_PROMOTION",
            )

        if mse > self._max_mse:
            return (
                "FAILED",
                "RETIRE_OR_ROUTE_TO_BASELINE",
            )

        if (
            brier_score is not None
            and brier_score > self._max_brier_score
        ):
            return (
                "FAILED",
                "RETIRE_OR_ROUTE_TO_BASELINE",
            )

        if abs(directional_bias) > self._max_absolute_bias:
            return (
                "DEGRADED",
                "PENALIZE_AND_RECALIBRATE",
            )

        return (
            "PASSED",
            "KEEP_ACTIVE",
        )