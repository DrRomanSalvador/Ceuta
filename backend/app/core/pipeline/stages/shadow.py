"""Event-driven Shadow Mode stage.

The stage is intentionally write-only with respect to production model state:
it consumes canonical observations and emits shadow forecasts. No calibrator,
parameter store, or production promotion API is reachable from this stage.
"""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from app.core.epistemology_p0.advanced import Observation

from ..bus import EventBus
from ..contracts import ObservationRecord, PipelineEvent
from ..shadow_mode import ForecastFunction, ShadowModeExecutor

SHADOW_OBSERVATION_EVENT = "pipeline.shadow.observation"
SHADOW_FORECAST_EVENT = "pipeline.shadow.forecast"


@dataclass(frozen=True, slots=True)
class ShadowForecastEvent:
    forecast_id: str
    model_version: str
    created_at: datetime
    status: str


class ShadowModeStage:
    """Consume observations asynchronously and publish shadow forecasts."""

    def __init__(
        self,
        bus: EventBus,
        *,
        executor: ShadowModeExecutor,
        forecast_fn: ForecastFunction,
        cutoff_time_fn: Callable[[ObservationRecord], datetime],
    ) -> None:
        self._bus = bus
        self._executor = executor
        self._forecast_fn = forecast_fn
        self._cutoff_time_fn = cutoff_time_fn
        self._queue: asyncio.Queue[PipelineEvent] | None = None
        self._task: asyncio.Task[None] | None = None

    async def start(self) -> None:
        if self._task is not None:
            raise RuntimeError("shadow stage already started")
        self._queue = await self._bus.subscribe(SHADOW_OBSERVATION_EVENT)
        self._task = asyncio.create_task(self._run(), name="ceutia-shadow-stage")

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        if self._queue is not None:
            await self._bus.unsubscribe(SHADOW_OBSERVATION_EVENT, self._queue)
        self._queue = None
        self._task = None

    async def _run(self) -> None:
        assert self._queue is not None
        while True:
            event = await self._queue.get()
            try:
                if not isinstance(event.payload, ObservationRecord):
                    raise TypeError("shadow observation event must carry ObservationRecord")
                record = event.payload
                observation = record_to_observation(record)
                cutoff_time = self._cutoff_time_fn(record)
                forecast = self._executor.forecast(
                    (observation,), cutoff_time=cutoff_time, forecast_fn=self._forecast_fn
                )
                await self._bus.publish(
                    PipelineEvent(
                        event_id=str(uuid4()),
                        event_type=SHADOW_FORECAST_EVENT,
                        created_at=cutoff_time,
                        correlation_id=record.observation_id,
                        source_stage="shadow",
                        schema_version="1.0",
                        payload=ShadowForecastEvent(
                            forecast_id=forecast.forecast_id,
                            model_version=self._executor.model_version,
                            created_at=cutoff_time,
                            status=forecast.status,
                        ),
                    )
                )
            finally:
                self._queue.task_done()


def record_to_observation(record: ObservationRecord) -> Observation:
    return Observation(
        variable=record.variable,
        value=record.value,
        event_time=record.event_time,
        available_at=record.available_at,
        source_ids=record.source_ids,
        evidence_ids=record.evidence_ids,
        quality=record.quality,
    )
