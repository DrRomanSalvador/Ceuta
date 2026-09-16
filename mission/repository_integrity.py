"""Fail-closed repository-head integrity checks for the mission control plane."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class IntegrityAssessment:
    status: str
    expected_head: str
    actual_head: str
    protocol_evidence: tuple[str, ...]


def assess_head(*, expected_head: str, actual_head: str, protocol_evidence: list[str] | tuple[str, ...]) -> IntegrityAssessment:
    if not expected_head or not actual_head:
        raise ValueError("Repository integrity requires expected and actual commit identities")
    evidence=tuple(protocol_evidence)
    if expected_head == actual_head:
        return IntegrityAssessment("MATCH", expected_head, actual_head, evidence)
    if not evidence:
        return IntegrityAssessment("UNRECONCILED_HEAD", expected_head, actual_head, evidence)
    return IntegrityAssessment("CHANGED_WITH_PROTOCOL_EVIDENCE", expected_head, actual_head, evidence)


def require_reconciliation(assessment: IntegrityAssessment) -> None:
    if assessment.status == "UNRECONCILED_HEAD":
        raise RuntimeError("Repository head changed without protocol evidence; reconciliation required")
