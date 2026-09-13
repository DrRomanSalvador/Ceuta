from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ResolvedEvent:
    event_id: str
    event_time: datetime
    source_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]


class EventResolver:
    def resolve(self, event_id: str, records: tuple[tuple[datetime, str, str], ...]) -> ResolvedEvent:
        if not records:
            raise ValueError("records must not be empty")
        times = [r[0] for r in records]
        if any(t.tzinfo is None or t.utcoffset() is None for t in times):
            raise ValueError("event timestamps must be timezone-aware")
        return ResolvedEvent(event_id, min(times), tuple(sorted({r[1] for r in records})), tuple(sorted({r[2] for r in records})))
