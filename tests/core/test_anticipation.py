from datetime import UTC, datetime, timedelta

import pytest

from app.core.epistemology_p0.advanced import (
    ComplexSystemAnticipationEngine,
    DynamicSystemMonitor,
    Interaction,
    Observation,
)


T0 = datetime(2026, 9, 1, tzinfo=UTC)


def observation(variable: str, value: float, day: int, evidence: str) -> Observation:
    timestamp = T0 + timedelta(days=day)
    return Observation(
        variable=variable,
        value=value,
        event_time=timestamp,
        available_at=timestamp,
        source_ids=(f"source-{variable}",),
        evidence_ids=(evidence,),
    )


def test_cycle_builds_trajectory_and_forecasts() -> None:
    engine = ComplexSystemAnticipationEngine(
        DynamicSystemMonitor([Interaction("migration", "health_load", 0.5)])
    )
    state, forecasts = engine.cycle(
        [
            observation("migration", 10, 0, "m0"),
            observation("migration", 14, 1, "m1"),
            observation("health_load", 20, 0, "h0"),
            observation("health_load", 21, 1, "h1"),
        ],
        as_of=T0 + timedelta(days=1),
        forecast_horizon=timedelta(days=1),
    )
    assert state.state_id == engine.trajectory[0].state_id
    assert len(forecasts) == 2
    assert len(engine.ledger.entries) == 2
    assert all(item.validation_status == "PENDING_PROSPECTIVE_VALIDATION" for item in engine.ledger.entries)


def test_regime_assessment_is_not_a_probability() -> None:
    engine = ComplexSystemAnticipationEngine(DynamicSystemMonitor())
    engine.monitor.ingest(
        [
            observation("tension", 1.0, 0, "e0"),
            observation("tension", 1.1, 1, "e1"),
            observation("tension", 0.9, 2, "e2"),
            observation("tension", 1.2, 3, "e3"),
            observation("tension", 0.3, 4, "e4"),
            observation("tension", 2.0, 5, "e5"),
            observation("tension", -0.2, 6, "e6"),
            observation("tension", 2.4, 7, "e7"),
        ],
        evaluation_time=T0 + timedelta(days=7),
    )
    state = engine.monitor.snapshot(as_of=T0 + timedelta(days=7))
    assessment = engine.assess_regimes(state)[0]
    assert assessment.regime == "DYNAMIC_CHANGE_SIGNAL"
    assert assessment.status == "UNVERIFIED"
    assert 0.0 <= assessment.score <= 1.0


def test_ledger_refuses_premature_resolution() -> None:
    engine = ComplexSystemAnticipationEngine(DynamicSystemMonitor())
    _, forecasts = engine.cycle(
        [observation("pressure", 10, 0, "e0"), observation("pressure", 12, 1, "e1")],
        as_of=T0 + timedelta(days=1),
        forecast_horizon=timedelta(days=2),
    )
    with pytest.raises(ValueError, match="before target_time"):
        engine.ledger.resolve(
            forecasts[0].forecast_id,
            realized_value=15,
            resolved_at=T0 + timedelta(days=2),
        )


def test_ledger_scores_only_after_target_time() -> None:
    engine = ComplexSystemAnticipationEngine(DynamicSystemMonitor())
    _, forecasts = engine.cycle(
        [observation("pressure", 10, 0, "e0"), observation("pressure", 12, 1, "e1")],
        as_of=T0 + timedelta(days=1),
        forecast_horizon=timedelta(days=1),
    )
    entry = engine.ledger.resolve(
        forecasts[0].forecast_id,
        realized_value=15,
        resolved_at=T0 + timedelta(days=2),
    )
    assert entry.validation_status == "SCORED_NOT_CALIBRATED"
    assert entry.forecast.realized_value == 15
    assert entry.forecast.score is not None
