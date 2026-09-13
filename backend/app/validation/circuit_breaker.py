"""Fail-closed mathematical gate for prospective calibration."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime


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


class CalibrationCircuitBreaker:
    """Fail-closed promotion gate for forecast calibration."""

    def __init__(
        self,
        *,
        max_degradation: float = 2.0,
        min_coverage: float = 0.80,
        min_sample_size: int = 10,
        require_baseline: bool = True,
        require_interval_coverage: bool = False,
    ) -> None:
        if not math.isfinite(max_degradation) or max_degradation < 0.0:
            raise ValueError("max_degradation must be finite and non-negative")
        if not 0.0 <= min_coverage <= 1.0:
            raise ValueError("min_coverage must be between 0 and 1")
        if min_sample_size < 1:
            raise ValueError("min_sample_size must be positive")
        self.max_degradation = max_degradation
        self.min_coverage = min_coverage
        self.min_sample_size = min_sample_size
        self.require_baseline = require_baseline
        self.require_interval_coverage = require_interval_coverage

    def evaluate(self, report: ValidationReport) -> bool:
        """Return True only when the numerical evidence satisfies every gate."""
        if not isinstance(report, ValidationReport):
            raise TypeError("report must be a ValidationReport")
        if report.sample_size < self.min_sample_size:
            return False
        if not all(math.isfinite(value) for value in (report.mae, report.mse, report.bias)):
            return False
        if report.mae < 0.0 or report.mse < 0.0:
            return False
        if self.require_baseline:
            if report.baseline_mse is None or not math.isfinite(report.baseline_mse):
                return False
            if report.baseline_mse < 0.0:
                return False
            if report.baseline_mse == 0.0:
                if report.mse > 0.0:
                    return False
            elif report.degradation_ratio is None:
                return False
        if report.degradation_ratio is not None:
            if not math.isfinite(report.degradation_ratio):
                return False
            if report.degradation_ratio < 0.0 or report.degradation_ratio > self.max_degradation:
                return False
        if self.require_interval_coverage and report.interval_coverage is None:
            return False
        if report.interval_coverage is not None:
            if not math.isfinite(report.interval_coverage):
                return False
            if not 0.0 <= report.interval_coverage <= 1.0:
                return False
            if report.interval_coverage < self.min_coverage:
                return False
        return report.passed
