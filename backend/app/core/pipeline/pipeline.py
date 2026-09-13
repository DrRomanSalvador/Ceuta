"""Deterministic local orchestration for CeutIA Phase 1."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Final
from uuid import uuid4

from .bus import EventBus
from .contracts import ObservationRecord, PipelineEvent
from .sources.synthetic import SyntheticSource
from .stages.normalization import (
    NORMALIZED_OBSERVATION_EVENT,
    NormalizationStage,
    RAW_OBSERVATION_EVENT,
)

SCHEMA_VERSION: Final[str] = "1.0"


class LocalDeterministicPipeline:
    """Run the first CeutIA event-driven circuit entirely in-process."""

    def __init__(self, source: SyntheticSource | None = None) -> None:
        self.bus = EventBus(queue_maxsize=128)
        self.source = source or SyntheticSource()
        self.normalization = NormalizationStage(
            self.bus,
            evaluation_time=self.source.start_time + self.source.available_delay + (len(self.source.values) - 1) * __import__("datetime").timedelta(minutes=1),
        )
        self._normalized_queue: asyncio.Queue[PipelineEvent] | None = None
        self._started = False

    async def start(self) -> None:
        if self._started:
            raise RuntimeError("pipeline already started")
        await self.normalization.start()
        self._normalized_queue = await self.bus.subscribe(NORMALIZED_OBSERVATION_EVENT)
        self._started = True

    async def run_once(self) -> tuple[ObservationRecord, ...]:
        if not self._started or self._normalized_queue is None:
            raise RuntimeError("pipeline must be started before run_once")

        expected = len(self.source.values)
        for record in self.source.records():
            await self.bus.publish(
                PipelineEvent(
                    event_id=str(uuid4()),
                    event_type=RAW_OBSERVATION_EVENT,
                    created_at=datetime.now(timezone.utc),
                    correlation_id=record.observation_id,
                    source_stage="synthetic",
                    schema_version=SCHEMA_VERSION,
                    payload=record,
                )
            )

        normalized: list[ObservationRecord] = []
        while len(normalized) < expected:
            event = await self._normalized_queue.get()
            try:
                if not isinstance(event.payload, ObservationRecord):
                    raise TypeError("normalized event payload must be ObservationRecord")
                normalized.append(event.payload)
            finally:
                self._normalized_queue.task_done()
        return tuple(normalized)

    async def stop(self) -> None:
        if not self._started:
            return
        await self.normalization.stop()
        if self._normalized_queue is not None:
            await self.bus.unsubscribe(NORMALIZED_OBSERVATION_EVENT, self._normalized_queue)
            self._normalized_queue = None
        await self.bus.close()
        self._started = False

    async def __aenter__(self) -> "LocalDeterministicPipeline":
        await self.start()
        return self

    async def __aexit__(self, exc_type: object, exc: object, tb: object) -> None:
        await self.stop()
