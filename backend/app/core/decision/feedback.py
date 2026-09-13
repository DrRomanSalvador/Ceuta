"""Closed-loop decision outcome and retrospective evaluation services."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .control_plane import DecisionAuditChain, DecisionOutcome, DecisionQuality, DecisionQualityEvaluator
from .persistence import SQLiteDecisionStore


@dataclass(frozen=True, slots=True)
class DecisionEvaluationBatch:
    evaluations: tuple[DecisionQuality, ...]
    mean_utility_error: float
    mean_harm_error: float
    mean_quality_score: float


class DecisionFeedbackService:
    """Persist observed outcomes and calculate retrospective decision quality."""

    def __init__(self, store: SQLiteDecisionStore, evaluator: DecisionQualityEvaluator | None = None, audit: DecisionAuditChain | None = None) -> None:
        self.store = store
        self.evaluator = evaluator or DecisionQualityEvaluator()
        self.audit = audit or DecisionAuditChain(store)

    def close_decision(self, outcome: DecisionOutcome, *, best_alternative_utility: float | None = None) -> DecisionQuality:
        self.store.record_outcome(outcome)
        quality = self.evaluator.evaluate(outcome, best_alternative_utility=best_alternative_utility)
        self.audit.append(outcome.decision_id, "decision_outcome", {
            "option_id": outcome.option_id,
            "outcome_at": outcome.outcome_at,
            "expected_utility": outcome.expected_utility,
            "observed_utility": outcome.observed_utility,
            "utility_error": outcome.utility_error,
            "expected_harm": outcome.expected_harm,
            "observed_harm": outcome.observed_harm,
            "harm_error": outcome.harm_error,
            "best_alternative_utility": best_alternative_utility,
            "regret": quality.regret,
            "quality_score": quality.quality_score,
        })
        return quality

    def evaluate(self, outcomes: Sequence[DecisionOutcome]) -> DecisionEvaluationBatch:
        if not outcomes:
            raise ValueError("at least one outcome is required")
        evaluations = tuple(self.evaluator.evaluate(x) for x in outcomes)
        return DecisionEvaluationBatch(
            evaluations=evaluations,
            mean_utility_error=sum(x.utility_error for x in evaluations) / len(evaluations),
            mean_harm_error=sum(x.harm_error for x in evaluations) / len(evaluations),
            mean_quality_score=sum(x.quality_score for x in evaluations) / len(evaluations),
        )


__all__ = ["DecisionEvaluationBatch", "DecisionFeedbackService"]
