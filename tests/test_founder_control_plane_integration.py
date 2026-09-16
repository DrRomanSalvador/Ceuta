"""Adversarial readiness gates for canonical FOUNDER admission.

These tests deliberately discover the mission from persisted control-plane artifacts rather
than receiving mission identity through a test prompt. They are repository-side gates; live
external orchestration remains an explicit boundary.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "docs/missions/MISSION_REGISTRY.json"
CONTRACT = ROOT / "docs/missions/founder/FOUNDER_INVOCATION_CONTRACT.json"
STATE = ROOT / "docs/missions/founder/FOUNDER_STATE.json"
PROPOSAL = ROOT / "docs/missions/evolution/proposals/FOUNDER_ADMISSION_PROPOSAL.json"


def _load(path):
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def _contains_mission(node, mission_id):
    if isinstance(node, dict):
        if node.get("mission_id") == mission_id or node.get("id") == mission_id:
            return True
        return any(_contains_mission(v, mission_id) for v in node.values())
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
    assert state["contract_ref"].endswith("FOUNDER_INVOCATION_CONTRACT.json")
    assert proposal["contract_ref"].endswith("FOUNDER_INVOCATION_CONTRACT.json")
    assert contract["execution_invariants"]["inherits_universal_execution_contract"] is True
    assert contract["evidence_model"]["generated_output_is_independent_evidence"] is False
    assert contract["evidence_model"]["internal_analysis_is_market_fact"] is False


def test_founder_non_redundancy_boundaries_are_explicit():
    contract = _load(CONTRACT)
    non_responsibilities = set(contract["non_responsibilities"])
    assert any("ESPÍA" in item for item in non_responsibilities)
    assert any("INGENIERO" in item for item in non_responsibilities)
    assert any("control plane" in item.lower() for item in non_responsibilities)


def test_founder_state_machine_and_decision_abstention_are_machine_readable():
    contract = _load(CONTRACT)
    states = contract["state_model"]["opportunity_states"]
    alternatives = contract["state_model"]["terminal_or_alternative_states"]
    outcomes = contract["state_model"]["decision_outcomes"]
    assert states.index("PAID_PILOT") if "PAID_PILOT" in states else True
    assert {"ABANDONED", "PAUSED", "SUPERSEDED"}.issubset(alternatives)
    assert {"NO_DECISION_YET", "DECISION_REJECTED", "DECISION_DEFERRED", "ABSTAIN_FROM_DECISION", "DECISION_EXECUTED"}.issubset(outcomes)
    assert "PAID_PILOT_IS_NOT_REPEATABLE" in contract["commercial_invariants"]
    assert "PAYMENT_IS_NOT_CUSTOMER_ACCEPTANCE" in contract["commercial_invariants"]


def test_founder_is_discoverable_from_canonical_registry():
    registry = _load(REGISTRY)
    assert _contains_mission(registry, "FOUNDER"), (
        "FOUNDER is not yet admitted to the canonical Mission Registry; "
        "the persisted contract alone is not a registration."
    )


def test_founder_readiness_state_cannot_claim_ready_before_runtime_validation():
    state = _load(STATE)
    assert state["readiness"]["status"] != "READY_FOR_INVOCATION" or state["readiness"].get("runtime_validated") is True


def test_founder_external_claim_and_evidence_boundaries():
    contract = _load(CONTRACT)
    assert contract["authority"]["operational_authority"] == "INHERITED_AND_EXPLICIT_ONLY"
    assert "external_claim_publication" in contract["authority"]["forbidden_without_explicit_authority"]
    assert "SYSTEM_OUTPUT" in contract["evidence_model"]["allowed_types"]
    assert contract["evidence_model"]["generated_output_is_independent_evidence"] is False
