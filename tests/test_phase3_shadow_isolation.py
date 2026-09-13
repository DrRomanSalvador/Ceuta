from datetime import datetime, timedelta, timezone

import pytest

from app.core.epistemology_p0.advanced import Forecast, Observation
from app.core.pipeline.shadow_mode import ShadowModeExecutor
from app.core.pipeline.sources.shadow_engine import ShadowEngine, TemporalLeakageError

UTC = timezone.utc


def make_forecast(items, *, cutoff_time):
    assert items
    current = items[-1]
    return Forecast(
        forecast_id="phase3-test",
        variable=current.variable,
        cutoff_time=cutoff_time,
        target_time=cutoff_time + timedelta(hours=1),
        point=current.value + 1.0,
        lower=current.value,
        upper=current.value + 2.0,
        method="test",
        state_id="shadow",
        evidence_ids=current.evidence_ids,
        status="UNVERIFIED",
    )


def test_only_available_observations_reach_forecaster():
    t0 = datetime(2026, 1, 1, tzinfo=UTC)
    cutoff = t0 + timedelta(hours=1)
    observed = Observation("risk", 10.0, t0, t0 + timedelta(minutes=30), ("a",), ("e1",))
    future = Observation("risk", 100.0, t0, cutoff + timedelta(seconds=1), ("a",), ("e2",))
    seen = []

    def recorder(items, *, cutoff_time):
        seen.append(items)
        return make_forecast(items, cutoff_time=cutoff_time)

    result = ShadowEngine().execute((observed, future), cutoff_time=cutoff, forecast_fn=recorder)
    assert seen == [(observed,)]
    assert result.forecast.status == "SHADOW_EVALUATION"
    assert result.record.status == "SHADOW_EVALUATION"


def test_shadow_has_no_production_mutation_capability():
    engine = ShadowEngine()
    assert engine.production_mutation_supported is False
    assert not hasattr(engine, "promote")
    assert not hasattr(engine, "update_model")


def test_legacy_executor_uses_secondary_ledger():
    t0 = datetime(2026, 1, 1, tzinfo=UTC)
    executor = ShadowModeExecutor(model_version="phase3")
    forecast = executor.forecast(
        (Observation("risk", 10.0, t0, t0, ("a",), ("e1",)),),
        cutoff_time=t0,
        forecast_fn=make_forecast,
    )
    assert forecast.status == "SHADOW_EVALUATION"
    assert len(executor.ledger.records) == 1
    assert executor.production_mutation_supported is False


def test_invalid_temporal_observation_fails_closed():
    t0 = datetime(2026, 1, 1, tzinfo=UTC)
    invalid = Observation("risk", 10.0, t0, t0 - timedelta(seconds=1), ("a",), ("e1",))
    with pytest.raises(TemporalLeakageError, match="cannot precede"):
        ShadowEngine().execute((invalid,), cutoff_time=t0, forecast_fn=make_forecast)
