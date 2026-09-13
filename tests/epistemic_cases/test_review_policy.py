from backend.app.core.decision.review_policy import DecisionRisk, ReviewDisposition, ReviewPolicy


def test_review_policy_is_risk_based():
    policy = ReviewPolicy("risk-1", frozenset({DecisionRisk.LOW}), frozenset({DecisionRisk.MODERATE, DecisionRisk.HIGH}), frozenset({DecisionRisk.CRITICAL}))
    assert policy.disposition(DecisionRisk.LOW) is ReviewDisposition.AUTO
    assert policy.disposition(DecisionRisk.HIGH) is ReviewDisposition.HUMAN_REVIEW
    assert policy.disposition(DecisionRisk.CRITICAL) is ReviewDisposition.ABSTAIN
