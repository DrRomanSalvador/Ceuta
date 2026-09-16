from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


class AutonomousChainError(ValueError):
    """Raised when autonomous mission chaining cannot safely proceed."""


@dataclass(frozen=True, slots=True)
class ScientificWorkEvent:
    """Durable scientific signal used to derive work; it is not evidence by itself."""

    event_id: str
    event_type: str
    source_refs: tuple[str, ...]
    scientific_reason: str
    affected_refs: tuple[str, ...]
    capability_implications: tuple[str, ...]
    validation_status: str
    provenance_refs: tuple[str, ...]
    state_version: str
    emitted_at: str

    def validate(self) -> None:
        required = {
            "event_id": self.event_id,
            "event_type": self.event_type,
            "scientific_reason": self.scientific_reason,
            "validation_status": self.validation_status,
            "state_version": self.state_version,
            "emitted_at": self.emitted_at,
        }
        missing = [name for name, value in required.items() if not str(value).strip()]
        if missing or not self.source_refs or not self.provenance_refs:
            raise AutonomousChainError(f"SCIENTIFIC_EVENT_INVALID: missing={missing}")
        if self.validation_status not in {"UNVALIDATED", "VALIDATED", "REQUIRES_REVALIDATION", "REJECTED"}:
            raise AutonomousChainError(f"SCIENTIFIC_EVENT_STATUS_INVALID: {self.validation_status}")


@dataclass(frozen=True, slots=True)
class TaskCandidate:
    task_id: str
    why_this_task: str
    why_now: str
    expected_value: str
    acceptance_criteria: tuple[str, ...]
    stop_condition: str
    capability_required: tuple[str, ...]
    source_event_refs: tuple[str, ...]
    dependency_refs: tuple[str, ...] = ()
    external_boundary: bool = False


@dataclass(frozen=True, slots=True)
class MissionCandidate:
    mission_id: str
    capability_match: bool
    scientific_compatibility: bool
    authority_match: bool
    required_inputs_available: bool
    validation_path_available: bool
    dependency_satisfied: bool
    evidence_backed_fit: int
    activation_cost: int
    duplication_risk: int
    unresolved_dependencies: int
    can_extend: bool = False

    @property
    def eligible(self) -> bool:
        return all((
            self.capability_match,
            self.scientific_compatibility,
            self.authority_match,
            self.required_inputs_available,
            self.validation_path_available,
            self.dependency_satisfied,
        ))


@dataclass(frozen=True, slots=True)
class ActivationDecision:
    task_id: str
    selected_mission: str | None
    precedence: str
    alternatives_considered: tuple[str, ...]
    reason: str
    circuit_broken: bool = False


@dataclass(frozen=True, slots=True)
class ScientificConsequence:
    consequence_id: str
    source_result_refs: tuple[str, ...]
    classification: str
    downstream_task_refs: tuple[str, ...]
    revalidation_refs: tuple[str, ...]
    material: bool


@dataclass(frozen=True, slots=True)
class ProcessObservation:
    """Persistable observation of an asynchronous activity and its dependencies."""

    process_id: str
    process_type: str
    started_at: str
    current_status: str
    last_observed_at: str
    expected_result: str
    dependencies: tuple[str, ...]
    dependent_tasks: tuple[str, ...]
    independent_tasks_available: tuple[str, ...]
    next_observation_condition: str

    def validate(self) -> None:
        required = {
            "process_id": self.process_id,
            "process_type": self.process_type,
            "started_at": self.started_at,
            "current_status": self.current_status,
            "last_observed_at": self.last_observed_at,
            "expected_result": self.expected_result,
            "next_observation_condition": self.next_observation_condition,
        }
        missing = [name for name, value in required.items() if not str(value).strip()]
        if missing:
            raise AutonomousChainError(f"PROCESS_OBSERVATION_INVALID: missing={missing}")
        if self.current_status not in {"RUNNING", "WAITING", "COMPLETED", "FAILED", "CANCELLED"}:
            raise AutonomousChainError(f"PROCESS_STATUS_INVALID: {self.current_status}")


