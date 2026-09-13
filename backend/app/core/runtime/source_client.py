"""Network boundary for authoritative-source refresh.

Only URLs explicitly registered in OfficialSourceRegistry may be retrieved. The
client uses conditional HTTP requests, bounded timeouts and content hashing. A
network response is data, not truth: downstream evidence gates remain mandatory.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping

import httpx

from .official_sources import OfficialSourceRegistry, SourceSnapshot


@dataclass(frozen=True, slots=True)
class RetrievedSource:
    source_id: str
    status_code: int
    content: bytes
    snapshot: SourceSnapshot
    headers: Mapping[str, str]


class OfficialSourceClient:
    def __init__(self, registry: OfficialSourceRegistry, *, timeout_seconds: float = 15.0,
                 max_bytes: int = 10_000_000) -> None:
        if timeout_seconds <= 0 or max_bytes <= 0:
            raise ValueError("timeout and max_bytes must be positive")
        self.registry = registry
        self.timeout_seconds = timeout_seconds
        self.max_bytes = max_bytes
        self._client = httpx.Client(timeout=timeout_seconds, follow_redirects=True)

    def close(self) -> None:
        self._client.close()

    def refresh(self, source_id: str, *, now: datetime | None = None) -> RetrievedSource:
        source = self.registry.metadata().get(source_id)
        if source is None or not source.enabled:
            raise KeyError(source_id)
        timestamp = now or datetime.now(timezone.utc)
        if timestamp.tzinfo is None or timestamp.utcoffset() is None:
            raise ValueError("now must be timezone-aware")
        previous = self.registry.latest_snapshot(source_id)
        headers: dict[str, str] = {"Accept": "application/json, text/html, text/plain, */*"}
        if previous is not None:
            if previous.etag:
                headers["If-None-Match"] = previous.etag
            if previous.last_modified:
                headers["If-Modified-Since"] = previous.last_modified
        response = self._client.get(source.url, headers=headers)
        if response.status_code == 304 and previous is not None:
            snapshot = SourceSnapshot(source_id, timestamp, previous.content_hash, 304,
                                      previous.etag, previous.last_modified, True)
            self.registry.register_snapshot(snapshot)
            return RetrievedSource(source_id, 304, b"", snapshot, dict(response.headers))
        content = response.content
        if len(content) > self.max_bytes:
            raise ValueError("official source response exceeds configured size limit")
        snapshot = SourceSnapshot.from_bytes(
            source_id, content, timestamp, response.status_code,
            etag=response.headers.get("etag"),
            last_modified=response.headers.get("last-modified"),
            verified=response.status_code < 400,
        )
        self.registry.register_snapshot(snapshot)
        return RetrievedSource(source_id, response.status_code, content, snapshot, dict(response.headers))
