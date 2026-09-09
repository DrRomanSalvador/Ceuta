"""Registro auditable de fuentes. Sin scores de fiabilidad inventados."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class SourceType(str, Enum):
    INSTITUTIONAL = "institutional"
    SCIENTIFIC = "scientific"
    MEDIA = "media"
    SOCIAL = "social"
    UNKNOWN = "unknown"


class SourceStatus(str, Enum):
    REGISTERED = "registered"
    FETCHED = "fetched"
    FAILED = "failed"
    NO_VERIFICADO = "no_verificado"


@dataclass
class SourceRecord:
    source_id: str
    url: str
    source_type: SourceType
    status: SourceStatus
    fetched_at_utc: str | None = None
    http_status: int | None = None
    content_sha256: str | None = None
    excerpt: str = ""
    notes: str = ""
    extra: dict[str, Any] = field(default_factory=dict)


_REGISTRY: dict[str, SourceRecord] = {}


def register_source(
    source_id: str,
    url: str,
    source_type: SourceType = SourceType.UNKNOWN,
    notes: str = "",
) -> SourceRecord:
    rec = SourceRecord(
        source_id=source_id,
        url=url,
        source_type=source_type,
        status=SourceStatus.REGISTERED,
        notes=notes,
    )
    _REGISTRY[source_id] = rec
    return rec


def update_fetch(
    source_id: str,
    *,
    http_status: int | None,
    content_sha256: str | None,
    excerpt: str,
) -> SourceRecord:
    rec = _REGISTRY[source_id]
    rec.http_status = http_status
    rec.content_sha256 = content_sha256
    rec.excerpt = excerpt[:500]
    rec.fetched_at_utc = datetime.now(timezone.utc).isoformat()
    rec.status = SourceStatus.FETCHED if http_status and 200 <= http_status < 300 else SourceStatus.FAILED
    return rec


def get_source(source_id: str) -> SourceRecord | None:
    return _REGISTRY.get(source_id)


def list_sources() -> list[SourceRecord]:
    return list(_REGISTRY.values())
    