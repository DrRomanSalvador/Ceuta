from app.core.scientific.intervention_independent_validation import (
    EvaluationStatus,
    InterventionIndependentValidationLedger,
    ValidationLane,
    ValidationObservation,
)


def test_intervened_success_is_not_naive_false_positive_without_counterfactual():
    observation = ValidationObservation(
        "o1", "p1", ValidationLane.INTERVENTION, True, True, False, None,
        ("e1",), ("warning:p1",), "2026-09-15T00:00:00+00:00",
    )
    assert observation.evaluation_status is EvaluationStatus.COUNTERFACTUAL_REQUIRED
    assert observation.ordinary_accuracy_label is None


def test_shadow_lane_remains_ordinary_scoreable():
    observation = ValidationObservation(
        "o2", "p2", ValidationLane.SHADOW, True, False, False, None,
        ("e2",), ("warning:p2",), "2026-09-15T00:00:00+00:00",
    )
    assert observation.evaluation_status is EvaluationStatus.SCOREABLE
    assert observation.ordinary_accuracy_label == "false_positive"


def test_validation_persistence_integrity(tmp_path):
    ledger = InterventionIndependentValidationLedger(str(tmp_path / "validation.sqlite"))
    observation = ValidationObservation(
        "o3", "p3", ValidationLane.CONTROL, False, False, False, None,
        ("e3",), ("control:p3",), "2026-09-15T00:00:00+00:00",
    )
    ledger.append(observation)
    assert ledger.verify_integrity()
