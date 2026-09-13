"""Lossless projection of epistemic claims into decision inputs."""
from __future__ import annotations

from dataclasses import dataclass

from .epistemic import EpistemicClaim, EpistemicStatus


@dataclass(frozen=True, slots=True)
class DecisionEvidenceItem:
    claim_id: str
    text: str
    epistemic_status: EpistemicStatus
    source_refs: tuple[str, ...]
    as_of: str | None
    valid_until: str | None


def project_claim(claim: EpistemicClaim) -> DecisionEvidenceItem:
    return DecisionEvidenceItem(claim.claim_id, claim.text, claim.status, claim.source_refs, claim.as_of, claim.valid_until)


def is_fact(claim: DecisionEvidenceItem) -> bool:
    return claim.epistemic_status is EpistemicStatus.OBSERVED


def is_forecast(claim: DecisionEvidenceItem) -> bool:
    return claim.epistemic_status is EpistemicStatus.FORECAST


def is_reported(claim: DecisionEvidenceItem) -> bool:
    return claim.epistemic_status is EpistemicStatus.REPORTED


__all__ = ["DecisionEvidenceItem", "is_fact", "is_forecast", "is_reported", "project_claim"]
