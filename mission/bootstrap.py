"""Validate and summarize the persistent CeutIA + SERPIENTE mission state.

The bootstrap is fail-closed for control-plane invariants. It validates the
scientific mission memory and the executable multi-mission control-plane layer;
it does not equate repository consistency with scientific validity.
"""
from __future__ import annotations

import json
from pathlib import Path

MISSION_DIR = Path(__file__).parent
STATE_PATH = MISSION_DIR / "CEUTIA_SERPIENTE_MISSION_STATE.json"
MEMORY_PATH = MISSION_DIR / "SCIENTIFIC_MISSION_MEMORY.json"
RECONCILIATION_PATH = MISSION_DIR / "STATE_RECONCILIATION_001.md"
CURRENT_RECONCILIATION_PATH = MISSION_DIR / "CURRENT_MISSION_RECONCILIATION.json"
CONTROL_PLANE_STATE_PATH = MISSION_DIR / "MISSION_CONTROL_PLANE_STATE.json"
STATE_MACHINE_PATH = MISSION_DIR / "MISSION_STATE_MACHINE.json"
HANDOFF_REGISTRY_PATH = MISSION_DIR / "MISSION_HANDOFF_REGISTRY.json"
REGISTRY_PATH = MISSION_DIR / "MISSION_REGISTRY.json"
QUEUE_PATH = MISSION_DIR / "AUTONOMOUS_WORK_QUEUE.json"
REQUIRED_KEYS = {"schema_version","mission_id","mission_identity","purpose","scope","architecture","scientific_principles","epistemology","current_state","current_capabilities","limitations","temporal_model","system_model","forecasting","uncertainty","early_warning","prevention","self_monitoring","acquisition","evaluation","governance","testing","git_state_at_persistence","authoritative_documents","bibliography_map","open_frontiers","mission_loop","closure_criteria","replication"}
MEMORY_REQUIRED_KEYS = {"schema_version","mission_id","purpose","memory_principle","identity","reconstruction_order","knowledge_domains","concepts","discovery_relationships","decision_genealogy","negative_knowledge","capability_lineage","scenario_memory","method_gate","mission_algorithm","reconstruction_invariant","closure_rule"}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle: return json.load(handle)


def load_state(path: Path = STATE_PATH) -> dict:
    state=load_json(path); missing=sorted(REQUIRED_KEYS-state.keys())
    if missing: raise ValueError(f"Mission state missing required keys: {missing}")
    return state


def load_memory(path: Path = MEMORY_PATH) -> dict:
    memory=load_json(path); missing=sorted(MEMORY_REQUIRED_KEYS-memory.keys())
    if missing: raise ValueError(f"Scientific mission memory missing required keys: {missing}")
    return memory


def load_current_reconciliation(path: Path = CURRENT_RECONCILIATION_PATH) -> dict: return load_json(path)


def validate_state(state: dict) -> None:
    identity=state["mission_identity"]
    if identity["mission_type"]!="continuous_cumulative_autonomous_scientific_engineering": raise ValueError("Mission type is not continuous/cumulative/autonomous")
    if identity["not_a_new_phase"] is not True or identity["premature_closure_forbidden"] is not True: raise ValueError("Mission continuity invariant is broken")
    principles=set(state["scientific_principles"]); required={"prediction != causation","correlation != mechanism","calibration != validity","CI green != scientific validation","implementation != effectiveness","NOT_ESTABLISHED != NOT_IMPLEMENTABLE"}
    if not required.issubset(principles): raise ValueError("Core scientific boundary principles are incomplete")
    status=state["current_state"]
    if status["GLOBAL_ENGINEERING_AUDIT"]!="AUDIT_COMPLETE" or status["SCIENTIFIC_LIMITATION_RESOLUTION"]!="COMPLETE" or status["PROSPECTIVE_PREDICTIVE_VALIDITY"]!="NOT_ESTABLISHED": raise ValueError("Unexpected scientific/engineering state promotion")
    if state["mission_loop"][:3]!=["RECONSTRUCT","INTEGRATE","DISCOVER"] or "PERSIST" not in state["mission_loop"]: raise ValueError("Mission loop is incomplete")


def validate_memory(memory: dict) -> None:
    if memory["mission_id"]!="CEUTIA_SERPIENTE_CONTINUOUS_SCIENTIFIC_ENGINEERING": raise ValueError("Scientific memory targets a different mission")
    identity=memory["identity"]
    if not identity["mission_is_continuous"] or identity["maximum_knowledge_to_capability_is_not_a_phase"] is not True or identity["premature_closure_forbidden"] is not True: raise ValueError("Scientific memory breaks continuity")
    concepts={item["id"] for item in memory["concepts"]}
    if len(concepts)!=len(memory["concepts"]): raise ValueError("Duplicate scientific concept IDs")
    for relation in memory["discovery_relationships"]:
        if relation["from"] not in concepts or relation["to"] not in concepts: raise ValueError("Discovery relationship references unknown concept")
    if len(memory["decision_genealogy"])<5 or len(memory["negative_knowledge"])<10 or len(memory["discovery_relationships"])<10: raise ValueError("Scientific memory is unexpectedly shallow")
    required_methods={"SCIENTIFIC_NEED","PHENOMENON","DATA","IDENTIFIABILITY","ASSUMPTIONS","IMPLEMENTABILITY","TESTABILITY","INCREMENTAL_VALUE"}
    if set(memory["method_gate"])!=required_methods: raise ValueError("Scientific method gate is incomplete")
    if memory["mission_algorithm"][:3]!=["RECONSTRUCT","INTEGRATE","DISCOVER"] or "PERSIST" not in memory["mission_algorithm"]: raise ValueError("Persistent mission algorithm is incomplete")


