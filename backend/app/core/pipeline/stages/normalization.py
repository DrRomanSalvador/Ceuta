"""Normalization stage for the deterministic Phase 1 pipeline."""

from __future__ import annotations

import asyncio
from dataclasses import replace
from datetime import datetime, timezone
from hashlib import sha256
import math
from typing import Final

from ..bus import EventBus
from ..contracts import ObservationRecord, PipelineEvent

RAW_OBSERVATION_EVENT: Final[str] = "observation.raw"
NORMALIZED_OBSERVATION_EVENT: Final[str] = "observation.normalized"
SCHEMA_VERSION: Final[str] = "1.0"


class NormalizationStage:
    """Consume raw observations and publish canonical normalized observations."""

    def __init__(self, bus: EventBus, *, evaluation_time: datetime | None = None) -> None:
        self.bus = bus
        self.evaluation_time = evaluation_time
        self._queue: asyncio.Queue[PipelineEvent] | None = None
        self._task: asyncio.Task[None] | None = None
        self._stop = asyncio.Event()

    async def start(self) -> None:
        if self._task is not None:
            raise RuntimeError("normalization stage already started")
        self._queue = await self.bus.subscribe(RAW_OBSERVATION_EVENT)
        self._stop.clear()
        self._task = asyncio.create_task(self.run(), name="ceutia-normalization")

    async def run(self) -> None:
        if self._queue is None:
            raise RuntimeError("normalization stage is not started")
        while not self._stop.is_set():
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=0.1)
            except asyncio.TimeoutError:
                continue
            try:
                observation = self._normalize(event.payload)
                await self.bus.publish(
                    PipelineEvent(
                        event_id=event.event_id + ":normalized",
                        event_type=NORMALIZED_OBSERVATION_EVENT,
                        created_at=self._now(),
                        correlation_id=event.correlation_id,
                        source_stage="normalization",
                        schema_version=SCHEMA_VERSION,
                        payload=observation,
                    )
                )
            finally:
                self._queue.task_done()

    def _normalize(self, payload: object) -> ObservationRecord:
        if not isinstance(payload, ObservationRecord):
            raise TypeError("raw observation payload must be ObservationRecord")
        observation = payload
        if not math.isfinite(observation.value):
            raise ValueError("observation value must be finite")
        if observation.available_at < observation.event_time:
            raise ValueError("available_at cannot precede event_time")
        if self.evaluation_time is not None and observation.available_at > self.evaluation_time:
            raise ValueError("observation is not available at evaluation_time")

        provenance_material = "|".join(
            (
                observation.observation_id,
                observation.variable,
                repr(observation.value),
                observation.unit or "",
                observation.event_time.isoformat(),
                observation.available_at.isoformat(),
                ",".join(observation.source_ids),
                ",".join(observation.evidence_ids),
                observation.domain,
                repr(observation.quality),
            )
        )
        provenance_hash = sha256(provenance_material.encode("utf-8")).hexdigest()
        return replace(observation, provenance_hash=provenance_hash)

    async def stop(self) -> None:
        self._stop.set()
        if self._task is not None:
            await self._task
            self._task = None
        if self._queue is not None:
            await self.bus.unsubscribe(RAW_OBSERVATION_EVENT, self._queue)
            self._queue = None

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)
