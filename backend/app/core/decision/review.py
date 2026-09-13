"""Human review and override enforcement for CeutIA decisions."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256

from .control_plane import DecisionAuditChain, HumanDecisionReview


class HumanReviewService:
    def __init__(self, audit: DecisionAuditChain) -> None:
        self.audit = audit

    def resolve(
        self,
        *,
        decision_id: str,
        actor_id: str,
        authority: str,
        original_disposition: str,
        human_disposition: str,
        reason: str,
        modified_option: str | None = None,
    ) -> HumanDecisionReview:
        if not actor_id.strip() or not authority.strip():
            raise ValueError("authorized actor and authority are required")
        if not reason.strip():
            raise ValueError("human review requires a reason")
        timestamp = datetime.now(timezone.utc).isoformat()
        review_id = sha256(f"{decision_id}|{actor_id}|{timestamp}".encode()).hexdigest()
        review = HumanDecisionReview(
            decision_id=decision_id,
            review_id=review_id,
            actor_id=actor_id,
            authority=authority,
            original_disposition=original_disposition,
            human_disposition=human_disposition,
            reason=reason,
            modified_option=modified_option,
            timestamp=timestamp,
        )
        self.audit.append(decision_id, "human_review", {
            "review_id": review.review_id,
            "actor_id": review.actor_id,
            "authority": review.authority,
            "original_disposition": review.original_disposition,
            "human_disposition": review.human_disposition,
            "modified_option": review.modified_option,
            "reason": review.reason,
        })
        return review


__all__ = ["HumanReviewService"]
