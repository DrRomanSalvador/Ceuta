"""Calibration metrics for probabilistic forecasts.

These metrics evaluate declared prediction intervals against observed outcomes.
They do not label a forecast calibrated without prospective outcome data.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class IntervalObservation:
    lower: float
    upper: float
    observed: float

    def __post_init__(self) -> None:
        if not all(isfinite(v) for v in (self.lower, self.upper, self.observed)):
            raise ValueError("interval values must be finite")
        if self.lower > self.upper:
            raise ValueError("lower must not exceed upper")


@dataclass(frozen=True, slots=True)
class CalibrationResult:
    nominal_coverage: float
    empirical_coverage: float
    coverage_error: float
    mean_interval_width: float
    sample_size: int
    calibrated: bool
    tolerance: float


class ForecastCalibrationEngine:
    def evaluate_intervals(
        self,
        observations: tuple[IntervalObservation, ...],
        *,
        nominal_coverage: float,
        tolerance: float = 0.05,
    ) -> CalibrationResult:
        if not observations:
            raise ValueError("observations must not be empty")
        if not 0.0 < nominal_coverage < 1.0:
            raise ValueError("nominal_coverage must be in (0,1)")
        if tolerance < 0 or not isfinite(tolerance):
            raise ValueError("tolerance must be finite and non-negative")
        covered = sum(item.lower <= item.observed <= item.upper for item in observations)
        empirical = covered / len(observations)
        error = empirical - nominal_coverage
        width = sum(item.upper - item.lower for item in observations) / len(observations)
        return CalibrationResult(
            nominal_coverage=nominal_coverage,
            empirical_coverage=empirical,
            coverage_error=error,
            mean_interval_width=width,
            sample_size=len(observations),
            calibrated=abs(error) <= tolerance,
            tolerance=tolerance,
        )
