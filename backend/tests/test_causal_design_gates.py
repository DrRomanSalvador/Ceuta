from app.core.causal.contracts import CausalEdge, CausalHypothesis
from app.core.causal.graph import CausalGraph
from app.core.causal.identification import CausalIdentifier


def test_causal_identification_blocks_when_design_assumptions_are_missing() -> None:
    graph = CausalGraph([CausalEdge("x", "y")])
    hypothesis = CausalHypothesis(
        hypothesis_id="h1",
        exposure="x",
        outcome="y",
        estimand="ATE",
    )

    assessment = CausalIdentifier().assess(graph, hypothesis)

    assert not assessment.identified
    assert "target_population_not_declared" in assessment.blockers
    assert "positivity_not_declared" in assessment.blockers
    assert "interference_not_addressed" in assessment.blockers
