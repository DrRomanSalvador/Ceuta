"""Auditable registry for authoritative external sources.

CeutIA must distinguish source authority from evidence strength. This module stores
source metadata and produces immutable retrieval records; network retrieval is kept
outside inference so a failed refresh can never silently masquerade as current data.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import Mapping


@dataclass(frozen=True, slots=True)
class OfficialSource:
    source_id: str
    publisher: str
    url: str
    jurisdiction: str
    refresh_interval: timedelta
    enabled: bool = True

    def __post_init__(self) -> None:
        if not self.source_id or not self.publisher or not self.url:
            raise ValueError("official source requires id, publisher and url")
        if self.refresh_interval <= timedelta(0):
            raise ValueError("refresh interval must be positive")


@dataclass(frozen=True, slots=True)
class SourceSnapshot:
    source_id: str
    retrieved_at: datetime
    content_hash: str
    http_status: int
    etag: str | None = None
    last_modified: str | None = None
    verified: bool = False
    error: str | None = None

    def __post_init__(self) -> None:
        if self.retrieved_at.tzinfo is None or self.retrieved_at.utcoffset() is None:
            raise ValueError("retrieved_at must be timezone-aware")
        if not self.content_hash or len(self.content_hash) != 64:
            raise ValueError("content_hash must be a SHA-256 digest")
        if not 100 <= self.http_status <= 599:
            raise ValueError("invalid HTTP status")

    @classmethod
    def from_bytes(cls, source_id: str, payload: bytes, retrieved_at: datetime,
                   http_status: int, *, etag: str | None = None,
                   last_modified: str | None = None, verified: bool = True) -> "SourceSnapshot":
        return cls(source_id, retrieved_at, sha256(payload).hexdigest(), http_status,
                   etag, last_modified, verified)


@dataclass(frozen=True, slots=True)
class SourceFreshness:
    source_id: str
    current: bool
    age_seconds: float
    refresh_due: bool
    reason: str


class OfficialSourceRegistry:
    """Policy layer for official-source synchronization.

    It does not claim that a publisher is correct merely because it is official.
    Publisher authority, document freshness, integrity and downstream evidential
    quality remain separate dimensions.
    """

    def __init__(self, sources: tuple[OfficialSource, ...]) -> None:
        ids = [s.source_id for s in sources]
        if len(ids) != len(set(ids)):
            raise ValueError("source ids must be unique")
        self._sources = {s.source_id: s for s in sources}
        self._snapshots: dict[str, SourceSnapshot] = {}

    def register_snapshot(self, snapshot: SourceSnapshot) -> None:
        if snapshot.source_id not in self._sources:
            raise KeyError(snapshot.source_id)
        previous = self._snapshots.get(snapshot.source_id)
        if previous is not None and snapshot.retrieved_at < previous.retrieved_at:
            raise ValueError("source snapshots must be monotonic in retrieval time")
        self._snapshots[snapshot.source_id] = snapshot

    def freshness(self, now: datetime) -> tuple[SourceFreshness, ...]:
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("now must be timezone-aware")
        out: list[SourceFreshness] = []
        for source in self._sources.values():
            snapshot = self._snapshots.get(source.source_id)
            if not source.enabled:
                out.append(SourceFreshness(source.source_id, False, float("inf"), True, "disabled"))
                continue
            if snapshot is None:
                out.append(SourceFreshness(source.source_id, False, float("inf"), True, "never_retrieved"))
                continue
            age = max(0.0, (now - snapshot.retrieved_at).total_seconds())
            due = age > source.refresh_interval.total_seconds()
            current = snapshot.verified and snapshot.http_status < 400 and not due
            reason = "current" if current else ("refresh_due" if due else "unverified")
            out.append(SourceFreshness(source.source_id, current, age, due, reason))
        return tuple(out)

    def metadata(self) -> Mapping[str, OfficialSource]:
        return dict(self._sources)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
