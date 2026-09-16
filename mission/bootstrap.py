"""Fail-closed bootstrap for the persistent scientific and multi-mission state."""
from __future__ import annotations
import json
from pathlib import Path

MISSION_DIR=Path(__file__).parent
STATE_PATH=MISSION_DIR/"CEUTIA_SERPIENTE_MISSION_STATE.json"; MEMORY_PATH=MISSION_DIR/"SCIENTIFIC_MISSION_MEMORY.json"
RECONCILIATION_PATH=MISSION_DIR/"STATE_RECONCILIATION_001.md"; CURRENT_RECONCILIATION_PATH=MISSION_DIR/"CURRENT_MISSION_RECONCILIATION.json"
CONTROL_PLANE_STATE_PATH=MISSION_DIR/"MISSION_CONTROL_PLANE_STATE.json"; STATE_MACHINE_PATH=MISSION_DIR/"MISSION_STATE_MACHINE.json"
HANDOFF_REGISTRY_PATH=MISSION_DIR/"MISSION_HANDOFF_REGISTRY.json"; REGISTRY_PATH=MISSION_DIR/"MISSION_REGISTRY.json"; QUEUE_PATH=MISSION_DIR/"AUTONOMOUS_WORK_QUEUE.json"; EVENT_LOG_PATH=MISSION_DIR/"MISSION_EVENT_LOG.jsonl"
CONSTITUTION_PATH=MISSION_DIR/"MISSION_SYSTEM_CONSTITUTION.md"; SHARED_STANDARD_PATH=MISSION_DIR/"shared_standard.py"
REQUIRED_KEYS={"schema_version","mission_id","mission_identity","purpose","scope","architecture","scientific_principles","epistemology","current_state","current_capabilities","limitations","temporal_model","system_model","forecasting","uncertainty","early_warning","prevention","self_monitoring","acquisition","evaluation","governance","testing","git_state_at_persistence","authoritative_documents","bibliography_map","open_frontiers","mission_loop","closure_criteria","replication"}
MEMORY_REQUIRED_KEYS={"schema_version","mission_id","purpose","memory_principle","identity","reconstruction_order","knowledge_domains","concepts","discovery_relationships","decision_genealogy","negative_knowledge","capability_lineage","scenario_memory","method_gate","mission_algorithm","reconstruction_invariant","closure_rule"}

def load_json(path:Path)->dict:
    with path.open("r",encoding="utf-8") as h:return json.load(h)

def load_state(path:Path=STATE_PATH)->dict:
    s=load_json(path); m=sorted(REQUIRED_KEYS-s.keys())
    if m: raise ValueError(f"Mission state missing required keys: {m}")
    return s

def load_memory(path:Path=MEMORY_PATH)->dict:
    m=load_json(path); missing=sorted(MEMORY_REQUIRED_KEYS-m.keys())
    if missing: raise ValueError(f"Scientific mission memory missing required keys: {missing}")
    return m

def load_current_reconciliation(path:Path=CURRENT_RECONCILIATION_PATH)->dict:return load_json(path)

def validate_state(state):
    i=state["mission_identity"]
    if i["mission_type"]!="continuous_cumulative_autonomous_scientific_engineering" or i["not_a_new_phase"] is not True or i["premature_closure_forbidden"] is not True: raise ValueError("Mission continuity invariant is broken")
    required={"prediction != causation","correlation != mechanism","calibration != validity","CI green != scientific validation","implementation != effectiveness","NOT_ESTABLISHED != NOT_IMPLEMENTABLE"}
    if not required.issubset(set(state["scientific_principles"])): raise ValueError("Core scientific boundary principles are incomplete")
    c=state["current_state"]
    if c["GLOBAL_ENGINEERING_AUDIT"]!="AUDIT_COMPLETE" or c["SCIENTIFIC_LIMITATION_RESOLUTION"]!="COMPLETE" or c["PROSPECTIVE_PREDICTIVE_VALIDITY"]!="NOT_ESTABLISHED": raise ValueError("Unexpected scientific/engineering status promotion")
    if state["mission_loop"][:3]!=["RECONSTRUCT","INTEGRATE","DISCOVER"] or "PERSIST" not in state["mission_loop"]: raise ValueError("Mission loop incomplete")

def validate_memory(memory):
    if memory["mission_id"]!="CEUTIA_SERPIENTE_CONTINUOUS_SCIENTIFIC_ENGINEERING": raise ValueError("Scientific memory targets a different mission")
    i=memory["identity"]
    if not i["mission_is_continuous"] or i["maximum_knowledge_to_capability_is_not_a_phase"] is not True or i["premature_closure_forbidden"] is not True: raise ValueError("Scientific memory continuity invariant is broken")
    concepts={x["id"] for x in memory["concepts"]}
    if len(concepts)!=len(memory["concepts"]): raise ValueError("Duplicate scientific concept IDs")
    for r in memory["discovery_relationships"]:
        if r["from"] not in concepts or r["to"] not in concepts: raise ValueError("Unknown concept in relationship")
    if len(memory["decision_genealogy"])<5 or len(memory["negative_knowledge"])<10 or len(memory["discovery_relationships"])<10: raise ValueError("Scientific memory unexpectedly shallow")
    if set(memory["method_gate"])!={"SCIENTIFIC_NEED","PHENOMENON","DATA","IDENTIFIABILITY","ASSUMPTIONS","IMPLEMENTABILITY","TESTABILITY","INCREMENTAL_VALUE"}: raise ValueError("Scientific method gate incomplete")
    if memory["mission_algorithm"][:3]!=["RECONSTRUCT","INTEGRATE","DISCOVER"] or "PERSIST" not in memory["mission_algorithm"]: raise ValueError("Mission algorithm incomplete")

