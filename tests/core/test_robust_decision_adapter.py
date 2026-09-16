from app.core.scientific.governance_signals import GovernanceDisposition, ScientificGovernance
from app.core.scientific.robust_decision import (
    BayesianModelAverager,
    CausalIdentificationContract,
    ExploratoryModel,
    ModelForecast,
    RobustDecisionMaker,
)
from app.core.scientific.robust_decision_adapter import RobustDecisionGovernanceAdapter


def test_low_robustness_and_model_disagreement_gate_governance(tmp_path):
    futures = ExploratoryModel({"shock": (0.0, 1.0, 2.0)}).futures()
    profiles = RobustDecisionMaker(threshold=0.0).evaluate(
        {"fragile": lambda f: 5.0 if dict(f.assumptions)["shock"] < 1 else -5.0, "safe": lambda f: 1.0},
        futures,
    )
    ensemble = BayesianModelAverager().combine(
        (ModelForecast("a", 1.0, -0.1, 0.95), ModelForecast("b", 1.0, -0.1, 0.05))
    )
    adapter = RobustDecisionGovernanceAdapter(code_revision="rev", configuration_hash="cfg")
    value = adapter.to_input(
        evidence_ids=("e1",), provenance_refs=("p1",), evidence_quality=0.9,
        independent_evidence_ratio=0.9, contradiction_ratio=0.0,
        robustness=profiles[-1], ensemble=ensemble,
    )
    signal = ScientificGovernance(storage_path=str(tmp_path / "g.sqlite")).evaluate("d1", value)
    assert signal.disposition in {GovernanceDisposition.REVIEW_REQUIRED, GovernanceDisposition.ABSTAIN}
    assert value.model_conflict


def test_non_identified_causal_claim_cannot_release(tmp_path):
    futures = ExploratoryModel({"shock": (0.0, 1.0)}).futures()
    profile = RobustDecisionMaker().evaluate({"safe": lambda _: 1.0}, futures)[0]
    causal = CausalIdentificationContract("ATE", "T", "Y", (), ("consistency", "positivity"))
    adapter = RobustDecisionGovernanceAdapter(code_revision="rev", configuration_hash="cfg")
    value = adapter.to_input(
        evidence_ids=("e1",), provenance_refs=("p1",), evidence_quality=0.9,
        independent_evidence_ratio=0.9, contradiction_ratio=0.0,
        robustness=profile, causal=causal,
    )
    signal = ScientificGovernance(storage_path=str(tmp_path / "g.sqlite")).evaluate("d1", value)
    assert signal.disposition == GovernanceDisposition.ABSTAIN
