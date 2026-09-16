"""Fail-closed bootstrap for the persistent scientific and multi-mission state."""
from __future__ import annotations
import json
from pathlib import Path

MISSION_DIR=Path(__file__).parent
STATE_PATH=MISSION_DIR/"CEUTIA_SERPIENTE_MISSION_STATE.json"; MEMORY_PATH=MISSION_DIR/"SCIENTIFIC_MISSION_MEMORY.json"
RECONCILIATION_PATH=MISSION_DIR/"STATE_RECONCILIATION_001.md"; CURRENT_RECONCILIATION_PATH=MISSION_DIR/"CURRENT_MISSION_RECONCILIATION.json"
CONTROL_PLANE_STATE_PATH=MISSION_DIR/"MISSION_CONTROL_PLANE_STATE.json"; STATE_MACHINE_PATH=MISSION_DIR/"MISSION_STATE_MACHINE.json"
HANDOFF_REGISTRY_PATH=MISSION_DIR/"MISSION_HANDOFF_REGISTRY.json"; REGISTRY_PATH=MISSION_DIR/"MISSION_REGISTRY.json"; QUEUE_PATH=MISSION_DIR/"AUTONOMOUS_WORK_QUEUE.json"; EVENT_LOG_PATH=MISSION_DIR/"MISSION_EVENT_LOG.jsonl"; CLAIMS_PATH=MISSION_DIR/"MISSION_WORK_CLAIMS.json"
CONTRIBUTION_PATH=MISSION_DIR/"MISSION_CONTRIBUTION_REGISTRY.json"; CONTRADICTION_PATH=MISSION_DIR/"MISSION_CONTRADICTION_REGISTRY.json"; LIFECYCLE_PATH=MISSION_DIR/"MISSION_LIFECYCLE_LEDGER.json"
CONSTITUTION_PATH=MISSION_DIR/"MISSION_SYSTEM_CONSTITUTION.md"; SHARED_STANDARD_PATH=MISSION_DIR/"shared_standard.py"; ROMAN_CONTRACT_PATH=MISSION_DIR/"ROMAN_INVOCATION_CONTRACT.json"; ROMAN_STATE_PATH=MISSION_DIR/"ROMAN_MISSION_STATE.json"
REQUIRED_KEYS={"schema_version","mission_id","mission_identity","purpose","scope","architecture","scientific_principles","epistemology","current_state","current_capabilities","limitations","temporal_model","system_model","forecasting","uncertainty","early_warning","prevention","self_monitoring","acquisition","evaluation","governance","testing","git_state_at_persistence","authoritative_documents","bibliography_map","open_frontiers","mission_loop","closure_criteria","replication"}
MEMORY_REQUIRED_KEYS={"schema_version","mission_id","purpose","memory_principle","identity","reconstruction_order","knowledge_domains","concepts","discovery_relationships","decision_genealogy","negative_knowledge","capability_lineage","scenario_memory","method_gate","mission_algorithm","reconstruction_invariant","closure_rule"}
DERIVED_CONCEPT_IDS={"future_leakage","forecast_forensics","dynamic_derivatives","predictive_validity","confidence_intervals","prospective_validity","claim_governance","false_trajectory","system_of_systems","multisystem_risk","interaction_selection","self_monitoring","causal_governance","operational_effectiveness","continuous_acquisition"}

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
    known_relationship_endpoints=concepts | DERIVED_CONCEPT_IDS
    for r in memory["discovery_relationships"]:
        if r["from"] not in known_relationship_endpoints or r["to"] not in known_relationship_endpoints: raise ValueError(f"Unknown concept in relationship: {r['from']} -> {r['to']}")
    if len(memory["decision_genealogy"])<5 or len(memory["negative_knowledge"])<10 or len(memory["discovery_relationships"])<10: raise ValueError("Scientific memory unexpectedly shallow")
    if set(memory["method_gate"])!={"SCIENTIFIC_NEED","PHENOMENON","DATA","IDENTIFIABILITY","ASSUMPTIONS","IMPLEMENTABILITY","TESTABILITY","INCREMENTAL_VALUE"}: raise ValueError("Scientific method gate incomplete")
    if memory["mission_algorithm"][:3]!=["RECONSTRUCT","INTEGRATE","DISCOVER"] or "PERSIST" not in memory["mission_algorithm"]: raise ValueError("Mission algorithm incomplete")

def validate_repository_layout():
    for p in (MEMORY_PATH,RECONCILIATION_PATH,CURRENT_RECONCILIATION_PATH,CONTROL_PLANE_STATE_PATH,STATE_MACHINE_PATH,HANDOFF_REGISTRY_PATH,REGISTRY_PATH,QUEUE_PATH,EVENT_LOG_PATH,CLAIMS_PATH,CONTRIBUTION_PATH,CONTRADICTION_PATH,LIFECYCLE_PATH,CONSTITUTION_PATH,SHARED_STANDARD_PATH,ROMAN_CONTRACT_PATH,ROMAN_STATE_PATH):
        if not p.exists(): raise FileNotFoundError(f"Missing mission persistence artifact: {p}")

