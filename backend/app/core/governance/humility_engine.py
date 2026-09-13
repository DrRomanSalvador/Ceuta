from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class EpistemicAssessment:
    confidence: float
    evidence_count: int
    contradictory_count: int
    abstain: bool
    reason: str


class HumilityEngine:
    def assess(self, *, confidence: float, evidence_count: int, contradictory_count: int, minimum_evidence: int = 2) -> EpistemicAssessment:
        if not 0.0 <= confidence <= 1.0:
            raise ValueError("confidence must be in [0,1]")
        abstain = evidence_count < minimum_evidence or contradictory_count > 0
        reason = "insufficient or contradictory evidence" if abstain else "evidence threshold satisfied"
        return EpistemicAssessment(confidence, evidence_count, contradictory_count, abstain, reason)
