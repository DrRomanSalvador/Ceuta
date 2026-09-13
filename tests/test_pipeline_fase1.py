"""Deterministic tests for the CeutIA Phase 1 local event pipeline."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256

import pytest

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
    pipeline.normalization.evaluation_time = source.start_time
    await pipeline.start()
    try:
        with pytest.raises(asyncio.TimeoutError):
            await asyncio.wait_for(pipeline.run_once(), timeout=0.2)
    finally:
        await pipeline.stop()
