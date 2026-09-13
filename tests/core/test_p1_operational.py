"""
P1 — Tests de integración operativa (extremo a extremo mínimo).

Circuito: claim → evidence → observation contractual → peso modelo
         → pull_context → dossier con hipótesis rivales
         → versionado de artefactos
"""

from __future__ import annotations

from datetime import datetime, timezone

from backend.app.core.epistemology_p0.evidence.models import (
    create_evidence,
    Uncertainty,
    UncertaintyType,
)
from backend.app.core.epistemology_p0.epistemology.states import EpistemicStatus
from backend.app.core.epistemology_p0.registry import ClaimRegistry
from backend.app.core.epistemology_p0.operational.bridge import ObservationBridge
from backend.app.core.epistemology_p0.operational.uncertainty import (
    propagate_interval,
    combine_uncertainties,
    weight_by_confidence,
)
from backend.app.core.epistemology_p0.operational.versioning import (
    VersionRegistry,
    ArtifactKind,
)
from backend.app.core.epistemology_p0.operational.context_service import ContextService
from backend.app.core.epistemology_p0.contracts.ceutia_serpiente import PullContextRequest


def test_e2e_claim_to_observation_payload():
    reg = ClaimRegistry()
    cid = reg.register_claim("Tasa X es 12%", "src-1", "doc-1")
    ev = create_evidence(
        source_id="src-1",
        document_id="doc-1",
        claim_id=cid,
        value=12,
        unit="percent",
        semantic_definition="Tasa X según metodología oficial",
        source_reliability=0.8,
        source_independence="primary",
        uncertainty=Uncertainty(type=UncertaintyType.INTERVAL, lower=10, upper=14),
    )
    reg.add_evidence(ev)

    bridge = ObservationBridge()
    obs = bridge.emit(ev, variable="rate_x", geography="CE")
    payload = bridge.as_payload(obs)

    assert payload["variable"] == "rate_x"
    assert payload["value"] == 12
    assert payload["semantic_definition"]
    assert payload["source"]["source_id"] == "src-1"
    assert payload["epistemic_status"] == "ATTRIBUTED_CLAIM"
    assert payload["uncertainty"]["lower"] == 10
    assert "model_weight" in payload
    assert 0.0 < payload["model_weight"] <= 1.0
    # Nunca escalar desnudo
    assert "observation_id" in payload
    assert "schema_version" in payload


def test_uncertainty_propagation_and_combine():
    a = propagate_interval(100.0, relative_error=0.05, absolute_error=1.0, confidence=0.9)
    b = propagate_interval(100.0, relative_error=0.02, absolute_error=0.5, confidence=0.8)
    assert a.lower < 100 < a.upper
    env = combine_uncertainties([a, b], method="envelope")
    assert env is not None
    assert env.lower <= a.lower
    assert env.upper >= a.upper


def test_weight_penalizes_dependence():
    high = weight_by_confidence(0.9, 0.0)
    low = weight_by_confidence(0.9, 0.9)
    assert high > low


def test_version_registry_append_only():
    vr = VersionRegistry()
    r1 = vr.register(
        kind=ArtifactKind.SCHEMA,
        name="observation",
        version="1.0",
        actor="system",
        justification="Contrato inicial auditoría",
    )
    r2 = vr.register(
        kind=ArtifactKind.SCHEMA,
        name="observation",
        version="1.1",
        actor="system",
        justification="Añadir model_weight",
        parent_version="1.0",
    )
    assert vr.latest(ArtifactKind.SCHEMA, "observation").version == "1.1"
    hist = vr.history(kind=ArtifactKind.SCHEMA, name="observation")
    assert len(hist) == 2
    assert hist[0].record_id == r1.record_id


def test_pull_context_returns_dossier_with_rivals():
    reg = ClaimRegistry()
    cid = reg.register_claim("Anomalía en tasa", "src-a", "doc-a")
    ev = create_evidence(
        source_id="src-a",
        document_id="doc-a",
        claim_id=cid,
        value=5,
        semantic_definition="Indicador Y",
        source_reliability=0.5,
        source_independence="secondary",
        unavailable_fields={"event_time": "Fuente no reporta fecha de evento"},
    )
    reg.add_evidence(ev)
    # simular revisión
    v2 = ev.create_new_version(justification="Corrección menor", value=5.1)
    reg.add_evidence_version(v2)

    svc = ContextService(reg)
    req = PullContextRequest(
        variable="indicator_y",
        interval_start="2024-01-01T00:00:00Z",
        interval_end="2024-06-01T00:00:00Z",
        geography="CE",
        anomaly_type="sudden_drop",
        competing_hypotheses=["Cambio real del fenómeno"],
    )
    dossier = svc.pull_context(req)
    d = dossier.to_dict()
    assert d["variable"] == "indicator_y"
    assert len(d["explanations"]) >= 1
    assert len(d["rival_hypotheses"]) >= 1
    assert any(
        e["explanation_type"] in ("ingestion_artifact", "retrospective_revision", "other")
        for e in d["explanations"]
    )


def test_closed_loop_registry_bridge_context():
    """Circuito cerrado mínimo auditable."""
    reg = ClaimRegistry()
    cid = reg.register_claim("Carga hospitalaria 72%", "src-h", "doc-h")
    ev = create_evidence(
        source_id="src-h",
        document_id="doc-h",
        claim_id=cid,
        value=72,
        unit="percent",
        semantic_definition="Ocupación de camas hospitalarias",
        source_reliability=0.85,
        source_independence="primary",
        uncertainty=Uncertainty(type=UncertaintyType.INTERVAL, lower=70, upper=74),
    )
    reg.add_evidence(ev)

    bridge = ObservationBridge()
    obs = bridge.emit(ev, variable="hospital_occupancy", geography="CE")
    payload = bridge.as_payload(obs)

    svc = ContextService(reg)
    dossier = svc.pull_context(
        PullContextRequest(
            variable="hospital_occupancy",
            interval_start="2024-01-01T00:00:00Z",
            interval_end="2024-12-31T00:00:00Z",
            geography="CE",
            anomaly_type="threshold_approach",
            competing_hypotheses=[],
        )
    )

    vr = VersionRegistry()
    vr.register(
        kind=ArtifactKind.PIPELINE,
        name="closed_loop_demo",
        version="0.1.0",
        actor="p1-test",
        justification="Demo circuito claim→obs→context",
        metadata={
            "observation_id": payload["observation_id"],
            "dossier_request_id": dossier.request_id,
        },
    )

    assert payload["epistemic_status"] == EpistemicStatus.ATTRIBUTED_CLAIM.value
    assert dossier.request_id.startswith("ctx-")
    assert vr.latest(ArtifactKind.PIPELINE, "closed_loop_demo") is not None
