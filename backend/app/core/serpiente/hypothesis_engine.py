from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Hypothesis:
    hypothesis_id: str
    statement: str
    evidence_for: tuple[str, ...]
    evidence_against: tuple[str, ...]
    missing_evidence: tuple[str, ...]
    independence_group: str

    @property
    def net_evidence(self) -> int:
        return len(self.evidence_for) - len(self.evidence_against)


class CompetingHypothesisEngine:
    def compare(self, hypotheses: tuple[Hypothesis, ...]) -> tuple[Hypothesis, ...]:
        if not hypotheses:
            raise ValueError("at least one hypothesis is required")
        groups = [h.independence_group for h in hypotheses]
        if len(groups) != len(set(groups)) and len(hypotheses) > 1:
            raise ValueError("hypotheses must have distinct independence groups")
        return tuple(sorted(hypotheses, key=lambda h: (-h.net_evidence, h.hypothesis_id)))
