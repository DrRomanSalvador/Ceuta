from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CalibrationDrift:
    model_id: str
    baseline_error: float
    current_error: float
    drift: float
    alert: bool


class CalibrationDriftDetector:
    def compare(self, model_id: str, *, baseline_error: float, current_error: float, threshold: float) -> CalibrationDrift:
        drift = current_error - baseline_error
        return CalibrationDrift(model_id, baseline_error, current_error, drift, drift > threshold)
