"""Fail-closed decision authorization contract."""
from __future__ import annotations

from enum import StrEnum


class SafetyDisposition(StrEnum):
    AUTHORIZE = "authorize"
    HUMAN_REVIEW = "human_review"
    ABSTAIN = "abstain"
    BLOCK = "block"


def fail_closed(*, dependencies_resolved: bool, evidence_sufficient: bool, data_valid: bool, control_checks_passed: bool) -> SafetyDisposition:
    if not data_valid or not control_checks_passed:
        return SafetyDisposition.BLOCK
    if not dependencies_resolved or not evidence_sufficient:
        return SafetyDisposition.ABSTAIN
    return SafetyDisposition.AUTHORIZE


__all__ = ["SafetyDisposition", "fail_closed"]