def validate_repository_layout():
    for p in (MEMORY_PATH,RECONCILIATION_PATH,CURRENT_RECONCILIATION_PATH,CONTROL_PLANE_STATE_PATH,STATE_MACHINE_PATH,HANDOFF_REGISTRY_PATH,REGISTRY_PATH,QUEUE_PATH,EVENT_LOG_PATH,CONSTITUTION_PATH,SHARED_STANDARD_PATH):
        if not p.exists(): raise FileNotFoundError(f"Missing mission persistence artifact: {p}")

def validate_current_reconciliation(r):
    if r["mission_id"]!="CEUTIA_SERPIENTE_CONTINUOUS_SCIENTIFIC_ENGINEERING": raise ValueError("Current reconciliation targets another mission")
    x=r["corrections"]["response_coupling"]
    if x["status"]!="ACTIVE_FRONTIER" or x["empirical_state"]!="NOT_ESTABLISHED": raise ValueError("Response-coupling frontier incorrectly closed")

def validate_shared_standard():
    try:
        from .shared_standard import QualityLevel, enforce_claim_evidence, validate_autonomous_continuation
    except ImportError:
        from shared_standard import QualityLevel, enforce_claim_evidence, validate_autonomous_continuation
    if [x.value for x in QualityLevel] != list(range(10)):
        raise ValueError("Shared quality ladder is incomplete")
    enforce_claim_evidence(claim_level=QualityLevel.VERIFIED, evidence_level=QualityLevel.VERIFIED)
    if not validate_autonomous_continuation(authorized=True, scientifically_justified=True, technically_feasible=True, controlled=True, in_scope=True):
        raise ValueError("Autonomous continuation gate unexpectedly denies a fully authorized action")

def validate_control_plane():
    try:
        from .control_plane import ControlPlaneContract,MissionState,validate_handoff,validate_waiting_policy,validate_mission_contract
        from .event_log import load_jsonl,validate_chain
    except ImportError:
        from control_plane import ControlPlaneContract,MissionState,validate_handoff,validate_waiting_policy,validate_mission_contract
        from event_log import load_jsonl,validate_chain
    cp=load_json(CONTROL_PLANE_STATE_PATH); sm=load_json(STATE_MACHINE_PATH); hr=load_json(HANDOFF_REGISTRY_PATH); registry=load_json(REGISTRY_PATH); queue=load_json(QUEUE_PATH)
    ControlPlaneContract().validate_distinctions()
    if cp["status"] not in {"PARTIALLY_VALIDATED","VALIDATED"}: raise ValueError("Invalid control-plane status")
    if sm["mission_state_machine"]["states"]!=[s.value for s in MissionState]: raise ValueError("Persisted mission state machine differs from executable machine")
    for h in hr["items"]: validate_handoff(h)
    for q in queue["items"]: validate_waiting_policy(q)
    for m in cp["missions"]: validate_mission_contract(m)
    if len(cp["missions"])!=cp["mission_registry_source_evidence"]["mission_count_evidenced_in_source"]: raise ValueError("Control-plane mission projection count mismatch")
    if registry["discovery_status"]=="COMPLETE" and registry.get("repository_verified_mission_count")!=len(cp["missions"]): raise ValueError("Legacy registry falsely claims complete discovery")
    events=load_jsonl(EVENT_LOG_PATH); last_hash=validate_chain(events)
    return {"mission_count":len(cp["missions"]),"handoff_count":len(hr["items"]),"queue_count":len(queue["items"]),"event_count":len(events),"event_head":last_hash,"status":cp["status"]}

def main()->int:
    s=load_state(); m=load_memory(); r=load_current_reconciliation(); validate_state(s); validate_memory(m); validate_repository_layout(); validate_current_reconciliation(r); validate_shared_standard(); cp=validate_control_plane()
    print(f"MISSION_ID={s['mission_id']}"); print(f"AGENT_ROLE={s['mission_identity']['agent_role']}"); print(f"ENGINEERING_STATUS={s['current_state']['ENGINEERING_STATUS']}"); print(f"SCIENTIFIC_LIMITATION_RESOLUTION={s['current_state']['SCIENTIFIC_LIMITATION_RESOLUTION']}"); print(f"PROSPECTIVE_PREDICTIVE_VALIDITY={s['current_state']['PROSPECTIVE_PREDICTIVE_VALIDITY']}"); print(f"CONTROL_PLANE={cp['status']}"); print(f"CONTROL_PLANE_MISSIONS={cp['mission_count']}"); print(f"CONTROL_PLANE_HANDOFFS={cp['handoff_count']}"); print(f"CONTROL_PLANE_EVENTS={cp['event_count']}"); print(f"EVENT_CHAIN_HEAD={cp['event_head']}"); print("SHARED_STANDARD=LOADED_AND_EXECUTABLE"); print("RESPONSE_COUPLING=ACTIVE_FRONTIER"); print("MISSION_STATE=VALID"); return 0

if __name__=="__main__":raise SystemExit(main())
