from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256

import pytest

from app.core.epistemology_p0.advanced import Forecast, Observation
from app.core.pipeline.shadow_metrics import compute_shadow_gap
from app.core.pipeline.shadow_mode import ShadowModeExecutor
from app.core.pipeline.sources.deduplication import EvidenceDeduplicator
from app.core.pipeline.sources.real_base import RealSourceEnvelope, SourceObservation
from app.core.pipeline.stages.causality_guard import (
    AssociationEvidence,
    CausalityGuard,
    InteractionStatus,
)

UTC = timezone.utc


def _forecast(observations: tuple[Observation, ...], *, cutoff_time: datetime) -> Forecast:
    assert observations
    current = observations[-1]
    return Forecast(
        forecast_id=f"forecast-{cutoff_time.timestamp()}",
        variable=current.variable,
        cutoff_time=cutoff_time,
        target_time=cutoff_time + timedelta(hours=1),
        point=current.value + 1.0,
        lower=current.value,
        upper=current.value + 2.0,
        method="shadow-test",
        state_id="shadow-state",
        evidence_ids=current.evidence_ids,
        status="UNVERIFIED",
    )


def test_shadow_mode_respects_available_at_and_never_promotes() -> None:
    t0 = datetime(2026, 1, 1, tzinfo=UTC)
    cutoff = t0 + timedelta(hours=1)
    observations = (
        Observation("risk", 10.0, t0, t0 + timedelta(minutes=10), ("source-a",), ("e1",)),
        Observation("risk", 20.0, cutoff, cutoff + timedelta(minutes=20), ("source-a",), ("e2",)),
    )
    executor = ShadowModeExecutor(model_version="shadow-test-v1")

    forecast = executor.forecast(observations, cutoff_time=cutoff, forecast_fn=_forecast)

    assert forecast.status == "SHADOW_EVALUATION"
    assert forecast.point == 21.0
    assert executor.production_mutation_supported is False
    assert all(item.forecast.status == "SHADOW_EVALUATION" for item in executor.ledger.entries)

    with pytest.raises(ValueError, match="before target_time"):
        executor.resolve(
            forecast.forecast_id,
            realized_value=22.0,
            resolved_at=forecast.target_time - timedelta(seconds=1),
            baseline_prediction=20.0,
        )

    evaluation = executor.resolve(
        forecast.forecast_id,
        realized_value=22.0,
        resolved_at=forecast.target_time,
        baseline_prediction=20.0,
    )
    assert evaluation.squared_error == 1.0
    assert executor.production_mutation_supported is False


def test_shadow_metrics_measure_gap_against_baseline() -> None:
    t0 = datetime(2026, 1, 1, tzinfo=UTC)
    executor = ShadowModeExecutor(model_version="shadow-test-v1")
    observations = (
        Observation("risk", 10.0, t0, t0, ("source-a",), ("e1",)),
        Observation("risk", 11.0, t0 + timedelta(hours=1), t0 + timedelta(hours=1), ("source-a",), ("e2",)),
    )
    forecast = executor.forecast(observations, cutoff_time=t0 + timedelta(hours=1), forecast_fn=_forecast)
    executor.resolve(
        forecast.forecast_id,
        realized_value=13.0,
        resolved_at=forecast.target_time,
        baseline_prediction=12.0,
    )
    report = compute_shadow_gap(executor.evaluations)
    assert report.sample_size == 1
    assert report.model_mse == 1.0
    assert report.baseline_mse == 1.0
    assert report.mse_gap == 0.0


def test_association_cannot_become_causal_without_prospective_history() -> None:
    guard = CausalityGuard(min_prospective_evaluations=30)
    evidence = AssociationEvidence(
        upstream="migration",
        downstream="health",
        observations=100,
        prospective_evaluations=29,
        directional_accuracy=0.90,
        baseline_improvement=0.20,
    )
    decision = guard.evaluate(evidence)
    assert decision.status is InteractionStatus.OBSERVED_ASSOCIATION
    assert decision.allowed_in_scenarios is False


def test_prospective_support_allows_scenario_influence_but_not_causal_label() -> None:
    guard = CausalityGuard(min_prospective_evaluations=30)
    evidence = AssociationEvidence(
        upstream="migration",
        downstream="health",
        observations=100,
        prospective_evaluations=30,
        directional_accuracy=0.70,
        baseline_improvement=0.10,
    )
    decision = guard.evaluate(evidence)
    assert decision.status is InteractionStatus.PROSPECTIVELY_SUPPORTED
    assert decision.allowed_in_scenarios is True
    assert "causal" in decision.reason


def test_real_source_preserves_temporal_boundary_and_mirror_deduplication() -> None:
    t0 = datetime(2026, 1, 1, tzinfo=UTC)
    payload = b"same-source-event"
    digest = sha256(payload).hexdigest()
    first = RealSourceEnvelope(
        source_id="publisher-a",
        source_kind="feed",
        canonical_uri="https://a.example/feed",
        fetched_at=t0 + timedelta(minutes=30),
        payload=payload,
        content_hash=digest,
        event_time=t0,
    )
    mirror = RealSourceEnvelope(
        source_id="publisher-b",
        source_kind="feed",
        canonical_uri="https://b.example/feed",
        fetched_at=t0 + timedelta(hours=1),
        payload=payload,
        content_hash=digest,
        event_time=t0,
        upstream_source_id="publisher-a",
    )
    dedup = EvidenceDeduplicator()
    assert dedup.register_envelope(first).independent is True
    decision = dedup.register_envelope(mirror)
    assert decision.independent is False
    assert decision.reason == "exact_payload_duplicate"

    observation = SourceObservation(
        variable="risk",
        value=1.0,
        event_time=t0,
        available_at=t0 + timedelta(hours=1),
        domain="social",
        source_id="publisher-a",
        evidence_id="e1",
        provenance_hash=digest,
    )
    record = observation.to_record()
    assert record.event_time == t0
    assert record.available_at > record.event_time
