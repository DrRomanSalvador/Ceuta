"""Repository-side universal mission discovery and invocation contract."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any
REQUIRED_REQUEST_FIELDS=("mission_id","operation","request_id","session_id","requested_at","authority_context","input_refs","expected_output_type","base_state_version")
REQUIRED_RESPONSE_FIELDS=("mission_id","request_id","operation","status","result_refs","source_refs","evidence_level","state_version_read","state_delta_ref","handoff_refs","conflict_status","next_authorized_action")
@dataclass(frozen=True)
class InvocationEnvelope:
    mission_id:str; operation:str; request_id:str; session_id:str; requested_at:str; authority_context:dict[str,bool]; input_refs:list[str]; expected_output_type:str; base_state_version:str

def discover(registry:dict[str,Any],*,mission_id:str|None=None,canonical_name:str|None=None)->dict[str,Any]:
    if not mission_id and not canonical_name: raise ValueError("Discovery requires mission_id or canonical_name")
    matches=[m for m in registry.get("missions",[]) if (mission_id and m.get("mission_id")==mission_id) or (canonical_name and m.get("canonical_name")==canonical_name)]
    if not matches:
        for capability in registry.get("constitutional_capabilities",{}).values():
            if (mission_id and capability.get("mission_id")==mission_id) or (canonical_name and capability.get("canonical_name")==canonical_name):
                matches.append({**capability,"current_status":capability.get("current_status","ACTIVE"),"bootstrap":capability.get("runtime"),"invocation_contract":capability.get("invocation_contract")})
    if not matches: raise LookupError("MISSION_NOT_DISCOVERABLE")
    if len(matches)>1: raise ValueError("MISSION_IDENTITY_AMBIGUOUS")
    return dict(matches[0])

def validate_request(request:dict[str,Any])->InvocationEnvelope:
    missing=[f for f in REQUIRED_REQUEST_FIELDS if f not in request]
    if missing: raise ValueError(f"Invocation missing required fields: {missing}")
    if not request["mission_id"] or not request["operation"] or not request["request_id"] or not request["session_id"]: raise ValueError("Invocation identity fields cannot be empty")
    if not isinstance(request["authority_context"],dict): raise ValueError("authority_context must be a mapping")
    return InvocationEnvelope(**{f:request[f] for f in REQUIRED_REQUEST_FIELDS})

def authorize_invocation(*,mission:dict[str,Any],envelope:InvocationEnvelope)->None:
    if mission.get("mission_id")!=envelope.mission_id: raise PermissionError("Invocation mission identity mismatch")
    if mission.get("current_status") in {"RETIRED","SUSPENDED","BLOCKED"}: raise PermissionError(f"Mission cannot be invoked in state {mission.get('current_status')}")
    if not envelope.authority_context.get("CAN_INVOKE",False): raise PermissionError("CAN_INVOKE is required")

def validate_response(response:dict[str,Any])->None:
    missing=[f for f in REQUIRED_RESPONSE_FIELDS if f not in response]
    if missing: raise ValueError(f"Invocation response missing required fields: {missing}")
    if response["state_delta_ref"] in (None,"") and response.get("status")=="SUCCESS": raise ValueError("Successful invocation must reference a state delta or explicit NO_PERSISTENCE_DELTA")

def compare_and_swap(*,current_state_version:str,base_state_version:str,state_delta:dict[str,Any])->str:
    if current_state_version!=base_state_version: raise RuntimeError("STALE_STATE_VERSION: stale writer rejected; create conflict instead of overwriting newer state")
    if not state_delta: raise ValueError("State delta cannot be empty")
    return "CAS_ACCEPTED"

def fresh_chat_discovery(registry:dict[str,Any],mission_id:str)->dict[str,Any]:
    mission=discover(registry,mission_id=mission_id)
    if not mission.get("invocation_contract") and not mission.get("bootstrap"): raise ValueError("Discovered mission lacks invocation/bootstrap contract references")
    return {"mission_id":mission["mission_id"],"canonical_name":mission.get("canonical_name",mission.get("mission_name")),"discovered":True,"runtime_validation":"PENDING_EXTERNAL_ORCHESTRATOR"}
