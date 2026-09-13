"""Multidomain dynamic-state stage for the CeutIA event pipeline."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from hashlib import sha256
from typing import Final, Iterable
from uuid import UUID, uuid5, NAMESPACE_URL

from ...epistemology_p0.advanced.dynamic_system import (
    DynamicSystemMonitor,
    Interaction as CoreInteraction,
    Observation as CoreObservation,
)
from ..bus import EventBus
from ..contracts import (
    DomainState,
    Interaction,
    InteractionEffect,
    ObservationRecord,
    PipelineEvent,
    SystemStateContract,
    VariableState,
)

NORMALIZED_OBSERVATION_EVENT: Final[str] = "observation.normalized"
SYSTEM_STATE_EVENT: Final[str] = "system.state"
SCHEMA_VERSION: Final[str] = "1.0"
_STATE_NAMESPACE: Final[UUID] = uuid5(NAMESPACE_URL, "https://ceutia.local/system-state")


class DynamicStateStage:
    """Accumulate normalized observations and emit immutable system states.

    The stage delegates temporal state, velocity, acceleration and configured
    association effects to the existing DynamicSystemMonitor. It deliberately
    does not infer causality from temporal association.
    """

    def __init__(
        self,
        bus: EventBus,
        *,
        interactions: Iterable[Interaction] = (),
    ) -> None:
        self.bus = bus
        self.interactions = tuple(interactions)
        self._monitor = DynamicSystemMonitor(
            CoreInteraction(
                upstream=item.upstream,
                downstream=item.downstream,
                coupling=item.coupling,
                lag_steps=item.lag_steps,
                mechanism=item.mechanism,
            )
            for item in self.interactions
        )
        self._observations: dict[str, ObservationRecord] = {}
        self._queue: asyncio.Queue[PipelineEvent] | None = None
        self._task: asyncio.Task[None] | None = None
        self._stop = asyncio.Event()
        self._latest_state: SystemStateContract | None = None

    async def start(self) -> None:
        if self._task is not None:
            raise RuntimeError("state stage already started")
        self._queue = await self.bus.subscribe(NORMALIZED_OBSERVATION_EVENT)
        self._stop.clear()
        self._task = asyncio.create_task(self.run(), name="ceutia-state")

    async def run(self) -> None:
        if self._queue is None:
            raise RuntimeError("state stage is not started")
        while not self._stop.is_set():
            try:
                event = await asyncio.wait_for(self._queue.get(), timeout=0.1)
            except asyncio.TimeoutError:
                continue
            try:
                state = self._process(event)
                await self.bus.publish(
                    PipelineEvent(
                        event_id=event.event_id + ":state",
                        event_type=SYSTEM_STATE_EVENT,
                        created_at=self._now(),
                        correlation_id=event.correlation_id,
                        source_stage="state",
                        schema_version=SCHEMA_VERSION,
                        payload=state,
                    )
                )
            except (TypeError, ValueError):
                # Scientific pipeline stages fail closed: malformed input is
                # rejected and never promoted to the next stage.
                continue
            finally:
                self._queue.task_done()

    def _process(self, payload: PipelineEvent) -> SystemStateContract:
        if not isinstance(payload.payload, ObservationRecord):
            raise TypeError("normalized observation payload must be ObservationRecord")
        observation = payload.payload
        if observation.observation_id in self._observations:
            return self._latest_state or self._build_state(observation.available_at)

        core_observation = CoreObservation(
            variable=observation.variable,
            value=observation.value,
            event_time=observation.event_time,
            available_at=observation.available_at,
            source_ids=observation.source_ids,
            evidence_ids=observation.evidence_ids,
            quality=observation.quality,
        )
        self._monitor.ingest((core_observation,), evaluation_time=observation.available_at)
        self._observations[observation.observation_id] = observation
        state = self._build_state(observation.available_at)
        self._latest_state = state
        return state

    def _build_state(self, as_of: datetime) -> SystemStateContract:
        core_state = self._monitor.snapshot(as_of=as_of)
        variables = {
            item.variable: VariableState(
                variable=item.variable,
                value=item.value,
                previous_value=item.previous_value,
                velocity=item.velocity,
                acceleration=item.acceleration,
                observations=item.observations,
                updated_at=item.updated_at,
                evidence_ids=item.evidence_ids,
            )
            for item in core_state.variables
        }

        observations_by_domain: dict[str, list[ObservationRecord]] = {}
        for observation in self._observations.values():
            if observation.available_at <= as_of:
                observations_by_domain.setdefault(observation.domain, []).append(observation)

        domains = tuple(
            DomainState(
                domain=domain,
                variables=tuple(
                    variables[name]
                    for name in sorted({item.variable for item in records})
                    if name in variables
                ),
                observation_ids=tuple(item.observation_id for item in sorted(records, key=lambda x: x.event_time)),
            )
            for domain, records in sorted(observations_by_domain.items())
        )
        if not domains:
            raise ValueError("cannot emit a system state without an eligible domain")

        effects = tuple(
            InteractionEffect(
                upstream=item.upstream,
                downstream=item.downstream,
                coupling=item.coupling,
                upstream_velocity=item.upstream_velocity,
                estimated_effect=item.estimated_effect,
                interpretation=item.interpretation,
                status=item.status,
            )
            for item in core_state.interaction_effects
        )
        observation_ids = tuple(
            item.observation_id
            for item in sorted(self._observations.values(), key=lambda x: (x.event_time, x.observation_id))
            if item.available_at <= as_of
        )
        state_material = "|".join((as_of.isoformat(), *observation_ids, SCHEMA_VERSION))
        state_id = "state-" + sha256(state_material.encode("utf-8")).hexdigest()[:16]
        return SystemStateContract(
            state_id=state_id,
            as_of=as_of,
            domains=domains,
            interactions=self.interactions,
            interaction_effects=effects,
            observation_ids=observation_ids,
            schema_version=SCHEMA_VERSION,
        )

    @property
    def latest_state(self) -> SystemStateContract | None:
        return self._latest_state

    async def stop(self) -> None:
        self._stop.set()
        if self._task is not None:
            await self._task
            self._task = None
        if self._queue is not None:
            await self.bus.unsubscribe(NORMALIZED_OBSERVATION_EVENT, self._queue)
            self._queue = None

    @staticmethod
    def _now() -> datetime:
        return datetime.now(timezone.utc)
