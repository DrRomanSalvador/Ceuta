"""Authoritative-source ingestion boundary for decision evidence.

Network retrieval remains separate from epistemic interpretation. A parser is
required to convert a verified source snapshot into explicit evidence records;
raw network content is never promoted to decision evidence automatically.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Sequence

from .official_sources import OfficialSourceRegistry, SourceSnapshot
from .source_client import OfficialSourceClient, RetrievedSource
from .decision_lifecycle import DecisionEvidence


@dataclass(frozen=True, slots=True)
class SourceIngestionResult:
    source_id: str
    snapshot: SourceSnapshot
    evidence: tuple[DecisionEvidence, ...]
    decision_ready: bool
    reasons: tuple[str, ...]


EvidenceParser = Callable[[RetrievedSource], Sequence[DecisionEvidence]]


class OfficialSourceIngestionEngine:
    """Refresh registered sources and admit only provenance-complete evidence."""

    def __init__(self, registry: OfficialSourceRegistry, client: OfficialSourceClient) -> None:
        if client.registry is not registry:
            raise ValueError("source client and registry must be identical")
        self.registry = registry
        self.client = client

    def refresh(self, source_id: str, parser: EvidenceParser, *, now: datetime | None = None) -> SourceIngestionResult:
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("now must be timezone-aware")
        retrieved = self.client.refresh(source_id, now=timestamp)
        reasons: list[str] = []
        if not retrieved.snapshot.verified or retrieved.status_code >= 400:
            reasons.append("source snapshot is unverified or unsuccessful")
        try:
            parsed = tuple(parser(retrieved))
        except Exception as exc:
            return SourceIngestionResult(source_id, retrieved.snapshot, (), False, (f"evidence parser failed: {type(exc).__name__}",))
        for item in parsed:
            if item.source_id != source_id:
                raise ValueError("parser returned evidence for a different source")
            if item.content_hash != retrieved.snapshot.content_hash:
                raise ValueError("evidence content hash does not match source snapshot")
            if not item.provenance_refs:
                raise ValueError("evidence without provenance cannot be admitted")
        if not parsed:
            reasons.append("source produced no admissible evidence")
        if retrieved.status_code == 304 and not parsed:
            reasons.append("conditional refresh returned no materialized evidence")
        return SourceIngestionResult(source_id, retrieved.snapshot, parsed, not reasons, tuple(reasons))

    def freshness(self, *, now: datetime | None = None):
        timestamp = now or datetime.now(timezone.utc)
        return self.registry.freshness(timestamp)


__all__ = ["EvidenceParser", "OfficialSourceIngestionEngine", "SourceIngestionResult"]
