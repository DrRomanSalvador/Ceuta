"""Temporal state persistence with an explicit observation-availability boundary."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .contracts import ObservationRecord


@dataclass(frozen=True, slots=True)
class StateSnapshot:
    as_of: datetime
    observations: tuple[ObservationRecord, ...]


class TemporalStateStore:
    """Append-only in-process state store with fail-closed temporal queries."""

    def __init__(self) -> None:
        self._records: dict[str, ObservationRecord] = {}

    def append(self, records: tuple[ObservationRecord, ...] | list[ObservationRecord]) -> int:
        for record in records:
            existing = self._records.get(record.observation_id)
            if existing is not None and existing.provenance_hash != record.provenance_hash:
                raise ValueError(f"observation id collision: {record.observation_id}")
            self._records[record.observation_id] = record
        return len(records)

    def snapshot(self, *, as_of: datetime) -> StateSnapshot:
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise ValueError("as_of must be timezone-aware")
        eligible = tuple(
            sorted(
                (
                    record
                    for record in self._records.values()
                    if record.event_time <= as_of and record.available_at <= as_of
                ),
                key=lambda record: (record.event_time, record.observation_id),
            )
        )
        return StateSnapshot(as_of=as_of, observations=eligible)

    def all_records(self) -> tuple[ObservationRecord, ...]:
        return tuple(sorted(self._records.values(), key=lambda item: item.event_time))
