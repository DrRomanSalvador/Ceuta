from datetime import datetime, timezone

from app.core.decision.decision_system import DecisionContext, DecisionMode, DecisionObjective, DecisionOption, ScenarioOutcome
from app.core.decision.review_policy import DecisionRisk
from app.core.evidence.epistemic import EpistemicStatus


def _context(risk: DecisionRisk) -> DecisionContext:
    return DecisionContext(
        decision_id="d-live",
        decision_maker="operator",
        horizon="24h",
        objectives=(DecisionObjective("expected_utility", 1.0),),
        risk_class=risk,
    )


def _option() -> DecisionOption:
    return DecisionOption(
        option_id="a",
        outcomes=(ScenarioOutcome("s", 1.0, utility=10.0, harm=0.0),),
        uncertainty=0.1,
    )


def test_risk_policy_is_terminal_without_uncertainty_cutoff():
    from app.core.decision.decision_system import DecisionSystem

    system = DecisionSystem()
    recommendation = system.recommend(_context(DecisionRisk.CRITICAL), (_option(),), mode=DecisionMode.UTILITY)
    assert recommendation.disposition.value == "abstain"
    assert any("risk policy" in reason for reason in recommendation.reasons)


def test_arbitrary_uncertainty_cutoff_is_rejected():
    from app.core.decision.decision_system import DecisionSystem

    try:
        DecisionSystem().recommend(_context(DecisionRisk.LOW), (_option(),), max_uncertainty=0.5)
    except ValueError as exc:
        assert "arbitrary uncertainty cutoffs" in str(exc)
    else:
        raise AssertionError("arbitrary uncertainty cutoff must not be accepted")


def test_epistemic_status_is_explicitly_available_to_runtime_contract():
    assert EpistemicStatus.INSUFFICIENT_EVIDENCE.value == "insufficient_evidence"
    assert datetime.now(timezone.utc).tzinfo is not None
