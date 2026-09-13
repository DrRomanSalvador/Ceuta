"""Operational automation-bias controls for human-in-the-loop decisions."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class RelianceDisposition(StrEnum):
    INDEPENDENT_REVIEW = "independent_review"
    AGREEMENT = "agreement"
    DISAGREEMENT = "disagreement"
    OVERRIDE = "override"
    UNRESOLVED = "unresolved"


@dataclass(frozen=True, slots=True)
class HumanReviewProtocol:
    review_id: str
    decision_id: str
    reviewer_id: str
    model_recommendation: str
    human_initial_judgment: str
    final_judgment: str
    rationale: str
    disposition: RelianceDisposition
    model_visible_before_initial_judgment: bool

    def __post_init__(self) -> None:
        if not all(value.strip() for value in (self.review_id, self.decision_id, self.reviewer_id, self.rationale)):
            raise ValueError("review identity and rationale are required")
        if self.model_visible_before_initial_judgment and self.disposition is RelianceDisposition.INDEPENDENT_REVIEW:
            raise ValueError("independent review cannot be claimed when the model was visible beforehand")

    @property
    def automation_reliance_observable(self) -> bool:
        return bool(self.model_recommendation.strip() and self.final_judgment.strip())

    @property
    def disagreement_recorded(self) -> bool:
        return self.human_initial_judgment.strip() != self.model_recommendation.strip()


class AutomationBiasGate:
    """Requires observable human reasoning rather than treating human review as a label."""

    def evaluate(self, protocol: HumanReviewProtocol) -> bool:
        if not protocol.automation_reliance_observable:
            return False
        if not protocol.rationale.strip():
            return False
        if protocol.disposition is RelianceDisposition.UNRESOLVED:
            return False
        return True


__all__ = ["AutomationBiasGate", "HumanReviewProtocol", "RelianceDisposition"]