@dataclass(frozen=True, slots=True)
class WorkQueue:
    """Explicit queue projection preventing running work from being mistaken for waiting."""

    executable_now: tuple[str, ...] = ()
    running: tuple[str, ...] = ()
    blocked: tuple[str, ...] = ()
    delegated: tuple[str, ...] = ()
    external: tuple[str, ...] = ()
    completed: tuple[str, ...] = ()
    cancelled: tuple[str, ...] = ()

    @property
    def active(self) -> bool:
        return bool(self.executable_now or self.running or self.blocked or self.delegated)

    @property
    def waiting_is_valid(self) -> bool:
        return not self.active

    def validate(self) -> None:
        buckets = {
            "executable_now": self.executable_now,
            "running": self.running,
            "blocked": self.blocked,
            "delegated": self.delegated,
            "external": self.external,
            "completed": self.completed,
            "cancelled": self.cancelled,
        }
        seen: dict[str, str] = {}
        for bucket, items in buckets.items():
            for item in items:
                if not item.strip():
                    raise AutonomousChainError(f"WORK_QUEUE_INVALID: empty item in {bucket}")
                prior = seen.get(item)
                if prior is not None:
                    raise AutonomousChainError(f"WORK_QUEUE_DUPLICATE: {item} in {prior} and {bucket}")
                seen[item] = bucket


@dataclass(frozen=True, slots=True)
class FixedPointState:
    executable_open_work: int
    unprocessed_derived_work: int
    unintegrated_completed_work: int
    unreconciled_state: int
    unverified_internal_repair: int
    untested_executable_change: int
    unfollowed_active_handoff: int
    active_internal_processes: int = 0
    unresolved_critical_contradictions: int = 0
    unprocessed_high_value_discovery: int = 0
    required_integration_pending: int = 0
    repairable_regression: int = 0
    material_capability_gap: int = 0


