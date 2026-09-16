"""Constitutional COORDINATOR and ESPEJO runtime.

This module extends the existing control-plane/event-log primitives.  It does
not create a second mission registry: coordination state is a projection of
mission/agent/task/command state and is persisted with version checks and the
existing append-only event log.
"""
from __future__ import annotations

import copy
import json
import os
import tempfile
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Iterator

from .event_log import append_payload

try:
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None


STATE_PATH = Path(__file__).with_name("COORDINATION_STATE.json")
EVENT_PATH = Path(__file__).with_name("MISSION_EVENT_LOG.jsonl")


class Authority(str, Enum):
    HUMAN = "HUMAN_AUTHORITY"
    CONSTITUTION = "CONSTITUTION"
    SECURITY = "SECURITY"
    COORDINATOR = "COORDINATOR"
    MISSION = "MISSION_CONTRACT"
    AGENT = "AGENT_PREFERENCE"
    MIRROR = "MIRROR_PREFERENCE"


class CommandType(str, Enum):
    CONTINUE = "CONTINUE"
    CHECKPOINT = "CHECKPOINT"
    SPLIT = "SPLIT"
    REQUEST_MIRROR = "REQUEST_MIRROR"
    PAUSE = "PAUSE"
    STANDBY = "STANDBY"
    RESUME = "RESUME"
    REDIRECT = "REDIRECT"
    DELEGATE = "DELEGATE"
    HANDOFF = "HANDOFF"
    RECOVER = "RECOVER"
    ABANDON = "ABANDON"
    REPRIORITIZE = "REPRIORITIZE"


class CommandState(str, Enum):
    ISSUED = "ISSUED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    EXECUTING = "EXECUTING"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    CONFLICT = "COMMAND_CONFLICT"


class MirrorAction(str, Enum):
    ASSIST = "ASSIST"
    REVIEW = "REVIEW"
    VERIFY = "VERIFY"
    RESEARCH = "RESEARCH"
    TEST = "TEST"
    RED_TEAM = "RED_TEAM"
    CHECKPOINT = "CHECKPOINT"
    RECOVERY = "RECOVERY"
    PREPARE = "PREPARE"


class MirrorState(str, Enum):
    REQUESTED = "REQUESTED"
    OBSERVING = "OBSERVING"
    AUTHORITY_CHECKED = "AUTHORITY_CHECKED"
    ASSIGNED = "ASSIGNED"
    EXECUTING = "EXECUTING"
    VALIDATING = "VALIDATING"
    PERSISTED = "PERSISTED"
    HANDOFF = "HANDOFF"
    RETURNED = "RETURNED"
    CONFLICT = "CONFLICT"


class CoordinationError(ValueError):
    """Base error for constitutional coordination violations."""


class StaleStateError(CoordinationError):
    """Mutation was based on an obsolete coordination-state version."""


class CommandConflict(CoordinationError):
    """A command conflicts with a higher authority or existing command."""


class OwnershipConflict(CoordinationError):
    """A mirror attempted to acquire work owned by another actor."""


@dataclass(frozen=True)
class Command:
    order_id: str
    issuer: str
    target: str
    mission: str
    reason: str
    authority_basis: str
    issued_at: str
    state: str
    expected_effect: str
    acknowledgement: str | None
    execution_result: str | None
    command_type: str
    expected_version: int
    reversible: bool = True


@dataclass(frozen=True)
class MirrorInvocation:
    mirror_id: str
    mirror_of: str
    mission: str
    target_agent: str
    task: str
    problem: str
    capability_required: str
    limits: tuple[str, ...]
    priority: str
    authority: str
    expected_result: str
    action: str
    functional_role: str
    state: str
    mission_owner: str
    subtask_owner: str


@dataclass(frozen=True)
class DeferredHypothesis:
    hypothesis_id: str
    author: str
    timestamp: str
    context: str
    reasoning: str
    alternative_proposed: str
    suspension_reason: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _initial_state() -> dict[str, Any]:
    return {
        "schema_version": "1.0.0",
        "state_version": 0,
        "updated_at": utc_now(),
        "agents": {},
        "missions": {},
        "tasks": {},
        "priorities": {},
        "checkpoints": {},
        "commands": {},
        "interventions": [],
        "mirrors": {},
        "standby": {},
        "recovery": [],
        "conflicts": [],
        "handoffs": [],
        "pending_reviews": [],
        "deferred_hypotheses": {},
    }


