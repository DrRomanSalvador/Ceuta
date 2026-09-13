from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class EvidenceLevel(StrEnum):
    FACT = "FACT"
    INFERENCE = "INFERENCE"
    HYPOTHESIS = "HYPOTHESIS"
    UNVERIFIED = "UNVERIFIED"


@dataclass(frozen=True, slots=True)
class EvidenceItem:
    evidence_id: str
    level: EvidenceLevel
    statement: str
    source_ids: tuple[str, ...]
    observed_at: str


class EvidenceLayer:
    def stratify(self, items: tuple[EvidenceItem, ...]) -> tuple[EvidenceItem, ...]:
        return tuple(sorted(items, key=lambda x: (x.level.value, x.evidence_id)))

    def insufficient_evidence_message(self) -> str:
        return "No hay evidencia suficiente para sostener una conclusión."
