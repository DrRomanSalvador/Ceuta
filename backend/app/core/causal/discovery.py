"""Conservative hypothesis generation; discovery proposes, identification disposes."""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Mapping, Sequence


@dataclass(frozen=True)
class AssociationCandidate:
    exposure: str
    outcome: str
    score: float
    lag: float | None = None


class CausalHypothesisGenerator:
    """Generate candidates without upgrading statistical association to causality."""

    def generate(
        self,
        candidates: Sequence[AssociationCandidate],
        variables: Sequence[str],
    ) -> tuple[tuple[str, str], ...]:
        pairs = {(c.exposure, c.outcome) for c in candidates if c.exposure != c.outcome}
        # Interaction search is deliberately explicit and never asserted as causal.
        interactions = tuple(combinations(sorted(set(variables)), 2))
        return tuple(sorted(pairs | set(interactions)))

    @staticmethod
    def association_is_not_causation(candidate: AssociationCandidate) -> bool:
        return candidate.exposure != candidate.outcome
