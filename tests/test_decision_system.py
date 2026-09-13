import pytest

from backend.app.core.decision.decision_system import (
    DecisionContext,
    DecisionDisposition,
    DecisionMode,
    DecisionObjective,
    DecisionOption,
    DecisionSystem,
    InformationRequest,
    ScenarioOutcome,
)


def outcome(sid: str, probability: float, utility: float, harm: float, regret: float = 0.0):
    return ScenarioOutcome(sid, probability, utility, harm, regret)


def test_recommendation_supports_robust_utility_and_harm_policies():
    context = DecisionContext("d1", "human_authority", "72h", (DecisionObjective("public_value", 1.0),))
    options = (
        DecisionOption("A", (outcome("s1", .5, 10, 2, 4), outcome("s2", .5, 0, 1, 8)), uncertainty=.2),
        DecisionOption("B", (outcome("s1", .5, 7, 1, 2), outcome("s2", .5, 5, 1, 3)), uncertainty=.2),
    )
    system = DecisionSystem()
    robust = system.recommend(context, options, mode=DecisionMode.ROBUST)
    utility = system.recommend(context, options, mode=DecisionMode.UTILITY)
    harm = system.recommend(context, options, mode=DecisionMode.HARM_MINIMIZATION)
    assert robust.option_id == "B"
    assert utility.option_id == "A"
    assert harm.option_id == "B"


def test_abstention_is_fail_closed():
    context = DecisionContext("d2", "human_authority", "24h", (DecisionObjective("safety", 1.0),))
    option = DecisionOption("A", (outcome("s1", 1.0, 5, 2),), uncertainty=.9)
    result = DecisionSystem().recommend(context, (option,), max_uncertainty=.5)
    assert result.disposition is DecisionDisposition.ABSTAIN
    assert result.option_id == "ABSTAIN"


def test_uncertainty_can_force_human_review():
    context = DecisionContext("d3", "human_authority", "24h", (DecisionObjective("safety", 1.0),))
    option = DecisionOption("A", (outcome("s1", 1.0, 5, 2),), uncertainty=.4)
    result = DecisionSystem().recommend(context, (option,), human_review_threshold=.35)
    assert result.disposition is DecisionDisposition.HUMAN_REVIEW


def test_information_value_is_explicit_and_ranked():
    system = DecisionSystem()
    ranked = system.rank_information((
        InformationRequest("low", 2, 3, 1),
        InformationRequest("high", 10, 2, 1),
    ))
    assert ranked[0].question == "high"
    assert ranked[0].net_value == 8


def test_contracts_reject_invalid_probability_mass():
    with pytest.raises(ValueError):
        DecisionOption("A", (outcome("s1", .8, 1, 1),), uncertainty=.1)
