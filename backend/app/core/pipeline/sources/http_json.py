"""Allowlisted HTTP JSON source adapter with deterministic provenance."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
from urllib.parse import urlparse

import httpx

from ..contracts import ObservationRecord
from .adapter import SourceEnvelope


@dataclass(frozen=True, slots=True)
class JsonHttpSourceAdapter:
    source_id: str
    url: str
    allowed_hosts: tuple[str, ...]
    timeout_seconds: float = 10.0

    def __post_init__(self) -> None:
        parsed = urlparse(self.url)
        if parsed.scheme != "https" or not parsed.hostname:
            raise ValueError("source URL must use HTTPS")
        if parsed.hostname not in self.allowed_hosts:
            raise ValueError("source host is not allowlisted")
        if self.timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")

    async def fetch(self, *, now: datetime) -> SourceEnvelope:
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("now must be timezone-aware")
        async with httpx.AsyncClient(timeout=self.timeout_seconds, follow_redirects=False) as client:
            response = await client.get(self.url, headers={"Accept": "application/json"})
            response.raise_for_status()
            if "application/json" not in response.headers.get("content-type", "").lower():
                raise ValueError("source response is not JSON")
            payload = response.content
        return SourceEnvelope(
            source_id=self.source_id,
            canonical_uri=self.url,
            fetched_at=now,
            payload=payload,
            content_hash=sha256(payload).hexdigest(),
        )

    def parse(self, envelope: SourceEnvelope) -> tuple[ObservationRecord, ...]:
        data = json.loads(envelope.payload.decode("utf-8"))
        if not isinstance(data, list):
            raise ValueError("JSON source payload must be a list")
        records: list[ObservationRecord] = []
        for item in data:
            if not isinstance(item, dict):
                raise ValueError("each source item must be an object")
            required = {"observation_id", "variable", "value", "event_time", "available_at", "domain"}
            if not required.issubset(item):
                raise ValueError("source item is missing required observation fields")
            records.append(
                ObservationRecord(
                    observation_id=str(item["observation_id"]),
                    variable=str(item["variable"]),
                    value=float(item["value"]),
                    unit=str(item["unit"]) if item.get("unit") is not None else None,
                    event_time=datetime.fromisoformat(str(item["event_time"])),
                    available_at=datetime.fromisoformat(str(item["available_at"])),
                    source_ids=(self.source_id,),
                    evidence_ids=tuple(str(x) for x in item.get("evidence_ids", ())),
                    domain=str(item["domain"]),
                    quality=float(item.get("quality", 1.0)),
                    provenance_hash=sha256(
                        json.dumps(item, sort_keys=True, separators=(",", ":")).encode("utf-8")
                    ).hexdigest(),
                )
            )
        return tuple(records)
