from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256

import pytest

from app.core.epistemology_p0.advanced import Forecast, Observation
from app.core.pipeline.deduplication import EvidenceDeduplicator
from app.core.pipeline.sources.real_base import RealSourceEnvelope
from app.core.pipeline.sources.shadow_engine import ShadowEngine, TemporalLeakageError
from app.core.pipeline.stages.causality_guard import AssociationEvidence, CausalityGuard, InteractionStatus

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
        status="SHADOW_EVALUATION",
    )


def test_temporal_leakage_fails_closed() -> None:
    t0 = datetime(2026, 1, 1, tzinfo=UTC)
    observation = Observation("risk", 10.0, t0, t0 - timedelta(seconds=1), ("source-a",), ("e1",))
    with pytest.raises(TemporalLeakageError, match="cannot precede"):
        ShadowEngine.validate_temporal_boundary(observation)


def test_shadow_engine_uses_secondary_ledger_only() -> None:
    t0 = datetime(2026, 1, 1, tzinfo=UTC)
    cutoff = t0 + timedelta(hours=1)
    observations = (
        Observation("risk", 10.0, t0, t0 + timedelta(minutes=10), ("source-a",), ("e1",)),
        Observation("risk", 20.0, cutoff, cutoff + timedelta(minutes=20), ("source-a",), ("e2",)),
    )
    engine = ShadowEngine(model_version="shadow-test-v1")
    result = engine.execute(observations, cutoff_time=cutoff, forecast_fn=_forecast)
    assert result.record.status == "SHADOW_EVALUATION"
    assert result.record.point == 11.0
    assert engine.production_mutation_supported is False
    assert len(engine.ledger.records) == 1


def test_shadow_engine_rejects_forecast_target_before_cutoff() -> None:
    t0 = datetime(2026, 1, 1, tzinfo=UTC)
    observation = Observation("risk", 10.0, t0, t0, ("source-a",), ("e1",))

    def bad_forecast(observations: tuple[Observation, ...], *, cutoff_time: datetime) -> Forecast:
        return Forecast(
            forecast_id="bad",
            variable="risk",
            cutoff_time=cutoff_time,
            target_time=cutoff_time - timedelta(seconds=1),
            point=1.0,
            lower=0.0,
            upper=2.0,
            method="test",
            state_id="state",
            evidence_ids=("e1",),
            status="SHADOW_EVALUATION",
        )

    with pytest.raises(TemporalLeakageError, match="target"):
        ShadowEngine().execute((observation,), cutoff_time=t0, forecast_fn=bad_forecast)


def test_mirror_sources_do_not_inflate_independent_evidence() -> None:
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
    cluster = dedup.cluster(decision.cluster_id)
    assert cluster.canonical_source_id == "publisher-a"
    assert cluster.member_source_ids == ("publisher-a", "publisher-b")


def test_association_is_blocked_without_prospective_history() -> None:
    guard = CausalityGuard(min_prospective_evaluations=30)
    evidence = AssociationEvidence("migration", "health", 100, 29, 0.90, 0.20)
    decision = guard.evaluate(evidence)
    assert decision.status is InteractionStatus.OBSERVED_ASSOCIATION
    assert decision.allowed_in_scenarios is False


def test_prospective_support_is_not_causality() -> None:
    guard = CausalityGuard(min_prospective_evaluations=30)
    evidence = AssociationEvidence("migration", "health", 100, 30, 0.70, 0.10)
    decision = guard.evaluate(evidence)
    assert decision.status is InteractionStatus.PROSPECTIVELY_SUPPORTED
    assert decision.allowed_in_scenarios is True
    assert decision.status is not InteractionStatus.CAUSAL


def test_causality_guard_rejects_below_directional_threshold() -> None:
    guard = CausalityGuard(min_prospective_evaluations=30, min_directional_accuracy=0.60)
    evidence = AssociationEvidence("migration", "health", 100, 30, 0.59, 0.50)
    decision = guard.evaluate(evidence)
    assert decision.status is InteractionStatus.REJECTED
    assert decision.allowed_in_scenarios is False


def test_causality_guard_rejects_without_baseline_improvement() -> None:
    guard = CausalityGuard(min_prospective_evaluations=30, min_baseline_improvement=0.01)
    evidence = AssociationEvidence("migration", "health", 100, 30, 0.90, 0.00)
    decision = guard.evaluate(evidence)
    assert decision.status is InteractionStatus.REJECTED
    assert decision.allowed_in_scenarios is False
