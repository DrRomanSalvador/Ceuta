from backend.app.core.causal.advanced import (
    ActiveCausalLearning,
    ActiveCausalQuery,
    CausalEffect,
    CausalModel,
    CausalModelEnsemble,
    CausalStressTester,
    ConfoundingAnalyzer,
    CounterfactualEngine,
    CrossDomainCausalEngine,
    FeedbackAnalyzer,
    InteractionAnalyzer,
    ProspectiveCausalValidator,
    RegimeCausalEngine,
    TemporalCausalAnalyzer,
    TemporalObservation,
)


def test_temporal_precedence_is_explicit_and_not_causality() -> None:
    observations = [
        TemporalObservation("x", 0, 1),
        TemporalObservation("x", 1, 2),
        TemporalObservation("y", 2, 3),
    ]
    relations = TemporalCausalAnalyzer().relations(observations)
    assert any(r.cause == "x" and r.effect == "y" for r in relations)
    assert not hasattr(relations[0], "identified")


def test_unresolved_confounding_blocks_claim() -> None:
    assert ConfoundingAnalyzer.adjustment_status(["z"], []) == "unresolved_confounding"
    assert ConfoundingAnalyzer.adjustment_status(["z"], ["z"]) == "known_backdoor_candidates_addressed"


def test_interactions_are_candidates_not_causal_claims() -> None:
    assert InteractionAnalyzer.candidates("x", ["z"]) == ("x*z",)
    assert InteractionAnalyzer.classify(2.0, None) == "untested"


def test_model_disagreement_is_preserved() -> None:
    models = [
        CausalModel("a", (("x", "y"),), ("consistency",), 0.6),
        CausalModel("b", (("z", "y"),), ("consistency",), 0.4),
    ]
    assert ("x", "y") in CausalModelEnsemble.disagreement(models)
    assert ("z", "y") in CausalModelEnsemble.disagreement(models)


def test_counterfactual_requires_identification() -> None:
    try:
        CounterfactualEngine.compute(1.0, 2.0, False, ["a"])
    except ValueError:
        pass
    else:
        raise AssertionError("unidentified counterfactual must be rejected")


def test_cross_domain_links_are_explicit() -> None:
    links = CrossDomainCausalEngine.connect([
        ("health", "admissions", "mobility", "flows"),
        ("health", "admissions", "health", "beds"),
    ])
    assert links == (("health", "admissions", "mobility", "flows"),)


def test_regime_dependence_is_preserved() -> None:
    effects = [
        CausalEffect("x", "y", "ATE", 1.0, 0.5, 1.5, True, ("a",), regime="normal"),
        CausalEffect("x", "y", "ATE", -1.0, -1.5, -0.5, True, ("a",), regime="crisis"),
    ]
    assert RegimeCausalEngine.compare(effects)["normal"] == (1.0,)
    assert RegimeCausalEngine.compare(effects)["crisis"] == (-1.0,)


def test_feedback_requires_lag() -> None:
    loop = FeedbackAnalyzer.assess(["x", "y"], 0.8, True, threshold=2.0, hysteresis=True)
    assert loop.lagged and loop.hysteresis and loop.tipping_threshold == 2.0


def test_stress_testing_breaks_assumptions_explicitly() -> None:
    model = CausalModel("m", (("x", "y"),), ("no_unmeasured_confounding",))
    challenges = CausalStressTester.challenge(model, ["positivity", "no_unmeasured_confounding"])
    assert [c.target_assumption for c in challenges] == ["positivity"]


def test_active_learning_ranks_information_per_cost() -> None:
    queries = [
        ActiveCausalQuery("q1", "measure z", "confounding", 1.0, 2.0, 1.0, "resolve confounding"),
        ActiveCausalQuery("q2", "measure x", "direction", 2.0, 1.0, 1.0, "resolve direction"),
    ]
    assert ActiveCausalLearning.rank(queries)[0].query_id == "q2"


def test_prospective_validation_is_closed_loop() -> None:
    result = ProspectiveCausalValidator.validate("h1", 2.0, 2.1, 0.2, "i1")
    assert result.validated and result.error == 0.1
