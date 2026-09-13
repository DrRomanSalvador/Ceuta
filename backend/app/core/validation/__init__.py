"""Validation infrastructure for prediction-gating in CeutIA.

This package does not produce operational predictions. It defines the contracts and
metrics required before any future prediction capability may be enabled.
"""

from .prediction_gate import (
    CalibrationSummary,
    PredictionValidationGate,
    ValidationStatus,
    ValidationSummary,
    brier_score,
    binary_classification_metrics,
    expected_calibration_error,
)

__all__ = [
    "CalibrationSummary",
    "PredictionValidationGate",
    "ValidationStatus",
    "ValidationSummary",
    "brier_score",
    "binary_classification_metrics",
    "expected_calibration_error",
]
