"""Evidence deduplication and source-mirror detection.

Exact payload hashes are definitive duplicates. Parser-supplied semantic
fingerprints identify the underlying event independently of publisher identity,
so propagation through multiple outlets does not inflate independent evidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Iterable

from .real_base import RealSourceEnvelope, SourceObservation


@dataclass(frozen=True, slots=True)
class EvidenceCluster:
    cluster_id: str
    canonical_source_id: str
    member_source_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    exact_duplicate: bool
    mirror_detected: bool


@dataclass(frozen=True, slots=True)
class DeduplicationDecision:
    accepted: bool
    cluster_id: str
    independent: bool
    reason: str


class EvidenceDeduplicator:
    """Stateful, fail-closed deduplicator for one runtime process."""

    def __init__(self, *, mirror_window_seconds: int = 86_400) -> None:
        if mirror_window_seconds < 0:
            raise ValueError("mirror_window_seconds must be non-negative")
        self._mirror_window_seconds = mirror_window_seconds
        self._payload_owner: dict[str, str] = {}
        self._fingerprint_owner: dict[str, str] = {}
        self._source_lineage: dict[str, str] = {}
        self._clusters: dict[str, set[str]] = {}

    def register_envelope(self, envelope: RealSourceEnvelope) -> DeduplicationDecision:
        previous = self._payload_owner.get(envelope.content_hash)
        if previous is not None:
            cluster = self._cluster_for(previous)
            self._clusters.setdefault(cluster, set()).add(envelope.source_id)
            self._source_lineage[envelope.source_id] = previous
            return DeduplicationDecision(False, cluster, False, "exact_payload_duplicate")
        if envelope.upstream_source_id is not None:
            canonical = self._source_lineage.get(envelope.upstream_source_id, envelope.upstream_source_id)
            cluster = self._cluster_for(canonical)
            self._payload_owner[envelope.content_hash] = canonical
            self._source_lineage[envelope.source_id] = canonical
            self._clusters.setdefault(cluster, set()).add(envelope.source_id)
            return DeduplicationDecision(False, cluster, False, "declared_upstream_mirror")
        self._payload_owner[envelope.content_hash] = envelope.source_id
        cluster = self._cluster_for(envelope.source_id)
        self._clusters.setdefault(cluster, set()).add(envelope.source_id)
        return DeduplicationDecision(True, cluster, True, "new_payload")

    def register_observations(self, observations: Iterable[SourceObservation]) -> tuple[SourceObservation, ...]:
        accepted: list[SourceObservation] = []
        for observation in observations:
            fingerprint = observation.content_fingerprint or self._fallback_fingerprint(observation)
            owner = self._fingerprint_owner.get(fingerprint)
            if owner is not None:
                self._source_lineage.setdefault(observation.source_id, owner)
                continue
            self._fingerprint_owner[fingerprint] = observation.source_id
            accepted.append(observation)
        return tuple(accepted)

    def cluster_members(self, cluster_id: str) -> tuple[str, ...]:
        return tuple(sorted(self._clusters.get(cluster_id, set())))

    @staticmethod
    def _fallback_fingerprint(observation: SourceObservation) -> str:
        if observation.event_time.tzinfo is None or observation.event_time.utcoffset() is None:
            raise ValueError("event_time must be timezone-aware")
        canonical = "|".join(
            (
                observation.variable.casefold().strip(),
                format(float(observation.value), ".12g"),
                observation.event_time.isoformat(),
                observation.domain.casefold().strip(),
            )
        )
        return sha256(canonical.encode("utf-8")).hexdigest()

    def _cluster_for(self, source_id: str) -> str:
        canonical = self._source_lineage.get(source_id, source_id)
        return f"evidence-cluster-{sha256(canonical.encode()).hexdigest()[:16]}"
