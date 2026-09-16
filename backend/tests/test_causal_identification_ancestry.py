from app.core.causal.contracts import CausalEdge
from app.core.causal.graph import CausalGraph


def test_backdoor_candidates_include_non_immediate_exposure_ancestors() -> None:
    graph = CausalGraph(
        [
            CausalEdge("u", "m"),
            CausalEdge("m", "x"),
            CausalEdge("x", "y"),
        ]
    )

    assert graph.backdoor_candidates("x", "y") == ("m", "u")