def validate_current_reconciliation(r):
    if r["mission_id"]!="CEUTIA_SERPIENTE_CONTINUOUS_SCIENTIFIC_ENGINEERING": raise ValueError("Current reconciliation targets another mission")
    x=r["corrections"]["response_coupling"]
    if x["status"]!="ACTIVE_FRONTIER" or x["empirical_state"]!="NOT_ESTABLISHED": raise ValueError("Response-coupling frontier incorrectly closed")

def validate_shared_standard():
    try:
        from .shared_standard import QualityLevel, enforce_claim_evidence, validate_autonomous_continuation, validate_attribution
    except ImportError:
        from shared_standard import QualityLevel, enforce_claim_evidence, validate_autonomous_continuation, validate_attribution
    if [x.value for x in QualityLevel] != list(range(10)): raise ValueError("Shared quality ladder is incomplete")
    enforce_claim_evidence(claim_level=QualityLevel.VERIFIED, evidence_level=QualityLevel.VERIFIED)
    if not validate_autonomous_continuation(authorized=True, scientifically_justified=True, technically_feasible=True, controlled=True, in_scope=True): raise ValueError("Autonomous continuation gate unexpectedly denies a fully authorized action")
    validate_attribution({field:"BOOTSTRAP" for field in ("DISCOVERED_BY","PROPOSED_BY","IMPLEMENTED_BY","REVIEWED_BY","VALIDATED_BY","AUTHORIZED_BY")}, require_authorization=True)

def validate_control_plane():
    try:
        from .control_plane import ControlPlaneContract,MissionState,validate_handoff,validate_waiting_policy,validate_mission_contract,validate_registry_consistency
        from .event_log import load_jsonl,validate_chain
        from .replay import replay
        from .shared_standard import validate_contradiction,validate_attribution
        from .invocation_runtime import discover
    except ImportError:
        from control_plane import ControlPlaneContract,MissionState,validate_handoff,validate_waiting_policy,validate_mission_contract,validate_registry_consistency
        from event_log import load_jsonl,validate_chain
        from replay import replay
        from shared_standard import validate_contradiction,validate_attribution
        from invocation_runtime import discover
    cp=load_json(CONTROL_PLANE_STATE_PATH); sm=load_json(STATE_MACHINE_PATH); hr=load_json(HANDOFF_REGISTRY_PATH); registry=load_json(REGISTRY_PATH); queue=load_json(QUEUE_PATH); claims=load_json(CLAIMS_PATH); contributions=load_json(CONTRIBUTION_PATH); contradictions=load_json(CONTRADICTION_PATH); lifecycle=load_json(LIFECYCLE_PATH); roman_contract=load_json(ROMAN_CONTRACT_PATH); roman_state=load_json(ROMAN_STATE_PATH)
    ControlPlaneContract().validate_distinctions()
    if cp["status"] not in {"PARTIALLY_VALIDATED","VALIDATED"}: raise ValueError("Invalid control-plane status")
    if sm["mission_state_machine"]["states"]!=[s.value for s in MissionState]: raise ValueError("Persisted mission state machine differs from executable machine")
    for h in hr["items"]: validate_handoff(h)
    for q in queue["items"]: validate_waiting_policy(q)
    for m in cp["missions"]: validate_mission_contract(m)
    if len(cp["missions"])!=cp["mission_registry_source_evidence"]["mission_count_evidenced_in_source"]: raise ValueError("Control-plane mission projection count mismatch")
    validate_registry_consistency(registry, projected_count=cp["mission_registry_source_evidence"]["mission_count_evidenced_in_source"])
    roman=discover(registry,mission_id="ROMAN")
    if roman.get("current_status")!="ADMITTED_REPOSITORY_RUNTIME_PENDING": raise ValueError("ROMAN current registry status is incorrectly promoted")
    if roman.get("invocation_contract")!=str(Path("mission/ROMAN_INVOCATION_CONTRACT.json")): raise ValueError("ROMAN invocation contract reference is incorrect")
    if roman_contract.get("operating_standard_version")!="MISSION_SYSTEM_CONSTITUTION_1.0" or roman_state.get("operating_standard_version")!="MISSION_SYSTEM_CONSTITUTION_1.0": raise ValueError("ROMAN does not inherit the canonical constitution")
    if roman_state.get("status")!="ADMITTED_REPOSITORY_RUNTIME_PENDING": raise ValueError("ROMAN state is incorrectly promoted")
    if claims.get("registry_id")!="CEUTIA_SERPIENTE_MISSION_WORK_CLAIMS" or not isinstance(claims.get("claims"),dict) or not isinstance(claims.get("history",[]),list): raise ValueError("Invalid persistent work-claim registry")
    if contributions.get("registry_id")!="CEUTIA_SERPIENTE_MISSION_CONTRIBUTION_REGISTRY" or not isinstance(contributions.get("items"),list): raise ValueError("Invalid contribution registry")
    for contribution in contributions["items"]: validate_attribution(contribution, require_authorization=True)
    if contradictions.get("registry_id")!="CEUTIA_SERPIENTE_MISSION_CONTRADICTION_REGISTRY" or not isinstance(contradictions.get("items"),list): raise ValueError("Invalid contradiction registry")
    for contradiction in contradictions["items"]: validate_contradiction(contradiction)
    if lifecycle.get("registry_id")!="CEUTIA_SERPIENTE_MISSION_LIFECYCLE_LEDGER" or any(not isinstance(lifecycle.get(k),list) for k in ("admissions","retirements","recoveries","conflicts")): raise ValueError("Invalid mission lifecycle ledger")
    for admission in lifecycle["admissions"]:
        if admission.get("mission_id")=="ROMAN":
            if admission.get("status")!="ADMITTED_REPOSITORY_RUNTIME_PENDING": raise ValueError("ROMAN admission must remain runtime-pending until live validation")
            if admission.get("authorized_by")!="MISSION-01" or not admission.get("evidence"): raise ValueError("ROMAN admission lacks owner/authority evidence")
            if admission.get("contract",{}).get("operating_standard_version")!="MISSION_SYSTEM_CONSTITUTION_1.0": raise ValueError("ROMAN does not explicitly inherit the canonical operating standard")
    events=load_jsonl(EVENT_LOG_PATH); last_hash=validate_chain(events)
    replayed=replay(EVENT_LOG_PATH)
    replayed_roman=replayed.missions.get("ROMAN")
    if not replayed_roman: raise ValueError("Canonical replay did not reconstruct ROMAN admission")
    if replayed_roman.get("status")!=roman_state.get("status"): raise ValueError("Replay/materialized ROMAN status divergence")
    if replayed.last_hash!=last_hash: raise ValueError("Replay/event-chain head divergence")
    return {"mission_count":len(cp["missions"]),"handoff_count":len(hr["items"]),"queue_count":len(queue["items"]),"claim_count":len(claims["claims"]),"contribution_count":len(contributions["items"]),"contradiction_count":len(contradictions["items"]),"lifecycle_admissions":len(lifecycle["admissions"]),"lifecycle_retirements":len(lifecycle["retirements"]),"event_count":len(events),"event_head":last_hash,"replay_event_head":replayed.last_hash,"replay_mission_count":len(replayed.missions),"status":cp["status"]}

