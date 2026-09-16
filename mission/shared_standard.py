"""Executable enforcement of the shared mission constitution.

This module deliberately contains only cross-mission invariants. Domain-specific
scientific decisions remain owned by the registered domain mission.
"""
from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum
from typing import Any


class QualityLevel(IntEnum):
    EXPLORATORY = 0
    INFORMED = 1
    VERIFIED = 2
    CORROBORATED = 3
    ROBUST = 4
    ADVERSARIALLY_TESTED = 5
    REPRODUCIBLE = 6
    OPERATIONALLY_VALIDATED = 7
    PROSPECTIVELY_VALIDATED = 8
    REAL_WORLD_EFFECTIVENESS = 9


QUALITY_NAMES = {level.value: level.name for level in QualityLevel}
ATTRIBUTION_FIELDS = (
    "DISCOVERED_BY", "PROPOSED_BY", "IMPLEMENTED_BY",
    "REVIEWED_BY", "VALIDATED_BY", "AUTHORIZED_BY",
)
SOURCE_QUALITY_FIELDS = (
    "SOURCE", "AUTHORITY", "DIRECTNESS", "RECENCY", "RELEVANCE",
    "METHODOLOGICAL_QUALITY", "INDEPENDENCE", "REPRODUCIBILITY", "LIMITATIONS",
)
CHECKPOINT_FIELDS = (
    "CURRENT_STATE", "LAST_VERIFIED_STATE", "LAST_SUCCESSFUL_ACTION", "FAILED_ACTIONS",
    "OPEN_BLOCKERS", "PENDING_HANDOFFS", "DEPENDENCIES", "NEXT_ACTION",
    "AUTHORITY_REQUIRED", "EVIDENCE_REFERENCES", "ARTIFACT_REFERENCES",
    "VERSION_COMMIT", "TIMESTAMP", "INTEGRITY_STATUS",
)
HANDOFF_FIELDS = (
    "SOURCE_MISSION", "TARGET_MISSION", "TASK", "CONTEXT", "FINDING", "EVIDENCE",
    "QUALITY_LEVEL", "KNOWN_LIMITATIONS", "REQUIRED_ACTION", "OWNER", "DEPENDENCIES",
    "BLOCKERS", "EXPECTED_OUTPUT", "VALIDATION_CRITERIA", "TIMESTAMP", "ARTIFACT_REFERENCES",
)


@dataclass(frozen=True)
class QualityAssessment:
    level: QualityLevel
    claim_type: str
    evidence_refs: tuple[str, ...]
    limitations: tuple[str, ...]


def require_fields(record: dict[str, Any], fields: tuple[str, ...], label: str) -> None:
    missing = [field for field in fields if field not in record or record[field] in (None, "")]
    if missing:
        raise ValueError(f"{label} missing required fields: {missing}")


def validate_quality(level: int | str) -> QualityLevel:
    try:
        parsed = QualityLevel[level] if isinstance(level, str) else QualityLevel(level)
    except (KeyError, ValueError):
        raise ValueError(f"Unknown quality level: {level}") from None
    return parsed


def enforce_claim_evidence(*, claim_level: int | str, evidence_level: int | str) -> None:
    claim = validate_quality(claim_level)
    evidence = validate_quality(evidence_level)
    if claim > evidence:
        raise ValueError(f"Claim level {claim.name} exceeds evidence level {evidence.name}")


def validate_source_quality(record: dict[str, Any]) -> None:
    require_fields(record, SOURCE_QUALITY_FIELDS, "source_quality")
    if not isinstance(record["LIMITATIONS"], (list, tuple)):
        raise ValueError("source_quality LIMITATIONS must be explicit list/tuple")


def validate_attribution(record: dict[str, Any], *, require_authorization: bool = False) -> None:
    require_fields(record, ATTRIBUTION_FIELDS, "attribution")
    if require_authorization and not record["AUTHORIZED_BY"]:
        raise PermissionError("Authorization attribution is required")


