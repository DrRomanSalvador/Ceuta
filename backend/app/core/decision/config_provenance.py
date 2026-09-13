"""Immutable execution-configuration provenance."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True, slots=True)
class ConfigurationProvenance:
    configuration_id: str
    version: str
    source_refs: tuple[str, ...]
    values: dict[str, object]

    def __post_init__(self) -> None:
        if not self.configuration_id or not self.version:
            raise ValueError("configuration_id and version are required")
        if not self.source_refs:
            raise ValueError("configuration provenance requires source references")

    def canonical_payload(self) -> dict[str, object]:
        return {"configuration_id": self.configuration_id, "version": self.version, "source_refs": self.source_refs, "values": self.values}

    def fingerprint(self) -> str:
        payload = json.dumps(self.canonical_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return sha256(payload.encode()).hexdigest()


__all__ = ["ConfigurationProvenance"]
