"""Fail-closed repository gate for COORDINATOR / ESPEJO constitutional capabilities."""
from __future__ import annotations

import json
from pathlib import Path

MISSION_DIR = Path(__file__).parent
REGISTRY_PATH = MISSION_DIR / "MISSION_REGISTRY.json"
STATE_PATH = MISSION_DIR / "COORDINATION_STATE.json"
DOC_PATH = MISSION_DIR / "COORDINATOR_ESPEJO_CONSTITUTION.md"

COMMANDS = {
    "CONTINUE", "CHECKPOINT", "SPLIT", "REQUEST_MIRROR", "PAUSE", "STANDBY", "RESUME",
    "REDIRECT", "DELEGATE", "HANDOFF", "RECOVER", "ABANDON", "REPRIORITIZE",
}
ACTIONS = {"ASSIST", "REVIEW", "VERIFY", "RESEARCH", "TEST", "RED_TEAM", "CHECKPOINT", "RECOVERY", "PREPARE"}
REQUIRED_STATE_KEYS = {
    "schema_version", "state_version", "updated_at", "agents", "missions", "tasks", "priorities",
    "checkpoints", "commands", "interventions", "mirrors", "standby", "recovery", "conflicts",
    "handoffs", "pending_reviews", "deferred_hypotheses",
}


def validate() -> dict[str, object]:
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    if not DOC_PATH.exists():
        raise ValueError("COORDINATOR/ESPEJO constitutional documentation is missing")
    capabilities = registry.get("constitutional_capabilities", {})
    for identity, hierarchy, runtime in (
        ("COORDINATOR", "H1", "mission/coordination.py"),
        ("ESPEJO", "H3", "mission/coordination.py"),
    ):
        capability = capabilities.get(identity)
        if not capability:
            raise ValueError(f"Missing constitutional capability registration: {identity}")
        if capability.get("identity") != identity or capability.get("hierarchy") != hierarchy:
            raise ValueError(f"Invalid identity/hierarchy registration: {identity}")
        if capability.get("runtime") != runtime or capability.get("mission_ownership") is not False:
            raise ValueError(f"Invalid runtime/ownership boundary: {identity}")
    if not REQUIRED_STATE_KEYS.issubset(state):
        raise ValueError(f"Coordination state missing keys: {sorted(REQUIRED_STATE_KEYS - set(state))}")
    if state.get("schema_version") not in {"1.0.0", "1.1.0"}:
        raise ValueError("Unsupported coordination state schema")
    if not isinstance(state.get("state_version"), int) or state["state_version"] < 0:
        raise ValueError("Invalid coordination state version")
    for order_id, command in state["commands"].items():
        required = {"order_id", "issuer", "target", "mission", "reason", "authority_basis", "issued_at", "state", "expected_effect", "acknowledgement", "execution_result", "command_type"}
        if not required.issubset(command):
            raise ValueError(f"Command {order_id} is incomplete")
        if order_id != command["order_id"]:
            raise ValueError("Command dictionary key does not match order_id")
        if command["command_type"] not in COMMANDS:
            raise ValueError(f"Unsupported command persisted: {command['command_type']}")
        if command["authority_basis"] not in {"COORDINATOR", "HUMAN_AUTHORITY"}:
            raise ValueError("Command authority escaped constitutional boundary")
    for mirror_id, mirror in state["mirrors"].items():
        required = {"mirror_id", "mirror_of", "mission", "target_agent", "task", "capability_required", "action", "functional_role", "mission_owner", "subtask_owner"}
        if not required.issubset(mirror):
            raise ValueError(f"Mirror {mirror_id} is incomplete")
        if mirror_id != mirror["mirror_id"] or mirror["subtask_owner"] == mirror["mission_owner"]:
            raise ValueError("Mirror identity and mission ownership collapsed")
        if mirror["action"] not in ACTIONS:
            raise ValueError(f"Unsupported mirror action persisted: {mirror['action']}")
    for handoff in state["handoffs"]:
        if handoff.get("mission_owner") == handoff.get("subtask_owner"):
            raise ValueError("Mirror handoff collapsed mission owner and subtask owner")
    return {
        "status": "REPOSITORY_GATE_VALID",
        "coordinator_commands": len(state["commands"]),
        "mirror_invocations": len(state["mirrors"]),
        "state_version": state["state_version"],
        "external_live_orchestration": "NOT_ESTABLISHED",
    }


if __name__ == "__main__":
    print(json.dumps(validate(), sort_keys=True))
