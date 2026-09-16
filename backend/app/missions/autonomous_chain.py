from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


class AutonomousChainError(ValueError):
    """Raised when autonomous mission chaining cannot safely proceed."""


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
    def fixed_point(*, executable_open_work: int, unprocessed_derived_work: int,
                    unintegrated_completed_work: int, unreconciled_state: int,
                    unverified_internal_repair: int, untested_executable_change: int,
                    unfollowed_active_handoff: int) -> bool:
        return all(value == 0 for value in (
            executable_open_work,
            unprocessed_derived_work,
            unintegrated_completed_work,
            unreconciled_state,
            unverified_internal_repair,
            untested_executable_change,
            unfollowed_active_handoff,
        ))
