from backend.app.core.decision.epistemic_gate import EpistemicDecisionGate, EpistemicDisposition
from backend.app.core.decision.review_policy import DecisionRisk, ReviewDisposition, ReviewPolicy
from backend.app.core.decision.temporal_feedback import FeedbackWindow
from backend.app.core.evidence.epistemic import EpistemicStatus


def test_abstention_is_explicit_not_fallback_allow():
    result = EpistemicDecisionGate().evaluate(EpistemicStatus.INSUFFICIENT_EVIDENCE)
    assert result.disposition is EpistemicDisposition.ABSTAIN


def test_human_review_is_explicit():
    policy = ReviewPolicy("safety-1", frozenset({DecisionRisk.LOW}), frozenset({DecisionRisk.MODERATE}), frozenset({DecisionRisk.HIGH, DecisionRisk.CRITICAL}))
    assert policy.disposition(DecisionRisk.MODERATE) is ReviewDisposition.HUMAN_REVIEW


def test_temporal_feedback_requires_post_decision_outcomes():
    window = FeedbackWindow("2026-09-13T10:00:00+00:00", "2026-09-13T11:00:00+00:00", "2026-09-14T10:00:00+00:00")
    assert window.outcome_time > window.decision_time