class AutonomousMissionChain:
    """Deterministic, evidence-gated routing primitives for the mission control plane."""

    PRECEDENCE = (
        "EXISTING_CAPABILITY",
        "EXISTING_MISSION_EXTENSION",
        "CROSS_MISSION_COLLABORATION",
        "TEMPORARY_TASK_FORCE",
        "NEW_MISSION",
    )

    @staticmethod
    def emit_scientific_event(event: ScientificWorkEvent) -> ScientificWorkEvent:
        """Validate a durable trigger before it can enter work discovery."""
        event.validate()
        return event

    @staticmethod
    def validate_task(task: TaskCandidate) -> None:
        required = {
            "task_id": task.task_id,
            "why_this_task": task.why_this_task,
            "why_now": task.why_now,
            "expected_value": task.expected_value,
            "stop_condition": task.stop_condition,
        }
        missing = [name for name, value in required.items() if not str(value).strip()]
        if missing or not task.acceptance_criteria or not task.capability_required or not task.source_event_refs:
            raise AutonomousChainError(f"TASK_CONTRACT_INVALID: missing={missing}")
        if task.expected_value.upper() in {"NONE", "NEGATIVE"}:
            raise AutonomousChainError("TASK_NOT_JUSTIFIED: expected value is not material")

    @classmethod
    def select_existing(cls, task: TaskCandidate, candidates: Sequence[MissionCandidate]) -> ActivationDecision:
        cls.validate_task(task)
        if task.external_boundary:
            return ActivationDecision(task.task_id, None, "EXTERNAL_BOUNDARY", tuple(c.mission_id for c in candidates), "Task explicitly requires an unavailable external capability.")

        eligible = [c for c in candidates if c.eligible]
        if not eligible:
            return ActivationDecision(task.task_id, None, "NO_EXISTING_CAPABILITY", tuple(c.mission_id for c in candidates), "No existing mission satisfies all hard gates; MissionEvolutionEngine precedence must be evaluated.")

        direct = [c for c in eligible if not c.can_extend]
        extend = [c for c in eligible if c.can_extend]
        pool = direct or extend
        selected = min(pool, key=lambda c: (-c.evidence_backed_fit, c.activation_cost, c.duplication_risk, c.unresolved_dependencies, c.mission_id))
        precedence = "EXISTING_CAPABILITY" if direct else "EXISTING_MISSION_EXTENSION"
        return ActivationDecision(
            task.task_id,
            selected.mission_id,
            precedence,
            tuple(c.mission_id for c in candidates),
            "Hard gates passed; selected by evidence-backed fit, activation cost, duplication risk, unresolved dependencies and stable mission ID.",
        )

    @classmethod
    def replay_selection_trace(
        cls,
        tasks: Sequence[TaskCandidate],
        candidates_by_task: Mapping[str, Sequence[MissionCandidate]],
    ) -> tuple[ActivationDecision, ...]:
        """Replay routing deterministically from persisted task/candidate inputs without live state."""
        decisions: list[ActivationDecision] = []
        seen: set[str] = set()
        for task in tasks:
            if task.task_id in seen:
                raise AutonomousChainError(f"REPLAY_DUPLICATE_TASK: {task.task_id}")
            seen.add(task.task_id)
            candidates = candidates_by_task.get(task.task_id, ())
            decisions.append(cls.select_existing(task, candidates))
        return tuple(decisions)

    @staticmethod
    def consequence(*, consequence_id: str, source_result_refs: Sequence[str], classification: str,
                    downstream_task_refs: Sequence[str], revalidation_refs: Sequence[str], material: bool) -> ScientificConsequence:
        allowed = {"COMPATIBLE", "EXTENDS", "MODIFIES", "CONTRADICTS", "REFUTES", "INCONCLUSIVE"}
        if classification not in allowed:
            raise AutonomousChainError(f"UNKNOWN_COHERENCE_CLASS: {classification}")
        if not source_result_refs:
            raise AutonomousChainError("CONSEQUENCE_REQUIRES_PROVENANCE")
        if classification in {"MODIFIES", "CONTRADICTS", "REFUTES"} and material and not revalidation_refs:
            raise AutonomousChainError("MATERIAL_CHANGE_REQUIRES_REVALIDATION")
        return ScientificConsequence(consequence_id, tuple(source_result_refs), classification, tuple(downstream_task_refs), tuple(revalidation_refs), material)

    @staticmethod
    def circuit_break(reason: str, *, provenance_ok: bool = True, authority_ok: bool = True,
                      recursion_depth: int = 0, max_recursion_depth: int = 8,
                      task_count: int = 0, max_tasks: int = 1000) -> bool:
        if not reason.strip():
            raise AutonomousChainError("CIRCUIT_BREAK_REQUIRES_REASON")
        return (not provenance_ok) or (not authority_ok) or recursion_depth >= max_recursion_depth or task_count >= max_tasks

    @staticmethod
    def observe_process(process: ProcessObservation) -> ProcessObservation:
        """Validate a live process observation; RUNNING remains active work, never passive waiting."""
        process.validate()
        if process.current_status == "RUNNING" and not process.next_observation_condition.strip():
            raise AutonomousChainError("RUNNING_PROCESS_REQUIRES_OBSERVATION_CONDITION")
        return process

    @staticmethod
    def queue_state(queue: WorkQueue) -> str:
        queue.validate()
        if queue.executable_now:
            return "EXECUTABLE"
        if queue.running or queue.blocked or queue.delegated:
            return "ACTIVE"
        if queue.external:
            return "EXTERNAL_ONLY"
        return "QUIESCENT"

    @staticmethod
    def fixed_point_state(state: FixedPointState) -> bool:
        values = (
            state.executable_open_work,
            state.unprocessed_derived_work,
            state.unintegrated_completed_work,
            state.unreconciled_state,
            state.unverified_internal_repair,
            state.untested_executable_change,
            state.unfollowed_active_handoff,
            state.active_internal_processes,
            state.unresolved_critical_contradictions,
            state.unprocessed_high_value_discovery,
            state.required_integration_pending,
            state.repairable_regression,
            state.material_capability_gap,
        )
        if any(value < 0 for value in values):
            raise AutonomousChainError("FIXED_POINT_COUNTS_MUST_BE_NON_NEGATIVE")
        return all(value == 0 for value in values)

    @staticmethod
    def fixed_point(*, executable_open_work: int, unprocessed_derived_work: int,
                    unintegrated_completed_work: int, unreconciled_state: int,
                    unverified_internal_repair: int, untested_executable_change: int,
                    unfollowed_active_handoff: int, active_internal_processes: int = 0,
                    unresolved_critical_contradictions: int = 0,
                    unprocessed_high_value_discovery: int = 0,
                    required_integration_pending: int = 0,
                    repairable_regression: int = 0,
                    material_capability_gap: int = 0) -> bool:
        return AutonomousMissionChain.fixed_point_state(FixedPointState(
            executable_open_work=executable_open_work,
            unprocessed_derived_work=unprocessed_derived_work,
            unintegrated_completed_work=unintegrated_completed_work,
            unreconciled_state=unreconciled_state,
            unverified_internal_repair=unverified_internal_repair,
            untested_executable_change=untested_executable_change,
            unfollowed_active_handoff=unfollowed_active_handoff,
            active_internal_processes=active_internal_processes,
            unresolved_critical_contradictions=unresolved_critical_contradictions,
            unprocessed_high_value_discovery=unprocessed_high_value_discovery,
            required_integration_pending=required_integration_pending,
            repairable_regression=repairable_regression,
            material_capability_gap=material_capability_gap,
        ))
