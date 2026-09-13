"""Fail-closed mathematical gate for prospective calibration.

The circuit breaker prevents an unvalidated model revision from replacing the
last validated revision. It is intentionally conservative: insufficient data,
non-finite metrics, missing comparators, poor interval coverage, or excessive
regression all block promotion.
"""

from __future__ import annotations

import math

from app.core.pipeline.contracts import ValidationReport


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
        """Return True only when the report is safe to promote.

        This method deliberately ignores ``report.passed`` as a source of
        truth. Promotion is recomputed from the numerical evidence so a caller
        cannot bypass the gate by setting a boolean flag.
        """
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
            # A zero baseline with a non-zero model error has an undefined /
            # infinite degradation ratio and must never be promoted.
            if report.baseline_mse == 0.0:
                if report.mse > 0.0:
                    return False
            elif report.degradation_ratio is None:
                return False

        if report.degradation_ratio is not None:
            if not math.isfinite(report.degradation_ratio):
                return False
            if report.degradation_ratio < 0.0:
                return False
            if report.degradation_ratio > self.max_degradation:
                return False

        if self.require_interval_coverage:
            if report.interval_coverage is None:
                return False
            if not math.isfinite(report.interval_coverage):
                return False
        if report.interval_coverage is not None:
            if not 0.0 <= report.interval_coverage <= 1.0:
                return False
            if report.interval_coverage < self.min_coverage:
                return False

        # The report's own flag is useful as an audit field but cannot turn a
        # failed mathematical gate into a pass. Conversely, a report marked
        # failed is never promoted even if its raw metrics happen to pass.
        return report.passed
