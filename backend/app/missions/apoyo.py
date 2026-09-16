from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Iterator, Mapping, Sequence

try:
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None

from .registry import MissionRegistry, MissionRegistryError


class ApoyoError(RuntimeError):
    """Raised when an APOYO invariant cannot be safely enforced."""


APOYO_STATES = {
    "BORN", "REGISTERED", "WAITING", "WAITING_FOR_AGENT", "WAITING_FOR_TASK",
    "WAITING_AT_MEETING_POINT", "READY", "DISCOVERING", "INVOKED", "ASSISTING",
    "EXECUTING_SUPPORT_TASK", "VALIDATING", "PERSISTING", "HANDOFF_PENDING",
    "RETURNING_TO_MEETING_POINT", "SPAWNING_SUCCESSOR", "REPLICATING", "RECOVERING", "RETIRED",
}
COLLABORATION_STATES = {
    "OFFERED", "REQUESTED", "ASSIGNED", "ACCEPTED", "RUNNING", "VALIDATING",
    "PERSISTING", "RETURNING_CONTROL", "COMPLETED", "FAILED", "REJECTED", "HANDED_BACK",
}
ACTIVE_AGENT_STATES = {"ACTIVE", "WORKING", "INVOKED", "ASSISTING", "RUNNING", "WAITING_FOR_INSTRUCTION", "CHECKPOINT"}
PROSPECTIVE_AGENT_STATES = {"ENTERING_MISSION", "READY_TO_START", "UPCOMING", "NEAR_ENTRY"}
PRINCIPAL_ACTOR_IDS = {"ROMÁN", "ROMAN"}
RECOVERY_COMMANDS = {
    "APOYO", "RETURN", "GO BACK", "RETURN TO MEETING POINT", "MEETING POINT",
    "RECOVER YOUR ROLE", "RECOVER ROLE", "RETOMA APOYO", "CONTINUA COMO APOYO", "CONTINÚA COMO APOYO",
    "VUELVE", "REGRESA", "VUELVE AL MEETING POINT", "REGRESA AL MEETING POINT",
}


@dataclass(frozen=True, slots=True)
class CollaborationRequest:
    requesting_mission: str
    request_id: str
    requested_capability: str
    objective: str
    scope: str
    urgency: str
    constraints: tuple[str, ...]
    expected_output: str
    authority: Mapping[str, bool]
    existing_work_refs: tuple[str, ...] = ()
    capability_gap: str = ""
    deadline_if_any: str | None = None

    def validate(self) -> None:
        required = {
            "requesting_mission": self.requesting_mission, "request_id": self.request_id,
            "requested_capability": self.requested_capability, "objective": self.objective,
            "scope": self.scope, "urgency": self.urgency, "expected_output": self.expected_output,
        }
        missing = [name for name, value in required.items() if not str(value).strip()]
        if missing:
            raise ApoyoError(f"REQUEST_MISSING_FIELDS: {','.join(missing)}")
        if not self.authority.get("CAN_INVOKE", False):
            raise ApoyoError("REQUEST_AUTHORITY_DENIED")


@dataclass(frozen=True, slots=True)
class ReplicationRequest:
    requesting_mission: str
    request_id: str
    requested_capability: str
    objective: str
    scope: str
    authority: Mapping[str, bool]
    preferred_account: str | None = None


