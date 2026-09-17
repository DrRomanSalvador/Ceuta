"""Regression tests for the hereditary ESPÍA scientific control plane."""
from __future__ import annotations

import json
from pathlib import Path

from app.core.scientific.continuity import (
    REQUIRED_ARTIFACTS,
    REQUIRED_MASTER_KEYS,
    validate_continuity,
)


ROOT = Path(__file__).resolve().parents[2]


def test_required_continuity_artifacts_exist() -> None:
    missing = [path for path in REQUIRED_ARTIFACTS if not (ROOT / path).is_file()]
    assert missing == []


def test_master_state_contains_recovery_contract() -> None:
    state = json.loads((ROOT / "mission/SCIENTIFIC_MASTER_STATE.json").read_text(encoding="utf-8"))
    assert all(key in state for key in REQUIRED_MASTER_KEYS)
    assert state["agent"] == "ESPÍA"
    assert state["unit_of_work"] == "SCIENTIFIC_REQUIREMENT"
    assert state["unit_of_evidence"] == "SCIENTIFIC_CLAIM"
    assert state["unit_of_failure"] == "FALSIFIABLE_SCIENTIFIC_FAILURE_MODE"


def test_negative_knowledge_is_mandatory() -> None:
    registry = json.loads((ROOT / "mission/NEGATIVE_KNOWLEDGE_REGISTRY.json").read_text(encoding="utf-8"))
    categories = registry["categories"]
    assert {
        "what_we_know",
        "what_we_do_not_know",
        "what_we_cannot_identify",
        "what_we_cannot_predict",
        "what_we_have_failed_to_validate",
        "what_requires_new_data",
    } <= set(categories)


def test_continuity_structure_validates() -> None:
    report = validate_continuity(ROOT)
    assert report.ok, report.as_dict()
    # The persisted SHA describes the last reconciled repository state. A new
    # commit legitimately requires reconciliation; it must not be confused
    # with structural corruption.
    assert report.structural_errors == ()