@contextmanager
def _locked(path: Path) -> Iterator[None]:
    lock_path = path.with_suffix(path.suffix + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as handle:
        if fcntl is not None:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


class CoordinationStore:
    """Versioned, atomic, append-audited coordination projection."""

    def __init__(self, state_path: Path = STATE_PATH, event_path: Path = EVENT_PATH):
        self.state_path = Path(state_path)
        self.event_path = Path(event_path)

    def load(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return _initial_state()
        data = json.loads(self.state_path.read_text(encoding="utf-8"))
        self._validate(data)
        return data

    @staticmethod
    def _validate(data: dict[str, Any]) -> None:
        required = set(_initial_state())
        missing = required - set(data)
        if missing:
            raise CoordinationError(f"coordination state missing fields: {sorted(missing)}")
        if not isinstance(data["state_version"], int) or data["state_version"] < 0:
            raise CoordinationError("invalid coordination state_version")

    def _write(self, data: dict[str, Any]) -> None:
        self._validate(data)
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(prefix="coordination-", suffix=".json", dir=self.state_path.parent)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(data, handle, sort_keys=True, indent=2, ensure_ascii=False)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_name, self.state_path)
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)

    def mutate(self, *, actor: str, event_type: str, mission_id: str,
               expected_version: int | None, mutation: Any) -> dict[str, Any]:
        with _locked(self.state_path):
            state = self.load()
            current = state["state_version"]
            if expected_version is not None and expected_version != current:
                raise StaleStateError(f"expected coordination version {expected_version}, observed {current}")
            new_state = copy.deepcopy(state)
            mutation(new_state)
            new_state["state_version"] = current + 1
            new_state["updated_at"] = utc_now()
            self._write(new_state)
            append_payload(
                self.event_path,
                event_type=event_type,
                mission_id=mission_id,
                actor=actor,
                timestamp=new_state["updated_at"],
                payload={"state_version": new_state["state_version"], "state": event_type},
            )
            return new_state


