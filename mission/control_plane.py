"""Executable multi-mission control-plane primitives.

Dependency-free enforcement of lifecycle transitions, ownership, work claims,
handoffs, dependency graphs, reconciliation and evidence-bearing completion.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any

class MissionState(str, Enum):
    UNKNOWN="UNKNOWN"; DISCOVERED="DISCOVERED"; REGISTERED="REGISTERED"; BOOTSTRAP_PENDING="BOOTSTRAP_PENDING"; BOOTSTRAPPED="BOOTSTRAPPED"; READY="READY"; ACTIVE="ACTIVE"; BLOCKED="BLOCKED"; WAITING_EXTERNAL="WAITING_EXTERNAL"; WAITING_INTERNAL="WAITING_INTERNAL"; HANDOFF_PENDING="HANDOFF_PENDING"; VALIDATION_PENDING="VALIDATION_PENDING"; INTEGRATION_PENDING="INTEGRATION_PENDING"; SUSPENDED="SUSPENDED"; RECOVERY_REQUIRED="RECOVERY_REQUIRED"; RETIRED="RETIRED"; COMPLETE="COMPLETE"
class HandoffState(str, Enum):
    CREATED="CREATED"; VALIDATION_PENDING="VALIDATION_PENDING"; READY="READY"; ACCEPTED="ACCEPTED"; REJECTED="REJECTED"; IMPLEMENTING="IMPLEMENTING"; IMPLEMENTED="IMPLEMENTED"; VERIFIED="VERIFIED"; INTEGRATED="INTEGRATED"; SUPERSEDED="SUPERSEDED"
ALLOWED_TRANSITIONS={MissionState.UNKNOWN:{MissionState.DISCOVERED},MissionState.DISCOVERED:{MissionState.REGISTERED},MissionState.REGISTERED:{MissionState.BOOTSTRAP_PENDING,MissionState.SUSPENDED},MissionState.BOOTSTRAP_PENDING:{MissionState.BOOTSTRAPPED,MissionState.RECOVERY_REQUIRED},MissionState.BOOTSTRAPPED:{MissionState.READY,MissionState.RECOVERY_REQUIRED},MissionState.READY:{MissionState.ACTIVE,MissionState.BLOCKED,MissionState.WAITING_INTERNAL,MissionState.WAITING_EXTERNAL},MissionState.ACTIVE:{MissionState.BLOCKED,MissionState.WAITING_INTERNAL,MissionState.WAITING_EXTERNAL,MissionState.HANDOFF_PENDING,MissionState.VALIDATION_PENDING,MissionState.INTEGRATION_PENDING,MissionState.SUSPENDED,MissionState.RECOVERY_REQUIRED,MissionState.COMPLETE},MissionState.BLOCKED:{MissionState.ACTIVE,MissionState.WAITING_INTERNAL,MissionState.WAITING_EXTERNAL,MissionState.RECOVERY_REQUIRED},MissionState.WAITING_EXTERNAL:{MissionState.ACTIVE,MissionState.BLOCKED,MissionState.RECOVERY_REQUIRED},MissionState.WAITING_INTERNAL:{MissionState.ACTIVE,MissionState.BLOCKED,MissionState.RECOVERY_REQUIRED},MissionState.HANDOFF_PENDING:{MissionState.ACTIVE,MissionState.VALIDATION_PENDING,MissionState.INTEGRATION_PENDING,MissionState.RECOVERY_REQUIRED},MissionState.VALIDATION_PENDING:{MissionState.ACTIVE,MissionState.INTEGRATION_PENDING,MissionState.RECOVERY_REQUIRED,MissionState.SUSPENDED},MissionState.INTEGRATION_PENDING:{MissionState.ACTIVE,MissionState.COMPLETE,MissionState.RECOVERY_REQUIRED},MissionState.SUSPENDED:{MissionState.READY,MissionState.ACTIVE,MissionState.RECOVERY_REQUIRED,MissionState.RETIRED},MissionState.RECOVERY_REQUIRED:{MissionState.BOOTSTRAP_PENDING,MissionState.SUSPENDED,MissionState.RETIRED},MissionState.RETIRED:set(),MissionState.COMPLETE:{MissionState.RETIRED,MissionState.RECOVERY_REQUIRED}}
def utc_now(): return datetime.now(timezone.utc).isoformat()
def require_fields(obj,fields,label):
    missing=[f for f in fields if f not in obj or obj[f] in (None,"")]
    if missing: raise ValueError(f"{label} missing required fields: {missing}")
def transition(current,target,*,authorized_actor,evidence,preconditions_met=True):
    if target not in ALLOWED_TRANSITIONS[current]: raise ValueError(f"Illegal mission transition: {current.value} -> {target.value}")
    if not preconditions_met: raise ValueError("Transition preconditions are not satisfied")
    if not evidence or not authorized_actor: raise ValueError("State transition requires actor and evidence")
    return {"from":current.value,"to":target.value,"trigger":"explicit_control_plane_transition","authorized_actor":authorized_actor,"evidence":evidence,"timestamp":utc_now()}
def validate_mission_contract(mission):
    required=("mission_id","mission_name","mission_version","mission_class","mission_status","mission_owner","authority_scope","repository_scope","allowed_write_surfaces","forbidden_write_surfaces","inputs","outputs","dependencies","dependents","handoff_contract","validation_contract","state_source","current_objective","current_gap","next_authorized_action","completion_criteria","failure_policy","recovery_policy")
    require_fields(mission,required,"mission"); mission_id=mission["mission_id"]
    if not (mission_id.startswith("MISSION-") or mission_id=="ROMAN"): raise ValueError("Mission IDs must use MISSION-* or the canonical ROMAN namespace")
    if mission_id=="ROMAN" and mission["mission_status"] not in {"REGISTERED_SOURCE_REQUIRES_ADMISSION","REGISTERED","BOOTSTRAP_PENDING","BOOTSTRAPPED","READY","ACTIVE"}: raise ValueError("ROMAN has an invalid lifecycle status")
    if set(mission["allowed_write_surfaces"]) & set(mission["forbidden_write_surfaces"]): raise ValueError(f"Overlapping write boundaries: {mission_id}")
def validate_registry_consistency(registry,*,projected_count=None):
    missions=registry.get("missions"); count=registry.get("repository_verified_mission_count")
    if not isinstance(missions,list) or not isinstance(count,int): raise ValueError("Mission registry lacks verifiable mission collection/count")
    if count!=len(missions): raise ValueError("Repository verified mission count does not match registry entries")
    if registry.get("discovery_status")=="COMPLETE" and projected_count is not None and count!=projected_count: raise ValueError("Registry claims complete discovery while projected mission count disagrees")
def validate_handoff(handoff):
    required=("handoff_id","source_mission","destination_mission","timestamp","source_commit","finding","evidence","affected_surface","severity","required_action","proposed_action","constraints","dependencies","validation_required","acceptance_criteria","status")
    require_fields(handoff,required,"handoff"); status=HandoffState(handoff["status"])
    if status==HandoffState.INTEGRATED:
        if not handoff.get("integrated_at"): raise ValueError("Integrated handoff requires integrated_at")
        if handoff.get("verification_state")!=HandoffState.VERIFIED.value: raise ValueError("Integrated handoff requires verification_state=VERIFIED")
def can_modify_surface(*,mission_id,surface,mission): return mission.get("mission_id")==mission_id and surface in mission.get("allowed_write_surfaces",[]) and surface not in mission.get("forbidden_write_surfaces",[])
def acquire_work_claim(work,*,mission_id,actor,lease_id,now=None):
    require_fields(work,("work_id","mission_owner","surface","objective","status"),"work")
    if work["mission_owner"]!=mission_id: raise PermissionError("Mission cannot claim work owned by another mission")
    if not actor or not lease_id: raise PermissionError("Work claim requires actor and lease identity")
    if work.get("claim",{}).get("status")=="ACTIVE": raise RuntimeError("Work is already actively claimed")
    return {"status":"ACTIVE","mission_id":mission_id,"actor":actor,"lease_id":lease_id,"acquired_at":now or utc_now()}
def release_work_claim(claim,*,actor):
    if claim.get("status")!="ACTIVE": raise ValueError("Only active claims can be released")
    if not actor or actor!=claim.get("actor"): raise PermissionError("Only the claiming actor may release the claim")
    return {**claim,"status":"RELEASED","released_by":actor,"released_at":utc_now()}
def validate_dependency_graph(missions,edges):
    ids={m["mission_id"] for m in missions}
    for m in missions: validate_mission_contract(m)
    for e in edges:
        if e["source"] not in ids or e["target"] not in ids: raise ValueError(f"Orphan dependency edge: {e}")
    adjacency={i:[] for i in ids}
    for e in edges: adjacency[e["source"]].append(e["target"])
    visiting=set(); visited=set()
    def dfs(n):
        if n in visiting: raise ValueError(f"Dependency cycle detected at {n}")
        if n in visited: return
        visiting.add(n)
        for child in adjacency[n]: dfs(child)
        visiting.remove(n); visited.add(n)
    for n in ids: dfs(n)
def reconcile(*,documented,actual,evidence):
    if not evidence: raise ValueError("Reconciliation requires evidence")
    status="CONSISTENT" if documented==actual else ("UNKNOWN" if actual is None else "CONFLICTING")
    return {"status":status,"documented":documented,"actual":actual,"evidence":evidence,"claim_frozen":status!="CONSISTENT","timestamp":utc_now()}
def validate_waiting_policy(item):
    if item.get("status")=="WAITING" and not item.get("blocking_dependency"): raise ValueError("WAITING work requires a blocking_dependency")
    if item.get("status")=="DONE": raise ValueError("DONE is not a valid autonomous queue terminal state")
def select_next_work(items):
    candidates=[]
    for item in items:
        validate_waiting_policy(item)
        if item.get("status") in {"PENDING","READY","ACTIVE"} and not item.get("blocking_dependencies"): candidates.append(item)
    if not candidates: raise LookupError("No non-blocked executable work item exists")
    order={"CRITICAL":0,"HIGH":1,"MEDIUM":2,"LOW":3}
    return sorted(candidates,key=lambda x:(order.get(x.get("priority"),99),-float(x.get("centrality",0)),x["work_id"]))[0]
def validate_no_self_authorization(mission_id,action,*,human_authorization_required):
    if human_authorization_required and mission_id.startswith("MISSION-"): raise PermissionError(f"{mission_id} cannot self-authorize: {action}")
def validate_checkpoint(checkpoint): require_fields(checkpoint,("mission_id","current_state","current_objective","current_findings","current_blockers","current_handoffs","completed_work","uncompleted_work","next_authorized_action","last_verified_commit","validation_status"),"checkpoint")
def validate_completion_evidence(record):
    require_fields(record,("work_id","artifact","verification_method","evidence_status"),"completion")
    if record["evidence_status"] not in {"TESTED","VERIFIED","VALIDATED","PROSPECTIVELY_EVALUATED","PROSPECTIVELY_VALIDATED","OPERATIONALLY_EFFECTIVE"}: raise ValueError("Completion claim lacks evidence-bearing status")
@dataclass(frozen=True)
class ControlPlaneContract:
    documented_states:tuple[str,...]=( "DOCUMENTED","REGISTERED","DEFINED","BOOTSTRAPPED","AUTHORIZED","ACTIVE","EXECUTING","BLOCKED","WAITING","HANDOFF_PENDING","HANDOFF_ACCEPTED","INTEGRATED","VALIDATED","COMPLETE" )
    def validate_distinctions(self):
        if len(set(self.documented_states))!=len(self.documented_states): raise ValueError("Duplicate control-plane states")
        if "WAITING" not in self.documented_states or "ACTIVE" not in self.documented_states: raise ValueError("Required distinctions missing")
__all__=["MissionState","HandoffState","ControlPlaneContract","transition","validate_mission_contract","validate_registry_consistency","validate_handoff","can_modify_surface","acquire_work_claim","release_work_claim","validate_dependency_graph","reconcile","select_next_work","validate_checkpoint","validate_completion_evidence","validate_no_self_authorization"]