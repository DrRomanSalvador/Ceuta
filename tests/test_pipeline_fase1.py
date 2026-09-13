"""Deterministic tests for the CeutIA Phase 1 local event pipeline."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta, timezone
from hashlib import sha256

import pytest

from backend.app.core.pipeline.contracts import ObservationRecord
from backend.app.core.pipeline.pipeline import LocalDeterministicPipeline
from backend.app.core.pipeline.sources.synthetic import SyntheticSource


@pytest.mark.asyncio
async def test_phase1_observation_propagates_to_normalization_deterministically() -> None:
    source = SyntheticSource(
        start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
        values=(2.0,),
        available_delay=timedelta(seconds=7),
    )

    async with LocalDeterministicPipeline(source) as pipeline:
        records = await pipeline.run_once()

    assert len(records) == 1
    record = records[0]
    assert record.variable == "synthetic.signal"
    assert record.value == 2.0
    assert record.event_time == datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert record.available_at == datetime(2026, 1, 1, 0, 0, 7, tzinfo=timezone.utc)
    assert record.available_at >= record.event_time

    canonical = "|".join(
        (
            record.observation_id,
            record.variable,
            repr(record.value),
            record.unit or "",
            record.event_time.isoformat(),
            record.available_at.isoformat(),
            ",".join(record.source_ids),
            ",".join(record.evidence_ids),
            record.domain,
            repr(record.quality),
        )
    )
    assert record.provenance_hash == sha256(canonical.encode("utf-8")).hexdigest()


@pytest.mark.asyncio
async def test_phase1_rejects_observation_not_yet_available() -> None:
    source = SyntheticSource(
        start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
        values=(1.0,),
        available_delay=timedelta(seconds=10),
    )
    pipeline = LocalDeterministicPipeline(source)
    await pipeline.start()
    try:
        available_observation = next(source.records())
        assert available_observation.available_at == pipeline.normalization.evaluation_time

        future_observation = replace(
            available_observation,
            available_at=available_observation.available_at + timedelta(seconds=1),
        )
        assert future_observation.available_at > pipeline.normalization.evaluation_time
        with pytest.raises(ValueError, match="not available"):
            pipeline.normalization._normalize(future_observation)
    finally:
        await pipeline.stop()


def test_phase1_contract_rejects_future_availability_order() -> None:
    with pytest.raises(ValueError, match="cannot precede"):
        ObservationRecord(
            observation_id="test",
            variable="synthetic.signal",
            value=1.0,
            unit="index",
            event_time=datetime(2026, 1, 1, 0, 0, 10, tzinfo=timezone.utc),
            available_at=datetime(2026, 1, 1, 0, 0, 9, tzinfo=timezone.utc),
            source_ids=("synthetic:phase1",),
            evidence_ids=("synthetic:phase1:evidence:0",),
            domain="synthetic",
            quality=1.0,
            provenance_hash="placeholder",
        )
