from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from app.core.pipeline.contracts import ObservationRecord


class SourceAdapter(Protocol):
    source_id: str
    def fetch(self, *, as_of: datetime) -> tuple[ObservationRecord, ...]: ...


@dataclass(frozen=True, slots=True)
class IngestionBatch:
    batch_id: str
    as_of: datetime
    observations: tuple[ObservationRecord, ...]
    source_ids: tuple[str, ...]


class IngestionOrchestrator:
    """Fan-in boundary: fetches sources at one temporal cutoff and preserves provenance."""

    def __init__(self, adapters: tuple[SourceAdapter, ...]) -> None:
        ids = tuple(adapter.source_id for adapter in adapters)
        if len(ids) != len(set(ids)):
            raise ValueError("source_id values must be unique")
        self._adapters = adapters

    def collect(self, *, batch_id: str, as_of: datetime) -> IngestionBatch:
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise ValueError("as_of must be timezone-aware")
        observations: list[ObservationRecord] = []
        for adapter in self._adapters:
            observations.extend(adapter.fetch(as_of=as_of))
        observations.sort(key=lambda item: (item.available_at, item.observation_id))
        return IngestionBatch(
            batch_id=batch_id,
            as_of=as_of,
            observations=tuple(observations),
            source_ids=tuple(adapter.source_id for adapter in self._adapters),
        )
