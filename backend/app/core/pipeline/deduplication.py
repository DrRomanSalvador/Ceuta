from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256

from .sources.real_base import RealSourceEnvelope, SourceObservation


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


def _require_time(value: datetime, field: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field} must be timezone-aware")


class EvidenceDeduplicator:
    def __init__(self, *, mirror_window_seconds: int = 86_400) -> None:
        if mirror_window_seconds < 0:
            raise ValueError("mirror_window_seconds must be non-negative")
        self._mirror_window_seconds = mirror_window_seconds
        self._payload_owner: dict[str, str] = {}
        self._fingerprint_owner: dict[str, str] = {}
        self._source_lineage: dict[str, str] = {}
        self._clusters: dict[str, set[str]] = {}
        self._cluster_evidence: dict[str, set[str]] = {}

    def register_envelope(self, envelope: RealSourceEnvelope) -> DeduplicationDecision:
        _require_time(envelope.fetched_at, "fetched_at")
        if envelope.event_time is not None:
            _require_time(envelope.event_time, "event_time")
            if envelope.event_time > envelope.fetched_at:
                raise ValueError("event_time cannot be later than fetched_at")
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
            _require_time(observation.event_time, "event_time")
            _require_time(observation.available_at, "available_at")
            if observation.available_at < observation.event_time:
                raise ValueError("available_at cannot precede event_time")
            fingerprint = observation.content_fingerprint or self._fallback_fingerprint(observation)
            owner = self._fingerprint_owner.get(fingerprint)
            if owner is not None:
                self._source_lineage.setdefault(observation.source_id, owner)
                cluster = self._cluster_for(owner)
                self._clusters.setdefault(cluster, set()).add(observation.source_id)
                self._cluster_evidence.setdefault(cluster, set()).add(observation.evidence_id)
                continue
            self._fingerprint_owner[fingerprint] = observation.source_id
            cluster = self._cluster_for(observation.source_id)
            self._clusters.setdefault(cluster, set()).add(observation.source_id)
            self._cluster_evidence.setdefault(cluster, set()).add(observation.evidence_id)
            accepted.append(observation)
        return tuple(accepted)

    def cluster(self, cluster_id: str) -> EvidenceCluster:
        members = tuple(sorted(self._clusters.get(cluster_id, set())))
        if not members:
            raise KeyError(cluster_id)
        canonical = min(self._source_lineage.get(item, item) for item in members)
        return EvidenceCluster(
            cluster_id=cluster_id,
            canonical_source_id=canonical,
            member_source_ids=members,
            evidence_ids=tuple(sorted(self._cluster_evidence.get(cluster_id, set()))),
            exact_duplicate=len(members) > 1,
            mirror_detected=any(self._source_lineage.get(item, item) != item for item in members),
        )

    def cluster_members(self, cluster_id: str) -> tuple[str, ...]:
        return tuple(sorted(self._clusters.get(cluster_id, set())))

    @staticmethod
    def _fallback_fingerprint(observation: SourceObservation) -> str:
        _require_time(observation.event_time, "event_time")
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
