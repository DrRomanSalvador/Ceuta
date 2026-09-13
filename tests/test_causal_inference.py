from backend.app.core.causal.contracts import (
    CausalEdge,
    CausalEvidence,
    CausalHypothesis,
    EpistemicLevel,
)
from backend.app.core.causal.engine import CausalInferenceEngine
from backend.app.core.causal.graph import CausalGraph
from backend.app.core.causal.intervention import Intervention


def test_association_cannot_become_causal_without_identification_gates():
    graph = CausalGraph([CausalEdge("x", "y")])
    hypothesis = CausalHypothesis(
        hypothesis_id="h1",
        exposure="x",
        outcome="y",
        estimand="ATE",
    )
    assessment = CausalInferenceEngine().assess(graph, hypothesis)
    assert assessment.causality_claim_allowed is False
    assert "causal_assumptions_not_declared" in assessment.residual_uncertainty
    assert "negative_controls_missing" in assessment.residual_uncertainty


def test_causal_claim_requires_identification_and_causal_evidence():
    graph = CausalGraph([CausalEdge("z", "x"), CausalEdge("x", "y")])
    hypothesis = CausalHypothesis(
        hypothesis_id="h2",
        exposure="x",
        outcome="y",
        estimand="ATE",
        assumed_confounders=("z",),
        negative_controls=("nc",),
        assumptions=("consistency", "positivity", "conditional_exchangeability"),
    )
    evidence = (
        CausalEvidence(
            evidence_id="e1",
            hypothesis_id="h2",
            level=EpistemicLevel.CAUSALLY_IDENTIFIED,
            strength=0.9,
            source_ids=("study",),
        ),
    )
    assessment = CausalInferenceEngine().assess(graph, hypothesis, evidence)
    assert assessment.identification.identified is True
    assert assessment.causality_claim_allowed is True


def test_intervention_is_distinct_from_observation():
    intervention = Intervention("x", 1)
    assert intervention.operator == "do"