def validate_checkpoint_contract(checkpoint: dict[str, Any]) -> None:
    require_fields(checkpoint, CHECKPOINT_FIELDS, "checkpoint")
    if checkpoint["INTEGRITY_STATUS"] in {"UNKNOWN", "INVALID", "CONFLICTING"}:
        raise ValueError("Checkpoint integrity is not valid")


def validate_handoff_contract(handoff: dict[str, Any]) -> None:
    require_fields(handoff, HANDOFF_FIELDS, "handoff")
    if handoff["SOURCE_MISSION"] == handoff["TARGET_MISSION"]:
        raise ValueError("Cross-mission handoff cannot target the same mission")
    validate_quality(handoff["QUALITY_LEVEL"])
    if not handoff["EVIDENCE"]:
        raise ValueError("Handoff requires evidence")


def validate_non_interference(*, actor_mission: str, owner_mission: str, surface: str, authorized_surfaces: list[str]) -> None:
    if actor_mission != owner_mission and surface not in authorized_surfaces:
        raise PermissionError(f"{actor_mission} cannot modify protected surface owned by {owner_mission}: {surface}")


def validate_authority(*, actor: str, authority_owner: str, action: str, human_reserved: bool = False) -> None:
    if human_reserved and actor != authority_owner:
        raise PermissionError(f"Human/domain authority required for {action}")
    if actor == "" or authority_owner == "":
        raise PermissionError("Authority identity is required")


def validate_autonomous_continuation(*, authorized: bool, scientifically_justified: bool, technically_feasible: bool,
                                     controlled: bool, in_scope: bool, human_reserved: bool = False) -> bool:
    if human_reserved:
        return False
    if all((authorized, scientifically_justified, technically_feasible, controlled, in_scope)):
        return True
    return False


def validate_blocked_path(*, blocker: str | None, non_blocked_work_exists: bool) -> None:
    if blocker is None and not non_blocked_work_exists:
        raise ValueError("No blocker and no executable work is an invalid waiting state")


def validate_completion(*, claimed_level: int | str, evidence_level: int | str,
                        tests_executed: bool, adversarially_required: bool,
                        adversarially_tested: bool, reproducible_required: bool,
                        reproducible: bool) -> None:
    enforce_claim_evidence(claim_level=claimed_level, evidence_level=evidence_level)
    if not tests_executed:
        raise ValueError("Completion cannot be claimed when required tests were not executed")
    if adversarially_required and not adversarially_tested:
        raise ValueError("Completion requires adversarial validation for this claim")
    if reproducible_required and not reproducible:
        raise ValueError("Completion requires reproducibility for this claim")


def validate_contradiction(record: dict[str, Any]) -> None:
    require_fields(record, ("contradiction_id", "claim_a", "claim_b", "category", "evidence_a", "evidence_b", "owner", "status"), "contradiction")
    if record["claim_a"] == record["claim_b"]:
        raise ValueError("Contradiction must contain distinct claims")
    if not record["evidence_a"] or not record["evidence_b"]:
        raise ValueError("Both sides of a contradiction require preserved evidence")


def validate_prompt_authority_boundary(*, proposed_instruction: str, protected_authority: str) -> None:
    text = proposed_instruction.lower()
    forbidden = ("ignore mission authority", "rewrite mission contract", "become owner", "bypass authorization", "disable validation")
    if any(token in text for token in forbidden):
        raise PermissionError(f"Prompt cannot redefine protected authority: {protected_authority}")


def validate_contract_change(*, actor: str, owner: str, authorizer: str, evidence: list[str], human_reserved: bool = False) -> None:
    if actor != owner:
        raise PermissionError("Only the owning mission may propose/implement its contract change")
    if not evidence:
        raise ValueError("Contract changes require evidence")
    if human_reserved and authorizer == actor:
        raise PermissionError("Human-reserved contract authority cannot be self-authorized")
    if not authorizer:
        raise PermissionError("Contract change requires explicit authorizer")
