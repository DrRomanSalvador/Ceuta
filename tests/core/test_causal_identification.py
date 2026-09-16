from app.core.causal.contracts import CausalEdge, CausalHypothesis
from app.core.causal.graph import CausalGraph
from app.core.causal.identification import CausalIdentifier


def _hypothesis(**overrides: object) -> CausalHypothesis:
    values: dict[str, object] = {
        "hypothesis_id": "h1",
        "exposure": "x",
        "outcome": "y",
        "estimand": "average_treatment_effect",
        "population": "target-population",
        "time_zero": "t0",
        "consistency_declared": True,
        "positivity_declared": True,
        "interference_addressed": True,
        "time_varying_confounding_addressed": True,
        "transportability_addressed": False,
        "assumptions": ("consistency", "positivity"),
    }
    values.update(overrides)
    return CausalHypothesis(**values)


def test_negative_controls_are_falsification_diagnostics_not_universal_identification_blockers() -> None:
    graph = CausalGraph([CausalEdge("x", "y")])

    assessment = CausalIdentifier().assess(graph, _hypothesis())

    assert assessment.identified is True
    assert "negative_control_tests_not_declared" in assessment.assumptions
    assert "negative_controls_missing" not in assessment.blockers


def test_transportability_is_not_required_for_internal_identification() -> None:
    graph = CausalGraph([CausalEdge("x", "y")])

    assessment = CausalIdentifier().assess(graph, _hypothesis())

    assert assessment.identified is True
    assert "transportability_not_established" in assessment.assumptions
    assert "transportability_not_addressed" not in assessment.blockers


def test_unaddressed_backdoor_candidate_still_blocks_identification() -> None:
    graph = CausalGraph([CausalEdge("u", "x"), CausalEdge("u", "y"), CausalEdge("x", "y")])

    assessment = CausalIdentifier().assess(graph, _hypothesis())

    assert assessment.identified is False
    assert "unaddressed_backdoor_candidates" in assessment.blockers
