"""Fail-closed repository gate for COORDINATOR / ESPEJO constitutional capabilities."""
from __future__ import annotations

import json
from pathlib import Path

MISSION_DIR = Path(__file__).parent
REGISTRY_PATH = MISSION_DIR / "MISSION_REGISTRY.json"
STATE_PATH = MISSION_DIR / "COORDINATION_STATE.json"
DOC_PATH = MISSION_DIR / "COORDINATOR_ESPEJO_CONSTITUTION.md"

COMMANDS = {"CONTINUE","CHECKPOINT","SPLIT","REQUEST_MIRROR","PAUSE","STANDBY","RESUME","REDIRECT","DELEGATE","HANDOFF","RECOVER","ABANDON","REPRIORITIZE"}
ACTIONS = {"ASSIST","REVIEW","VERIFY","RESEARCH","TEST","RED_TEAM","CHECKPOINT","RECOVERY","PREPARE"}
REQUIRED_STATE_KEYS = {"schema_version","state_version","updated_at","agents","missions","tasks","priorities","checkpoints","commands","interventions","mirrors","standby","recovery","conflicts","handoffs","pending_reviews","deferred_hypotheses"}

def validate() -> dict[str, object]:
    registry=json.loads(REGISTRY_PATH.read_text(encoding="utf-8")); state=json.loads(STATE_PATH.read_text(encoding="utf-8"))
    if not DOC_PATH.exists(): raise ValueError("COORDINATOR/ESPEJO constitutional documentation is missing")
    capabilities=registry.get("constitutional_capabilities",{})
    for identity,hierarchy,runtime in (("COORDINATOR","H1","mission/coordination.py"),("ESPEJO","H3","mission/coordination.py")):
        c=capabilities.get(identity)
        if not c: raise ValueError(f"Missing constitutional capability registration: {identity}")
        if c.get("identity")!=identity or c.get("hierarchy")!=hierarchy: raise ValueError(f"Invalid identity/hierarchy registration: {identity}")
        if c.get("runtime")!=runtime or c.get("mission_ownership") is not False: raise ValueError(f"Invalid runtime/ownership boundary: {identity}")
    if not REQUIRED_STATE_KEYS.issubset(state): raise ValueError(f"Coordination state missing keys: {sorted(REQUIRED_STATE_KEYS-set(state))}")
    if state.get("schema_version") not in {"1.0.0","1.1.0","1.2.0"}: raise ValueError("Unsupported coordination state schema")
    if not isinstance(state.get("state_version"),int) or state["state_version"]<0: raise ValueError("Invalid coordination state version")
    for oid,c in state["commands"].items():
        required={"order_id","issuer","target","mission","reason","authority_basis","issued_at","state","expected_effect","acknowledgement","execution_result","command_type"}
        if not required.issubset(c): raise ValueError(f"Command {oid} is incomplete")
        if oid!=c["order_id"] or c["command_type"] not in COMMANDS: raise ValueError(f"Invalid command identity/type: {oid}")
        if c["authority_basis"] not in {"COORDINATOR","HUMAN_AUTHORITY"}: raise ValueError("Command authority escaped constitutional boundary")
        if "provenance" not in c or c["provenance"].get("COMMAND_ISSUER")!=c["issuer"]: raise ValueError(f"Command {oid} lacks issuer provenance")
    for mid,m in state["mirrors"].items():
        required={"mirror_id","mirror_of","mission","target_agent","task","capability_required","action","functional_role","mission_owner","subtask_owner","provenance"}
        if not required.issubset(m): raise ValueError(f"Mirror {mid} is incomplete")
        if mid!=m["mirror_id"] or m["subtask_owner"]==m["mission_owner"]: raise ValueError("Mirror identity and mission ownership collapsed")
        if m["action"] not in ACTIONS or m["provenance"].get("MIRROR_OF")!=m["mirror_of"]: raise ValueError(f"Invalid mirror provenance/action: {mid}")
    for handoff in state["handoffs"]:
        if handoff.get("mission_owner")==handoff.get("subtask_owner"): raise ValueError("Mirror handoff collapsed mission owner and subtask owner")
    return {"status":"REPOSITORY_GATE_VALID","coordinator_commands":len(state["commands"]),"mirror_invocations":len(state["mirrors"]),"state_version":state["state_version"],"external_live_orchestration":"NOT_ESTABLISHED"}

if __name__ == "__main__": print(json.dumps(validate(),sort_keys=True))
