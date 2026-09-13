"""Adversarial tests for Layer 3 prediction validation gating."""

import pytest

from app.core.validation.prediction_gate import (
    PredictionValidationGate,
    ValidationStatus,
    ValidationSummary,
    brier_score,
    binary_classification_metrics,
    expected_calibration_error,
)


def _validated_summary(**overrides: object) -> ValidationSummary:
    values: dict[str, object] = {
        "temporal_integrity_passed": True,
        "out_of_sample_passed": True,
        "calibration_passed": True,
        "robustness_passed": True,
        "adversarial_passed": True,
        "drift_assessed": True,
        "test_samples": 100,
        "lead_time_seconds": 3600.0,
        "brier_score": 0.08,
        "expected_calibration_error": 0.03,
    }
    values.update(overrides)
    return ValidationSummary(**values)


def test_gate_blocks_when_any_mandatory_dimension_fails() -> None:
    summary = _validated_summary(adversarial_passed=False)
    gate = PredictionValidationGate(summary)

    assert gate.status is ValidationStatus.BLOCKED
    with pytest.raises(RuntimeError, match="adversarial"):
        gate.assert_operational_prediction_allowed()


def test_gate_blocks_without_out_of_sample_evidence() -> None:
    summary = _validated_summary(out_of_sample_passed=False)
    gate = PredictionValidationGate(summary)

    assert gate.status is ValidationStatus.BLOCKED


def test_gate_blocks_without_drift_assessment() -> None:
    summary = _validated_summary(drift_assessed=False)
    gate = PredictionValidationGate(summary)

    assert gate.status is ValidationStatus.BLOCKED


def test_gate_blocks_without_test_samples_or_lead_time() -> None:
    summary = _validated_summary(test_samples=0, lead_time_seconds=None)
    gate = PredictionValidationGate(summary)

    assert gate.status is ValidationStatus.BLOCKED
    with pytest.raises(RuntimeError, match="test_samples"):
        gate.assert_operational_prediction_allowed()


def test_validated_gate_can_be_explicitly_opened() -> None:
    gate = PredictionValidationGate(_validated_summary())

    assert gate.status is ValidationStatus.VALIDATED
    gate.assert_operational_prediction_allowed()


def test_brier_score_is_bounded_and_deterministic() -> None:
    assert brier_score([0.0, 1.0, 0.25, 0.75], [0, 1, 1, 0]) == pytest.approx(0.28125)


def test_binary_classification_metrics() -> None:
    metrics = binary_classification_metrics([1, 1, 0, 0], [1, 0, 1, 0])

    assert metrics["precision"] == pytest.approx(0.5)
    assert metrics["recall"] == pytest.approx(0.5)
    assert metrics["false_positive_rate"] == pytest.approx(0.5)
    assert metrics["false_negative_rate"] == pytest.approx(0.5)


def test_expected_calibration_error() -> None:
    summary = expected_calibration_error([0.1, 0.2, 0.8, 0.9], [0, 0, 1, 1], bins=2)

    assert summary.samples == 4
    assert summary.bins == 2
    assert summary.expected_calibration_error == pytest.approx(0.15)


@pytest.mark.parametrize(
    "probabilities,outcomes",
    [([], []), ([1.2], [1]), ([0.5], [2])],
)
def test_metric_inputs_fail_closed(probabilities: list[float], outcomes: list[int]) -> None:
    with pytest.raises(ValueError):
        brier_score(probabilities, outcomes)
