"""Explicit conflict taxonomy and resolution contract for evidence synthesis."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable


class ConflictType(StrEnum):
    VALUE = "value"
    TEMPORAL = "temporal"
    SCOPE = "scope"
    METHODOLOGICAL = "methodological"
    PROVENANCE = "provenance"
    EPISTEMIC = "epistemic"
    CAUSAL = "causal"
    DEPENDENCE = "dependence"
    DUPLICATE = "duplicate"


class ConflictStatus(StrEnum):
    UNRESOLVED = "unresolved"
    RESOLVED = "resolved"
    HUMAN_REVIEW = "human_review"


@dataclass(frozen=True, slots=True)
class EvidenceConflict:
    conflict_id: str
    conflict_type: ConflictType
    evidence_refs: tuple[str, ...]
    description: str
    status: ConflictStatus = ConflictStatus.UNRESOLVED

    def __post_init__(self) -> None:
        if not self.conflict_id or not self.description:
            raise ValueError("conflict_id and description are required")
        if len(self.evidence_refs) < 2:
            raise ValueError("a conflict requires at least two evidence references")


@dataclass(frozen=True, slots=True)
class ConflictSet:
    conflicts: tuple[EvidenceConflict, ...]

    @classmethod
    def from_iterable(cls, conflicts: Iterable[EvidenceConflict]) -> "ConflictSet":
        values = tuple(conflicts)
        ids = [item.conflict_id for item in values]
        if len(ids) != len(set(ids)):
            raise ValueError("conflict_id values must be unique")
        return cls(values)

    @property
    def unresolved(self) -> tuple[EvidenceConflict, ...]:
        return tuple(item for item in self.conflicts if item.status is ConflictStatus.UNRESOLVED)

    @property
    def requires_human_review(self) -> bool:
        return any(item.status is ConflictStatus.HUMAN_REVIEW for item in self.conflicts)


__all__ = ["ConflictSet", "ConflictStatus", "ConflictType", "EvidenceConflict"]
