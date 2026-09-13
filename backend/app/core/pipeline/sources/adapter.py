"""Fail-closed source adapter contracts and provenance-aware ingestion."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from typing import Iterable, Protocol

from ..contracts import ObservationRecord


@dataclass(frozen=True, slots=True)
class SourceEnvelope:
    """Raw source payload with immutable provenance metadata."""

    source_id: str
    canonical_uri: str
    fetched_at: datetime
    payload: bytes
    content_hash: str
    mirror_of: str | None = None

    def __post_init__(self) -> None:
        if not self.source_id or not self.canonical_uri:
            raise ValueError("source_id and canonical_uri are required")
        if self.fetched_at.tzinfo is None or self.fetched_at.utcoffset() is None:
            raise ValueError("fetched_at must be timezone-aware")
        if not self.payload:
            raise ValueError("payload must not be empty")
        expected = sha256(self.payload).hexdigest()
        if self.content_hash != expected:
            raise ValueError("content_hash does not match payload")
        if self.mirror_of == self.source_id:
            raise ValueError("mirror_of cannot equal source_id")


class SourceAdapter(Protocol):
    """Minimal asynchronous source contract used by the runtime daemon."""

    source_id: str

    async def fetch(self, *, now: datetime) -> SourceEnvelope:
        """Fetch one source snapshot without mutating pipeline state."""

    def parse(self, envelope: SourceEnvelope) -> Iterable[ObservationRecord]:
        """Convert a verified source snapshot into canonical observations."""


class ProvenanceRegistry:
    """Deduplicate exact payloads and mirror sources without losing provenance."""

    def __init__(self) -> None:
        self._content_to_source: dict[str, str] = {}
        self._observation_hashes: set[str] = set()

    def register_envelope(self, envelope: SourceEnvelope) -> str | None:
        previous = self._content_to_source.get(envelope.content_hash)
        self._content_to_source.setdefault(envelope.content_hash, envelope.source_id)
        return previous if previous != envelope.source_id else None

    def accept(self, observations: Iterable[ObservationRecord]) -> tuple[ObservationRecord, ...]:
        accepted: list[ObservationRecord] = []
        for observation in observations:
            if observation.provenance_hash in self._observation_hashes:
                continue
            self._observation_hashes.add(observation.provenance_hash)
            accepted.append(observation)
        return tuple(accepted)
