"""Canonical machine-readable serialization for CeutIA decision artifacts."""
from __future__ import annotations

import json
from dataclasses import asdict
from hashlib import sha256
from typing import Any

from .control_plane import DecisionAuditEvent, DecisionManifest


def _canonicalize(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _canonicalize(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))}
    if isinstance(value, (list, tuple)):
        return [_canonicalize(item) for item in value]
    if hasattr(value, "value"):
        return _canonicalize(value.value)
    return value


def manifest_semantic_payload(manifest: DecisionManifest) -> dict[str, Any]:
    """Return identity-bearing manifest fields; execution timestamps are excluded."""
    payload = asdict(manifest)
    payload.pop("created_at", None)
    return _canonicalize(payload)


def manifest_execution_payload(manifest: DecisionManifest) -> dict[str, Any]:
    """Return the complete manifest including execution timestamp."""
    return _canonicalize(asdict(manifest))


def manifest_semantic_fingerprint(manifest: DecisionManifest) -> str:
    """Hash semantic decision identity independently of execution timing."""
    canonical = json.dumps(
        manifest_semantic_payload(manifest),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(canonical).hexdigest()


def manifest_execution_fingerprint(manifest: DecisionManifest) -> str:
    """Hash the complete execution artifact, including execution timing."""
    canonical = json.dumps(
        manifest_execution_payload(manifest),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return sha256(canonical).hexdigest()


def serialize_manifest(manifest: DecisionManifest, *, include_execution_metadata: bool = True) -> str:
    """Serialize a manifest deterministically as UTF-8-compatible JSON text."""
    payload = (
        manifest_execution_payload(manifest)
        if include_execution_metadata
        else manifest_semantic_payload(manifest)
    )
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def serialize_audit_event(event: DecisionAuditEvent) -> str:
    """Serialize an audit event deterministically as JSON text."""
    return json.dumps(_canonicalize(asdict(event)), ensure_ascii=False, sort_keys=True, separators=(",", ":"))


__all__ = [
    "manifest_execution_fingerprint",
    "manifest_execution_payload",
    "manifest_semantic_fingerprint",
    "manifest_semantic_payload",
    "serialize_audit_event",
    "serialize_manifest",
]