def main()->int:
    s=load_state(); m=load_memory(); r=load_current_reconciliation(); validate_state(s); validate_memory(m); validate_repository_layout(); validate_current_reconciliation(r); validate_shared_standard(); cp=validate_control_plane()
    print(f"MISSION_ID={s['mission_id']}"); print(f"AGENT_ROLE={s['mission_identity']['agent_role']}"); print(f"ENGINEERING_STATUS={s['current_state']['ENGINEERING_STATUS']}"); print(f"SCIENTIFIC_LIMITATION_RESOLUTION={s['current_state']['SCIENTIFIC_LIMITATION_RESOLUTION']}"); print(f"PROSPECTIVE_PREDICTIVE_VALIDITY={s['current_state']['PROSPECTIVE_PREDICTIVE_VALIDITY']}"); print(f"CONTROL_PLANE={cp['status']}"); print(f"CONTROL_PLANE_MISSIONS={cp['mission_count']}"); print(f"CONTROL_PLANE_HANDOFFS={cp['handoff_count']}"); print(f"CONTROL_PLANE_CLAIMS={cp['claim_count']}"); print(f"CONTROL_PLANE_CONTRIBUTIONS={cp['contribution_count']}"); print(f"CONTROL_PLANE_CONTRADICTIONS={cp['contradiction_count']}"); print(f"CONTROL_PLANE_LIFECYCLE_ADMISSIONS={cp['lifecycle_admissions']}"); print(f"CONTROL_PLANE_LIFECYCLE_RETIREMENTS={cp['lifecycle_retirements']}"); print(f"CONTROL_PLANE_EVENTS={cp['event_count']}"); print(f"EVENT_CHAIN_HEAD={cp['event_head']}"); print(f"REPLAY_EVENT_HEAD={cp['replay_event_head']}"); print(f"REPLAY_MISSIONS={cp['replay_mission_count']}"); print("SHARED_STANDARD=LOADED_AND_EXECUTABLE"); print("ROMAN_DISCOVERY=REGISTERED_REPOSITORY_RUNTIME_PENDING"); print("RESPONSE_COUPLING=ACTIVE_FRONTIER"); print("MISSION_STATE=VALID"); return 0

if __name__=="__main__":raise SystemExit(main())