class Coordinator:
    """Operational coordinator; never a scientific authority or mission owner."""

    IDENTITY = "COORDINATOR"
    COMMANDS = frozenset(CommandType)

    def __init__(self, *, instance_id: str | None = None, store: CoordinationStore | None = None):
        self.instance_id = instance_id or f"COORD-{uuid.uuid4().hex[:12]}"
        self.store = store or CoordinationStore()

    def observe(self) -> dict[str, Any]:
        state = self.store.load()
        return {
            "instance_id": self.instance_id,
            "agents": copy.deepcopy(state["agents"]),
            "missions": copy.deepcopy(state["missions"]),
            "tasks": copy.deepcopy(state["tasks"]),
            "priorities": copy.deepcopy(state["priorities"]),
            "commands": copy.deepcopy(state["commands"]),
            "mirrors": copy.deepcopy(state["mirrors"]),
            "standby": copy.deepcopy(state["standby"]),
            "conflicts": copy.deepcopy(state["conflicts"]),
            "recovery": copy.deepcopy(state["recovery"]),
            "handoffs": copy.deepcopy(state["handoffs"]),
            "pending_reviews": copy.deepcopy(state["pending_reviews"]),
            "state_version": state["state_version"],
        }

    def register_agent(self, agent_id: str, mission_id: str, *, state: str = "ACTIVE", progress: bool = True,
                       expected_version: int | None = None) -> dict[str, Any]:
        def mutation(s: dict[str, Any]) -> None:
            s["agents"][agent_id] = {
                "agent_id": agent_id, "mission_id": mission_id, "state": state,
                "progress": bool(progress), "last_heartbeat": utc_now(),
                "last_checkpoint": None, "last_change": utc_now(),
            }
        return self.store.mutate(actor=self.instance_id, event_type="COORDINATOR_AGENT_REGISTERED", mission_id=mission_id, expected_version=expected_version, mutation=mutation)

    def update_observation(self, agent_id: str, *, state: str, progress: bool, last_checkpoint: str | None = None,
                           expected_version: int | None = None) -> dict[str, Any]:
        def mutation(s: dict[str, Any]) -> None:
            if agent_id not in s["agents"]:
                raise CoordinationError("unknown agent")
            agent = s["agents"][agent_id]
            agent.update({"state": state, "progress": bool(progress), "last_heartbeat": utc_now(), "last_change": utc_now()})
            if last_checkpoint is not None:
                agent["last_checkpoint"] = last_checkpoint
        mission_id = self.store.load()["agents"].get(agent_id, {}).get("mission_id", "UNKNOWN")
        return self.store.mutate(actor=self.instance_id, event_type="COORDINATOR_OBSERVATION", mission_id=mission_id, expected_version=expected_version, mutation=mutation)

    def issue(self, *, command_type: CommandType, target: str, mission: str, reason: str,
              authority_basis: str, expected_effect: str, expected_version: int | None = None,
              reversible: bool = True) -> dict[str, Any]:
        if command_type not in self.COMMANDS:
            raise CoordinationError("unsupported coordinator command")
        if authority_basis not in {Authority.COORDINATOR.value, Authority.HUMAN.value}:
            raise CommandConflict("coordinator command lacks valid operational authority basis")
        if command_type in {CommandType.REDIRECT, CommandType.ABANDON} and authority_basis != Authority.HUMAN.value:
            raise CommandConflict(f"{command_type.value} requires superior/human authority in this runtime")
        order_id = f"ORD-{uuid.uuid4().hex}"
        command = Command(order_id, self.instance_id, target, mission, reason, authority_basis, utc_now(), CommandState.ISSUED.value, expected_effect, None, None, command_type.value, self.store.load()["state_version"], reversible)
        def mutation(s: dict[str, Any]) -> None:
            s["commands"][order_id] = asdict(command)
            s["interventions"].append({"order_id": order_id, "issuer": self.instance_id, "type": command_type.value, "target": target, "mission": mission, "timestamp": command.issued_at})
        return self.store.mutate(actor=self.instance_id, event_type="COORDINATOR_COMMAND_ISSUED", mission_id=mission, expected_version=expected_version, mutation=mutation)

    def request_mirror(self, *, target_agent: str, mission: str, task: str, problem: str,
                       capability_required: str, limits: list[str], priority: str,
                       authority: str, expected_result: str, expected_version: int | None = None) -> dict[str, Any]:
        return self.issue(command_type=CommandType.REQUEST_MIRROR, target=target_agent, mission=mission,
                          reason=problem, authority_basis=authority, expected_effect=expected_result,
                          expected_version=expected_version)

    def checkpoint_then_pause(self, *, target: str, mission: str, checkpoint_id: str,
                              expected_version: int | None = None) -> dict[str, Any]:
        def mutation(s: dict[str, Any]) -> None:
            s["checkpoints"][checkpoint_id] = {"checkpoint_id": checkpoint_id, "mission": mission, "target": target, "created_at": utc_now(), "state": "PERSISTED"}
        state = self.store.mutate(actor=self.instance_id, event_type="COORDINATOR_CHECKPOINT", mission_id=mission, expected_version=expected_version, mutation=mutation)
        return self.issue(command_type=CommandType.PAUSE, target=target, mission=mission, reason="safe pause after checkpoint", authority_basis=Authority.COORDINATOR.value, expected_effect="paused with recoverable checkpoint", expected_version=state["state_version"])

    def standby(self, *, target: str, mission: str, checkpoint_id: str, expected_version: int | None = None) -> dict[str, Any]:
        state = self.store.load()
        if checkpoint_id not in state["checkpoints"]:
            raise CoordinationError("STANDBY requires a persisted checkpoint")
        return self.issue(command_type=CommandType.STANDBY, target=target, mission=mission,
                          reason="temporary operational standby", authority_basis=Authority.COORDINATOR.value,
                          expected_effect="identity and recoverability preserved", expected_version=expected_version)

    def detect_execution(self, agent_id: str) -> str:
        agent = self.store.load()["agents"].get(agent_id)
        if not agent:
            raise CoordinationError("unknown agent")
        if agent["state"] == "ACTIVE" and agent["progress"]:
            return "ACTIVE_PROGRESSING_NO_INTERVENTION"
        if agent["state"] == "ACTIVE" and not agent["progress"]:
            return "ACTIVE_NO_PROGRESS_REVIEW"
        if agent["state"] in {"RUNNING", "EXECUTING"} and agent["progress"]:
            return "LONG_RUNNING_PROGRESS_CONTINUE"
        return "OBSERVE_AND_CLASSIFY"

    def persist_deferred_hypothesis(self, hypothesis: DeferredHypothesis, *, mission_id: str,
                                    expected_version: int | None = None) -> dict[str, Any]:
        def mutation(s: dict[str, Any]) -> None:
            s["deferred_hypotheses"][hypothesis.hypothesis_id] = asdict(hypothesis)
        return self.store.mutate(actor=self.instance_id, event_type="DEFERRED_HYPOTHESIS", mission_id=mission_id, expected_version=expected_version, mutation=mutation)


