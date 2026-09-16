from pathlib import Path

import pytest

from app.missions.registry import MissionRegistry, MissionRegistryError


REPOSITORY_ROOT = Path(__file__).resolve().parents[2]


def test_roman_is_discoverable_from_canonical_registry() -> None:
    registry = MissionRegistry(REPOSITORY_ROOT)

    mission = registry.get("ROMAN")

    assert mission["canonical_name"] == "ROMÁN"
    assert mission["mission_type"] == "AUTHORIAL_INTELLECTUAL_FORENSIC"
    assert mission["status"] == "ACTIVE"


def test_roman_contract_is_separate_from_engineering_and_scientific_missions() -> None:
    registry = MissionRegistry(REPOSITORY_ROOT)

    mission = registry.get("ROMAN")
    contract = registry.load_contract("ROMAN")

    assert mission["mission_id"] not in {"MISSION-01", "MISSION-02"}
    assert contract["mission_id"] == "ROMAN"
    assert "AUDIT" in contract["operations"]
    assert contract["model_generation_separation"]["generated_text_is_authentic_source"] is False


def test_roman_invocation_requires_authority_and_uses_contract_operation() -> None:
    registry = MissionRegistry(REPOSITORY_ROOT)

    envelope = registry.build_invocation(
        mission_id="ROMAN",
        operation="audit",
        request_id="test-request",
        session_id="test-session",
        requested_at="2026-09-16T10:00:00Z",
        authority_context={"CAN_INVOKE": True},
        input_refs=("source:test",),
        expected_output_type="ANALYSIS",
        base_state_version="state:test",
    )

    assert envelope.operation == "AUDIT"
    assert envelope.mission_id == "ROMAN"


def test_roman_invocation_fails_closed_without_invoke_authority() -> None:
    registry = MissionRegistry(REPOSITORY_ROOT)

    with pytest.raises(MissionRegistryError, match="CAN_INVOKE"):
        registry.build_invocation(
            mission_id="ROMAN",
            operation="AUDIT",
            request_id="test-request",
            session_id="test-session",
            requested_at="2026-09-16T10:00:00Z",
            authority_context={"CAN_INVOKE": False},
            input_refs=(),
            expected_output_type="ANALYSIS",
            base_state_version="state:test",
        )
