"""Layer 3 validation contracts and metrics.

The module deliberately gates operational prediction rather than implementing a
predictive model. A model cannot be operationally enabled unless temporal,
out-of-sample, calibration, robustness, adversarial and drift requirements have
been explicitly evaluated.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from typing import Sequence


class ValidationStatus(StrEnum):
    BLOCKED = "BLOCKED"
    VALIDATED = "VALIDATED"


@dataclass(frozen=True, slots=True)
class CalibrationSummary:
    expected_calibration_error: float
    bins: int
    samples: int

    def __post_init__(self) -> None:
        if self.bins < 1:
            raise ValueError("bins must be positive")
        if self.samples < 1:
            raise ValueError("samples must be positive")
        if not 0.0 <= self.expected_calibration_error <= 1.0:
            raise ValueError("expected_calibration_error must be in [0, 1]")


@dataclass(frozen=True, slots=True)
class ValidationSummary:
    temporal_integrity_passed: bool
    out_of_sample_passed: bool
    calibration_passed: bool
    robustness_passed: bool
    adversarial_passed: bool
    drift_assessed: bool
    test_samples: int
    lead_time_seconds: float | None
    brier_score: float | None = None
    expected_calibration_error: float | None = None

    @property
    def status(self) -> ValidationStatus:
        lead_time_valid = self.lead_time_seconds is not None and self.lead_time_seconds >= 0
        return (
            ValidationStatus.VALIDATED
            if all(
                (
                    self.temporal_integrity_passed,
                    self.out_of_sample_passed,
                    self.calibration_passed,
                    self.robustness_passed,
                    self.adversarial_passed,
                    self.drift_assessed,
                    self.test_samples > 0,
                    lead_time_valid,
                )
            )
            else ValidationStatus.BLOCKED
        )


class PredictionValidationGate:
    """Final gate before any future operational prediction is enabled."""

    def __init__(self, summary: ValidationSummary) -> None:
        self.summary = summary

    @property
    def status(self) -> ValidationStatus:
        return self.summary.status

    def assert_operational_prediction_allowed(self) -> None:
        """Fail closed unless every mandatory validation dimension has passed."""
        if self.status is not ValidationStatus.VALIDATED:
            failed = [
                name
                for name, passed in (
                    ("temporal_integrity", self.summary.temporal_integrity_passed),
                    ("out_of_sample", self.summary.out_of_sample_passed),
                    ("calibration", self.summary.calibration_passed),
                    ("robustness", self.summary.robustness_passed),
                    ("adversarial", self.summary.adversarial_passed),
                    ("drift_assessed", self.summary.drift_assessed),
                )
                if not passed
            ]
            if self.summary.test_samples <= 0:
                failed.append("test_samples")
            if self.summary.lead_time_seconds is None or self.summary.lead_time_seconds < 0:
                failed.append("lead_time")
            raise RuntimeError(
                "Operational prediction is blocked; validation requirements not satisfied: "
                + ", ".join(failed)
            )


def _validate_binary_inputs(probabilities: Sequence[float], outcomes: Sequence[int]) -> None:
    if len(probabilities) != len(outcomes) or not probabilities:
        raise ValueError("probabilities and outcomes must have the same non-zero length")
    for probability in probabilities:
        if not isfinite(probability) or not 0.0 <= probability <= 1.0:
            raise ValueError("probabilities must be finite values in [0, 1]")
    if any(outcome not in (0, 1) for outcome in outcomes):
        raise ValueError("outcomes must be binary values 0 or 1")


def brier_score(probabilities: Sequence[float], outcomes: Sequence[int]) -> float:
    """Return the binary Brier score; lower is better."""
    _validate_binary_inputs(probabilities, outcomes)
    return sum((probability - outcome) ** 2 for probability, outcome in zip(probabilities, outcomes)) / len(
        outcomes
    )


def binary_classification_metrics(
    predictions: Sequence[int], outcomes: Sequence[int]
) -> dict[str, float]:
    """Return precision, recall, false-positive and false-negative rates."""
    if len(predictions) != len(outcomes) or not predictions:
        raise ValueError("predictions and outcomes must have the same non-zero length")
    if any(value not in (0, 1) for value in predictions + outcomes):
        raise ValueError("predictions and outcomes must be binary values 0 or 1")

    true_positive = sum(prediction == outcome == 1 for prediction, outcome in zip(predictions, outcomes))
    true_negative = sum(prediction == outcome == 0 for prediction, outcome in zip(predictions, outcomes))
    false_positive = sum(prediction == 1 and outcome == 0 for prediction, outcome in zip(predictions, outcomes))
    false_negative = sum(prediction == 0 and outcome == 1 for prediction, outcome in zip(predictions, outcomes))

    precision_denominator = true_positive + false_positive
    recall_denominator = true_positive + false_negative
    negative_denominator = true_negative + false_positive
    positive_denominator = true_positive + false_negative

    return {
        "precision": true_positive / precision_denominator if precision_denominator else 0.0,
        "recall": true_positive / recall_denominator if recall_denominator else 0.0,
        "false_positive_rate": false_positive / negative_denominator if negative_denominator else 0.0,
        "false_negative_rate": false_negative / positive_denominator if positive_denominator else 0.0,
    }


def expected_calibration_error(
    probabilities: Sequence[float], outcomes: Sequence[int], bins: int = 10
) -> CalibrationSummary:
    """Calculate equal-width expected calibration error for binary forecasts."""
    _validate_binary_inputs(probabilities, outcomes)
    if bins < 1:
        raise ValueError("bins must be positive")

    total_error = 0.0
    count = len(probabilities)
    for index in range(bins):
        lower = index / bins
        upper = (index + 1) / bins
        members = [
            (probability, outcome)
            for probability, outcome in zip(probabilities, outcomes)
            if lower <= probability < upper or (index == bins - 1 and probability == 1.0)
        ]
        if not members:
            continue
        mean_probability = sum(item[0] for item in members) / len(members)
        observed_frequency = sum(item[1] for item in members) / len(members)
        total_error += abs(mean_probability - observed_frequency) * len(members) / count

    return CalibrationSummary(
        expected_calibration_error=total_error,
        bins=bins,
        samples=count,
    )
