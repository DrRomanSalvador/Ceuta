from datetime import UTC, datetime

import pytest

from app.core.epistemology_p0.advanced.hypotheses import Hypothesis, RivalHypothesisSet
from app.core.epistemology_p0.advanced.semantic_graph import EdgeKind, NodeKind, SemanticGraph


def _graph() -> SemanticGraph:
    graph = SemanticGraph()
    for node_id, kind in (
        ("s1", NodeKind.SOURCE),
        ("c1", NodeKind.CLAIM),
        ("e1", NodeKind.EVIDENCE),
        ("e2", NodeKind.EVIDENCE),
        ("h1", NodeKind.HYPOTHESIS),
        ("h2", NodeKind.HYPOTHESIS),
        ("v1", NodeKind.VARIABLE),
        ("p1", NodeKind.CLAIM),
        ("proc1", NodeKind.ENTITY),
        ("proc2", NodeKind.ENTITY),
        ("i1", NodeKind.EVENT),
    ):
        graph.add_node(kind, node_id, node_id)
    return graph


def test_required_relation_types_exist_separately_from_epistemic_states():
    assert {
        EdgeKind.ASSOCIATION,
        EdgeKind.TEMPORAL_PRECEDENCE,
        EdgeKind.SUPPORTS,
        EdgeKind.CONTRADICTS,
        EdgeKind.SOURCE_DEPENDENCY,
        EdgeKind.CAUSAL_HYPOTHESIS,
        EdgeKind.CAUSALITY_SUPPORTED,
        EdgeKind.OBSERVES,
        EdgeKind.PREDICTS,
        EdgeKind.REPORTED_BY,
        EdgeKind.ACQUIRED_BY,
        EdgeKind.REVISED_BY,
        EdgeKind.INTERVENED_ON_BY,
        EdgeKind.MODIFIES,
        EdgeKind.CONDITIONS,
        EdgeKind.CONFOUNDS,
        EdgeKind.FEEDS_BACK_TO,
    }.issubset(set(EdgeKind))


def test_association_does_not_imply_causality():
    graph = _graph()
    edge = graph.add_edge(EdgeKind.ASSOCIATION, "e1", "e2")
    assert edge.kind is EdgeKind.ASSOCIATION
    assert not any(item.kind is EdgeKind.CAUSALITY_SUPPORTED for item in graph.edges.values())


def test_predictive_relation_matches_canonical_forecast_time_semantics():
    graph = _graph()
    edge = graph.add_edge(
        EdgeKind.PREDICTS,
        "e1",
        "p1",
        properties={
            "prediction_id": "pred-1",
            "origin_time": datetime(2026, 9, 15, 8, 0, tzinfo=UTC),
            "horizon": "30d",
        },
    )
    assert edge.kind is EdgeKind.PREDICTS
    assert not any(item.kind in {EdgeKind.CAUSAL_HYPOTHESIS, EdgeKind.CAUSALITY_SUPPORTED} for item in graph.edges.values())


def test_predicts_rejects_embedded_causality_claim():
    graph = _graph()
    with pytest.raises(ValueError, match="causality claim"):
        graph.add_edge(
            EdgeKind.PREDICTS,
            "e1",
            "p1",
            properties={
                "prediction_id": "pred-1",
                "origin_time": datetime(2026, 9, 15, 8, 0, tzinfo=UTC),
                "horizon": "30d",
                "causality_claim": True,
            },
        )


def test_observation_reporting_acquisition_revision_and_intervention_require_identity():
    graph = _graph()
    with pytest.raises(ValueError, match="observation_id"):
        graph.add_edge(EdgeKind.OBSERVES, "proc1", "e1")
    with pytest.raises(ValueError, match="reporting_process_id"):
        graph.add_edge(EdgeKind.REPORTED_BY, "e1", "proc1")
    with pytest.raises(ValueError, match="acquisition_process_id"):
        graph.add_edge(EdgeKind.ACQUIRED_BY, "e1", "proc1")
    with pytest.raises(ValueError, match="revision_id"):
        graph.add_edge(EdgeKind.REVISED_BY, "e1", "e2")
    with pytest.raises(ValueError, match="intervention_id"):
        graph.add_edge(EdgeKind.INTERVENED_ON_BY, "e1", "i1")


def test_reflexive_process_edges_are_distinct_noncausal_labels():
    graph = _graph()
    modifies = graph.add_edge(EdgeKind.MODIFIES, "i1", "v1", properties={"mechanism_id": "m-1"})
    conditions = graph.add_edge(EdgeKind.CONDITIONS, "v1", "e1", properties={"condition_id": "cond-1"})
    confounds = graph.add_edge(EdgeKind.CONFOUNDS, "v1", "e2", properties={"confounder_id": "conf-1"})
    feedback = graph.add_edge(
        EdgeKind.FEEDS_BACK_TO,
        "p1",
        "e1",
        properties={"lag": "one_cycle", "mechanism": "intervention_changes_observation_process"},
    )
    assert {modifies.kind, conditions.kind, confounds.kind, feedback.kind} == {
        EdgeKind.MODIFIES,
        EdgeKind.CONDITIONS,
        EdgeKind.CONFOUNDS,
        EdgeKind.FEEDS_BACK_TO,
    }
    assert all(edge.kind not in {EdgeKind.CAUSALITY_SUPPORTED} for edge in graph.edges.values())


