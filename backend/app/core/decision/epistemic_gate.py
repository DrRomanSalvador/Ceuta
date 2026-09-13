"""Operational gate for unknown and insufficient-evidence states."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from ..evidence.epistemic import EpistemicStatus


class EpistemicDisposition(StrEnum):
    ALLOW = "allow"
    HUMAN_REVIEW = "human_review"
    ABSTAIN = "abstain"


@dataclass(frozen=True, slots=True)
class EpistemicGateResult:
    disposition: EpistemicDisposition
    status: EpistemicStatus
    reason: str


class EpistemicDecisionGate:
    def evaluate(self, status: EpistemicStatus) -> EpistemicGateResult:
        if status is EpistemicStatus.INSUFFICIENT_EVIDENCE:
            return EpistemicGateResult(EpistemicDisposition.ABSTAIN, status, "insufficient_evidence")
        if status is EpistemicStatus.UNKNOWN:
            return EpistemicGateResult(EpistemicDisposition.HUMAN_REVIEW, status, "unknown_state_requires_review")
        if status is EpistemicStatus.HYPOTHESIS:
            return EpistemicGateResult(EpistemicDisposition.HUMAN_REVIEW, status, "hypothesis_cannot_be_treated_as_fact")
        if status is EpistemicStatus.FORECAST:
            return EpistemicGateResult(EpistemicDisposition.HUMAN_REVIEW, status, "forecast_requires_explicit_forecast_semantics")
        if status is EpistemicStatus.REPORTED:
            return EpistemicGateResult(EpistemicDisposition.HUMAN_REVIEW, status, "reported_value_is_not_observed_fact")
        return EpistemicGateResult(EpistemicDisposition.ALLOW, status, "epistemic_status_is_decision_eligible")


__all__ = ["EpistemicDecisionGate", "EpistemicDisposition", "EpistemicGateResult"]
