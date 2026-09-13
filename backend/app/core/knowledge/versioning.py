from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class KnowledgeVersion:
    version_id: str
    entity_id: str
    valid_from: datetime
    valid_to: datetime | None
    evidence_ids: tuple[str, ...]
    supersedes: str | None = None

    def __post_init__(self) -> None:
        if self.valid_from.tzinfo is None or self.valid_from.utcoffset() is None:
            raise ValueError("valid_from must be timezone-aware")
        if self.valid_to is not None and self.valid_to < self.valid_from:
            raise ValueError("valid_to cannot precede valid_from")


class KnowledgeStore:
    def __init__(self) -> None:
        self._versions: list[KnowledgeVersion] = []

    def append(self, version: KnowledgeVersion) -> None:
        self._versions.append(version)

    def as_of(self, entity_id: str, at: datetime) -> tuple[KnowledgeVersion, ...]:
        return tuple(v for v in self._versions if v.entity_id == entity_id and v.valid_from <= at and (v.valid_to is None or at < v.valid_to))

    def history(self, entity_id: str) -> tuple[KnowledgeVersion, ...]:
        return tuple(sorted((v for v in self._versions if v.entity_id == entity_id), key=lambda v: v.valid_from))
