"""Machine-readable traceability from scientific method to implementation and validation."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ValidationStatus(StrEnum):
    NOT_VALIDATED = "not_validated"
    STRUCTURAL_CHECKED = "structural_checked"
    EMPIRICALLY_VALIDATED = "empirically_validated"
    INVALIDATED = "invalidated"
    SUPERSEDED = "superseded"


@dataclass(frozen=True, slots=True)
class ScientificMethodRecord:
    method_id: str
    proposition: str
    literature_refs: tuple[str, ...]
    assumptions: tuple[str, ...]
    mathematical_formulation: str
    implementation_refs: tuple[str, ...]
    validation_refs: tuple[str, ...]
    validation_status: ValidationStatus
    limitations: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.method_id or not self.proposition or not self.mathematical_formulation:
            raise ValueError("scientific method identity, proposition and formulation are required")
        if not self.assumptions or not self.limitations:
            raise ValueError("scientific methods require explicit assumptions and limitations")
        if not self.implementation_refs:
            raise ValueError("scientific methods require implementation references")
        if self.validation_status is not ValidationStatus.NOT_VALIDATED and not self.validation_refs:
            raise ValueError("validated methods require validation references")


class ScientificMethodRegistry:
    def __init__(self, records: tuple[ScientificMethodRecord, ...] = ()) -> None:
        self._records: dict[str, ScientificMethodRecord] = {}
        for record in records:
            self.register(record)

    def register(self, record: ScientificMethodRecord) -> None:
        if record.method_id in self._records:
            raise ValueError(f"duplicate scientific method: {record.method_id}")
        self._records[record.method_id] = record

    def get(self, method_id: str) -> ScientificMethodRecord:
        try:
            return self._records[method_id]
        except KeyError as exc:
            raise KeyError(f"unknown scientific method: {method_id}") from exc

    def all(self) -> tuple[ScientificMethodRecord, ...]:
        return tuple(self._records.values())

    def implementation_is_governed(self, method_id: str, implementation_ref: str) -> bool:
        record = self.get(method_id)
        return implementation_ref in record.implementation_refs and record.validation_status not in {ValidationStatus.INVALIDATED, ValidationStatus.SUPERSEDED}


__all__ = ["ScientificMethodRecord", "ScientificMethodRegistry", "ValidationStatus"]
