"""Conflict resolution without a single-authority override rule."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .conflicts import ConflictStatus, ConflictType, EvidenceConflict


class ResolutionDisposition(StrEnum):
    RESOLVED = "resolved"
    HUMAN_REVIEW = "human_review"
    ABSTAIN = "abstain"


@dataclass(frozen=True, slots=True)
class EvidenceResolution:
    conflict_id: str
    disposition: ResolutionDisposition
    selected_refs: tuple[str, ...]
    rationale: str
    policy_version: str


class ConflictResolver:
    """Requires multidimensional evidence appraisal; authority alone cannot resolve conflict."""

    def resolve(self, conflict: EvidenceConflict, *, policy_version: str) -> EvidenceResolution:
        if not policy_version:
            raise ValueError("policy_version is required")
        if conflict.status is ConflictStatus.RESOLVED:
            return EvidenceResolution(conflict.conflict_id, ResolutionDisposition.RESOLVED, conflict.evidence_refs, "pre-resolved by persisted evidence synthesis", policy_version)
        if conflict.conflict_type in {ConflictType.DEPENDENCE, ConflictType.DUPLICATE, ConflictType.PROVENANCE}:
            return EvidenceResolution(conflict.conflict_id, ResolutionDisposition.HUMAN_REVIEW, (), "dependency or provenance cannot be resolved by source authority alone", policy_version)
        if conflict.conflict_type in {ConflictType.CAUSAL, ConflictType.METHODOLOGICAL, ConflictType.EPISTEMIC}:
            return EvidenceResolution(conflict.conflict_id, ResolutionDisposition.HUMAN_REVIEW, (), "requires appraisal of assumptions, applicability and epistemic status", policy_version)
        return EvidenceResolution(conflict.conflict_id, ResolutionDisposition.HUMAN_REVIEW, (), "conflicting evidence requires explicit comparative appraisal rather than authority ranking", policy_version)


__all__ = ["ConflictResolver", "EvidenceResolution", "ResolutionDisposition"]
