from app.core.decision.decision_system import DecisionMode
from app.core.decision.engine import (
    ActionAlternative,
    DecisionAction,
    DecisionEngine,
    EpistemicGate,
    Scenario,
)
from app.core.decision.optimization import ValueOfInformation


def _options() -> tuple[ActionAlternative, ActionAlternative]:
    return (
        ActionAlternative(
            "observe",
            (
                Scenario("good", 0.7, 10.0, 1.0),
                Scenario("bad", 0.3, 2.0, 0.0),
            ),
            resource_cost=1.0,
        ),
        ActionAlternative(
            "act",
            (
                Scenario("good", 0.7, 14.0, 2.0),
                Scenario("bad", 0.3, -10.0, 20.0),
            ),
            resource_cost=1.0,
        ),
    )


def test_failed_epistemic_gate_abstains() -> None:
    result = DecisionEngine().evaluate(
        decision_id="d1",
        options=_options(),
        gate=EpistemicGate(True, True, False, True),
    )
    assert result.audit.action is DecisionAction.ABSTAIN
    assert "not_calibrated" in result.audit.epistemic_failures


def test_positive_information_value_becomes_action() -> None:
    info = ValueOfInformation("measure", 8.0, 2.0, 6.0, ("valid",))
    result = DecisionEngine().evaluate(
        decision_id="d2",
        options=_options(),
        gate=EpistemicGate(True, True, True, True),
        information_request=info,
    )
    assert result.audit.action is DecisionAction.ACQUIRE_INFORMATION
    assert result.audit.selected_option == "INFORMATION_ACQUISITION"


def test_robust_decision_respects_harm_constraint() -> None:
    result = DecisionEngine().evaluate(
        decision_id="d3",
        options=_options(),
        gate=EpistemicGate(True, True, True, True),
        mode=DecisionMode.ROBUST,
        max_harm=3.0,
    )
    assert result.audit.action is DecisionAction.RECOMMEND
    assert result.audit.selected_option == "observe"
    assert result.score is not None
    assert result.score.expected_harm <= 3.0


def test_regret_is_computed_against_best_action_per_scenario() -> None:
    result = DecisionEngine().evaluate(
        decision_id="d4",
        options=_options(),
        gate=EpistemicGate(True, True, True, True),
        mode=DecisionMode.REGRET,
    )
    assert result.score is not None
    assert result.score.maximum_regret >= 0.0
