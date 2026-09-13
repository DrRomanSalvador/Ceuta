from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class TraceRecord:
    trace_id: str
    operation: str
    occurred_at: datetime
    input_ids: tuple[str, ...]
    output_ids: tuple[str, ...]
    model_version: str | None


class TraceabilityLedger:
    def __init__(self) -> None:
        self._records: list[TraceRecord] = []

    def append(self, record: TraceRecord) -> None:
        if record.occurred_at.tzinfo is None or record.occurred_at.utcoffset() is None:
            raise ValueError("occurred_at must be timezone-aware")
        self._records.append(record)

    @property
    def records(self) -> tuple[TraceRecord, ...]:
        return tuple(self._records)
