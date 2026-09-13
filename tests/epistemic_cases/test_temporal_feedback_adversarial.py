import pytest

from backend.app.core.decision.temporal_feedback import FeedbackWindow


def test_pre_decision_outcome_is_rejected():
    with pytest.raises(ValueError):
        FeedbackWindow("2026-09-13T10:00:00+00:00", "2026-09-13T09:00:00+00:00", "2026-09-14T10:00:00+00:00")


def test_outcome_after_horizon_is_rejected():
    with pytest.raises(ValueError):
        FeedbackWindow("2026-09-13T10:00:00+00:00", "2026-09-15T10:00:00+00:00", "2026-09-14T10:00:00+00:00")
