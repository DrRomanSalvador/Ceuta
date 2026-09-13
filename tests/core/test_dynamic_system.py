from datetime import UTC, datetime, timedelta

import pytest

from app.core.epistemology_p0.advanced.dynamic_system import (
    DynamicSystemMonitor,
    Interaction,
    Observation,
)


T0 = datetime(2026, 9, 1, tzinfo=UTC)


def obs(variable: str, value: float, day: int, evidence: str) -> Observation:
    timestamp = T0 + timedelta(days=day)
    return Observation(
        variable=variable,
        value=value,
        event_time=timestamp,
        available_at=timestamp,
        source_ids=(f"source-{variable}",),
        evidence_ids=(evidence,),
    )


def test_future_information_is_blocked() -> None:
    monitor = DynamicSystemMonitor()
    future = obs("migration_pressure", 10, 2, "ev-future")
    with pytest.raises(ValueError, match="future information leak"):
        monitor.ingest([future], evaluation_time=T0)


def test_state_contains_velocity_and_evidence_trace() -> None:
    monitor = DynamicSystemMonitor()
    monitor.ingest(
        [obs("migration_pressure", 10, 0, "ev-1"), obs("migration_pressure", 14, 1, "ev-2")],
        evaluation_time=T0 + timedelta(days=1),
    )
    state = monitor.snapshot(as_of=T0 + timedelta(days=1))
    variable = state.variable("migration_pressure")
    assert variable.value == 14
    assert variable.velocity == 4 / 86400
    assert variable.evidence_ids == ("ev-1", "ev-2")


def test_cross_domain_interaction_enters_state_and_forecast() -> None:
    monitor = DynamicSystemMonitor([Interaction("migration_pressure", "health_load", 0.5)])
    monitor.ingest(
        [
            obs("migration_pressure", 10, 0, "ev-m1"),
            obs("migration_pressure", 14, 1, "ev-m2"),
            obs("health_load", 20, 0, "ev-h1"),
            obs("health_load", 21, 1, "ev-h2"),
        ],
        evaluation_time=T0 + timedelta(days=1),
    )
    state = monitor.snapshot(as_of=T0 + timedelta(days=1))
    assert len(state.interaction_effects) == 1
    effect = state.interaction_effects[0]
    assert effect.upstream == "migration_pressure"
    assert effect.downstream == "health_load"
    assert effect.status == "UNVERIFIED"
    forecast = monitor.forecast(variable="health_load", horizon=timedelta(days=1), state=state)
    assert forecast.method == "velocity_baseline_plus_association_coupling"
    assert forecast.point > 21


def test_forecast_is_explicitly_unverified_and_traceable() -> None:
    monitor = DynamicSystemMonitor([Interaction("migration_pressure", "health_load", 0.7)])
    monitor.ingest(
        [
            obs("migration_pressure", 10, 0, "ev-1"),
            obs("migration_pressure", 12, 1, "ev-2"),
            obs("migration_pressure", 15, 2, "ev-3"),
        ],
        evaluation_time=T0 + timedelta(days=2),
    )
    state = monitor.snapshot(as_of=T0 + timedelta(days=2))
    forecast = monitor.forecast(
        variable="migration_pressure",
        horizon=timedelta(days=1),
        state=state,
    )
    assert forecast.status == "UNVERIFIED"
    assert forecast.method == "velocity_baseline_plus_association_coupling"
    assert forecast.state_id == state.state_id
    assert forecast.cutoff_time == state.as_of
    assert forecast.evidence_ids == ("ev-1", "ev-2", "ev-3")


def test_forecast_can_be_closed_loop_scored() -> None:
    monitor = DynamicSystemMonitor()
    monitor.ingest(
        [obs("pressure", 10, 0, "ev-1"), obs("pressure", 12, 1, "ev-2")],
        evaluation_time=T0 + timedelta(days=1),
    )
    state = monitor.snapshot(as_of=T0 + timedelta(days=1))
    forecast = monitor.forecast(variable="pressure", horizon=timedelta(days=1), state=state)
    resolved = monitor.resolve_forecast(forecast.forecast_id, realized_value=15)
    assert resolved.realized_value == 15
    assert resolved.score is not None
    assert resolved.score >= 0


def test_early_warning_does_not_claim_tipping_point() -> None:
    monitor = DynamicSystemMonitor()
    observations = [
        obs("social_tension", 1.0, 0, "e0"),
        obs("social_tension", 1.1, 1, "e1"),
        obs("social_tension", 0.9, 2, "e2"),
        obs("social_tension", 1.2, 3, "e3"),
        obs("social_tension", 0.3, 4, "e4"),
        obs("social_tension", 2.0, 5, "e5"),
        obs("social_tension", -0.2, 6, "e6"),
        obs("social_tension", 2.4, 7, "e7"),
    ]
    monitor.ingest(observations, evaluation_time=T0 + timedelta(days=7))
    state = monitor.snapshot(as_of=T0 + timedelta(days=7))
    assert state.early_warnings
    assert any("increasing_variance" in warning.indicators for warning in state.early_warnings)
    assert all("tipping-point prediction" in warning.interpretation for warning in state.early_warnings)
