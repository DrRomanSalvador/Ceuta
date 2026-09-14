"""Runtime configuration for authoritative sources.

URLs are deployment configuration, never hard-coded guesses. This keeps the
repository auditable while allowing the production deployment to register only
sources that have been explicitly verified by the operator.
"""
from __future__ import annotations

import json
import os
from datetime import timedelta

from .official_sources import OfficialSource, OfficialSourceRegistry


def load_official_source_registry() -> OfficialSourceRegistry:
    raw = os.getenv("CEUTIA_OFFICIAL_SOURCES_JSON", "[]").strip()
    try:
        entries = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("CEUTIA_OFFICIAL_SOURCES_JSON must be valid JSON") from exc
    if not isinstance(entries, list):
        raise ValueError("CEUTIA_OFFICIAL_SOURCES_JSON must be a JSON list")
    sources: list[OfficialSource] = []
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("each official source must be a JSON object")
        interval = float(entry.get("refresh_interval_seconds", 3600))
        sources.append(OfficialSource(
            source_id=str(entry["source_id"]),
            publisher=str(entry["publisher"]),
            url=str(entry["url"]),
            jurisdiction=str(entry.get("jurisdiction", "Ceuta")),
            refresh_interval=timedelta(seconds=interval),
            enabled=bool(entry.get("enabled", True)),
        ))
    return OfficialSourceRegistry(tuple(sources))


__all__ = ["load_official_source_registry"]
