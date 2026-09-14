"""Decision outcome feedback linked to model-release governance."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from app.core.decision.control_plane import DecisionOutcome, DecisionQuality, DecisionQualityEvaluator, DecisionAuditChain
from app.core.decision.persistence import SQLiteDecisionStore
from .model_governance import ModelGovernanceRecord


@dataclass(frozen=True, slots=True)
class FeedbackDisposition:
    decision_id: str
    model_refs: tuple[str, ...]
    quality: DecisionQuality
    review_required: bool
    reason: str
    evaluated_at: str


class FeedbackGovernanceService:
    """Turns observed outcomes into auditable model/decision review signals."""

    def __init__(self, store: SQLiteDecisionStore, *, quality_evaluator: DecisionQualityEvaluator | None = None) -> None:
        self.store = store
        self.evaluator = quality_evaluator or DecisionQualityEvaluator()
        self.audit = DecisionAuditChain(store)

    def close(
        self,
        outcome: DecisionOutcome,
        *,
        model_refs: tuple[str, ...],
        best_alternative_utility: float | None = None,
        maximum_absolute_utility_error: float = 1.0,
        maximum_absolute_harm_error: float = 1.0,
    ) -> FeedbackDisposition:
        if maximum_absolute_utility_error < 0 or maximum_absolute_harm_error < 0:
            raise ValueError("feedback thresholds must be non-negative")
        self.store.record_outcome(outcome)
        quality = self.evaluator.evaluate(outcome, best_alternative_utility=best_alternative_utility)
        review_required = abs(quality.utility_error) > maximum_absolute_utility_error or abs(quality.harm_error) > maximum_absolute_harm_error
        reason = "model/decision review required" if review_required else "outcome within configured retrospective error bounds"
        evaluated_at = datetime.now(timezone.utc).isoformat()
        self.audit.append(outcome.decision_id, "retrospective_evaluation", {
            "model_refs": model_refs,
            "quality_score": quality.quality_score,
            "utility_error": quality.utility_error,
            "harm_error": quality.harm_error,
            "regret": quality.regret,
            "review_required": review_required,
            "reason": reason,
        })
        return FeedbackDisposition(outcome.decision_id, model_refs, quality, review_required, reason, evaluated_at)


__all__ = ["FeedbackDisposition", "FeedbackGovernanceService"]