def test_dependency_and_feedback_edges_remain_noncausal_labels():
    graph = _graph()
    dependency = graph.add_edge(
        EdgeKind.DEPENDS_ON,
        "e1",
        "v1",
        properties={"semantic_status": "computational_dependency"},
    )
    feedback = graph.add_edge(
        EdgeKind.FEEDS_BACK_TO,
        "p1",
        "e1",
        properties={"lag": "one_cycle", "mechanism": "intervention_changes_observation_process"},
    )
    assert dependency.kind is EdgeKind.DEPENDS_ON
    assert feedback.kind is EdgeKind.FEEDS_BACK_TO
    assert all(edge.kind is not EdgeKind.CAUSALITY_SUPPORTED for edge in graph.edges.values())


def test_temporal_precedence_requires_ordered_times():
    graph = _graph()
    earlier = datetime(2026, 9, 13, 8, 0, tzinfo=UTC)
    later = datetime(2026, 9, 13, 9, 0, tzinfo=UTC)
    edge = graph.add_edge(
        EdgeKind.TEMPORAL_PRECEDENCE,
        "e1",
        "e2",
        properties={"earlier_time": earlier, "later_time": later},
    )
    assert edge.kind is EdgeKind.TEMPORAL_PRECEDENCE


def test_temporal_precedence_cannot_be_used_as_causality():
    graph = _graph()
    with pytest.raises(ValueError, match="earlier_time"):
        graph.add_edge(EdgeKind.TEMPORAL_PRECEDENCE, "e1", "e2", properties={})


def test_causal_hypothesis_requires_mechanism_alternatives_predictions_and_falsification():
    graph = _graph()
    with pytest.raises(ValueError, match="missing"):
        graph.add_edge(
            EdgeKind.CAUSAL_HYPOTHESIS,
            "h1",
            "c1",
            properties={"hypothesis_id": "H1"},
        )


def test_causal_hypothesis_can_be_recorded_without_being_confirmed():
    graph = _graph()
    edge = graph.add_edge(
        EdgeKind.CAUSAL_HYPOTHESIS,
        "h1",
        "c1",
        properties={
            "hypothesis_id": "H1",
            "mechanism": "proposed mechanism",
            "evidence_ids": ["e1"],
            "alternative_explanations": ["H2", "H3"],
            "predictions": ["prediction-1"],
            "falsification_criterion": "prediction fails prospectively",
        },
    )
    assert edge.kind is EdgeKind.CAUSAL_HYPOTHESIS
    assert edge.properties["hypothesis_id"] == "H1"


def test_causality_supported_requires_validation_method():
    graph = _graph()
    properties = {
        "hypothesis_id": "H1",
        "mechanism": "mechanism",
        "evidence_ids": ["e1", "e2"],
        "alternative_explanations": ["H2"],
        "predictions": ["prediction"],
        "falsification_criterion": "criterion",
    }
    with pytest.raises(ValueError, match="validation_method"):
        graph.add_edge(EdgeKind.CAUSALITY_SUPPORTED, "h1", "c1", properties=properties)


def test_causality_confirmed_is_rejected():
    graph = _graph()
    properties = {
        "hypothesis_id": "H1",
        "mechanism": "mechanism",
        "evidence_ids": ["e1", "e2"],
        "alternative_explanations": ["H2"],
        "predictions": ["prediction"],
        "falsification_criterion": "criterion",
        "validation_method": "prospective observational test",
        "causality_confirmed": True,
    }
    with pytest.raises(ValueError, match="CAUSALITY_CONFIRMED"):
        graph.add_edge(EdgeKind.CAUSALITY_SUPPORTED, "h1", "c1", properties=properties)


def test_source_dependency_requires_explicit_relation():
    graph = _graph()
    with pytest.raises(ValueError, match="dependency relation"):
        graph.add_edge(EdgeKind.SOURCE_DEPENDENCY, "s1", "e1", properties={})


def _hypothesis(code: str) -> Hypothesis:
    return Hypothesis(
        hypothesis_id=f"hyp-{code}",
        code=code,
        statement=f"Explanation {code}",
        predictions=(f"prediction-{code}",),
        favorable_evidence_ids=("e1",),
        contrary_evidence_ids=("e2",),
        confounders=("confounder",),
        falsification_criterion="predefined criterion",
        missing_data=("none identified",),
        verification_cost="medium",
        action_consequence="act if supported",
        inaction_consequence="monitor if unresolved",
    )


def test_rival_hypothesis_set_requires_h1_to_h5():
    rival_set = RivalHypothesisSet("c1")
    for code in ("H1", "H2"):
        rival_set.add(_hypothesis(code))
    with pytest.raises(ValueError, match="H3"):
        rival_set.require_complete_rivals()


def test_complete_rival_hypothesis_set_is_falsifiable():
    rival_set = RivalHypothesisSet.build_required_set(
        "c1", [_hypothesis(code) for code in ("H1", "H2", "H3", "H4", "H5")]
    )
    assert {hypothesis.code for hypothesis in rival_set.require_complete_rivals()} == {
        "H1", "H2", "H3", "H4", "H5"
    }
    assert rival_set.evidence_ids() == {"e1", "e2"}


def test_hypothesis_does_not_change_canonical_epistemic_status():
    hypothesis = _hypothesis("H1")
    assert "epistemic_status" not in hypothesis.to_dict()
