"""Deterministic end-to-end tests for the CeutIA state stage."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from backend.app.core.pipeline.contracts import SystemStateContract
from backend.app.core.pipeline.pipeline import LocalDeterministicPipeline
from backend.app.core.pipeline.sources.synthetic import SyntheticSource


@pytest.mark.asyncio
async def test_phase2_state_propagates_end_to_end() -> None:
    source = SyntheticSource(
        start_time=datetime(2026, 1, 1, tzinfo=timezone.utc),
        values=(1.0, 1.5, 2.0),
        available_delay=timedelta(seconds=5),
    )

    async with LocalDeterministicPipeline(source) as pipeline:
        normalized, state = await pipeline.run_once_with_state()

    assert len(normalized) == 3
    assert isinstance(state, SystemStateContract)
    assert state.schema_version == "1.0"
    assert state.as_of == datetime(2026, 1, 1, 0, 2, 5, tzinfo=timezone.utc)
    assert state.observation_ids == tuple(item.observation_id for item in normalized)
    assert len(state.domains) == 1
    assert state.domains[0].domain == "synthetic"
    assert len(state.domains[0].variables) == 1

    variable = state.domains[0].variables[0]
    assert variable.variable == "synthetic.signal"
    assert variable.value == 2.0
    assert variable.previous_value == 1.5
    assert variable.observations == 3
    assert variable.velocity == pytest.approx((2.0 - 1.5) / 60.0)
    assert variable.acceleration == pytest.approx(0.0)


def test_phase2_state_contract_rejects_invalid_temporal_state() -> None:
    from backend.app.core.pipeline.contracts import DomainState, VariableState

    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc)
    variable = VariableState(
        variable="synthetic.signal",
        value=1.0,
        previous_value=None,
        velocity=None,
        acceleration=None,
        observations=1,
        updated_at=timestamp,
        evidence_ids=("synthetic:evidence:0",),
    )
    domain = DomainState(
        domain="synthetic",
        variables=(variable,),
        observation_ids=("observation-1",),
    )

    with pytest.raises(ValueError):
        from backend.app.core.pipeline.contracts import SystemStateContract

        SystemStateContract(
            state_id="state-invalid",
            as_of=datetime(2025, 12, 31, tzinfo=timezone.utc),
            domains=(domain,),
            interactions=(),
            interaction_effects=(),
            observation_ids=("observation-1",),
            schema_version="1.0",
        )
