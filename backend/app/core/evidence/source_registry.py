"""Structured source registry and claim-to-evidence traceability for CeutIA."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from urllib.parse import urlparse


class SourceVerification(StrEnum):
    UNVERIFIED = "unverified"
    PRIMARY_SOURCE_VERIFIED = "primary_source_verified"
    DOI_VERIFIED = "doi_verified"
    INSTITUTIONALLY_VERIFIED = "institutionally_verified"


class SourceRole(StrEnum):
    EVIDENCE = "evidence"
    CONTEXT = "context"
    SIGNAL = "signal"
    GOVERNANCE = "governance"


@dataclass(frozen=True, slots=True)
class SourceRecord:
    source_id: str
    title: str
    source_class: str
    url: str
    publisher: str
    published_at: str | None
    accessed_at: str
    verification: SourceVerification
    role: SourceRole
    design: str | None = None
    population: str | None = None
    context: str | None = None
    assumptions: tuple[str, ...] = ()
    risk_of_bias: str | None = None
    applicability: str | None = None
    limitations: tuple[str, ...] = ()
    conflicts_of_interest: str | None = None
    independence: str | None = None
    validation_level: str | None = None
    doi: str | None = None

    def __post_init__(self) -> None:
        if not self.source_id.strip() or not self.title.strip():
            raise ValueError("source identity and title are required")
        parsed = urlparse(self.url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("source url must be an absolute http(s) URL")
        if self.verification is SourceVerification.DOI_VERIFIED and not self.doi:
            raise ValueError("DOI verification requires a DOI")
        if self.role is SourceRole.EVIDENCE and self.verification is SourceVerification.UNVERIFIED:
            raise ValueError("unverified sources cannot be registered as evidence")


@dataclass(frozen=True, slots=True)
class ClaimEvidenceLink:
    claim_id: str
    source_id: str
    relation: str
    excerpt_ref: str | None = None
    supports_claim: bool = True

    def __post_init__(self) -> None:
        if not self.claim_id.strip() or not self.source_id.strip() or not self.relation.strip():
            raise ValueError("claim-to-evidence link requires claim, source and relation")


class SourceRegistry:
    """Deterministic in-memory registry; persistence is supplied by the decision store layer."""

    def __init__(self) -> None:
        self._sources: dict[str, SourceRecord] = {}
        self._links: list[ClaimEvidenceLink] = []

    def register(self, source: SourceRecord) -> None:
        existing = self._sources.get(source.source_id)
        if existing is not None and existing != source:
            raise ValueError(f"source_id already registered with different metadata: {source.source_id}")
        self._sources[source.source_id] = source

    def link_claim(self, link: ClaimEvidenceLink) -> None:
        if link.source_id not in self._sources:
            raise KeyError(f"unknown source_id: {link.source_id}")
        if link not in self._links:
            self._links.append(link)

    def source(self, source_id: str) -> SourceRecord | None:
        return self._sources.get(source_id)

    def sources_for_claim(self, claim_id: str) -> tuple[SourceRecord, ...]:
        ids = {link.source_id for link in self._links if link.claim_id == claim_id}
        return tuple(self._sources[source_id] for source_id in sorted(ids))

    def links_for_claim(self, claim_id: str) -> tuple[ClaimEvidenceLink, ...]:
        return tuple(link for link in self._links if link.claim_id == claim_id)

    def evidence_traceable(self, claim_id: str) -> bool:
        return bool(self.sources_for_claim(claim_id))


__all__ = ["ClaimEvidenceLink", "SourceRecord", "SourceRegistry", "SourceRole", "SourceVerification"]
