from app.core.decision.config_provenance import ConfigurationProvenance
from app.core.decision.persistence import SQLiteDecisionStore
from app.core.decision.policy import PolicyProvenance
from app.core.evidence.citation_trace import CitationTrace
from app.core.evidence.source_registry import ClaimEvidenceLink, SourceRecord, SourceRole, SourceVerification


def _source() -> SourceRecord:
    return SourceRecord("src-1", "Verified source", "guideline", "https://example.org/source", "Publisher", None, "2026-09-13T00:00:00+00:00", SourceVerification.PRIMARY_SOURCE_VERIFIED, SourceRole.EVIDENCE)


def test_schema_four_recovers_source_links_and_citations(tmp_path) -> None:
    store = SQLiteDecisionStore(str(tmp_path / "decision.db"))
    store.record_source(_source())
    store.record_claim_evidence_link(ClaimEvidenceLink("claim-1", "src-1", "supports"))
    store.record_citation_trace(CitationTrace("claim-1", "src-1", "p. 4", "abc", "2026-09-13T00:00:00+00:00"))
    registry = store.source_registry()
    assert registry.evidence_traceable("claim-1")
    assert store.citation_registry().traceable("claim-1")


def test_policy_and_configuration_provenance_persist(tmp_path) -> None:
    store = SQLiteDecisionStore(str(tmp_path / "decision.db"))
    from app.core.decision.provenance_persistence import DecisionProvenanceStore
    provenance = DecisionProvenanceStore(store.connection)
    policy = PolicyProvenance("policy-1", "1", "2026-09-13T00:00:00+00:00", None, ("src-1",), "test", {"review": "required"})
    configuration = ConfigurationProvenance("config-1", "1", ("src-1",), {"mode": "robust"})
    provenance.record_policy(policy)
    provenance.record_configuration(configuration)
    assert provenance.policy("policy-1", "1") == policy
    assert provenance.configuration("config-1", "1") == configuration
