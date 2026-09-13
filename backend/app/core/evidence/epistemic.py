"""Explicit epistemic-status contracts for CeutIA evidence and claims."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class EpistemicStatus(StrEnum):
    OBSERVED = "observed"
    REPORTED = "reported"
    DERIVED = "derived"
    ESTIMATED = "estimated"
    FORECAST = "forecast"
    INFERRED = "inferred"
    HYPOTHESIS = "hypothesis"
    UNKNOWN = "unknown"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


@dataclass(frozen=True, slots=True)
class EpistemicClaim:
    """A claim whose epistemic status cannot be silently upgraded downstream."""

    claim_id: str
    text: str
    status: EpistemicStatus
    source_refs: tuple[str, ...] = ()
    as_of: str | None = None
    valid_until: str | None = None
    uncertainty_ref: str | None = None

    def __post_init__(self) -> None:
        if not self.claim_id.strip():
            raise ValueError("claim_id must not be empty")
        if not self.text.strip():
            raise ValueError("claim text must not be empty")
        if self.status in {
            EpistemicStatus.OBSERVED,
            EpistemicStatus.REPORTED,
            EpistemicStatus.DERIVED,
            EpistemicStatus.ESTIMATED,
            EpistemicStatus.FORECAST,
            EpistemicStatus.INFERRED,
            EpistemicStatus.HYPOTHESIS,
        } and not self.source_refs:
            raise ValueError("evidence-bearing epistemic claims require source references")


_EPISTEMIC_ORDER: dict[EpistemicStatus, int] = {
    EpistemicStatus.OBSERVED: 0,
    EpistemicStatus.REPORTED: 1,
    EpistemicStatus.DERIVED: 2,
    EpistemicStatus.ESTIMATED: 3,
    EpistemicStatus.FORECAST: 4,
    EpistemicStatus.INFERRED: 4,
    EpistemicStatus.HYPOTHESIS: 5,
    EpistemicStatus.UNKNOWN: 6,
    EpistemicStatus.INSUFFICIENT_EVIDENCE: 6,
}


def epistemic_distance(status: EpistemicStatus) -> int:
    """Return ordering distance from direct observation; not a probability."""
    return _EPISTEMIC_ORDER[status]


def may_support_decision(status: EpistemicStatus) -> bool:
    """Only statuses with an explicit evidentiary basis may enter decision support."""
    return status not in {EpistemicStatus.UNKNOWN, EpistemicStatus.INSUFFICIENT_EVIDENCE}


__all__ = [
    "EpistemicClaim",
    "EpistemicStatus",
    "epistemic_distance",
    "may_support_decision",
]
