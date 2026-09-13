"""Layer 2 rival-hypothesis records for CeutIA."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Iterable


REQUIRED_RIVAL_CODES = ("H1", "H2", "H3", "H4", "H5")


@dataclass(frozen=True, slots=True)
class Hypothesis:
    """Falsifiable explanation kept separate from epistemic status."""

    hypothesis_id: str
    code: str
    statement: str
    predictions: tuple[str, ...]
    favorable_evidence_ids: tuple[str, ...]
    contrary_evidence_ids: tuple[str, ...]
    confounders: tuple[str, ...]
    falsification_criterion: str
    missing_data: tuple[str, ...]
    verification_cost: str
    action_consequence: str
    inaction_consequence: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if self.code not in REQUIRED_RIVAL_CODES:
            raise ValueError("hypothesis code must be one of H1-H5")
        if not self.statement.strip():
            raise ValueError("hypothesis statement is required")
        if not self.predictions:
            raise ValueError("hypothesis requires predictions")
        if not self.falsification_criterion.strip():
            raise ValueError("hypothesis requires a falsification criterion")
        if not self.missing_data:
            raise ValueError("hypothesis must state missing data, including none if applicable")

    def to_dict(self) -> dict:
        return {
            "hypothesis_id": self.hypothesis_id,
            "code": self.code,
            "statement": self.statement,
            "predictions": self.predictions,
            "favorable_evidence_ids": self.favorable_evidence_ids,
            "contrary_evidence_ids": self.contrary_evidence_ids,
            "confounders": self.confounders,
            "falsification_criterion": self.falsification_criterion,
            "missing_data": self.missing_data,
            "verification_cost": self.verification_cost,
            "action_consequence": self.action_consequence,
            "inaction_consequence": self.inaction_consequence,
            "created_at": self.created_at.isoformat(),
        }


class RivalHypothesisSet:
    """Collection of rival explanations for one claim."""

    def __init__(self, claim_id: str) -> None:
        self.claim_id = claim_id
        self._items: dict[str, Hypothesis] = {}

    def add(self, hypothesis: Hypothesis) -> None:
        if hypothesis.hypothesis_id in self._items:
            raise ValueError("hypothesis_id already exists")
        self._items[hypothesis.hypothesis_id] = hypothesis

    def require_complete_rivals(self) -> tuple[Hypothesis, ...]:
        codes = {item.code for item in self._items.values()}
        missing = set(REQUIRED_RIVAL_CODES) - codes
        if missing:
            raise ValueError(f"rival hypothesis set incomplete: missing={sorted(missing)}")
        return tuple(self._items.values())

    def values(self) -> tuple[Hypothesis, ...]:
        return tuple(self._items.values())

    def evidence_ids(self) -> set[str]:
        return {
            evidence_id
            for hypothesis in self._items.values()
            for evidence_id in (
                *hypothesis.favorable_evidence_ids,
                *hypothesis.contrary_evidence_ids,
            )
        }

    @staticmethod
    def build_required_set(
        claim_id: str, hypotheses: Iterable[Hypothesis]
    ) -> RivalHypothesisSet:
        result = RivalHypothesisSet(claim_id)
        for hypothesis in hypotheses:
            result.add(hypothesis)
        result.require_complete_rivals()
        return result
