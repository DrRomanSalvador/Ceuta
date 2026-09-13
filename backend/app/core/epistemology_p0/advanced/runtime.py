"""Executable runtime adapter for the closed-loop CeutIA anticipation engine.

This module provides a dependency-free demonstration/runtime boundary. Real
source adapters can replace the observation factory without changing the
state, interaction, forecast or prospective-validation contracts.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from .anticipation import ComplexSystemAnticipationEngine
from .dynamic_system import DynamicSystemMonitor, Interaction, Observation


@dataclass(frozen=True, slots=True)
class RuntimeCycleResult:
    state_id: str
    variables: tuple[str, ...]
    forecast_ids: tuple[str, ...]
    forecast_targets: tuple[datetime, ...]


def build_demo_engine() -> ComplexSystemAnticipationEngine:
    """Build a deterministic two-variable coupled-system runtime."""
    monitor = DynamicSystemMonitor(
        interactions=(
            Interaction("migration_pressure", "health_pressure", coupling=0.25),
            Interaction("health_pressure", "migration_pressure", coupling=0.10),
        )
    )
    return ComplexSystemAnticipationEngine(monitor, model_version="runtime-baseline-v1")


def run_demo_cycle(*, as_of: datetime | None = None) -> RuntimeCycleResult:
    """Execute one complete monitor -> state -> interaction -> forecast cycle."""
    evaluation_time = as_of or datetime.now(timezone.utc)
    observations: list[Observation] = []
    for offset, migration, health in (
        (timedelta(hours=-2), 10.0, 4.0),
        (timedelta(hours=-1), 11.0, 4.4),
        (timedelta(0), 12.5, 5.0),
    ):
        event_time = evaluation_time + offset
        observations.extend(
            (
                Observation(
                    variable="migration_pressure",
                    value=migration,
                    event_time=event_time,
                    available_at=event_time,
                    source_ids=("demo-source-migration",),
                    evidence_ids=(f"demo-evidence-migration-{offset.total_seconds()}",),
                ),
                Observation(
                    variable="health_pressure",
                    value=health,
                    event_time=event_time,
                    available_at=event_time,
                    source_ids=("demo-source-health",),
                    evidence_ids=(f"demo-evidence-health-{offset.total_seconds()}",),
                ),
            )
        )

    engine = build_demo_engine()
    state, forecasts = engine.cycle(
        observations,
        as_of=evaluation_time,
        forecast_horizon=timedelta(hours=1),
    )
    return RuntimeCycleResult(
        state_id=state.state_id,
        variables=tuple(item.variable for item in state.variables),
        forecast_ids=tuple(item.forecast_id for item in forecasts),
        forecast_targets=tuple(item.target_time for item in forecasts),
    )


def main() -> int:
    result = run_demo_cycle()
    print(
        {
            "state_id": result.state_id,
            "variables": result.variables,
            "forecast_ids": result.forecast_ids,
            "forecast_targets": tuple(item.isoformat() for item in result.forecast_targets),
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
