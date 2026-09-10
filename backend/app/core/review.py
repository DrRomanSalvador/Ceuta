from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ReviewLevel(str, Enum):
    NONE = "NONE"
    HUMAN = "HUMAN"
    TWO_PERSON = "TWO_PERSON"
    BLOCKED = "BLOCKED"


@dataclass(frozen=True, slots=True)
class ReviewGate:
    level: ReviewLevel
    required: bool
    reason: str


_LEVELS = {
    "BASELINE": ReviewLevel.NONE,
    "ATTENTION": ReviewLevel.NONE,
    "WARNING": ReviewLevel.HUMAN,
    "DANGER": ReviewLevel.TWO_PERSON,
    "CRITICAL": ReviewLevel.BLOCKED,
}


def review_gate(
    alert_level: str,
    *,
    rights_impact: bool = False,
) -> ReviewGate:

    if rights_impact:
        return ReviewGate(
            ReviewLevel.TWO_PERSON,
            True,
            "Potential rights impact requires human review.",
        )

    level = _LEVELS.get(
        alert_level.upper(),
        ReviewLevel.BLOCKED,
    )

    return ReviewGate(
        level,
        level != ReviewLevel.NONE,
        f"Review policy for alert level {alert_level!r}.",
    )


def can_publish(
    level: str,
    human_reviewed: bool,
    second_reviewer: bool = False,
) -> bool:

    gate = review_gate(level)

    if gate.level == ReviewLevel.NONE:
        return True

    if gate.level == ReviewLevel.HUMAN:
        return human_reviewed

    if gate.level == ReviewLevel.TWO_PERSON:
        return (
            human_reviewed
            and second_reviewer
        )

    return False