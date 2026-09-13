"""Closed-loop decision outcome and retrospective evaluation services."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence

from .control_plane import DecisionOutcome, DecisionQuality, DecisionQualityEvaluator
from .persistence import SQLiteDecisionStore


@dataclass(frozen=True, slots=True)
class DecisionEvaluationBatch:
    evaluations: tuple[DecisionQuality, ...]
    mean_utility_error: float
    mean_harm_error: float
    mean_quality_score: float


class DecisionFeedbackService:
    """Persist observed outcomes and calculate retrospective decision quality."""

    def __init__(self, store: SQLiteDecisionStore, evaluator: DecisionQualityEvaluator | None = None) -> None:
        self.store = store
        self.evaluator = evaluator or DecisionQualityEvaluator()

    def close_decision(self, outcome: DecisionOutcome, *, best_alternative_utility: float | None = None) -> DecisionQuality:
        self.store.record_outcome(outcome)
        return self.evaluator.evaluate(outcome, best_alternative_utility=best_alternative_utility)

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
