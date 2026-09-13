"""Strict contracts for heterogeneous real-world source adapters.

Real ingestion is deliberately separated from normalization. Adapters preserve
source truth, provenance and both temporal boundaries; they never mutate model
state and never infer event time from retrieval time.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from typing import Protocol
from urllib.parse import urlsplit, urlunsplit

from ..contracts import ObservationRecord


@dataclass(frozen=True, slots=True)
class RealSourceEnvelope:
    """Immutable raw source snapshot with explicit temporal/provenance metadata."""

    source_id: str
    source_kind: str
    canonical_uri: str
    fetched_at: datetime
    payload: bytes
    content_hash: str
    event_time: datetime | None = None
    publisher_id: str | None = None
    upstream_source_id: str | None = None

    def __post_init__(self) -> None:
        if not self.source_id or not self.source_kind or not self.canonical_uri:
            raise ValueError("source identity fields are required")
        parts = urlsplit(self.canonical_uri)
        if parts.scheme not in {"http", "https"} or not parts.netloc:
            raise ValueError("canonical_uri must be an absolute HTTP(S) URI")
        for name in ("fetched_at", "event_time"):
            value = getattr(self, name)
            if value is not None and (value.tzinfo is None or value.utcoffset() is None):
                raise ValueError(f"{name} must be timezone-aware")
        if not self.payload:
            raise ValueError("payload must not be empty")
        if self.content_hash != sha256(self.payload).hexdigest():
            raise ValueError("content_hash does not match payload")
        if self.upstream_source_id == self.source_id:
            raise ValueError("upstream_source_id cannot equal source_id")

    @property
    def canonical_host(self) -> str:
        return urlsplit(self.canonical_uri).netloc.lower()


@dataclass(frozen=True, slots=True)
class SourceObservation:
    """Adapter-level observation before source-independent normalization."""

    variable: str
    value: float
    event_time: datetime
    available_at: datetime
    domain: str
    source_id: str
    evidence_id: str
    provenance_hash: str
    content_fingerprint: str | None = None
    quality: float = 1.0
    unit: str | None = None

    def __post_init__(self) -> None:
        if self.event_time.tzinfo is None or self.event_time.utcoffset() is None:
            raise ValueError("event_time must be timezone-aware")
        if self.available_at.tzinfo is None or self.available_at.utcoffset() is None:
            raise ValueError("available_at must be timezone-aware")
        if self.available_at < self.event_time:
            raise ValueError("available_at cannot precede event_time")
        if self.content_fingerprint is not None and not self.content_fingerprint:
            raise ValueError("content_fingerprint must not be empty when provided")

    def to_record(self) -> ObservationRecord:
        return ObservationRecord(
            observation_id=self.provenance_hash,
            variable=self.variable,
            value=self.value,
            unit=self.unit,
            event_time=self.event_time,
            available_at=self.available_at,
            source_ids=(self.source_id,),
            evidence_ids=(self.evidence_id,),
            domain=self.domain,
            quality=self.quality,
            provenance_hash=self.provenance_hash,
        )


class RealSourceAdapter(Protocol):
    """Transport-independent contract for APIs, feeds and sensors."""

    source_id: str

    async def fetch(self, *, now: datetime) -> RealSourceEnvelope:
        """Fetch one immutable source snapshot; never mutate pipeline state."""

    def parse(self, envelope: RealSourceEnvelope) -> Iterable[SourceObservation]:
        """Parse source data without inventing missing event timestamps."""


def canonicalize_uri(uri: str) -> str:
    """Canonicalize a URI enough for deterministic source identity."""
    parts = urlsplit(uri.strip())
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        raise ValueError("uri must be an absolute HTTP(S) URI")
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), parts.path or "/", parts.query, ""))
