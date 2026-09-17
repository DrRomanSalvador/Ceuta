"""Executable scientific continuity control plane for ESPÍA.

The module deliberately uses only the Python standard library. Its purpose is
not to infer scientific truth; it verifies that the repository contains the
minimum canonical state required for a fresh ESPÍA instance to recover its
role, epistemic state, capability limits and next action.

Persisted state is treated as a snapshot. Current Git state remains
authoritative for implementation freshness and validation status.
"""
from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

REQUIRED_ARTIFACTS = (
    "docs/agents/ESPIA_IDENTITY.md",
    "docs/agents/ESPIA_RECOVERY.md",
    "mission/SCIENTIFIC_MASTER_STATE.json",
    "mission/SCIENTIFIC_REQUIREMENTS_REGISTRY.json",
    "mission/SCIENTIFIC_CLAIM_REGISTRY.json",
    "mission/SCIENTIFIC_CAPABILITY_MATRIX.json",
    "mission/NEGATIVE_KNOWLEDGE_REGISTRY.json",
    "mission/SCIENTIFIC_HANDOFF_REGISTRY.json",
    "mission/SCIENTIFIC_ADVERSARIAL_TEST_MATRIX.json",
    "AUTONOMOUS_ENGINEERING_STATE.json",
)

REQUIRED_MASTER_KEYS = (
    "schema_version", "state_id", "agent", "mission", "role",
    "engineering_boundary", "current_question", "unit_of_work",
    "unit_of_evidence", "unit_of_failure", "unit_of_progress", "unit_of_memory",
    "evidence_ladder", "epistemic_states", "scientific_surfaces",
    "global_status_axes", "negative_knowledge", "mandatory_failure_modes",
    "current_frontier", "next_executable_action", "recovery_sources",
    "repository_heads_at_reconciliation", "last_reconciled_at",
)

REQUIRED_NEGATIVE_CATEGORIES = (
    "what_we_know", "what_we_do_not_know", "what_we_cannot_identify",
    "what_we_cannot_predict", "what_we_have_failed_to_validate", "what_requires_new_data",
)

ALLOWED_CAPABILITY_STATUSES = {
    "NOT_CONSIDERED", "DISCOVERED", "RESEARCH_REQUIRED", "SPECIFIED", "IMPLEMENTED",
    "TESTED", "VALIDATED_RETROSPECTIVELY", "VALIDATED_TEMPORALLY",
    "VALIDATED_PROSPECTIVELY", "OPERATIONALLY_VALIDATED", "NOT_JUSTIFIED",
    "NOT_FEASIBLE", "EXTERNAL_DATA_REQUIRED", "SUPERSEDED",
}


@dataclass(frozen=True)
class ContinuityReport:
    ok: bool
    reconciliation_required: bool
    missing_artifacts: tuple[str, ...]
    structural_errors: tuple[str, ...]
    git_head: str | None
    persisted_head: str | None
    head_match: bool | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "reconciliation_required": self.reconciliation_required,
            "missing_artifacts": list(self.missing_artifacts),
            "structural_errors": list(self.structural_errors),
            "git_head": self.git_head,
            "persisted_head": self.persisted_head,
            "head_match": self.head_match,
        }


def repository_root(start: Path | None = None) -> Path:
    """Return the CeutIA repository root from this module's location."""
    candidate = (start or Path(__file__)).resolve()
    for path in (candidate, *candidate.parents):
        if (path / "AUTONOMOUS_ENGINEERING_STATE.json").is_file():
            return path
    raise FileNotFoundError("CeutIA repository root could not be located")


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root JSON value must be an object")
    return value


def _git_head(root: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=root, check=True,
            capture_output=True, text=True, timeout=5,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() or None


def validate_continuity(root: Path | None = None) -> ContinuityReport:
    """Validate continuity structure without asserting scientific truth."""
    repo = repository_root(root)
    missing = tuple(path for path in REQUIRED_ARTIFACTS if not (repo / path).is_file())
    errors: list[str] = []

    master: dict[str, Any] = {}
    master_path = repo / "mission/SCIENTIFIC_MASTER_STATE.json"
    if not master_path.is_file():
        errors.append("master_state_missing")
    else:
        try:
            master = _load_json(master_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"master_state_invalid:{exc}")

    for key in REQUIRED_MASTER_KEYS:
        if key not in master:
            errors.append(f"master_state_missing_key:{key}")
    if master.get("agent") != "ESPÍA":
        errors.append("master_state_agent_mismatch")
    if not master.get("current_question"):
        errors.append("master_state_empty_current_question")
    if not master.get("next_executable_action"):
        errors.append("master_state_empty_next_action")

    negative_path = repo / "mission/NEGATIVE_KNOWLEDGE_REGISTRY.json"
    if negative_path.is_file():
        try:
            negative = _load_json(negative_path)
            categories = negative.get("categories", {})
            for category in REQUIRED_NEGATIVE_CATEGORIES:
                if category not in categories:
                    errors.append(f"negative_knowledge_missing_category:{category}")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"negative_knowledge_invalid:{exc}")

    capability_path = repo / "mission/SCIENTIFIC_CAPABILITY_MATRIX.json"
    if capability_path.is_file():
        try:
            capability = _load_json(capability_path)
            allowed = set(capability.get("allowed_statuses", []))
            if not ALLOWED_CAPABILITY_STATUSES.issubset(allowed):
                errors.append("capability_matrix_missing_allowed_statuses")
            for index, item in enumerate(capability.get("capabilities", [])):
                status = item.get("current_status")
                if status not in ALLOWED_CAPABILITY_STATUSES:
                    errors.append(f"capability_status_invalid:{index}:{status}")
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"capability_matrix_invalid:{exc}")

    git_head = _git_head(repo)
    persisted_head = None
    if master:
        ceutia_head = master.get("repository_heads_at_reconciliation", {}).get("DrRomanSalvador/Ceuta", {})
        persisted_head = ceutia_head.get("sha") if isinstance(ceutia_head, dict) else None
    head_match = None if git_head is None or persisted_head is None else git_head == persisted_head
    reconciliation_required = head_match is False

    # A changed HEAD is expected after a state update or a merge. It is a
    # reconciliation signal, not structural corruption. The fresh instance
    # must surface it before relying on implementation-status assertions.
    return ContinuityReport(
        ok=not missing and not errors,
        reconciliation_required=reconciliation_required,
        missing_artifacts=missing,
        structural_errors=tuple(errors),
        git_head=git_head,
        persisted_head=persisted_head,
        head_match=head_match,
    )


def recover(root: Path | None = None) -> dict[str, Any]:
    """Return the machine-readable recovery object for a fresh ESPÍA instance."""
    repo = repository_root(root)
    report = validate_continuity(repo)
    master = _load_json(repo / "mission/SCIENTIFIC_MASTER_STATE.json")
    return {
        "recovery_status": "READY" if report.ok and not report.reconciliation_required else "RECONCILIATION_REQUIRED",
        "agent": master.get("agent"),
        "mission": master.get("mission"),
        "role": master.get("role"),
        "current_question": master.get("current_question"),
        "current_frontier": master.get("current_frontier"),
        "global_status_axes": master.get("global_status_axes", {}),
        "negative_knowledge": master.get("negative_knowledge", []),
        "next_executable_action": master.get("next_executable_action"),
        "report": report.as_dict(),
    }


if __name__ == "__main__":
    print(json.dumps(recover(), ensure_ascii=False, indent=2))
