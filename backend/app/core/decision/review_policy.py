"""Risk-based review controls; no universal uncertainty cutoff."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class DecisionRisk(StrEnum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class ReviewDisposition(StrEnum):
    AUTO = "auto"
    HUMAN_REVIEW = "human_review"
    ABSTAIN = "abstain"


@dataclass(frozen=True, slots=True)
class ReviewPolicy:
    policy_version: str
    auto_allowed: frozenset[DecisionRisk]
    review_required: frozenset[DecisionRisk]
    abstain_required: frozenset[DecisionRisk]

    def __post_init__(self) -> None:
        if not self.policy_version:
            raise ValueError("policy_version is required")
        if self.auto_allowed & self.abstain_required or self.auto_allowed & self.review_required:
            raise ValueError("review classes must be mutually exclusive")

    def disposition(self, risk: DecisionRisk) -> ReviewDisposition:
        if risk in self.abstain_required:
            return ReviewDisposition.ABSTAIN
        if risk in self.review_required:
            return ReviewDisposition.HUMAN_REVIEW
        if risk in self.auto_allowed:
            return ReviewDisposition.AUTO
        return ReviewDisposition.HUMAN_REVIEW


__all__ = ["DecisionRisk", "ReviewDisposition", "ReviewPolicy"]
