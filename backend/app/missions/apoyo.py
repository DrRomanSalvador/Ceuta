from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any, Iterator, Mapping, Sequence
from uuid import uuid4

try:
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None

from .registry import MissionRegistry, MissionRegistryError


class ApoyoError(RuntimeError):
    """Raised when an APOYO invariant cannot be safely enforced."""


APOYO_STATES = {
    "BORN", "REGISTERED", "WAITING", "DISCOVERING", "INVOKED", "ASSISTING",
    "VALIDATING", "PERSISTING", "RETURNING_CONTROL", "REPLICATING", "RECOVERING", "RETIRED",
}
COLLABORATION_STATES = {"INVOKED", "ASSISTING", "VALIDATING", "PERSISTING", "RETURNING_CONTROL", "COMPLETED", "REJECTED"}


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
            "requesting_mission": self.requesting_mission,
            "request_id": self.request_id,
            "requested_capability": self.requested_capability,
            "objective": self.objective,
            "scope": self.scope,
            "urgency": self.urgency,
            "expected_output": self.expected_output,
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
    """Persistent repository-side APOYO collaboration runtime.

    The runtime owns mission state and collaboration protocol. It does not claim
    to create external sessions, accounts or processes; those remain an external
    runtime boundary unless a verified provisioner is supplied by the deployment.
    """

    SCHEMA_VERSION = "1.0"
    MISSION_ID = "APOYO"

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
        return {
            "mission_id": self.MISSION_ID,
            "canonical_name": mission["canonical_name"],
            "meeting_point": self.load()["meeting_point"],
            "contract": str(self.contract_path.relative_to(self.root)),
            "state": self.load()["state"],
        }

    def bootstrap(self) -> dict[str, Any]:
        state = self.load()
        if state["mission_id"] != self.MISSION_ID:
            raise ApoyoError("IDENTITY_MISMATCH")
        state["state"] = "WAITING"
        state["instances"][state["instance_id"]]["state"] = "WAITING"
        self._persist(state)
        return state

    def invoke(self, request: CollaborationRequest) -> dict[str, Any]:
        request.validate()
        self._verify_requesting_mission(request.requesting_mission)
        state = self.load()
        if request.request_id in state["active_collaborations"] or request.request_id in state["completed_collaborations"]:
            raise ApoyoError("REQUEST_ID_ALREADY_USED")
        if self._would_duplicate(request, state):
            state["events"].append({"type": "NO_ACTION_DUPLICATE", "request_id": request.request_id, "at": self._now()})
            self._persist(state)
            return {"status": "NO_ACTION", "reason": "DUPLICATE_OR_ALREADY_COVERED"}
        collaboration = {
            "request_id": request.request_id,
            "requesting_mission": request.requesting_mission,
            "requested_capability": request.requested_capability,
            "objective": request.objective,
            "scope": request.scope,
            "urgency": request.urgency,
            "constraints": list(request.constraints),
            "expected_output": request.expected_output,
            "authority": dict(request.authority),
            "existing_work_refs": list(request.existing_work_refs),
            "capability_gap": request.capability_gap,
            "deadline_if_any": request.deadline_if_any,
            "state": "INVOKED",
            "instance_id": state["instance_id"],
            "created_at": self._now(),
            "updated_at": self._now(),
            "result": None,
            "evidence_refs": [],
        }
        state["active_collaborations"][request.request_id] = collaboration
        state["meeting_point"]["availability_state"] = "INVOKED"
        state["meeting_point"]["active_collaborations"].append(request.request_id)
        state["state"] = "INVOKED"
        state["instances"][state["instance_id"]]["state"] = "INVOKED"
        state["events"].append({"type": "COLLABORATION_INVOKED", "request_id": request.request_id, "at": self._now()})
        self._persist(state)
        return collaboration

    def accept(self, request_id: str) -> dict[str, Any]:
        return self._transition_collaboration(request_id, "ASSISTING")

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
        self._persist(state)
        collaboration["state"] = "COMPLETED"
        state["completed_collaborations"][request_id] = collaboration
        del state["active_collaborations"][request_id]
        state["meeting_point"]["active_collaborations"] = [x for x in state["meeting_point"]["active_collaborations"] if x != request_id]
        state["meeting_point"]["availability_state"] = "WAITING" if not state["active_collaborations"] else "ASSISTING"
        state["state"] = "WAITING" if not state["active_collaborations"] else "ASSISTING"
        instance_id = state["instance_id"]
        state["instances"][instance_id]["state"] = state["state"]
        state["handoffs"].append({"request_id": request_id, "requesting_mission": collaboration["requesting_mission"], "result": result, "evidence_refs": list(evidence_refs), "at": self._now()})
        state["events"].append({"type": "RETURN_CONTROL", "request_id": request_id, "at": self._now()})
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
        instance_id = self._next_instance_id(state, parent=state["instance_id"])
        spec = {
            "instance_id": instance_id,
            "parent_instance": state["instance_id"],
            "generation": state["generation"] + 1,
            "requested_by": request.requesting_mission,
            "request_id": request.request_id,
            "assigned_scope": request.scope,
            "requested_capability": request.requested_capability,
            "account": account,
            "status": "REPLICATION_NOT_EXECUTABLE_IN_CURRENT_RUNTIME",
            "reason": "No verified external session provisioner is available to this repository runtime.",
            "created_at": self._now(),
        }
        state["replication_history"].append(spec)
        state["events"].append({"type": "REPLICATION_REQUESTED", "request_id": request.request_id, "instance_id": instance_id, "status": spec["status"], "at": self._now()})
        self._persist(state)
        return spec

    def recover(self) -> dict[str, Any]:
        state = self.load()
        state["state"] = "RECOVERING"
        for instance in state["instances"].values():
            if instance.get("state") not in {"WAITING", "RETIRED"}:
                instance["state"] = "RECOVERING"
        state["events"].append({"type": "RECOVERY", "at": self._now()})
        self._persist(state)
        state["state"] = "WAITING" if not state["active_collaborations"] else "ASSISTING"
        state["instances"][state["instance_id"]]["state"] = state["state"]
        self._persist(state)
        return state

    def _verify_requesting_mission(self, mission_id: str) -> None:
        if mission_id == self.MISSION_ID:
            raise ApoyoError("SELF_INVOCATION_NOT_ALLOWED")
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
                item.get("requested_capability", "").casefold() == requested
                or item.get("objective", "").casefold() == objective
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
        state["state"] = new_state
        state["instances"][state["instance_id"]]["state"] = new_state
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
        if preferred is not None:
            if preferred not in values:
                raise ApoyoError("PREFERRED_ACCOUNT_NOT_AUTHORIZED")
            return preferred
        for account in values:
            return account
        raise ApoyoError("NO_ACCOUNT_AVAILABLE")

    @staticmethod
    def _next_instance_id(state: Mapping[str, Any], parent: str) -> str:
        generation = int(state.get("generation", 0)) + 1
        prefix = f"{parent}-001"
        candidates = [key for key in state.get("instances", {}) if key.startswith(prefix)]
        return f"{parent}-{len(candidates) + 1:03d}"

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
    def _validate_state(state: Mapping[str, Any]) -> None:
        if state.get("schema_version") != ApoyoRuntime.SCHEMA_VERSION or state.get("mission_id") != ApoyoRuntime.MISSION_ID:
            raise ApoyoError("INVALID_APOYO_STATE_IDENTITY")
        if state.get("state") not in APOYO_STATES:
            raise ApoyoError("INVALID_APOYO_STATE")
        if not isinstance(state.get("instances"), dict) or not isinstance(state.get("active_collaborations"), dict):
            raise ApoyoError("INVALID_APOYO_STATE_STRUCTURE")

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
