from datetime import UTC, datetime, timedelta

import pytest

from app.core.epistemology_p0.advanced.semantic_graph import NodeKind, SemanticGraph
from app.core.p0_contracts import (
    EpistemicStatus,
    EvidenceContract,
    SourceRelation,
    Uncertainty,
)

T0 = datetime(2026, 9, 13, 8, 0, tzinfo=UTC)


def _evidence(**overrides: object) -> EvidenceContract:
    data: dict[str, object] = {
        "evidence_id": "E-layer2",
        "claim": "controlled observation",
        "source_id": "S-layer2",
        "observed_at": T0,
        "ingestion_time": T0 + timedelta(minutes=1),
        "uncertainty": Uncertainty(kind="unknown", description="not quantified"),
        "epistemic_status": EpistemicStatus.UNKNOWN,
        "source_relation": SourceRelation.UNKNOWN,
    }
    data.update(overrides)
    return EvidenceContract.model_validate(data)


def test_graph_admits_only_temporally_eligible_canonical_evidence():
    graph = SemanticGraph()
    node = graph.add_evidence_contract(_evidence(), evaluation_time=T0 + timedelta(minutes=1))
    assert node.kind is NodeKind.EVIDENCE
    assert node.properties["epistemic_status"] == EpistemicStatus.UNKNOWN.value
    assert node.properties["available_at"] == T0.isoformat()


def test_graph_rejects_future_evidence_before_node_creation():
    graph = SemanticGraph()
    with pytest.raises(ValueError, match="not eligible"):
        graph.add_evidence_contract(
            _evidence(
                evidence_id="E-future",
                publication_time=T0 + timedelta(hours=1),
                ingestion_time=T0 + timedelta(hours=1, minutes=1),
            ),
            evaluation_time=T0,
        )
    assert "E-future" not in graph.nodes


def test_graph_preserves_contradicted_status():
    graph = SemanticGraph()
    node = graph.add_evidence_contract(
        _evidence(epistemic_status=EpistemicStatus.CONTRADICTED),
        evaluation_time=T0 + timedelta(minutes=1),
    )
    assert node.properties["epistemic_status"] == EpistemicStatus.CONTRADICTED.value


def test_graph_does_not_upgrade_unknown_to_fact():
    graph = SemanticGraph()
    node = graph.add_evidence_contract(
        _evidence(epistemic_status=EpistemicStatus.UNKNOWN),
        evaluation_time=T0 + timedelta(minutes=1),
    )
    assert node.properties["epistemic_status"] == EpistemicStatus.UNKNOWN.value
