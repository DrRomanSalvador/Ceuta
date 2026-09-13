"""24/7 fail-closed CeutIA operational daemon."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Protocol

from app.core.epistemology_p0.advanced import (
    ComplexSystemAnticipationEngine,
    DynamicSystemMonitor,
    Interaction,
    Observation,
)
from app.core.pipeline.sources.adapter import ProvenanceRegistry, SourceAdapter
from app.core.pipeline.state_store import TemporalStateStore
from app.core.pipeline.validation import ClosedLoopCalibrator


class Clock(Protocol):
    def now(self) -> datetime: ...


@dataclass(frozen=True, slots=True)
class RuntimeHealth:
    healthy: bool
    last_cycle_at: datetime | None
    cycles: int
    source_failures: int
    accepted_observations: int
    last_error: str | None


class CeutIADaemon:
    """Continuously ingest, build state, forecast, and prospectively validate."""

    def __init__(
        self,
        sources: tuple[SourceAdapter, ...],
        *,
        interactions: tuple[Interaction, ...] = (),
        interval: timedelta = timedelta(minutes=5),
        calibrator: ClosedLoopCalibrator | None = None,
    ) -> None:
        if interval.total_seconds() <= 0:
            raise ValueError("interval must be positive")
        self.sources = sources
        self.interval = interval
        self.registry = ProvenanceRegistry()
        self.store = TemporalStateStore()
        self.engine = ComplexSystemAnticipationEngine(DynamicSystemMonitor(interactions))
        self.calibrator = calibrator or ClosedLoopCalibrator()
        self._processed_observation_ids: set[str] = set()
        self._stop = asyncio.Event()
        self._health = RuntimeHealth(True, None, 0, 0, 0, None)

    async def cycle(self, *, now: datetime | None = None) -> RuntimeHealth:
        evaluation_time = now or datetime.now(UTC)
        accepted = 0
        failures = self._health.source_failures
        errors: list[str] = []
        for source in self.sources:
            try:
                envelope = await source.fetch(now=evaluation_time)
                self.registry.register_envelope(envelope)
                records = self.registry.accept(source.parse(envelope))
                self.store.append(records)
                accepted += len(records)
            except Exception as exc:  # noqa: BLE001 - isolate source failures
                failures += 1
                errors.append(f"{source.source_id}: {type(exc).__name__}: {exc}")

        snapshot = self.store.snapshot(as_of=evaluation_time)
        eligible = tuple(
            record for record in snapshot.observations if record.observation_id not in self._processed_observation_ids
        )
        if eligible:
            observations = tuple(
                Observation(
                    variable=item.variable,
                    value=item.value,
                    event_time=item.event_time,
                    available_at=item.available_at,
                    source_ids=item.source_ids,
                    evidence_ids=item.evidence_ids,
                    quality=item.quality,
                )
                for item in eligible
            )
            state, forecasts = self.engine.cycle(
                observations,
                as_of=evaluation_time,
                forecast_horizon=self.interval,
            )
            self._processed_observation_ids.update(item.observation_id for item in eligible)
            for forecast in forecasts:
                self.calibrator.register(forecast)
            _ = state

        cycles = self._health.cycles + 1
        self._health = RuntimeHealth(
            healthy=not errors,
            last_cycle_at=evaluation_time,
            cycles=cycles,
            source_failures=failures,
            accepted_observations=self._health.accepted_observations + accepted,
            last_error="; ".join(errors) if errors else None,
        )
        return self._health

    async def run_forever(self) -> None:
        """Run until stopped; source failures never promote or terminate the daemon."""
        while not self._stop.is_set():
            await self.cycle()
            try:
                await asyncio.wait_for(self._stop.wait(), timeout=self.interval.total_seconds())
            except asyncio.TimeoutError:
                continue

    def stop(self) -> None:
        self._stop.set()

    @property
    def health(self) -> RuntimeHealth:
        return self._health


def main() -> None:
    asyncio.run(CeutIADaemon((), interval=timedelta(minutes=5)).run_forever())


if __name__ == "__main__":
    main()
