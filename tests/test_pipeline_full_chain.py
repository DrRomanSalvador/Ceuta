import asyncio
from datetime import UTC, datetime, timedelta

import pytest

from app.core.epistemology_p0.advanced import (
    ComplexSystemAnticipationEngine,
    DynamicSystemMonitor,
    Interaction,
    Observation,
)
from app.core.pipeline.pipeline import LocalDeterministicPipeline
from app.core.pipeline.sources.synthetic import SyntheticSource
from app.core.pipeline.validation import ClosedLoopCalibrator
from app.validation.circuit_breaker import CalibrationCircuitBreaker


T0 = datetime(2026, 9, 1, tzinfo=UTC)


def test_full_chain_ingestion_to_recalibration() -> None:
    source = SyntheticSource(
        start_time=T0,
        available_delay=timedelta(0),
        values=(1.0, 1.5, 2.0, 2.5, 3.0),
    )

    async def run_pipeline() -> tuple[object, object]:
        async with LocalDeterministicPipeline(source) as pipeline:
            return await pipeline.run_once_with_state()

    normalized, normalized_state = asyncio.run(run_pipeline())
    assert len(normalized) == 5
    assert normalized_state.observation_ids == tuple(
        item.observation_id for item in normalized
    )

    observations = [
        Observation(
            "migration",
            10 + index,
            T0 + timedelta(days=index),
            T0 + timedelta(days=index),
            ("src-m",),
            (f"m{index}",),
        )
        for index in range(4)
    ] + [
        Observation(
            "health_load",
            20 + index,
            T0 + timedelta(days=index),
            T0 + timedelta(days=index),
            ("src-h",),
            (f"h{index}",),
        )
        for index in range(4)
    ]

    engine = ComplexSystemAnticipationEngine(
        DynamicSystemMonitor([Interaction("migration", "health_load", 0.5)])
    )
    state, forecasts = engine.cycle(
        observations,
        as_of=T0 + timedelta(days=3),
        forecast_horizon=timedelta(days=1),
    )
    assert state.interaction_effects
    assert forecasts

    scenarios = engine.assess_regimes(state)
    assert scenarios
    assert all(item.status == "UNVERIFIED" for item in scenarios)

    forecast = forecasts[0]
    calibrator = ClosedLoopCalibrator(
        CalibrationCircuitBreaker(min_sample_size=1, max_degradation=1.0),
        active_model_version="baseline-v1",
    )
    calibrator.register(forecast, baseline_prediction=0.0)

    with pytest.raises(ValueError, match="before target_time"):
        calibrator.resolve(
            forecast.forecast_id,
            realized_value=forecast.point,
            resolved_at=forecast.target_time - timedelta(seconds=1),
            candidate_model_version="candidate-v2",
        )

    decision = calibrator.resolve(
        forecast.forecast_id,
        realized_value=forecast.point,
        resolved_at=forecast.target_time,
        sample_size=1,
        candidate_model_version="candidate-v2",
    )
    assert decision.promoted is True
    assert decision.active_model_version == "candidate-v2"
    assert decision.report.mse == 0.0
    assert len(calibrator.reports) == 1
