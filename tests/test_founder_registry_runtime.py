from pathlib import Path

import pytest

from app.missions.registry import MissionRegistry, MissionRegistryError

ROOT = Path(__file__).resolve().parents[1]


def test_founder_is_discoverable_and_inherits_universal_execution_contract():
    registry = MissionRegistry(ROOT)
    mission = registry.get("FOUNDER")
    assert mission["mission_id"] == "FOUNDER"
    contract = registry.load_contract("FOUNDER")
    assert contract["mission_id"] == "FOUNDER"
    assert contract["execution_inheritance"] == "MANDATORY"
    assert contract["non_weakening"] is True
    assert contract["universal_execution_contract"]


def test_founder_canonical_invocation_requires_can_invoke():
    registry = MissionRegistry(ROOT)
    envelope = registry.build_invocation(
        mission_id="FOUNDER", operation="DISCOVER", request_id="req-1", session_id="session-1",
        requested_at="2026-09-16T14:00:00+00:00", authority_context={"CAN_INVOKE": True},
        input_refs=("docs/missions/founder/MISSION_STATE.json",), expected_output_type="RESULT", base_state_version="1",
    )
    assert envelope.mission_id == "FOUNDER"
    assert envelope.operation == "DISCOVER"


def test_founder_invocation_denies_missing_authority():
    registry = MissionRegistry(ROOT)
    with pytest.raises(MissionRegistryError, match="CAN_INVOKE"):
        registry.build_invocation(
            mission_id="FOUNDER", operation="DISCOVER", request_id="req-2", session_id="session-2",
            requested_at="2026-09-16T14:00:00+00:00", authority_context={"CAN_INVOKE": False},
            input_refs=(), expected_output_type="RESULT", base_state_version="1",
        )
