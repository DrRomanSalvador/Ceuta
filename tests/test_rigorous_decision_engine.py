import pytest

from backend.app.core.decision.rigorous_engine import Alternative, RigorousDecisionEngine


def test_expected_utility_selects_best_feasible_option_and_computes_regret():
    engine = RigorousDecisionEngine()
    alternatives = (
        Alternative("A", {"good": 10, "bad": -10}, {"good": 1, "bad": 8}),
        Alternative("B", {"good": 7, "bad": 3}, {"good": 1, "bad": 2}),
    )
    analyses = engine.analyze(alternatives, {"good": 0.5, "bad": 0.5})
    chosen = engine.select(analyses)
    assert chosen.option_id == "B"
    assert analyses[0].maximum_regret == pytest.approx(13.0)
    assert analyses[1].maximum_regret == pytest.approx(3.0)


def test_hard_harm_constraint_is_fail_closed():
    engine = RigorousDecisionEngine()
    alternatives = (
        Alternative("unsafe", {"s": 20}, {"s": 10}),
        Alternative("safe", {"s": 8}, {"s": 2}),
    )
    analyses = engine.analyze(alternatives, {"s": 1.0}, max_expected_harm=3)
    assert engine.select(analyses).option_id == "safe"
    assert analyses[0].feasible is False


def test_missing_scenario_is_rejected():
    engine = RigorousDecisionEngine()
    alternatives = (Alternative("A", {"s1": 1}, {"s1": 0}),)
    with pytest.raises(ValueError):
        engine.analyze(alternatives, {"s1": 0.5, "s2": 0.5})


def test_probability_mass_is_rejected_when_invalid():
    engine = RigorousDecisionEngine()
    alternative = Alternative("A", {"s": 1}, {"s": 0})
    with pytest.raises(ValueError):
        engine.analyze((alternative,), {"s": 0.9})
