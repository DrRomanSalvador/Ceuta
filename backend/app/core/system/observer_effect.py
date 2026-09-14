"""Contracts for systems in which measurement or publication can alter behaviour."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ObservationIntervention:
    observation_id: str
    announced_at: datetime
    target_population: str
    expected_behavioural_channel: str
    mechanism_evidence_refs: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.observation_id or not self.target_population or not self.expected_behavioural_channel:
            raise ValueError("observation intervention identity is incomplete")
        if self.announced_at.tzinfo is None or self.announced_at.utcoffset() is None:
            raise ValueError("announced_at must be timezone-aware")


@dataclass(frozen=True, slots=True)
class FeedbackAssessment:
    intervention_id: str
    feedback_present: bool
    affected_variables: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    attribution_status: str

    def __post_init__(self) -> None:
        if not self.intervention_id:
            raise ValueError("feedback intervention identity is required")
        if self.feedback_present and not self.affected_variables:
            raise ValueError("feedback-present assessment requires affected variables")


__all__ = ["FeedbackAssessment", "ObservationIntervention"]
