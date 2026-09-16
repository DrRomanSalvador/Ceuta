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

try:
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None


class ExecutionControlError(RuntimeError):
    """Raised when a universal execution invariant cannot be safely enforced."""


TASK_STATES = {"EXECUTABLE_NOW", "RUNNING", "BLOCKED_INTERNAL", "BLOCKED_EXTERNAL", "DELEGATED", "COMPLETED", "FAILED", "CANCELLED"}
LIVENESS_STATES = {"ACTIVE", "STALLED", "BLOCKED", "FAILED", "LOST", "RECOVERABLE", "UNKNOWN"}
REQUIRED_COHERENCE_CHECKS = {"contradiction", "duplication", "complexity", "degradation", "regression", "integration", "maintainability", "security", "persistence"}


@dataclass(frozen=True, slots=True)
class CoherenceGateResult:
    passed: bool
    checks: Mapping[str, bool]
    evidence_refs: tuple[str, ...] = ()
    failures: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ExecutionTask:
    task_id: str
    mission_id: str
    objective: str
    inputs: tuple[str, ...]
    dependencies: tuple[str, ...]
    success_criteria: tuple[str, ...]
    state: str = "EXECUTABLE_NOW"
    created_at: str = ""
    updated_at: str = ""
    evidence_refs: tuple[str, ...] = ()
    checkpoint_ref: str | None = None
    next_action: str = ""

    def __post_init__(self) -> None:
        if self.state not in TASK_STATES:
            raise ExecutionControlError(f"Invalid task state: {self.state}")
        if not self.task_id or not self.mission_id or not self.objective:
            raise ExecutionControlError("task_id, mission_id and objective are required")

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Checkpoint:
    checkpoint_id: str
    mission_id: str
    mission_version: str
    agent_id: str
    execution_id: str
    task_id: str
    subtask: str
    state: str
    state_version: str
    last_result: str
    last_verified_revision: str
    last_test_evidence: tuple[str, ...]
    next_authorized_action: str
    dependencies: tuple[str, ...]
    blockers: tuple[str, ...]
    delegated_tasks: tuple[str, ...]
    processes: tuple[str, ...]
    created_at: str

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


