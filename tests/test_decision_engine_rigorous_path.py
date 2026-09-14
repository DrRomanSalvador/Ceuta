import pytest

from backend.app.core.decision.decision_system import DecisionMode
from backend.app.core.decision.engine import ActionAlternative, DecisionAction, DecisionEngine, EpistemicGate, Scenario


def gate():
    return EpistemicGate(True, True, True, True, True, True)


def test_rigorous_path_uses_common_scenarios_and_cross_option_regret():
    engine = DecisionEngine()
    options = (
        ActionAlternative("A", (Scenario("s1", .5, 10, 1), Scenario("s2", .5, -10, 8))),
        ActionAlternative("B", (Scenario("s1", .5, 7, 1), Scenario("s2", .5, 3, 2))),
    )
    result = engine.evaluate_rigorously(decision_id="d1", options=options, gate=gate(), mode=DecisionMode.REGRET)
    assert result.audit.selected_option == "B"
    assert result.score is not None
    assert result.score.maximum_regret == pytest.approx(3.0)


def test_rigorous_path_abstains_when_epistemic_gate_fails():
    engine = DecisionEngine()
    result = engine.evaluate_rigorously(
        decision_id="d2",
        options=(),
        gate=EpistemicGate(True, False, True, True),
    )
    assert result.audit.action is DecisionAction.ABSTAIN
    assert "not_identifiable" in result.audit.epistemic_failures


def test_rigorous_path_rejects_mismatched_scenario_space():
    engine = DecisionEngine()
    options = (
        ActionAlternative("A", (Scenario("s1", 1.0, 1, 0),)),
        ActionAlternative("B", (Scenario("s2", 1.0, 2, 0),)),
    )
    with pytest.raises(ValueError):
        engine.evaluate_rigorously(decision_id="d3", options=options, gate=gate())
