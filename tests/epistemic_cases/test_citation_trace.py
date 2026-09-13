from backend.app.core.evidence.citation_trace import CitationTrace, CitationTraceRegistry


def test_exact_citation_trace_is_persistable_as_claim_metadata() -> None:
    registry = CitationTraceRegistry()
    registry.add(CitationTrace("claim:1", "src:1", "section-3/table-2", "sha256:abc", "2026-09-13T12:00:00+00:00"))
    assert registry.traceable("claim:1")
    assert registry.traces("claim:1")[0].locator == "section-3/table-2"
