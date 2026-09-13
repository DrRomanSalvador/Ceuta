"""
P1 — Registro de versiones de datos, reglas y modelos.

Toda transformación relevante queda auditada con versión, actor y justificación.
"""

from __future__ import annotations
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from enum import Enum
import uuid


class ArtifactKind(str, Enum):
    DATA = "data"
    RULE = "rule"
    MODEL = "model"
    SCHEMA = "schema"
    PIPELINE = "pipeline"


@dataclass(frozen=True)
class VersionRecord:
    record_id: str
    kind: ArtifactKind
    name: str
    version: str
    content_hash: Optional[str]
    actor: str
    justification: str
    created_at: str
    parent_version: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = asdict(self)
        d["kind"] = self.kind.value
        return d


class VersionRegistry:
    """Registro inmutable de versiones (append-only)."""

    def __init__(self) -> None:
        self._records: List[VersionRecord] = []
        self._latest: Dict[str, VersionRecord] = {}

    def register(
        self,
        *,
        kind: ArtifactKind,
        name: str,
        version: str,
        actor: str,
        justification: str,
        content_hash: Optional[str] = None,
        parent_version: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> VersionRecord:
        if not justification or not justification.strip():
            raise ValueError("justification is required")
        rec = VersionRecord(
            record_id=f"ver-{uuid.uuid4().hex[:12]}",
            kind=kind,
            name=name,
            version=version,
            content_hash=content_hash,
            actor=actor,
            justification=justification,
            created_at=datetime.now(timezone.utc).isoformat(),
            parent_version=parent_version,
            metadata=metadata or {},
        )
        self._records.append(rec)
        self._latest[f"{kind.value}:{name}"] = rec
        return rec

    def latest(self, kind: ArtifactKind, name: str) -> Optional[VersionRecord]:
        return self._latest.get(f"{kind.value}:{name}")

    def history(self, kind: Optional[ArtifactKind] = None, name: Optional[str] = None) -> List[VersionRecord]:
        out = self._records
        if kind is not None:
            out = [r for r in out if r.kind == kind]
        if name is not None:
            out = [r for r in out if r.name == name]
        return list(out)

    def to_list(self) -> List[dict]:
        return [r.to_dict() for r in self._records]