class Mirror:
    """Adaptive assistant; retains identity and never acquires mission ownership."""

    IDENTITY = "ESPEJO"
    ACTIONS = frozenset(MirrorAction)

    def __init__(self, *, instance_id: str | None = None, store: CoordinationStore | None = None):
        self.instance_id = instance_id or f"MIRROR-{uuid.uuid4().hex[:12]}"
        self.store = store or CoordinationStore()

    def invoke(self, *, mirror_of: str, mission: str, target_agent: str, task: str,
               problem: str, capability_required: str, limits: list[str], priority: str,
               authority: str, expected_result: str, action: MirrorAction,
               functional_role: str, mission_owner: str) -> dict[str, Any]:
        if action not in self.ACTIONS:
            raise CoordinationError("unsupported mirror action")
        if authority not in {Authority.COORDINATOR.value, Authority.HUMAN.value}:
            raise CommandConflict("mirror invocation requires coordinator or human authority")
        mirror_id = f"MIR-{uuid.uuid4().hex}"
        invocation = MirrorInvocation(mirror_id, mirror_of, mission, target_agent, task, problem,
                                      capability_required, tuple(limits), priority, authority, expected_result,
                                      action.value, functional_role, MirrorState.REQUESTED.value,
                                      mission_owner, self.instance_id)
        def mutation(s: dict[str, Any]) -> None:
            s["mirrors"][mirror_id] = asdict(invocation)
        return self.store.mutate(actor=self.instance_id, event_type="MIRROR_INVOCATION", mission_id=mission, expected_version=None, mutation=mutation)

    def claim_subtask(self, mirror_id: str, *, task_id: str, expected_version: int | None = None) -> dict[str, Any]:
        def mutation(s: dict[str, Any]) -> None:
            invocation = s["mirrors"].get(mirror_id)
            if not invocation:
                raise CoordinationError("unknown mirror invocation")
            if invocation["subtask_owner"] != self.instance_id:
                raise OwnershipConflict("mirror identity does not own invocation")
            task = s["tasks"].get(task_id)
            if task and task.get("subtask_owner") not in {None, self.instance_id}:
                raise OwnershipConflict("subtask already claimed")
            if not task:
                task = {"task_id": task_id, "mission": invocation["mission"], "mission_owner": invocation["mission_owner"], "status": "READY"}
                s["tasks"][task_id] = task
            task["subtask_owner"] = self.instance_id
            task["mirror_id"] = mirror_id
            task["status"] = "CLAIMED"
            invocation["state"] = MirrorState.ASSIGNED.value
        mission = self.store.load()["mirrors"].get(mirror_id, {}).get("mission", "UNKNOWN")
        return self.store.mutate(actor=self.instance_id, event_type="MIRROR_SUBTASK_CLAIMED", mission_id=mission, expected_version=expected_version, mutation=mutation)

    def complete(self, mirror_id: str, *, result: str, validated: bool, expected_version: int | None = None) -> dict[str, Any]:
        def mutation(s: dict[str, Any]) -> None:
            invocation = s["mirrors"].get(mirror_id)
            if not invocation or invocation["subtask_owner"] != self.instance_id:
                raise OwnershipConflict("mirror cannot complete foreign invocation")
            if not validated:
                raise CoordinationError("mirror handoff requires validation")
            invocation["state"] = MirrorState.RETURNED.value
            invocation["result"] = result
            invocation["validated"] = True
            s["handoffs"].append({"mirror_id": mirror_id, "mission_owner": invocation["mission_owner"], "subtask_owner": self.instance_id, "result": result, "timestamp": utc_now(), "control_returned": True})
        mission = self.store.load()["mirrors"].get(mirror_id, {}).get("mission", "UNKNOWN")
        return self.store.mutate(actor=self.instance_id, event_type="MIRROR_HANDOFF", mission_id=mission, expected_version=expected_version, mutation=mutation)

    def observe_recovery(self, mirror_id: str) -> dict[str, Any]:
        invocation = self.store.load()["mirrors"].get(mirror_id)
        if not invocation:
            raise CoordinationError("unknown mirror invocation")
        return copy.deepcopy(invocation)


__all__ = [
    "Authority", "CommandType", "CommandState", "MirrorAction", "MirrorState",
    "Command", "MirrorInvocation", "DeferredHypothesis", "CoordinationStore",
    "Coordinator", "Mirror", "CoordinationError", "StaleStateError",
    "CommandConflict", "OwnershipConflict",
]