class ApoyoRuntime:
    """Persistent APOYO runtime with explicit presence, reception and succession control.

    Repository state can prove logical continuity and record a required successor.
    It must never claim an external process/session exists unless a verified
    provisioner actually materializes it.
    """

    SCHEMA_VERSION = "1.1"
    MISSION_ID = "APOYO"
    MEETING_POINT_ID = "APOYO-MEETING-POINT"

    def __init__(self, repository_root: Path | str, state_path: Path | str | None = None) -> None:
        self.root = Path(repository_root).resolve()
        self.registry = MissionRegistry(self.root)
        self.state_path = Path(state_path).resolve() if state_path else self.root / "docs" / "missions" / "apoyo" / "APOYO_MISSION_STATE.json"
        self.lock_path = self.state_path.with_suffix(self.state_path.suffix + ".lock")
        self.account_path = self.root / "docs" / "missions" / "apoyo" / "APOYO_ACCOUNT_AUTHORIZATION.json"
        self.contract_path = self.root / "docs" / "missions" / "apoyo" / "APOYO_INVOCATION_CONTRACT.json"

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _version(state: Mapping[str, Any]) -> str:
        payload = dict(state)
        payload.pop("state_version", None)
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]

    def load(self) -> dict[str, Any]:
        try:
            state = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ApoyoError("APOYO_STATE_UNREADABLE") from exc
        self._validate_state(state)
        return state

    def discover(self) -> dict[str, Any]:
        try:
            mission = self.registry.get(self.MISSION_ID)
        except MissionRegistryError as exc:
            raise ApoyoError("APOYO_NOT_REGISTERED") from exc
        state = self.load()
        return {"mission_id": self.MISSION_ID, "canonical_name": mission["canonical_name"],
                "meeting_point": state["meeting_point"], "contract": str(self.contract_path.relative_to(self.root)),
                "state": state["state"]}

    def bootstrap(self) -> dict[str, Any]:
        state = self.load()
        self._assert_identity(state)
        state["mission_lifecycle"] = "ACTIVE"
        state["state"] = "WAITING_AT_MEETING_POINT"
        state["meeting_point"]["availability_state"] = "WAITING"
        state["meeting_point"]["current_instance"] = state["instance_id"]
        state["instances"][state["instance_id"]]["state"] = "WAITING_AT_MEETING_POINT"
        self._event(state, "MEETING_POINT_OCCUPIED", instance_id=state["instance_id"])
        state["completion"] = self._completion_snapshot(state, mission_complete=False)
        self._persist(state)
        return state

    def occupy_meeting_point(self, *, instance_id: str | None = None) -> dict[str, Any]:
        state = self.load()
        instance_id = instance_id or state["instance_id"]
        if instance_id not in state["instances"]:
            raise ApoyoError("UNKNOWN_APOYO_INSTANCE")
        current = state["meeting_point"].get("current_instance")
        if current and current != instance_id and self._instance_is_live(state, current):
            return {"claimed": False, "reason": "MEETING_POINT_ALREADY_OCCUPIED", "current_instance": current}
        state["meeting_point"]["current_instance"] = instance_id
        state["meeting_point"]["availability_state"] = "WAITING"
        state["state"] = "WAITING_AT_MEETING_POINT"
        state["mission_lifecycle"] = "ACTIVE"
        state["instances"][instance_id]["state"] = "WAITING_AT_MEETING_POINT"
        self._event(state, "MEETING_POINT_OCCUPIED", instance_id=instance_id)
        state["completion"] = self._completion_snapshot(state, mission_complete=False)
        self._persist(state)
        return {"claimed": True, "instance_id": instance_id, "meeting_point": self.MEETING_POINT_ID}

    def recover_role(self, command: str) -> dict[str, Any]:
        normalized = " ".join(command.strip().upper().split())
        if normalized not in RECOVERY_COMMANDS:
            raise ApoyoError("NOT_AN_APOYO_ROLE_RECOVERY_COMMAND")
        state = self.load()
        self._assert_identity(state)
        state["state"] = "RECOVERING"
        state["mission_lifecycle"] = "ACTIVE"
        state["meeting_point"]["current_instance"] = state["instance_id"]
        state["meeting_point"]["availability_state"] = "WAITING"
        self._event(state, "ROLE_RECOVERED", command=normalized)
        self._persist(state)
        self.occupy_meeting_point(instance_id=state["instance_id"])
        return self.load()

    def register_agent_presence(self, *, agent_id: str, mission_id: str, account: str | None,
                                repository: str, activity: str, state_name: str,
                                capability_refs: Sequence[str] = (), task: str | None = None) -> dict[str, Any]:
        if not agent_id.strip() or not mission_id.strip() or not repository.strip() or not state_name.strip():
            raise ApoyoError("AGENT_PRESENCE_FIELDS_REQUIRED")
        if mission_id == self.MISSION_ID:
            raise ApoyoError("USE_INSTANCE_REGISTRATION_FOR_APOYO")
        if mission_id not in PRINCIPAL_ACTOR_IDS:
            try:
                self.registry.get(mission_id)
            except MissionRegistryError as exc:
                raise ApoyoError(f"AGENT_MISSION_NOT_DISCOVERABLE: {mission_id}") from exc
        state = self.load()
        prior = state["known_agents"].get(agent_id, {})
        state["known_agents"][agent_id] = {
            "agent_id": agent_id, "mission_id": mission_id, "account": account,
            "repository": repository, "activity": activity, "state": state_name.upper(),
            "task": task, "capability_refs": list(capability_refs), "greeted": bool(prior.get("greeted", False)),
            "support_offered": bool(prior.get("support_offered", False)), "updated_at": self._now(),
        }
        self._event(state, "AGENT_ARRIVED", agent_id=agent_id, mission_id=mission_id, state=state_name.upper())
        state["mission_lifecycle"] = "ACTIVE"
        state["completion"] = self._completion_snapshot(state, mission_complete=False)
        self._persist(state)
        return state["known_agents"][agent_id]

    def remove_agent_presence(self, agent_id: str) -> dict[str, Any]:
        state = self.load()
        if agent_id in state["known_agents"]:
            state["known_agents"][agent_id]["state"] = "FINISHED"
            state["known_agents"][agent_id]["updated_at"] = self._now()
            self._event(state, "AGENT_DEPARTED", agent_id=agent_id)
            self._persist(state)
        return state

    def scan_active_agents(self) -> dict[str, Any]:
        state = self.load()
        active = [dict(agent) for agent in state["known_agents"].values() if agent.get("state", "").upper() in ACTIVE_AGENT_STATES]
        prospective = [dict(agent) for agent in state["known_agents"].values() if agent.get("state", "").upper() in PROSPECTIVE_AGENT_STATES]
        return {"agents": active, "active_agent": bool(active), "prospective_agents": prospective,
                "prospective_agent": bool(prospective), "source": "PERSISTED_AGENT_PRESENCE", "runtime_liveness_proven": False}

    def greet_agent(self, agent_id: str, *, non_intrusive: bool = True) -> dict[str, Any]:
        state = self.load()
        agent = state["known_agents"].get(agent_id)
        if not agent:
            raise ApoyoError("AGENT_NOT_REGISTERED")
        if not non_intrusive:
            raise ApoyoError("GREETING_REQUIRES_NON_INTRUSIVE_WINDOW")
        agent["greeted"] = True
        agent["updated_at"] = self._now()
        state["known_agents"][agent_id] = agent
        self._event(state, "AGENT_GREETED", agent_id=agent_id, mission_id=agent["mission_id"])
        state["mission_lifecycle"] = "ACTIVE"
        self._persist(state)
        return {"agent_id": agent_id, "status": "GREETING_RECORDED", "non_intrusive": True}

    def offer_support(self, agent_id: str, *, candidate_tasks: Sequence[str] = ()) -> dict[str, Any]:
        state = self.load()
        agent = state["known_agents"].get(agent_id)
        if not agent:
            raise ApoyoError("AGENT_NOT_REGISTERED")
        tasks = [str(t).strip() for t in candidate_tasks if str(t).strip()]
        if not tasks:
            tasks = [
                "auxiliary analysis or evidence review", "targeted verification or test execution",
                "documentation/evidence retrieval", "audit, contradiction or deduplication check", "handoff preparation",
            ]
        agent["support_offered"] = True
        agent["support_offer"] = {"tasks": tasks, "at": self._now(), "subordinate": True}
        agent["updated_at"] = self._now()
        state["known_agents"][agent_id] = agent
        self._event(state, "SUPPORT_OFFERED", agent_id=agent_id, candidate_tasks=tasks)
        state["mission_lifecycle"] = "ACTIVE"
        self._persist(state)
        return {"agent_id": agent_id, "status": "SUPPORT_OFFERED", "candidate_tasks": tasks, "subordinate": True}

    def assign_support_task(self, *, agent_id: str, request_id: str, capability: str,
                            objective: str, scope: str, authority: Mapping[str, bool],
                            expected_output: str = "result") -> dict[str, Any]:
        if not authority.get("CAN_INVOKE", False):
            raise ApoyoError("REQUEST_AUTHORITY_DENIED")
        state = self.load()
        agent = state["known_agents"].get(agent_id)
        if not agent:
            raise ApoyoError("AGENT_NOT_REGISTERED")
        if request_id in state["active_collaborations"] or request_id in state["completed_collaborations"]:
            raise ApoyoError("REQUEST_ID_ALREADY_USED")
        mission_id = agent["mission_id"]
        if mission_id not in PRINCIPAL_ACTOR_IDS:
            self._verify_requesting_mission(mission_id)
        collaboration = {
            "request_id": request_id, "requesting_mission": mission_id, "requesting_agent": agent_id,
            "requested_capability": capability, "objective": objective, "scope": scope, "urgency": "assigned",
            "constraints": [], "expected_output": expected_output, "authority": dict(authority), "state": "ASSIGNED",
            "instance_id": state["instance_id"], "created_at": self._now(), "updated_at": self._now(),
            "result": None, "evidence_refs": [],
        }
        state["active_collaborations"][request_id] = collaboration
        state["support_queue"] = [x for x in state.get("support_queue", []) if x.get("request_id") != request_id]
        self._event(state, "TASK_ASSIGNED", request_id=request_id, agent_id=agent_id, mission_id=mission_id)
        state["mission_lifecycle"] = "ACTIVE"
        state["state"] = "ASSISTING"
        state["instances"][state["instance_id"]]["state"] = "ASSISTING"
        self._persist(state)
        return collaboration

    def ensure_successor(self, *, reason: str, requesting_mission: str | None = None,
                          task_request_id: str | None = None) -> dict[str, Any]:
        if not reason.strip():
            raise ApoyoError("SUCCESSOR_REASON_REQUIRED")
        state = self.load()
        current = state["instance_id"]
        live_others = [i for i in state["instances"].values() if i["instance_id"] != current and self._instance_is_live(i)]
        if live_others and any(i.get("meeting_point_status") == "OCCUPIED" for i in live_others):
            return {"status": "ALREADY_COVERED", "instance_id": live_others[0]["instance_id"]}
        slot = state.setdefault("successor_slots", {})
        existing = slot.get(self.MEETING_POINT_ID)
        if existing and existing.get("status") in {"ACTIVATION_REQUIRED", "ACTIVATING", "READY"}:
            return existing
        next_id = self._next_global_instance_id(state)
        spec = {
            "lineage_id": state.get("lineage_id", "APOYO-LINEAGE-ROOT"), "parent_instance_id": current,
            "successor_instance_id": next_id, "instance_id": next_id, "generation": state["generation"] + 1,
            "creation_reason": reason, "creation_timestamp": self._now(), "meeting_point_status": "ACTIVATION_REQUIRED",
            "assigned_task": None, "requesting_mission": requesting_mission, "task_request_id": task_request_id,
            "status": "ACTIVATION_REQUIRED", "materialized": False,
            "runtime_boundary": "NO_VERIFIED_EXTERNAL_SESSION_PROVISIONER",
        }
        slot[self.MEETING_POINT_ID] = spec
        state["replication_history"].append(spec)
        self._event(state, "SUCCESSOR_REQUIRED", **{k: spec[k] for k in ("parent_instance_id", "successor_instance_id", "creation_reason")})
        self._event(state, "SUCCESSOR_ACTIVATION_REQUIRED", successor_instance_id=next_id, meeting_point=self.MEETING_POINT_ID)
        state["mission_lifecycle"] = "ACTIVE"
        self._persist(state)
        return spec

    def execute_support_task(self, request_id: str) -> dict[str, Any]:
        state = self.load()
        collaboration = self._active(state, request_id)
        collaboration["state"] = "RUNNING"
        collaboration["updated_at"] = self._now()
        state["active_collaborations"][request_id] = collaboration
        state["state"] = "EXECUTING_SUPPORT_TASK"
        state["instances"][state["instance_id"]]["state"] = "EXECUTING_SUPPORT_TASK"
        self._event(state, "TASK_STARTED", request_id=request_id)
        self._persist(state)
        return collaboration

    def invoke(self, request: CollaborationRequest) -> dict[str, Any]:
        request.validate()
        self._verify_requesting_mission(request.requesting_mission)
        state = self.load()
        state["mission_lifecycle"] = "ACTIVE"
        if request.request_id in state["active_collaborations"] or request.request_id in state["completed_collaborations"]:
            raise ApoyoError("REQUEST_ID_ALREADY_USED")
        if self._would_duplicate(request, state):
            self._event(state, "NO_ACTION_DUPLICATE", request_id=request.request_id)
            self._persist(state)
            return {"status": "NO_ACTION", "reason": "DUPLICATE_OR_ALREADY_COVERED"}
        collaboration = {
            "request_id": request.request_id, "requesting_mission": request.requesting_mission,
            "requested_capability": request.requested_capability, "objective": request.objective, "scope": request.scope,
            "urgency": request.urgency, "constraints": list(request.constraints), "expected_output": request.expected_output,
            "authority": dict(request.authority), "existing_work_refs": list(request.existing_work_refs),
            "capability_gap": request.capability_gap, "deadline_if_any": request.deadline_if_any, "state": "INVOKED",
            "instance_id": state["instance_id"], "created_at": self._now(), "updated_at": self._now(),
            "result": None, "evidence_refs": [],
        }
        state["active_collaborations"][request.request_id] = collaboration
        state["meeting_point"]["active_collaborations"].append(request.request_id)
        state["meeting_point"]["availability_state"] = "ASSIGNED"
        state["state"] = "INVOKED"
        state["instances"][state["instance_id"]]["state"] = "INVOKED"
        self._event(state, "TASK_REQUESTED", request_id=request.request_id)
        self._persist(state)
        return collaboration

    def accept(self, request_id: str) -> dict[str, Any]:
        return self._transition_collaboration(request_id, "ACCEPTED")

    def validate(self, request_id: str, *, evidence_refs: Sequence[str]) -> dict[str, Any]:
        if not evidence_refs:
            raise ApoyoError("VALIDATION_REQUIRES_EVIDENCE")
        state = self.load()
        collaboration = self._active(state, request_id)
        collaboration["state"] = "VALIDATING"
        collaboration["evidence_refs"] = list(evidence_refs)
        collaboration["updated_at"] = self._now()
        state["active_collaborations"][request_id] = collaboration
        state["state"] = "VALIDATING"
        self._event(state, "TASK_VALIDATING", request_id=request_id)
        self._persist(state)
        return collaboration

    def return_control(self, request_id: str, *, result: str, evidence_refs: Sequence[str]) -> dict[str, Any]:
        if not result.strip() or not evidence_refs:
            raise ApoyoError("HANDOFF_REQUIRES_RESULT_AND_EVIDENCE")
        state = self.load()
        collaboration = self._active(state, request_id)
        collaboration.update({"state": "RETURNING_CONTROL", "result": result, "evidence_refs": list(evidence_refs), "updated_at": self._now()})
        state["active_collaborations"][request_id] = collaboration
        state["state"] = "PERSISTING"
        self._event(state, "TASK_COMPLETED", request_id=request_id)
        self._persist(state)
        collaboration["state"] = "COMPLETED"
        state["completed_collaborations"][request_id] = collaboration
        del state["active_collaborations"][request_id]
        state["meeting_point"]["active_collaborations"] = [x for x in state["meeting_point"]["active_collaborations"] if x != request_id]
        state["meeting_point"]["availability_state"] = "WAITING"
        state["state"] = "RETURNING_TO_MEETING_POINT"
        state["instances"][state["instance_id"]]["state"] = "RETURNING_TO_MEETING_POINT"
        state["handoffs"].append({"request_id": request_id, "requesting_mission": collaboration["requesting_mission"], "result": result, "evidence_refs": list(evidence_refs), "at": self._now()})
        self._event(state, "RESULT_RETURNED", request_id=request_id)
        self._event(state, "SUPPORT_CONTINUES", request_id=request_id)
        state["mission_lifecycle"] = "ACTIVE"
        state["completion"] = self._completion_snapshot(state, mission_complete=False)
        self._persist(state)
        return collaboration

    def request_replication(self, request: ReplicationRequest) -> dict[str, Any]:
        if not request.authority.get("CAN_INVOKE", False):
            raise ApoyoError("REPLICATION_AUTHORITY_DENIED")
        self._verify_requesting_mission(request.requesting_mission)
        if not request.objective.strip() or not request.scope.strip() or not request.requested_capability.strip():
            raise ApoyoError("REPLICATION_SCOPE_INCOMPLETE")
        accounts = self._load_accounts()
        account = self._select_account(accounts, request.preferred_account)
        state = self.load()
        instance_id = self._next_global_instance_id(state)
        spec = {
            "instance_id": instance_id, "parent_instance_id": state["instance_id"], "generation": state["generation"] + 1,
            "requested_by": request.requesting_mission, "request_id": request.request_id, "assigned_scope": request.scope,
            "requested_capability": request.requested_capability, "account": account,
            "status": "REPLICATION_NOT_EXECUTABLE_IN_CURRENT_RUNTIME",
            "reason": "No verified external session provisioner is available to this repository runtime.",
            "materialized": False, "created_at": self._now(),
        }
        state["replication_history"].append(spec)
        self._event(state, "REPLICATION_REQUESTED", request_id=request.request_id, instance_id=instance_id, status=spec["status"])
        self._persist(state)
        return spec

    def can_complete(self) -> dict[str, Any]:
        state = self.load()
        scan = self.scan_active_agents()
        pending_collaborations = bool(state["active_collaborations"])
        pending_handoffs = bool(state.get("pending_handoffs", []))
        active_support_instances = [i for i in state["instances"].values() if self._instance_requires_coordination(i)]
        useful_support_tasks = bool(state.get("support_queue", []))
        executable_internal_work = bool(state.get("internal_work_queue", []))
        successor_needed = self._successor_needed(state)
        no_reason_to_keep_meeting_point = not (scan["active_agent"] or scan["prospective_agent"] or pending_collaborations or pending_handoffs or useful_support_tasks or executable_internal_work or successor_needed)
        complete = no_reason_to_keep_meeting_point and not active_support_instances
        return {
            "mission_complete": complete, "active_agents": len(scan["agents"]), "prospective_agents": len(scan["prospective_agents"]),
            "pending_collaborations": pending_collaborations, "pending_handoffs": pending_handoffs,
            "active_support_instances": len(active_support_instances), "useful_support_tasks": useful_support_tasks,
            "executable_internal_work": executable_internal_work, "successor_needed": successor_needed,
            "meeting_point_required": not no_reason_to_keep_meeting_point,
        }

    def final_scan(self) -> dict[str, Any]:
        result = self.can_complete()
        state = self.load()
        if not result["mission_complete"]:
            state["mission_lifecycle"] = "ACTIVE"
            state["completion"] = result
            self._persist(state)
            return result
        state["state"] = "RETIRED"
        state["mission_lifecycle"] = "COMPLETED"
        state["completion"] = result
        state["completed_at"] = self._now()
        self._event(state, "MISSION_COMPLETED")
        self._persist(state)
        return result

    def recover(self) -> dict[str, Any]:
        return self.recover_role("APOYO")

    def _verify_requesting_mission(self, mission_id: str) -> None:
        if mission_id == self.MISSION_ID:
            raise ApoyoError("SELF_INVOCATION_NOT_ALLOWED")
        if mission_id in PRINCIPAL_ACTOR_IDS:
            return
        try:
            self.registry.get(mission_id)
        except MissionRegistryError as exc:
            raise ApoyoError(f"REQUESTING_MISSION_NOT_DISCOVERABLE: {mission_id}") from exc

    @staticmethod
    def _would_duplicate(request: CollaborationRequest, state: Mapping[str, Any]) -> bool:
        requested = request.requested_capability.casefold()
        objective = request.objective.casefold()
        for item in state.get("active_collaborations", {}).values():
            if item.get("requesting_mission") == request.requesting_mission and (
                item.get("requested_capability", "").casefold() == requested or item.get("objective", "").casefold() == objective
            ):
                return True
        return False

    @staticmethod
    def _active(state: Mapping[str, Any], request_id: str) -> dict[str, Any]:
        item = state.get("active_collaborations", {}).get(request_id)
        if not isinstance(item, dict):
            raise ApoyoError(f"COLLABORATION_NOT_ACTIVE: {request_id}")
        return dict(item)

    def _transition_collaboration(self, request_id: str, new_state: str) -> dict[str, Any]:
        if new_state not in COLLABORATION_STATES:
            raise ApoyoError("INVALID_COLLABORATION_STATE")
        state = self.load()
        collaboration = self._active(state, request_id)
        collaboration["state"] = new_state
        collaboration["updated_at"] = self._now()
        state["active_collaborations"][request_id] = collaboration
        state["state"] = "ASSISTING" if new_state in {"ACCEPTED", "RUNNING"} else new_state
        state["instances"][state["instance_id"]]["state"] = state["state"]
        self._event(state, "TASK_ACCEPTED" if new_state == "ACCEPTED" else "COLLABORATION_STATE", request_id=request_id, state=new_state)
        self._persist(state)
        return collaboration

    def _load_accounts(self) -> dict[str, Any]:
        try:
            accounts = json.loads(self.account_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ApoyoError("ACCOUNT_AUTHORIZATION_UNREADABLE") from exc
        authorized = accounts.get("authorized_accounts")
        if accounts.get("required_account_count") != 3 or not isinstance(authorized, list) or len(authorized) != 3:
            raise ApoyoError("ACCOUNT_AUTHORIZATION_INVALID")
        if any(not isinstance(item, str) or not item.strip() for item in authorized):
            raise ApoyoError("ACCOUNT_AUTHORIZATION_NOT_CONFIGURED")
        if accounts.get("status") != "ACTIVE":
            raise ApoyoError("ACCOUNT_AUTHORIZATION_NOT_ACTIVE")
        return accounts

    @staticmethod
    def _select_account(accounts: Mapping[str, Any], preferred: str | None) -> str:
        values = list(accounts["authorized_accounts"])
        if preferred is not None and preferred not in values:
            raise ApoyoError("PREFERRED_ACCOUNT_NOT_AUTHORIZED")
        return preferred if preferred is not None else values[0]

    @staticmethod
    def _next_global_instance_id(state: Mapping[str, Any]) -> str:
        existing = state.get("instances", {})
        index = len(existing)
        while f"APOYO-{index:03d}" in existing:
            index += 1
        return f"APOYO-{index:03d}"

    @staticmethod
    def _instance_is_live(state_or_instance: Mapping[str, Any], instance_id: str | None = None) -> bool:
        item = state_or_instance.get(instance_id) if instance_id is not None else state_or_instance
        return isinstance(item, Mapping) and item.get("state") not in {None, "WAITING", "WAITING_AT_MEETING_POINT", "RETIRED", "FINISHED"}

    @classmethod
    def _instance_requires_coordination(cls, item: Mapping[str, Any]) -> bool:
        return item.get("state") not in {"WAITING", "WAITING_AT_MEETING_POINT", "READY", "RETIRED", "FINISHED"}

    @staticmethod
    def _successor_needed(state: Mapping[str, Any]) -> bool:
        slot = state.get("successor_slots", {}).get(ApoyoRuntime.MEETING_POINT_ID)
        return bool(slot and slot.get("status") == "ACTIVATION_REQUIRED")

    @staticmethod
    def _completion_snapshot(state: Mapping[str, Any], *, mission_complete: bool) -> dict[str, Any]:
        active_agents = [a for a in state.get("known_agents", {}).values() if a.get("state", "").upper() in ACTIVE_AGENT_STATES]
        prospective = [a for a in state.get("known_agents", {}).values() if a.get("state", "").upper() in PROSPECTIVE_AGENT_STATES]
        active_instances = [i for i in state.get("instances", {}).values() if ApoyoRuntime._instance_requires_coordination(i)]
        return {"mission_complete": mission_complete, "active_agents": len(active_agents), "prospective_agents": len(prospective),
                "pending_collaborations": bool(state.get("active_collaborations")), "pending_handoffs": bool(state.get("pending_handoffs", [])),
                "active_support_instances": len(active_instances), "useful_support_tasks": bool(state.get("support_queue", [])),
                "executable_internal_work": bool(state.get("internal_work_queue", [])), "successor_needed": ApoyoRuntime._successor_needed(state)}

    def _event(self, state: dict[str, Any], event_type: str, **payload: Any) -> None:
        state.setdefault("events", []).append({"type": event_type, "at": self._now(), **payload})

    def _persist(self, state: dict[str, Any]) -> None:
        with self._lock():
            current = self.load() if self.state_path.exists() else None
            if current is not None and state.get("state_version") not in {current.get("state_version"), "GENESIS"}:
                raise ApoyoError("STALE_STATE_VERSION")
            state["state_version"] = self._version(state)
            state["meeting_point"]["last_checkpoint"] = state["state_version"]
            self.state_path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp_name = tempfile.mkstemp(prefix=f".{self.state_path.name}.", dir=str(self.state_path.parent), text=True)
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    json.dump(state, handle, ensure_ascii=False, indent=2)
                    handle.write("\n")
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(tmp_name, self.state_path)
            finally:
                if os.path.exists(tmp_name):
                    os.unlink(tmp_name)

    @staticmethod
    def _assert_identity(state: Mapping[str, Any]) -> None:
        if state.get("mission_id") != ApoyoRuntime.MISSION_ID or state.get("identity", {}).get("canonical_name") != ApoyoRuntime.MISSION_ID:
            raise ApoyoError("IDENTITY_MISMATCH")

    @staticmethod
    def _validate_state(state: Mapping[str, Any]) -> None:
        if state.get("schema_version") != ApoyoRuntime.SCHEMA_VERSION or state.get("mission_id") != ApoyoRuntime.MISSION_ID:
            raise ApoyoError("INVALID_APOYO_STATE_IDENTITY")
        if state.get("state") not in APOYO_STATES:
            raise ApoyoError("INVALID_APOYO_STATE")
        for field in ("instances", "active_collaborations", "completed_collaborations", "known_agents", "meeting_point"):
            if not isinstance(state.get(field), dict):
                raise ApoyoError(f"INVALID_APOYO_STATE_STRUCTURE: {field}")
        if state.get("mission_lifecycle") not in {"ACTIVE", "COMPLETED"}:
            raise ApoyoError("INVALID_APOYO_LIFECYCLE")
        if state["meeting_point"].get("meeting_point_id") != ApoyoRuntime.MEETING_POINT_ID:
            raise ApoyoError("INVALID_MEETING_POINT_ID")

    @contextmanager
    def _lock(self) -> Iterator[None]:
        if fcntl is None:
            raise ApoyoError("CONCURRENCY_UNSUPPORTED: POSIX file locking is required")
        self.lock_path.parent.mkdir(parents=True, exist_ok=True)
        with self.lock_path.open("a+") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
