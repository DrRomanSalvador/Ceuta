"""
Tests P0 - fundamentos epistemológicos CeutIA.

Ubicación: tests/core/ (mismo patrón que el resto del proyecto).
Casos mínimos exigidos por la auditoría.
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from backend.app.core.epistemology_p0.epistemology.states import (
    EpistemicStatus,
    EpistemicStateMachine,
)
from backend.app.core.epistemology_p0.evidence.models import create_evidence, Location, Uncertainty, UncertaintyType
from backend.app.core.epistemology_p0.temporal.multitemporal import TemporalFilter, TemporalContext
from backend.app.core.epistemology_p0.sources.independence import (
    SourceIndependenceGraph,
    SourceNode,
    SourceRole,
    DependenceEdge,
    DependenceType,
)
from backend.app.core.epistemology_p0.contracts.ceutia_serpiente import (
    Observation,
    SourceRef,
    TimeBlock,
    PullContextRequest,
    ContextDossier,
    ContextExplanation,
)
from backend.app.core.epistemology_p0.registry import ClaimRegistry


def test_initial_claim_is_attributed():
    sm = EpistemicStateMachine()
    assert sm.current_status == EpistemicStatus.ATTRIBUTED_CLAIM


def test_cannot_jump_to_corroborated_without_evidence():
    sm = EpistemicStateMachine()
    with pytest.raises(ValueError, match="evidence_ids"):
        sm.transition(
            EpistemicStatus.CORROBORATED_FACT,
            justification="parece cierto",
            evidence_ids=[],
        )


def test_valid_transition_to_corroborated():
    sm = EpistemicStateMachine()
    t = sm.transition(
        EpistemicStatus.CORROBORATED_FACT,
        justification="Corroborado por fuente independiente src-002",
        evidence_ids=["ev-abc"],
        actor="analyst",
    )
    assert sm.current_status == EpistemicStatus.CORROBORATED_FACT
    assert t.from_status == EpistemicStatus.ATTRIBUTED_CLAIM


def test_single_source_claim_starts_as_attributed():
    ev = create_evidence(
        source_id="src-001",
        document_id="doc-001",
        claim_id="claim-001",
        value=12,
        unit="percent",
        semantic_definition="Tasa según definición oficial",
        source_reliability=0.6,
        source_independence="unknown",
    )
    assert ev.epistemic_status == EpistemicStatus.ATTRIBUTED_CLAIM
    assert ev.version == 1


def test_evidence_immutable_new_version():
    ev = create_evidence(
        source_id="src-001",
        document_id="doc-001",
        claim_id="claim-001",
        value=12,
        semantic_definition="Definición exacta",
        source_reliability=0.7,
        source_independence="primary",
    )
    new_ev = ev.create_new_version(
        justification="Corrección de valor tras revisión metodológica",
        value=11.5,
        actor="human_reviewer",
    )
    assert ev.value == 12
    assert new_ev.value == 11.5
    assert new_ev.version == 2


def test_ten_documents_same_communique():
    g = SourceIndependenceGraph()
    sources = [f"src-{i:02d}" for i in range(10)]
    for s in sources:
        g.add_source(SourceNode(s, s, SourceRole.SECONDARY))
    primary = sources[0]
    for s in sources[1:]:
        g.add_dependence(
            DependenceEdge(primary, s, DependenceType.SHARED_COMMUNIQUE, strength=0.95)
        )
    weight = g.effective_corroboration_weight(sources)
    assert weight < 3.0, f"Peso demasiado alto para fuentes dependientes: {weight}"
    clusters = g.detect_shared_communique_cluster(sources)
    assert len(clusters) >= 1
    assert len(clusters[0]) == 10


def test_two_contradictory_claims():
    reg = ClaimRegistry()
    c1 = reg.register_claim("El valor es 12%", "src-A", "doc-A")
    c2 = reg.register_claim("El valor es 8%", "src-B", "doc-B")
    ev1 = create_evidence(
        source_id="src-A", document_id="doc-A", claim_id=c1,
        value=12, unit="percent", semantic_definition="Tasa X",
        source_reliability=0.7, source_independence="primary",
    )
    ev2 = create_evidence(
        source_id="src-B", document_id="doc-B", claim_id=c2,
        value=8, unit="percent", semantic_definition="Tasa X",
        source_reliability=0.65, source_independence="primary",
    )
    reg.add_evidence(ev1)
    reg.add_evidence(ev2)
    link = reg.register_contradiction(
        ev1.evidence_id, ev2.evidence_id, c1,
        divergence_reason="Valores incompatibles para la misma variable",
    )
    assert link.resolution_status == "open"
    assert reg.evidences[ev1.evidence_id].epistemic_status == EpistemicStatus.CONTRADICTED


def test_backtest_rejects_future_ingestion():
    t0 = datetime(2024, 1, 1, tzinfo=timezone.utc)
    t1 = datetime(2024, 6, 1, tzinfo=timezone.utc)
    t_sim = datetime(2024, 3, 1, tzinfo=timezone.utc)

    ev_old = create_evidence(
        source_id="src-1", document_id="d1", claim_id="c1",
        value=10, semantic_definition="var",
        source_reliability=0.8, source_independence="primary",
    )
    object.__setattr__(ev_old, "ingestion_time", t0)

    ev_future = create_evidence(
        source_id="src-2", document_id="d2", claim_id="c2",
        value=20, semantic_definition="var",
        source_reliability=0.8, source_independence="primary",
    )
    object.__setattr__(ev_future, "ingestion_time", t1)

    filtered = TemporalFilter.filter_by_ingestion_time([ev_old, ev_future], t_sim)
    assert len(filtered) == 1
    assert filtered[0].value == 10

    with pytest.raises(ValueError, match="Contaminación retrospectiva"):
        TemporalFilter.assert_no_future_leak([ev_old, ev_future], t_sim)


def test_observation_no_naked_scalar():
    obs = Observation(
        variable="unemployment_rate",
        value=12,
        unit="percent",
        semantic_definition="Tasa de desempleo según metodología OIT",
        time=TimeBlock(ingestion_time=datetime.now(timezone.utc).isoformat()),
        geography="ES",
        source=SourceRef(source_id="src-001", document_id="doc-001", claim_id="claim-001"),
        provenance=[],
        confidence=0.72,
        uncertainty=None,
        source_dependence_ratio=0.0,
        corroboration=[],
        contradictions=[],
        methodology="Encuesta",
        epistemic_status="ATTRIBUTED_CLAIM",
    )
    d = obs.to_dict()
    assert set(d.keys()) >= {
        "variable", "value", "semantic_definition", "time",
        "source", "confidence", "epistemic_status", "schema_version",
    }
    assert d["epistemic_status"] == "ATTRIBUTED_CLAIM"


def test_pull_context_dossier():
    req = PullContextRequest(
        variable="unemployment_rate",
        interval_start="2024-01-01T00:00:00Z",
        interval_end="2024-03-31T23:59:59Z",
        geography="ES",
        anomaly_type="sudden_drop",
        competing_hypotheses=[
            "Cambio de definición",
            "Cambio real del fenómeno",
        ],
    )
    dossier = ContextDossier(
        request_id=req.request_id,
        variable=req.variable,
        explanations=[
            ContextExplanation(
                explanation_type="definition_change",
                description="La definición cambió en enero 2024",
                confidence=0.85,
            ),
        ],
        rival_hypotheses=req.competing_hypotheses,
        related_evidence_ids=["ev-099"],
    )
    d = dossier.to_dict()
    assert len(d["explanations"]) == 1
    assert d["explanations"][0]["explanation_type"] == "definition_change"


def test_full_chain_source_to_status():
    reg = ClaimRegistry()
    claim_id = reg.register_claim(
        statement="La tasa de X es 12%",
        source_id="src-primary",
        document_id="doc-001",
    )
    ev = create_evidence(
        source_id="src-primary",
        document_id="doc-001",
        claim_id=claim_id,
        value=12,
        unit="percent",
        semantic_definition="Tasa de X según metodología Y",
        source_reliability=0.7,
        source_independence="primary",
    )
    reg.add_evidence(ev)
    lineage = reg.get_claim_lineage(claim_id)
    assert lineage["claim"]["epistemic_status"] == "ATTRIBUTED_CLAIM"
    assert len(lineage["evidences"]) == 1
