from app.core.evidence.citation_trace import CitationTrace, CitationTraceRegistry
from app.core.evidence.provenance_gate import EvidenceProvenanceGate, ProvenanceDisposition
from app.core.evidence.source_registry import ClaimEvidenceLink, SourceRecord, SourceRegistry, SourceRole, SourceVerification


def _source(source_id: str = "src-1") -> SourceRecord:
    return SourceRecord(source_id, "Verified source", "guideline", "https://example.org/source", "Publisher", None, "2026-09-13T00:00:00+00:00", SourceVerification.PRIMARY_SOURCE_VERIFIED, SourceRole.EVIDENCE)


def test_provenance_requires_registered_source() -> None:
    gate = EvidenceProvenanceGate(SourceRegistry())
    result = gate.evaluate(("missing",))
    assert result.disposition is ProvenanceDisposition.ABSTAIN


def test_high_impact_claim_requires_exact_citation_when_registry_is_supplied() -> None:
    registry = SourceRegistry()
    registry.register(_source())
    registry.link_claim(ClaimEvidenceLink("claim-1", "src-1", "supports"))
    citations = CitationTraceRegistry()
    gate = EvidenceProvenanceGate(registry, citations)
    assert gate.evaluate(("src-1",), claim_ids=("claim-1",), high_impact=True).disposition is ProvenanceDisposition.HUMAN_REVIEW
    citations.add(CitationTrace("claim-1", "src-1", "p. 4", "abc", "2026-09-13T00:00:00+00:00"))
    assert gate.evaluate(("src-1",), claim_ids=("claim-1",), high_impact=True).disposition is ProvenanceDisposition.ALLOW
