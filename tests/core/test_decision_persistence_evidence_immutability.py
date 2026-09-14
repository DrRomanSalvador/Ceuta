from dataclasses import replace

from app.core.decision.persistence import SQLiteDecisionStore
from app.core.evidence.citation_trace import CitationTrace
from app.core.evidence.conflict_resolution import EvidenceResolution, ResolutionDisposition
from app.core.evidence.source_registry import (
    ClaimEvidenceLink,
    SourceRecord,
    SourceRole,
    SourceVerification,
)


def source() -> SourceRecord:
    return SourceRecord(
        source_id="s1",
        title="Primary source",
        source_class="official",
        url="https://example.org/source",
        publisher="Example",
        published_at="2026-09-15T00:00:00+00:00",
        accessed_at="2026-09-15T01:00:00+00:00",
        verification=SourceVerification.PRIMARY_SOURCE_VERIFIED,
        role=SourceRole.EVIDENCE,
    )


def test_conflict_resolution_duplicate_is_idempotent_and_conflict_fails(tmp_path):
    store = SQLiteDecisionStore(str(tmp_path / "decision.sqlite"))
    first = EvidenceResolution("c1", ResolutionDisposition.ABSTAIN, (), "uncertain", "p1")
    store.record_conflict_resolution("d1", first)
    store.record_conflict_resolution("d1", first)
    conflicting = EvidenceResolution("c1", ResolutionDisposition.HUMAN_REVIEW, (), "changed", "p1")
    try:
        store.record_conflict_resolution("d1", conflicting)
    except RuntimeError as exc:
        assert "identity collision" in str(exc)
    else:
        raise AssertionError("conflicting resolution overwrote persisted history")
    assert store.conflict_resolutions("d1") == (first,)
    store.close()


def test_source_link_trace_and_cycle_are_immutable_by_identity(tmp_path):
    store = SQLiteDecisionStore(str(tmp_path / "decision.sqlite"))
    s = source()
    store.record_source(s)
    store.record_source(s)
    try:
        store.record_source(replace(s, title="Changed"))
    except RuntimeError as exc:
        assert "identity collision" in str(exc)
    else:
        raise AssertionError("conflicting source metadata overwrote persisted history")

    link = ClaimEvidenceLink("c1", "s1", "supports", "excerpt-1", True)
    store.record_claim_evidence_link(link)
    store.record_claim_evidence_link(link)
    try:
        store.record_claim_evidence_link(ClaimEvidenceLink("c1", "s1", "supports", "excerpt-2", True))
    except RuntimeError as exc:
        assert "identity collision" in str(exc)
    else:
        raise AssertionError("conflicting claim link overwrote persisted history")

    trace = CitationTrace("c1", "s1", "page:1", "hash-1", "2026-09-15T01:00:00+00:00")
    store.record_citation_trace(trace)
    store.record_citation_trace(trace)
    try:
        store.record_citation_trace(CitationTrace("c1", "s1", "page:1", "hash-1", "2026-09-15T02:00:00+00:00"))
    except RuntimeError as exc:
        assert "identity collision" in str(exc)
    else:
        raise AssertionError("conflicting citation trace overwrote provenance")

    stages = ({"stage": "decision", "value": 1},)
    store.record_cycle(system_id="sys", as_of="2026-09-15T00:00:00+00:00", decision_id="d1", option_id="o1", disposition="recommend", lineage=("n1",), stages=stages)
    store.record_cycle(system_id="sys", as_of="2026-09-15T00:00:00+00:00", decision_id="d1", option_id="o1", disposition="recommend", lineage=("n1",), stages=stages)
    try:
        store.record_cycle(system_id="sys", as_of="2026-09-15T00:00:00+00:00", decision_id="d2", option_id="o1", disposition="recommend", lineage=("n1",), stages=stages)
    except RuntimeError as exc:
        assert "identity collision" in str(exc)
    else:
        raise AssertionError("conflicting cycle snapshot overwrote history")
    store.close()
