"""Temporal and causal boundaries for closed-loop outcome feedback."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class FeedbackWindow:
    decision_time: str
    outcome_time: str
    horizon_end: str

    def __post_init__(self) -> None:
        decision = self._parse(self.decision_time)
        outcome = self._parse(self.outcome_time)
        end = self._parse(self.horizon_end)
        if outcome < decision:
            raise ValueError("outcome cannot precede decision time")
        if end < decision:
            raise ValueError("feedback horizon cannot precede decision time")
        if outcome > end:
            raise ValueError("outcome falls outside declared feedback horizon")

    @staticmethod
    def _parse(value: str) -> datetime:
        try:
            parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError as exc:
            raise ValueError("feedback timestamps must use ISO-8601") from exc
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError("feedback timestamps must be timezone-aware")
        return parsed


@dataclass(frozen=True, slots=True)
class CausalFeedbackContract:
    intervention_ref: str
    target_ref: str
    comparator_ref: str
    time_zero: str
    identification_assumptions: tuple[str, ...]
    causal_question: str

    def __post_init__(self) -> None:
        if not all((self.intervention_ref, self.target_ref, self.comparator_ref, self.time_zero, self.causal_question)):
            raise ValueError("causal feedback requires intervention, target, comparator, time zero and question")
        if not self.identification_assumptions:
            raise ValueError("causal feedback requires explicit identification assumptions")

    def decision_ready(self) -> bool:
        return bool(self.intervention_ref and self.target_ref and self.comparator_ref and self.identification_assumptions)


__all__ = ["CausalFeedbackContract", "FeedbackWindow"]
