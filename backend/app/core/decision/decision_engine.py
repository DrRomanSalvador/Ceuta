from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DecisionOption:
    option_id: str
    expected_benefit: float
    expected_harm: float
    cost: float
    uncertainty: float


@dataclass(frozen=True, slots=True)
class Decision:
    option_id: str
    score: float
    abstained: bool
    reason: str


class DecisionEngine:
    def choose(self, options: tuple[DecisionOption, ...], *, max_uncertainty: float = 0.5) -> Decision:
        eligible = tuple(o for o in options if o.uncertainty <= max_uncertainty)
        if not eligible:
            return Decision("ABSTAIN", 0.0, True, "all options exceed uncertainty threshold")
        best = max(eligible, key=lambda o: o.expected_benefit - o.expected_harm - o.cost)
        return Decision(best.option_id, best.expected_benefit - best.expected_harm - best.cost, False, "selected within uncertainty constraint")
