"""Validate and summarize the persistent CeutIA + SERPIENTE mission state.

This tool is intentionally dependency-free. It verifies the machine-readable
mission identity and required invariants; it does not claim that repository
state equals scientific validity.
"""

from __future__ import annotations

import json
from pathlib import Path

MISSION_DIR = Path(__file__).parent
STATE_PATH = MISSION_DIR / "CEUTIA_SERPIENTE_MISSION_STATE.json"
RECONCILIATION_PATH = MISSION_DIR / "STATE_RECONCILIATION_001.md"
CURRENT_RECONCILIATION_PATH = MISSION_DIR / "CURRENT_MISSION_RECONCILIATION.json"
REQUIRED_KEYS = {
    "schema_version", "mission_id", "mission_identity", "purpose", "scope",
    "architecture", "scientific_principles", "epistemology", "current_state",
    "current_capabilities", "limitations", "temporal_model", "system_model",
    "forecasting", "uncertainty", "early_warning", "prevention", "self_monitoring",
    "acquisition", "evaluation", "governance", "testing", "git_state_at_persistence",
    "authoritative_documents", "bibliography_map", "open_frontiers", "mission_loop",
    "closure_criteria", "replication",
}


def load_state(path: Path = STATE_PATH) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        state = json.load(handle)
    missing = sorted(REQUIRED_KEYS - state.keys())
    if missing:
        raise ValueError(f"Mission state missing required keys: {missing}")
    return state


def load_current_reconciliation(path: Path = CURRENT_RECONCILIATION_PATH) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate_state(state: dict) -> None:
    identity = state["mission_identity"]
    if identity["mission_type"] != "continuous_cumulative_autonomous_scientific_engineering":
        raise ValueError("Mission type is not continuous/cumulative/autonomous")
    if identity["not_a_new_phase"] is not True:
        raise ValueError("Mission continuity invariant is broken")
    if identity["premature_closure_forbidden"] is not True:
        raise ValueError("Premature-closure invariant is broken")

    principles = set(state["scientific_principles"])
    required = {
        "prediction != causation", "correlation != mechanism", "calibration != validity",
        "CI green != scientific validation", "implementation != effectiveness",
        "NOT_ESTABLISHED != NOT_IMPLEMENTABLE",
    }
    if not required.issubset(principles):
        raise ValueError("Core scientific boundary principles are incomplete")

    status = state["current_state"]
    if status["GLOBAL_ENGINEERING_AUDIT"] != "AUDIT_COMPLETE":
        raise ValueError("Unexpected engineering-audit state")
    if status["SCIENTIFIC_LIMITATION_RESOLUTION"] != "COMPLETE":
        raise ValueError("Unexpected scientific-limitation state")
    if status["PROSPECTIVE_PREDICTIVE_VALIDITY"] != "NOT_ESTABLISHED":
        raise ValueError("Unexpected prospective-validity state")

    loop = state["mission_loop"]
    if loop[:3] != ["RECONSTRUCT", "INTEGRATE", "DISCOVER"] or "PERSIST" not in loop:
        raise ValueError("Mission loop is incomplete")


def validate_repository_layout() -> None:
    for path in (RECONCILIATION_PATH, CURRENT_RECONCILIATION_PATH):
        if not path.exists():
            raise FileNotFoundError(f"Missing mission reconciliation artifact: {path}")


def validate_current_reconciliation(reconciliation: dict) -> None:
    if reconciliation["mission_id"] != "CEUTIA_SERPIENTE_CONTINUOUS_SCIENTIFIC_ENGINEERING":
        raise ValueError("Current reconciliation targets a different mission")
    response = reconciliation["corrections"]["response_coupling"]
    if response["status"] != "ACTIVE_FRONTIER":
        raise ValueError("Response-coupling frontier was incorrectly closed")
    if response["empirical_state"] != "NOT_ESTABLISHED":
        raise ValueError("Response-effectiveness empirical state was promoted")


def main() -> int:
    state = load_state()
    reconciliation = load_current_reconciliation()
    validate_state(state)
    validate_repository_layout()
    validate_current_reconciliation(reconciliation)
    print(f"MISSION_ID={state['mission_id']}")
    print(f"AGENT_ROLE={state['mission_identity']['agent_role']}")
    print(f"ENGINEERING_STATUS={state['current_state']['ENGINEERING_STATUS']}")
    print(f"SCIENTIFIC_LIMITATION_RESOLUTION={state['current_state']['SCIENTIFIC_LIMITATION_RESOLUTION']}")
    print(f"PROSPECTIVE_PREDICTIVE_VALIDITY={state['current_state']['PROSPECTIVE_PREDICTIVE_VALIDITY']}")
    print(f"OPEN_FRONTIERS={len(state['open_frontiers'])}")
    print("RESPONSE_COUPLING=ACTIVE_FRONTIER")
    print("MISSION_STATE=VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
