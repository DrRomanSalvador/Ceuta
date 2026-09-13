from datetime import datetime, timedelta, timezone

from backend.app.core.epistemology_p0.contracts.ceutia_serpiente import PullContextRequest
from backend.app.core.epistemology_p0.evidence.models import create_evidence
from backend.app.core.epistemology_p0.operational.context_service import ContextService
from backend.app.core.epistemology_p0.registry import ClaimRegistry


T0 = datetime(2026, 9, 13, 8, 0, tzinfo=timezone.utc)


def test_context_service_excludes_evidence_not_yet_available():
    registry = ClaimRegistry()
    claim = registry.register_claim("event occurred", "source-a", "doc-a")
    evidence = create_evidence(
        source_id="source-a",
        document_id="doc-a",
        claim_id=claim,
        value=1,
        semantic_definition="indicator",
        source_reliability=0.8,
        source_independence="independent",
        event_time=T0 - timedelta(days=30),
        publication_time=T0 + timedelta(days=1),
    )
    registry.add_evidence(evidence)

    request = PullContextRequest(
        variable="indicator",
        interval_start=(T0 - timedelta(days=1)).isoformat(),
        interval_end=T0.isoformat(),
        geography=None,
        anomaly_type="test",
    )

    dossier = ContextService(registry).pull_context(request)

    assert evidence.evidence_id not in dossier.related_evidence_ids


def test_context_service_accepts_evidence_available_at_evaluation_time():
    registry = ClaimRegistry()
    claim = registry.register_claim("event occurred", "source-a", "doc-a")
    evidence = create_evidence(
        source_id="source-a",
        document_id="doc-a",
        claim_id=claim,
        value=1,
        semantic_definition="indicator",
        source_reliability=0.8,
        source_independence="independent",
        event_time=T0 - timedelta(days=30),
        publication_time=T0 - timedelta(hours=1),
    )
    registry.add_evidence(evidence)

    request = PullContextRequest(
        variable="indicator",
        interval_start=(T0 - timedelta(days=1)).isoformat(),
        interval_end=T0.isoformat(),
        geography=None,
        anomaly_type="test",
    )

    dossier = ContextService(registry).pull_context(request)

    assert evidence.evidence_id in dossier.related_evidence_ids
