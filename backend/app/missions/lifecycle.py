from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


class LifecycleError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class LifecycleReview:
    mission_id: str
    status: str
    evidence_refs: tuple[str, ...]
    reasons: tuple[str, ...]
    observed_value: str
    observed_complexity: str
    validation_state: str

    @property
    def action_required(self) -> bool:
        return self.status in {"REVIEW", "PROPOSE_RETIREMENT", "PROPOSE_REVISION"}


class MissionLifecycleGovernance:
    """Evidence-gated review layer for active missions."""

    REQUIRED_METRICS = ("value", "complexity", "validation", "redundancy", "coherence", "usage")

    @classmethod
    def review(cls, *, mission_id: str, metrics: Mapping[str, str], evidence_refs: Sequence[str]) -> LifecycleReview:
        if not mission_id.strip():
            raise LifecycleError("MISSION_ID is required")
        missing = [key for key in cls.REQUIRED_METRICS if not metrics.get(key)]
        if missing:
            raise LifecycleError(f"Lifecycle review is incomplete: missing {missing}")
        if not evidence_refs:
            raise LifecycleError("Lifecycle review requires explicit evidence references")

        reasons: list[str] = []
        if metrics["redundancy"].upper() in {"HIGH", "MATERIAL"}:
            reasons.append("material redundancy")
        if metrics["validation"].upper() in {"FAILED", "PERSISTENTLY_UNVALIDATED"}:
            reasons.append("persistent validation failure")
        if metrics["coherence"].upper() in {"BROKEN", "LOW"}:
            reasons.append("scope or identity coherence has degraded")
        if metrics["usage"].upper() in {"NONE", "DORMANT"}:
            reasons.append("mission has no observed operational use")
        if metrics["complexity"].upper() in {"EXCESSIVE", "HIGH"} and metrics["value"].upper() in {"LOW", "UNCERTAIN"}:
            reasons.append("complexity is not supported by observed value")

        if reasons and metrics["value"].upper() in {"NONE", "LOW", "NEGATIVE"}:
            status = "PROPOSE_RETIREMENT"
        elif reasons:
            status = "PROPOSE_REVISION"
        else:
            status = "ACTIVE_RETAIN"
        return LifecycleReview(mission_id, status, tuple(evidence_refs), tuple(reasons), metrics["value"], metrics["complexity"], metrics["validation"])

    @staticmethod
    def authorize_retirement(review: LifecycleReview, authority_context: Mapping[str, bool]) -> None:
        if review.status != "PROPOSE_RETIREMENT":
            raise LifecycleError("Retirement authorization requires a retirement proposal")
        if not authority_context.get("CAN_AUTHORIZE", False):
            raise LifecycleError("Mission retirement requires CAN_AUTHORIZE")
