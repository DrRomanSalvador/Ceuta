from app.core.scientific.robust_decision import (
    AdaptivePathway,
    BayesianModelAverager,
    CausalIdentificationContract,
    ExploratoryModel,
    ModelForecast,
    RobustDecisionMaker,
    Signpost,
)


def test_exploratory_model_enumerates_plausible_futures_without_probabilities():
    design = ExploratoryModel({"demand": (0.5, 1.0, 1.5), "growth": (-1.0, 0.0, 1.0)})
    futures = design.futures()
    assert len(futures) == 9
    assert all(len(f.assumptions) == 2 for f in futures)


def test_rdm_prefers_robust_strategy_over_high_average_strategy():
    futures = ExploratoryModel({"shock": (0.0, 1.0, 2.0, 3.0)}).futures()

    def fragile(future):
        return 10.0 if dict(future.assumptions)["shock"] < 2 else -10.0

    def robust(future):
        return 4.0

    profiles = RobustDecisionMaker(threshold=0.0).evaluate(
        {"fragile": fragile, "robust": robust}, futures
    )
    assert profiles[0].strategy_id == "robust"
    assert profiles[0].satisficing_rate == 1.0
    assert profiles[0].max_regret > 0


def test_adaptive_pathway_requires_persistent_signpost_trigger():
    pathway = AdaptivePathway(
        "p1",
        "strategy-a",
        (Signpost("s1", "stress", 0.8, "above", "switch-to-b"),),
        trigger_window=2,
    )
    assert pathway.next_actions({"stress": (0.9,)}) == ()
    assert pathway.next_actions({"stress": (0.7, 0.9)}) == ()
    assert pathway.next_actions({"stress": (0.9, 0.95)}) == ("switch-to-b",)


def test_bma_weights_validation_log_predictive_performance_and_exposes_disagreement():
    bma = BayesianModelAverager()
    outcome = bma.validation_log_score(0.8, True)
    assert outcome < 0
    ensemble = bma.combine(
        (
            ModelForecast("strong", 1.0, -0.1, 0.8),
            ModelForecast("weak", 1.0, -2.0, 0.2),
        )
    )
    assert ensemble.weights[0][0] == "strong"
    assert ensemble.weights[0][1] > ensemble.weights[1][1]
    assert 0.2 < ensemble.probability < 0.8
    assert ensemble.disagreement > 0


def test_causal_contract_refuses_implicit_identifiability():
    non_identified = CausalIdentificationContract(
        "ATE",
        "treatment",
        "outcome",
        ("age",),
        ("consistency", "positivity"),
    )
    assert not non_identified.identifiable

    identified = CausalIdentificationContract(
        "ATE",
        "treatment",
        "outcome",
        ("age", "baseline-risk"),
        ("consistency", "conditional_exchangeability", "positivity"),
        unobserved_confounding_sensitivity=0.3,
    )
    assert identified.identifiable
