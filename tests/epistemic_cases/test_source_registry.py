from backend.app.core.evidence.source_registry import (
    ClaimEvidenceLink,
    SourceRecord,
    SourceRegistry,
    SourceRole,
    SourceVerification,
)


def source() -> SourceRecord:
    return SourceRecord(
        source_id="src:1",
        title="Primary source",
        source_class="guideline",
        url="https://example.org/source",
        publisher="Example Institution",
        published_at="2026-01-01",
        accessed_at="2026-09-13",
        verification=SourceVerification.PRIMARY_SOURCE_VERIFIED,
        role=SourceRole.EVIDENCE,
    )


def test_claim_requires_registered_source() -> None:
    registry = SourceRegistry()
    registry.register(source())
    registry.link_claim(ClaimEvidenceLink("claim:1", "src:1", "supports"))
    assert registry.evidence_traceable("claim:1")
    assert registry.sources_for_claim("claim:1") == (source(),)


def test_unverified_source_cannot_be_decision_evidence() -> None:
    try:
        SourceRecord(
            source_id="src:unverified",
            title="Unverified",
            source_class="media",
            url="https://example.org/unverified",
            publisher="Example",
            published_at=None,
            accessed_at="2026-09-13",
            verification=SourceVerification.UNVERIFIED,
            role=SourceRole.EVIDENCE,
        )
    except ValueError:
        return
    raise AssertionError("unverified evidence source must be rejected")


def test_doi_verified_source_requires_doi() -> None:
    try:
        SourceRecord(
            source_id="src:doi",
            title="Methodological paper",
            source_class="methodological",
            url="https://example.org/paper",
            publisher="Example Journal",
            published_at="2026-01-01",
            accessed_at="2026-09-13",
            verification=SourceVerification.DOI_VERIFIED,
            role=SourceRole.EVIDENCE,
        )
    except ValueError:
        return
    raise AssertionError("DOI verification must require a DOI")