class UniversalExecutionRuntime:
    """Repository-side universal execution control.

    It enforces task transitions, coherence gates, atomic persistence, idempotent
    checkpoints and compare-and-swap state writes. It deliberately does not claim
    to be an external scheduler/process supervisor.
    """

    SCHEMA_VERSION = "1.0"

    def __init__(self, repository_root: Path | str, state_path: Path | str | None = None) -> None:
        self.root = Path(repository_root).resolve()
        self.state_path = Path(state_path).resolve() if state_path else self.root / "docs" / "missions" / "UNIVERSAL_EXECUTION_RUNTIME_STATE.json"
        self.lock_path = self.state_path.with_suffix(self.state_path.suffix + ".lock")
        self.state_path.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _now() -> str:
        return datetime.now(timezone.utc).isoformat()

    @staticmethod
    def _version(payload: Mapping[str, Any]) -> str:
        canonical = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]

    @classmethod
    def _next_version(cls, state: Mapping[str, Any]) -> str:
        payload = dict(state)
        payload.pop("state_version", None)
        return cls._version(payload)

    def load(self) -> dict[str, Any]:
        if not self.state_path.exists():
            return self._empty_state()
        try:
            state = json.loads(self.state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ExecutionControlError("UNIVERSAL_EXECUTION_STATE_UNREADABLE") from exc
        self._validate_state(state)
        return state

    def current_version(self) -> str:
        return str(self.load()["state_version"])

    def register_task(self, task: ExecutionTask, *, expected_version: str | None = None) -> str:
        with self._lock():
            state = self.load()
            self._assert_expected_version(state, expected_version)
            if task.task_id in state["tasks"]:
                raise ExecutionControlError(f"TASK_ALREADY_EXISTS: {task.task_id}")
            state["tasks"][task.task_id] = task.as_dict()
            state["state_version"] = self._next_version(state)
            self._write(state)
            return state["state_version"]

    def claim_task(self, task_id: str, *, expected_version: str | None = None) -> str:
        with self._lock():
            state = self.load()
            self._assert_expected_version(state, expected_version)
            task = self._task(state, task_id)
            if task["state"] != "EXECUTABLE_NOW":
                raise ExecutionControlError(f"TASK_NOT_EXECUTABLE: {task_id}")
            task["state"] = "RUNNING"
            task["updated_at"] = self._now()
            state["tasks"][task_id] = task
            state["state_version"] = self._next_version(state)
            self._write(state)
            return state["state_version"]

    def checkpoint(self, checkpoint: Checkpoint, *, expected_version: str | None = None) -> str:
        payload = checkpoint.as_dict()
        fingerprint = self._version(payload)
        with self._lock():
            state = self.load()
            self._assert_expected_version(state, expected_version)
            existing = state["checkpoints"].get(checkpoint.checkpoint_id)
            if existing is not None:
                if existing.get("fingerprint") != fingerprint:
                    raise ExecutionControlError(f"CHECKPOINT_ID_COLLISION: {checkpoint.checkpoint_id}")
                return state["state_version"]
            state["checkpoints"][checkpoint.checkpoint_id] = {"fingerprint": fingerprint, "payload": payload}
            state["last_checkpoint_id"] = checkpoint.checkpoint_id
            state["state_version"] = self._next_version(state)
            self._write(state)
            return state["state_version"]

    def complete_task(self, task_id: str, *, post_write_gate: CoherenceGateResult, result_ref: str, evidence_refs: Sequence[str], checkpoint_ref: str, expected_version: str | None = None) -> str:
        if not post_write_gate.passed:
            raise ExecutionControlError("POST_WRITE_COHERENCE_GATE_FAILED")
        if not result_ref or not checkpoint_ref:
            raise ExecutionControlError("COMPLETION_REQUIRES_RESULT_AND_CHECKPOINT")
        with self._lock():
            state = self.load()
            self._assert_expected_version(state, expected_version)
            task = self._task(state, task_id)
            if task["state"] != "RUNNING":
                raise ExecutionControlError(f"TASK_NOT_RUNNING: {task_id}")
            task.update({"state": "COMPLETED", "updated_at": self._now(), "evidence_refs": list(evidence_refs), "checkpoint_ref": checkpoint_ref, "next_action": "REASSESS_QUEUE", "result_ref": result_ref})
            state["tasks"][task_id] = task
            state["open_gate_failures"] = [x for x in state["open_gate_failures"] if x.get("task_id") != task_id]
            state["state_version"] = self._next_version(state)
            self._write(state)
            return state["state_version"]

    def mark_blocked(self, task_id: str, *, external: bool, reason: str, expected_version: str | None = None) -> str:
        if not reason.strip():
            raise ExecutionControlError("BLOCK_REASON_REQUIRED")
        with self._lock():
            state = self.load()
            self._assert_expected_version(state, expected_version)
            task = self._task(state, task_id)
            task["state"] = "BLOCKED_EXTERNAL" if external else "BLOCKED_INTERNAL"
            task["block_reason"] = reason
            task["updated_at"] = self._now()
            state["tasks"][task_id] = task
            state["state_version"] = self._next_version(state)
            self._write(state)
            return state["state_version"]

    def liveness(self, task_id: str, *, process_present: bool | None, seconds_since_progress: float | None, observation_interval_seconds: float | None) -> str:
        task = self._task(self.load(), task_id)
        if task["state"] in {"FAILED", "CANCELLED"}:
            return "FAILED"
        if task["state"] in {"BLOCKED_EXTERNAL", "BLOCKED_INTERNAL", "DELEGATED"}:
            return "BLOCKED"
        if process_present is False:
            return "RECOVERABLE" if task.get("checkpoint_ref") else "LOST"
        if process_present is True and (seconds_since_progress is None or observation_interval_seconds is None):
            return "ACTIVE"
        if process_present is True and seconds_since_progress is not None and observation_interval_seconds is not None:
            return "STALLED" if seconds_since_progress > observation_interval_seconds else "ACTIVE"
        return "UNKNOWN"

    def decide_continuation(self) -> str:
        state = self.load()
        tasks = list(state["tasks"].values())
        if any(t["state"] in {"EXECUTABLE_NOW", "RUNNING", "BLOCKED_INTERNAL"} for t in tasks):
            return "CONTINUE"
        if any(t["state"] == "BLOCKED_EXTERNAL" for t in tasks):
            return "WAIT"
        if state["open_gate_failures"]:
            return "CONTINUE"
        return "MISSION_COMPLETE_CANDIDATE"

    def fixed_point(self) -> bool:
        state = self.load()
        if self.decide_continuation() != "MISSION_COMPLETE_CANDIDATE":
            return False
        return all(bool(value) for value in state.get("fixed_point_requirements", {}).values())

    def record_policy_change(self, *, previous_version: str, new_version: str, reason: str, author: str, evidence: Sequence[str], impact: str, compatibility: str, validation: str, timestamp: str | None = None) -> str:
        event = {"event_type": "POLICY_CHANGE_EVENT", "previous_version": previous_version, "new_version": new_version, "reason": reason, "author": author, "evidence": list(evidence), "impact": impact, "compatibility": compatibility, "validation": validation, "timestamp": timestamp or self._now()}
        if not all(event[key] for key in ("previous_version", "new_version", "reason", "author", "evidence", "impact", "compatibility", "validation", "timestamp")):
            raise ExecutionControlError("POLICY_CHANGE_EVENT_INCOMPLETE")
        with self._lock():
            state = self.load()
            state["policy_change_events"].append(event)
            state["state_version"] = self._next_version(state)
            self._write(state)
            return state["state_version"]

    @staticmethod
    def pre_write_coherence_gate(*, checks: Mapping[str, bool], evidence_refs: Sequence[str]) -> CoherenceGateResult:
        missing = sorted(REQUIRED_COHERENCE_CHECKS - set(checks))
        failures = [key for key in sorted(REQUIRED_COHERENCE_CHECKS) if key in checks and not checks[key]]
        failures.extend(f"MISSING:{key}" for key in missing)
        if not evidence_refs:
            failures.append("MISSING:EVIDENCE_REFS")
        return CoherenceGateResult(not failures, dict(checks), tuple(evidence_refs), tuple(failures))

    @staticmethod
    def post_write_coherence_gate(*, checks: Mapping[str, bool], evidence_refs: Sequence[str], tests_passed: bool, persisted: bool) -> CoherenceGateResult:
        result = UniversalExecutionRuntime.pre_write_coherence_gate(checks=checks, evidence_refs=evidence_refs)
        failures = list(result.failures)
        if not tests_passed:
            failures.append("TESTS_FAILED")
        if not persisted:
            failures.append("PERSISTENCE_NOT_CONFIRMED")
        return CoherenceGateResult(not failures, dict(checks), tuple(evidence_refs), tuple(failures))

    def _task(self, state: Mapping[str, Any], task_id: str) -> dict[str, Any]:
        task = state.get("tasks", {}).get(task_id)
        if not isinstance(task, dict):
            raise ExecutionControlError(f"TASK_NOT_FOUND: {task_id}")
        return dict(task)

    @classmethod
    def _empty_state(cls) -> dict[str, Any]:
        state: dict[str, Any] = {
            "schema_version": cls.SCHEMA_VERSION,
            "state_version": "GENESIS",
            "tasks": {},
            "checkpoints": {},
            "open_gate_failures": [],
            "policy_change_events": [],
            "last_checkpoint_id": None,
            "fixed_point_requirements": {
                "constitution_defined": True,
                "contract_defined": True,
                "runtime_present": True,
                "persistence_present": True,
                "recovery_present": True,
                "zero_context_present": True,
                "tests_present": True,
                "cross_process_verified": False,
                "external_protection_verified": False,
            },
        }
        state["state_version"] = cls._version(state)
        return state

    @staticmethod
    def _validate_state(state: Mapping[str, Any]) -> None:
        if state.get("schema_version") != UniversalExecutionRuntime.SCHEMA_VERSION:
            raise ExecutionControlError("UNSUPPORTED_EXECUTION_STATE_SCHEMA")
        if not isinstance(state.get("tasks"), dict) or not isinstance(state.get("checkpoints"), dict):
            raise ExecutionControlError("INVALID_EXECUTION_STATE")
        for task_id, task in state["tasks"].items():
            if task.get("task_id") != task_id or task.get("state") not in TASK_STATES:
                raise ExecutionControlError(f"INVALID_TASK_STATE: {task_id}")

    @staticmethod
    def _assert_expected_version(state: Mapping[str, Any], expected_version: str | None) -> None:
        if expected_version is not None and expected_version != state.get("state_version"):
            raise ExecutionControlError("STALE_STATE_VERSION")

    def _write(self, state: Mapping[str, Any]) -> None:
        target = self.state_path
        target.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp_name = tempfile.mkstemp(prefix=f".{target.name}.", dir=str(target.parent), text=True)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                json.dump(state, handle, ensure_ascii=False, indent=2)
                handle.write("\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(tmp_name, target)
        finally:
            if os.path.exists(tmp_name):
                os.unlink(tmp_name)

    @contextmanager
    def _lock(self) -> Iterator[None]:
        if fcntl is None:
            raise ExecutionControlError("CONCURRENCY_UNSUPPORTED: POSIX file locking is required")
        with self.lock_path.open("a+") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX)
            try:
                yield
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
