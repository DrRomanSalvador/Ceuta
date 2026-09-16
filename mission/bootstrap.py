"""Validate and summarize the persistent CeutIA + SERPIENTE mission state.

This validator is intentionally dependency-free. It verifies mission identity,
continuity invariants and the integrity of the persistent scientific-memory
layer. It does not claim that repository state equals scientific validity.
"""

from __future__ import annotations

import json
from pathlib import Path

MISSION_DIR = Path(__file__).parent
STATE_PATH = MISSION_DIR / "CEUTIA_SERPIENTE_MISSION_STATE.json"
MEMORY_PATH = MISSION_DIR / "SCIENTIFIC_MISSION_MEMORY.json"
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
MEMORY_REQUIRED_KEYS = {
    "schema_version", "mission_id", "purpose", "memory_principle", "identity",
    "reconstruction_order", "knowledge_domains", "concepts", "discovery_relationships",
    "decision_genealogy", "negative_knowledge", "capability_lineage", "scenario_memory",
    "method_gate", "mission_algorithm", "reconstruction_invariant", "closure_rule",
}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_state(path: Path = STATE_PATH) -> dict:
    state = load_json(path)
    missing = sorted(REQUIRED_KEYS - state.keys())
    if missing:
        raise ValueError(f"Mission state missing required keys: {missing}")
    return state


def load_memory(path: Path = MEMORY_PATH) -> dict:
    memory = load_json(path)
    missing = sorted(MEMORY_REQUIRED_KEYS - memory.keys())
    if missing:
        raise ValueError(f"Scientific mission memory missing required keys: {missing}")
    return memory


def load_current_reconciliation(path: Path = CURRENT_RECONCILIATION_PATH) -> dict:
    return load_json(path)


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


def validate_memory(memory: dict) -> None:
    if memory["mission_id"] != "CEUTIA_SERPIENTE_CONTINUOUS_SCIENTIFIC_ENGINEERING":
        raise ValueError("Scientific memory targets a different mission")
    identity = memory["identity"]
    if identity["mission_is_continuous"] is not True:
        raise ValueError("Scientific memory breaks mission continuity")
    if identity["maximum_knowledge_to_capability_is_not_a_phase"] is not True:
        raise ValueError("Maximum Knowledge-to-Capability was incorrectly persisted as a phase")
    if identity["premature_closure_forbidden"] is not True:
        raise ValueError("Scientific memory permits premature closure")

    concepts = {item["id"] for item in memory["concepts"]}
    if len(concepts) != len(memory["concepts"]):
        raise ValueError("Scientific memory contains duplicate concept IDs")
    for relation in memory["discovery_relationships"]:
        if relation["from"] not in concepts or relation["to"] not in concepts:
            raise ValueError("Discovery relationship references an unknown concept")

    if len(memory["decision_genealogy"]) < 5:
        raise ValueError("Decision genealogy is unexpectedly shallow")
    if len(memory["negative_knowledge"]) < 10:
        raise ValueError("Negative knowledge registry is unexpectedly shallow")
    if len(memory["discovery_relationships"]) < 10:
        raise ValueError("Scientific relationship graph is unexpectedly shallow")

    required_methods = {
        "SCIENTIFIC_NEED", "PHENOMENON", "DATA", "IDENTIFIABILITY",
        "ASSUMPTIONS", "IMPLEMENTABILITY", "TESTABILITY", "INCREMENTAL_VALUE",
    }
    if set(memory["method_gate"]) != required_methods:
        raise ValueError("Scientific method gate is incomplete")

    required_algorithm_prefix = ["RECONSTRUCT", "INTEGRATE", "DISCOVER"]
    if memory["mission_algorithm"][:3] != required_algorithm_prefix or "PERSIST" not in memory["mission_algorithm"]:
        raise ValueError("Persistent mission algorithm is incomplete")


def validate_repository_layout() -> None:
    for path in (MEMORY_PATH, RECONCILIATION_PATH, CURRENT_RECONCILIATION_PATH):
        if not path.exists():
            raise FileNotFoundError(f"Missing mission persistence artifact: {path}")


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
    memory = load_memory()
    reconciliation = load_current_reconciliation()
    validate_state(state)
    validate_memory(memory)
    validate_repository_layout()
    validate_current_reconciliation(reconciliation)
    print(f"MISSION_ID={state['mission_id']}")
    print(f"AGENT_ROLE={state['mission_identity']['agent_role']}")
    print(f"ENGINEERING_STATUS={state['current_state']['ENGINEERING_STATUS']}")
    print(f"SCIENTIFIC_LIMITATION_RESOLUTION={state['current_state']['SCIENTIFIC_LIMITATION_RESOLUTION']}")
    print(f"PROSPECTIVE_PREDICTIVE_VALIDITY={state['current_state']['PROSPECTIVE_PREDICTIVE_VALIDITY']}")
    print(f"PERSISTENT_CONCEPTS={len(memory['concepts'])}")
    print(f"PERSISTENT_RELATIONSHIPS={len(memory['discovery_relationships'])}")
    print(f"PERSISTENT_NEGATIVE_KNOWLEDGE={len(memory['negative_knowledge'])}")
    print(f"OPEN_FRONTIERS={len(state['open_frontiers'])}")
    print("RESPONSE_COUPLING=ACTIVE_FRONTIER")
    print("MISSION_STATE=VALID")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
