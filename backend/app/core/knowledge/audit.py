from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class AuditRecord:
    record_id: str
    action: str
    actor: str
    occurred_at: datetime
    object_id: str
    evidence_ids: tuple[str, ...]


class RetrospectiveAuditEngine:
    def verify(self, records: tuple[AuditRecord, ...]) -> tuple[AuditRecord, ...]:
        ordered = tuple(sorted(records, key=lambda r: (r.occurred_at, r.record_id)))
        if any(r.occurred_at.tzinfo is None or r.occurred_at.utcoffset() is None for r in ordered):
            raise ValueError("audit timestamps must be timezone-aware")
        return ordered
