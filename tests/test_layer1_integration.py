from datetime import UTC, datetime, timedelta

import pytest

from backend.app.core.epistemology_p0.advanced.ingestion import BulkIngestionPipeline, IngestionRecord
from backend.app.core.epistemology_p0.epistemology.states import EpistemicStatus
from backend.app.core.epistemology_p0.evidence.models import create_evidence
from backend.app.core.epistemology_p0.registry import ClaimRegistry

T0 = datetime(2026, 9, 13, 8, 0, tzinfo=UTC)


def test_ingestion_admits_through_contract_and_preserves_unknown_uncertainty():
    registry = ClaimRegistry()
    result = BulkIngestionPipeline(registry).ingest_records([IngestionRecord(source_id="source-a", document_id="doc-a", statement="indicator=7", value=7, semantic_definition="indicator units", publication_time=T0.isoformat())])
    assert result.accepted == 1
    evidence = registry.evidences[result.evidence_ids[0]]
    assert evidence.uncertainty is not None
    assert evidence.uncertainty.type.value == "unknown"
    assert evidence.available_at == T0
    assert evidence.epistemic_status == EpistemicStatus.ATTRIBUTED_CLAIM


def test_ingestion_rejects_malformed_temporal_input_closed():
    registry = ClaimRegistry()
    result = BulkIngestionPipeline(registry).ingest_records([IngestionRecord(source_id="source-a", document_id="doc-a", statement="indicator=7", value=7, semantic_definition="indicator units", publication_time="not-a-timestamp")])
    assert result.accepted == 0
    assert result.rejected == 1
    assert "invalid temporal value" in result.errors[0]["error"]


def test_legacy_backtest_uses_available_at_not_event_time():
    registry = ClaimRegistry()
    claim = registry.register_claim("event occurred", "source-a", "doc-a")
    evidence = create_evidence(source_id="source-a", document_id="doc-a", claim_id=claim, value=1, semantic_definition="indicator", source_reliability=0.8, source_independence="independent", event_time=T0 - timedelta(days=30), publication_time=T0 + timedelta(days=1))
    registry.add_evidence(evidence)
    assert registry.get_evidences_for_backtest(T0) == []


def test_two_independent_source_groups_upgrade_to_corrob_fact():
    registry = ClaimRegistry()
    claim = registry.register_claim("x=1", "source-a", "doc-a")
    target = create_evidence(source_id="source-a", document_id="doc-a", claim_id=claim, value=1, semantic_definition="x", source_reliability=0.9, source_independence="independent")
    corroborator = create_evidence(source_id="source-b", document_id="doc-b", claim_id=claim, value=1, semantic_definition="x", source_reliability=0.9, source_independence="independent")
    registry.add_evidence(target)
    registry.add_evidence(corroborator)
    registry.corroborate(target.evidence_id, corroborator.evidence_id, independence_score=0.95, relationship_type="INDEPENDENT")
    assert registry.evidences[target.evidence_id].epistemic_status == EpistemicStatus.CORROBORATED_FACT


def test_dependent_corroboration_cannot_upgrade():
    registry = ClaimRegistry()
    claim = registry.register_claim("x=1", "source-a", "doc-a")
    target = create_evidence(source_id="source-a", document_id="doc-a", claim_id=claim, value=1, semantic_definition="x", source_reliability=0.9, source_independence="independent")
    dependent = create_evidence(source_id="source-b", document_id="doc-b", claim_id=claim, value=1, semantic_definition="x", source_reliability=0.9, source_independence="dependent")
    registry.add_evidence(target)
    registry.add_evidence(dependent)
    registry.corroborate(target.evidence_id, dependent.evidence_id, independence_score=0.95, relationship_type="DEPENDENT")
    assert registry.evidences[target.evidence_id].epistemic_status == EpistemicStatus.ATTRIBUTED_CLAIM


def test_revision_version_cannot_reenter_historical_backtest_at_original_publication():
    registry = ClaimRegistry()
    claim = registry.register_claim("x=1", "source-a", "doc-a")
    original = create_evidence(source_id="source-a", document_id="doc-a", claim_id=claim, value=1, semantic_definition="x", source_reliability=0.9, source_independence="independent", publication_time=T0)
    registry.add_evidence(original)
    revised = original.create_new_version("corrected value", value=2)
    registry.add_evidence_version(revised)
    assert revised.available_at > T0
    historical = registry.get_evidences_for_backtest(T0)
    assert historical == [original]
    assert revised not in historical


def test_direct_registry_admission_cannot_create_corrob_fact_from_one_source():
    registry = ClaimRegistry()
    claim = registry.register_claim("x=1", "source-a", "doc-a")
    invalid = create_evidence(source_id="source-a", document_id="doc-a", claim_id=claim, value=1, semantic_definition="x", source_reliability=0.9, source_independence="independent", epistemic_status=EpistemicStatus.CORROBORATED_FACT)
    with pytest.raises(ValueError, match="at least two independent sources"):
        registry.add_evidence(invalid)
