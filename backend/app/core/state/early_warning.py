"""Descriptive early-warning indicators for changing system dynamics.

Indicators are signals of changing dynamics, not proofs of impending
transitions. No universal threshold is encoded here.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class EarlyWarningIndicators:
    variance: float
    lag1_autocorrelation: float | None
    mean_recovery_time: float | None
    distribution_shift: float | None
    window_size: int
    warnings: tuple[str, ...]


class EarlyWarningEngine:
    def compute(self, values: tuple[float, ...], *, recovery_times: tuple[float, ...] = (), variance_reference: float | None = None, autocorrelation_reference: float | None = None) -> EarlyWarningIndicators:
        if len(values) < 2:
            raise ValueError("at least two values are required")
        if any(not isfinite(value) for value in values):
            raise ValueError("values must be finite")
        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / (len(values) - 1)
        lag1 = None
        if len(values) >= 3:
            centered = [value - mean for value in values]
            denominator = sum(value * value for value in centered[:-1])
            lag1 = sum(a * b for a, b in zip(centered, centered[1:])) / denominator if denominator else 0.0
        recovery = None
        if recovery_times:
            if any(time <= 0 or not isfinite(time) for time in recovery_times):
                raise ValueError("recovery times must be finite and positive")
            recovery = sum(recovery_times) / len(recovery_times)
        shift = None if variance_reference is None else variance - variance_reference
        warnings: list[str] = []
        if variance_reference is not None and variance > variance_reference:
            warnings.append("variance_increase")
        if autocorrelation_reference is not None and lag1 is not None and lag1 > autocorrelation_reference:
            warnings.append("autocorrelation_increase")
        if recovery is not None:
            warnings.append("recovery_times_observed")
        return EarlyWarningIndicators(variance, lag1, recovery, shift, len(values), tuple(warnings))
