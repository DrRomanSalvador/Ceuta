"""Versioned policy and configuration provenance contract."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json


@dataclass(frozen=True, slots=True)
class PolicyProvenance:
    policy_id: str
    version: str
    effective_from: str
    effective_until: str | None
    source_refs: tuple[str, ...]
    rationale: str
    configuration: dict[str, object]

    def __post_init__(self) -> None:
        if not self.policy_id or not self.version or not self.effective_from or not self.rationale:
            raise ValueError("policy identity, effective_from and rationale are required")
        if not self.source_refs:
            raise ValueError("policy provenance requires source references")

    def semantic_payload(self) -> dict[str, object]:
        return {
            "policy_id": self.policy_id,
            "version": self.version,
            "effective_from": self.effective_from,
            "effective_until": self.effective_until,
            "source_refs": self.source_refs,
            "rationale": self.rationale,
            "configuration": self.configuration,
        }

    def configuration_hash(self) -> str:
        canonical = json.dumps(self.configuration, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return sha256(canonical.encode()).hexdigest()

    def semantic_fingerprint(self) -> str:
        canonical = json.dumps(self.semantic_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return sha256(canonical.encode()).hexdigest()


__all__ = ["PolicyProvenance"]
