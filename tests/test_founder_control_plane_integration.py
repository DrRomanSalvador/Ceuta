"""Adversarial readiness gates for canonical FOUNDER admission."""
import json
from pathlib import Path

from app.missions.founder_domain import DECISION_OUTCOMES

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/missions/MISSION_REGISTRY.json"
CONTRACT = ROOT / "docs/missions/founder/INVOCATION_CONTRACT.json"
STATE = ROOT / "docs/missions/founder/MISSION_STATE.json"
PROPOSAL = ROOT / "docs/missions/evolution/proposals/FOUNDER_ADMISSION_PROPOSAL.json"


def _load(path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _contains_mission(node, mission_id):
    if isinstance(node, dict):
        return node.get("mission_id") == mission_id or any(_contains_mission(v, mission_id) for v in node.values())
    if isinstance(node, list):
        return any(_contains_mission(v, mission_id) for v in node)
    return False


def test_founder_artifacts_are_canonical_and_self_consistent():
    contract = _load(CONTRACT)
    state = _load(STATE)
    proposal = _load(PROPOSAL)
    assert contract["mission_id"] == "FOUNDER"
    assert state["mission_id"] == "FOUNDER"
    assert proposal["mission_id"] == "FOUNDER"
    assert state["provenance_required"] is True
    assert contract["invocation_contract"] == "docs/missions/founder/INVOCATION_CONTRACT.json"
    assert contract["state_location"] == "docs/missions/founder/MISSION_STATE.json"
    assert contract["evidence_location"] == "docs/missions/founder/EVIDENCE.json"
    assert contract["limitations"] == ["Must remain within the approved proposal scope.", "Generated output is not evidence."]


def test_founder_non_redundancy_boundaries_are_explicit():
    non_scope = set(_load(CONTRACT)["non_scope"])
    assert "scientific evidence generation" in non_scope
    assert "general engineering execution" in non_scope
    assert "global mission orchestration" in non_scope


def test_founder_decision_abstention_and_commercial_boundaries_are_machine_readable():
    assert {"NO_DECISION_YET", "DECISION_REJECTED", "DECISION_DEFERRED", "ABSTAIN_FROM_DECISION", "DECISION_EXECUTED"}.issubset(DECISION_OUTCOMES)
    contract = _load(CONTRACT)
    assert contract["operations"] == ["DISCOVER", "INVOKE", "EXECUTE", "VALIDATE", "HANDOFF", "PERSIST", "REVIEW", "RETIRE"]
    assert "Generated output is not evidence." in contract["limitations"]


def test_founder_is_discoverable_from_canonical_registry():
    assert _contains_mission(_load(REGISTRY), "FOUNDER")


def test_founder_readiness_state_cannot_claim_ready_before_runtime_validation():
    assert _load(STATE)["readiness"] != "READY_FOR_INVOCATION"


def test_founder_external_claim_and_evidence_boundaries():
    contract = _load(CONTRACT)
    assert contract["authority"]["CAN_AUTHORIZE"] is False
    assert contract["authority"]["CAN_MODIFY"] is False
    assert "Generated output is not evidence." in contract["limitations"]