def validate_repository_layout() -> None:
    for path in (MEMORY_PATH,RECONCILIATION_PATH,CURRENT_RECONCILIATION_PATH,CONTROL_PLANE_STATE_PATH,STATE_MACHINE_PATH,HANDOFF_REGISTRY_PATH,REGISTRY_PATH,QUEUE_PATH):
        if not path.exists(): raise FileNotFoundError(f"Missing mission persistence artifact: {path}")


def validate_current_reconciliation(reconciliation: dict) -> None:
    if reconciliation["mission_id"]!="CEUTIA_SERPIENTE_CONTINUOUS_SCIENTIFIC_ENGINEERING": raise ValueError("Current reconciliation targets a different mission")
    response=reconciliation["corrections"]["response_coupling"]
    if response["status"]!="ACTIVE_FRONTIER" or response["empirical_state"]!="NOT_ESTABLISHED": raise ValueError("Response-coupling frontier was incorrectly closed")


def validate_control_plane() -> dict:
    try:
        from .control_plane import ControlPlaneContract, HandoffState, MissionState, validate_handoff, validate_waiting_policy, validate_mission_contract
    except ImportError:
        from control_plane import ControlPlaneContract, HandoffState, MissionState, validate_handoff, validate_waiting_policy, validate_mission_contract
    cp=load_json(CONTROL_PLANE_STATE_PATH); sm=load_json(STATE_MACHINE_PATH); hr=load_json(HANDOFF_REGISTRY_PATH); registry=load_json(REGISTRY_PATH); queue=load_json(QUEUE_PATH)
    ControlPlaneContract().validate_distinctions()
    if cp["status"] not in {"PARTIALLY_VALIDATED","VALIDATED"}: raise ValueError("Invalid control-plane global status")
    if sm["mission_state_machine"]["states"] != [s.value for s in MissionState]: raise ValueError("Persisted mission state machine differs from executable state machine")
    for handoff in hr["items"]: validate_handoff(handoff)
    for item in queue["items"]: validate_waiting_policy(item)
    for mission in cp["missions"]: validate_mission_contract(mission)
    if len(cp["missions"]) != cp["mission_registry_source_evidence"]["mission_count_evidenced_in_source"]: raise ValueError("Control-plane mission projection count mismatch")
    if registry["discovery_status"]=="COMPLETE" and registry.get("repository_verified_mission_count") != len(cp["missions"]): raise ValueError("Legacy registry falsely claims complete discovery")
    return {"mission_count":len(cp["missions"]),"handoff_count":len(hr["items"]),"queue_count":len(queue["items"]),"status":cp["status"]}


def main() -> int:
    state=load_state(); memory=load_memory(); reconciliation=load_current_reconciliation(); validate_state(state); validate_memory(memory); validate_repository_layout(); validate_current_reconciliation(reconciliation); cp=validate_control_plane()
    print(f"MISSION_ID={state['mission_id']}"); print(f"AGENT_ROLE={state['mission_identity']['agent_role']}"); print(f"ENGINEERING_STATUS={state['current_state']['ENGINEERING_STATUS']}"); print(f"SCIENTIFIC_LIMITATION_RESOLUTION={state['current_state']['SCIENTIFIC_LIMITATION_RESOLUTION']}"); print(f"PROSPECTIVE_PREDICTIVE_VALIDITY={state['current_state']['PROSPECTIVE_PREDICTIVE_VALIDITY']}"); print(f"PERSISTENT_CONCEPTS={len(memory['concepts'])}"); print(f"PERSISTENT_RELATIONSHIPS={len(memory['discovery_relationships'])}"); print(f"PERSISTENT_NEGATIVE_KNOWLEDGE={len(memory['negative_knowledge'])}"); print(f"OPEN_FRONTIERS={len(state['open_frontiers'])}"); print(f"CONTROL_PLANE={cp['status']}"); print(f"CONTROL_PLANE_MISSIONS={cp['mission_count']}"); print(f"CONTROL_PLANE_HANDOFFS={cp['handoff_count']}"); print("RESPONSE_COUPLING=ACTIVE_FRONTIER"); print("MISSION_STATE=VALID"); return 0

if __name__=="__main__": raise SystemExit(main())
