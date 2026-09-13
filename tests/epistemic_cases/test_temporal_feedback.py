import pytest

from backend.app.core.decision.temporal_feedback import CausalFeedbackContract, FeedbackWindow


def test_feedback_window_is_temporally_ordered() -> None:
    window = FeedbackWindow(
        "2026-09-13T10:00:00+00:00",
        "2026-09-20T10:00:00+00:00",
        "2026-10-13T10:00:00+00:00",
    )
    assert window.outcome_time >= window.decision_time


def test_pre_decision_outcome_is_rejected() -> None:
    with pytest.raises(ValueError):
        FeedbackWindow(
            "2026-09-13T10:00:00+00:00",
            "2026-09-12T10:00:00+00:00",
            "2026-10-13T10:00:00+00:00",
        )


def test_causal_feedback_requires_identification_assumptions() -> None:
    with pytest.raises(ValueError):
        CausalFeedbackContract(
            intervention_ref="intervention:1",
            target_ref="target:1",
            comparator_ref="comparator:1",
            time_zero="2026-09-13T10:00:00+00:00",
            identification_assumptions=(),
            causal_question="What is the effect?",
        )
