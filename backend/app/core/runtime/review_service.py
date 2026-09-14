"""Authorized human review and override service for decision outputs."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256

from app.core.decision.control_plane import DecisionAuditChain, HumanDecisionReview
from app.core.decision.persistence import SQLiteDecisionStore
from app.core.decision.review_policy import DecisionRisk, ReviewPolicy, ReviewDisposition


@dataclass(frozen=True, slots=True)
class ReviewAuthorization:
    actor_id: str
    authority: str
    allowed_risks: frozenset[DecisionRisk]
    owner_scope: str | None = None

    def permits(self, risk: DecisionRisk) -> bool:
        return risk in self.allowed_risks


class DecisionReviewService:
    """Persists human disposition only after explicit authority checks."""

    def __init__(self, store: SQLiteDecisionStore, *, audit: DecisionAuditChain | None = None, policy: ReviewPolicy | None = None) -> None:
        self.store = store
        self.audit = audit or DecisionAuditChain(store)
        self.policy = policy

    def review(
        self,
        *,
        decision_id: str,
        risk_class: DecisionRisk,
        authorization: ReviewAuthorization,
        original_disposition: str,
        human_disposition: str,
        reason: str,
        modified_option: str | None = None,
    ) -> HumanDecisionReview:
        if not authorization.actor_id or not authorization.authority:
            raise PermissionError("human review requires actor identity and authority")
        if not authorization.permits(risk_class):
            raise PermissionError("actor is not authorized for this decision risk class")
        if not reason.strip():
            raise ValueError("human review reason is required")
        if original_disposition not in {item.value for item in ReviewDisposition} and not original_disposition:
            raise ValueError("invalid original disposition")
        timestamp = datetime.now(timezone.utc).isoformat()
        review_id = sha256(f"{decision_id}:{authorization.actor_id}:{timestamp}".encode()).hexdigest()
        review = HumanDecisionReview(
            decision_id=decision_id,
            review_id=review_id,
            actor_id=authorization.actor_id,
            authority=authorization.authority,
            original_disposition=original_disposition,
            human_disposition=human_disposition,
            reason=reason,
            modified_option=modified_option,
            timestamp=timestamp,
        )
        self.store.record_review(review)
        self.audit.append(decision_id, "human_review", {
            "review_id": review.review_id,
            "actor_id": review.actor_id,
            "authority": review.authority,
            "risk_class": risk_class.value,
            "original_disposition": original_disposition,
            "human_disposition": human_disposition,
            "modified_option": modified_option,
            "reason": reason,
        })
        return review


__all__ = ["DecisionReviewService", "ReviewAuthorization"]
