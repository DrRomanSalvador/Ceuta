"""Semantic identity separated from execution identity."""
from __future__ import annotations

from hashlib import sha256
import json
from typing import Mapping


def semantic_fingerprint(payload: Mapping[str, object]) -> str:
    canonical = json.dumps(dict(payload), sort_keys=True, default=str, separators=(",", ":"), ensure_ascii=False)
    return sha256(canonical.encode()).hexdigest()


def execution_fingerprint(payload: Mapping[str, object], *, execution_id: str, created_at: str) -> str:
    execution_payload = dict(payload)
    execution_payload.update({"execution_id": execution_id, "created_at": created_at})
    canonical = json.dumps(execution_payload, sort_keys=True, default=str, separators=(",", ":"), ensure_ascii=False)
    return sha256(canonical.encode()).hexdigest()


__all__ = ["execution_fingerprint", "semantic_fingerprint"]
