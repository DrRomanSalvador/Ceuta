from backend.app.core.decision.automation_bias import (
    AutomationBiasGate,
    HumanReviewProtocol,
    RelianceDisposition,
)


def protocol(**overrides):
    values = dict(
        review_id="review:1",
        decision_id="decision:1",
        reviewer_id="human:1",
        model_recommendation="option-a",
        human_initial_judgment="option-b",
        final_judgment="option-b",
        rationale="independent assessment found a material evidence conflict",
        disposition=RelianceDisposition.OVERRIDE,
        model_visible_before_initial_judgment=False,
    )
    values.update(overrides)
    return HumanReviewProtocol(**values)


def test_human_disagreement_is_observable() -> None:
    review = protocol()
    assert review.disagreement_recorded
    assert AutomationBiasGate().evaluate(review)


def test_unresolved_review_cannot_pass() -> None:
    review = protocol(disposition=RelianceDisposition.UNRESOLVED)
    assert not AutomationBiasGate().evaluate(review)


def test_independent_review_requires_model_blind_initial_judgment() -> None:
    try:
        protocol(
            disposition=RelianceDisposition.INDEPENDENT_REVIEW,
            model_visible_before_initial_judgment=True,
        )
    except ValueError:
        return
    raise AssertionError("independent review must not be claimed after prior model exposure")
