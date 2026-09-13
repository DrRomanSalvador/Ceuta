"""Human review and override enforcement for CeutIA decisions."""
from __future__ import annotations

from datetime import datetime, timezone
from hashlib import sha256

from .automation_bias import AutomationBiasGate, HumanReviewProtocol
from .control_plane import DecisionAuditChain, HumanDecisionReview


class HumanReviewService:
    def __init__(self, audit: DecisionAuditChain, automation_bias_gate: AutomationBiasGate | None = None) -> None:
        self.audit = audit
        self.automation_bias_gate = automation_bias_gate or AutomationBiasGate()

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
        automation_protocol: HumanReviewProtocol | None = None,
    ) -> HumanDecisionReview:
        if not actor_id.strip() or not authority.strip():
            raise ValueError("authorized actor and authority are required")
        if not reason.strip():
            raise ValueError("human review requires a reason")
        if automation_protocol is not None:
            if automation_protocol.decision_id != decision_id or automation_protocol.reviewer_id != actor_id:
                raise ValueError("automation-bias protocol identity does not match human review")
            if not self.automation_bias_gate.evaluate(automation_protocol):
                raise ValueError("automation-bias review protocol is incomplete")
        timestamp = datetime.now(timezone.utc).isoformat()
        review_id = sha256(f"{decision_id}|{actor_id}|{timestamp}".encode()).hexdigest()
        if automation_protocol is not None and automation_protocol.review_id != review_id:
            raise ValueError("automation-bias protocol must reference the generated review_id")
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
            "automation_bias_protocol": automation_protocol is not None,
        })
        record_review = getattr(self.audit.store, "record_review", None)
        if record_review is not None:
            record_review(review)
        return review


__all__ = ["HumanReviewService"]
