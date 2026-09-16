import json
from pathlib import Path

from app.missions.registry import MissionRegistry

ROOT = Path(__file__).resolve().parents[1]


def _contract():
    return json.loads((ROOT / "docs/missions/roman/ROMAN_INVOCATION_CONTRACT.json").read_text())


def test_roman_contract_declares_distinct_authority_capabilities_and_denies_authorization():
    authority = _contract()["authority"]
    required = {
        "can_read",
        "can_discover",
        "can_propose",
        "can_modify",
        "can_validate",
        "can_invoke",
        "can_authorize",
    }
    assert required.issubset(authority)
    assert authority["can_authorize"] is False
    assert authority["can_modify"] == "mission-scoped state only through authorized persistence protocol"
    assert authority["can_validate"] == "within authorial/intellectual domain only"


def test_roman_contract_preserves_conflicts_and_temporal_state_without_silent_resolution():
    contract = _contract()
    assert contract["temporal_model"] == "ROMAN(t)"
    assert "Preserve incompatible sources as contradiction records" in contract["conflict_policy"]
    assert "never average" in contract["conflict_policy"]
    assert "silently delete" in contract["conflict_policy"]
    assert "choose newer evidence automatically" in contract["conflict_policy"]


def test_roman_contract_explicitly_blocks_untraceable_and_global_identity_escalation():
    non_scope = set(_contract()["non_scope"])
    assert "untraceable memory as fact" in non_scope
    assert "global voice override" in non_scope
    assert "treating generated output as source evidence" in non_scope
    registry = MissionRegistry(ROOT)
    mission = registry.get("ROMAN")
    assert mission["mission_id"] == "ROMAN"
    assert mission["mission_type"] == "AUTHORIAL_INTELLECTUAL_FORENSIC"
