"""Decision-theoretic optimization primitives with explicit uncertainty handling."""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence


@dataclass(frozen=True, slots=True)
class DecisionScore:
    option_id: str
    expected_utility: float
    worst_case_utility: float
    expected_harm: float
    maximum_regret: float
    cvar_utility: float
    feasible: bool


@dataclass(frozen=True, slots=True)
class ValueOfInformation:
    question: str
    expected_value_of_sample_information: float
    acquisition_cost: float
    net_value: float
    assumptions: tuple[str, ...]


class DecisionOptimizer:
    """Finite-scenario optimizer; this layer never invents probabilities."""

    @staticmethod
    def _validate_probabilities(probabilities: Sequence[float]) -> None:
        if not probabilities or any(not isfinite(p) or p < 0 for p in probabilities):
            raise ValueError("probabilities must be finite and non-negative")
        if abs(sum(probabilities) - 1.0) > 1e-9:
            raise ValueError("probabilities must sum to one")

    @classmethod
    def score(cls, option_id: str, utilities: Sequence[float], harms: Sequence[float],
              probabilities: Sequence[float], *, resource_cost: float = 0.0,
              cvar_alpha: float = 0.95, max_harm: float | None = None,
              maximum_regret: float | None = None) -> DecisionScore:
        if not utilities or len({len(utilities), len(harms), len(probabilities)}) != 1:
            raise ValueError("utilities, harms and probabilities must have equal non-zero length")
        cls._validate_probabilities(probabilities)
        if not 0 < cvar_alpha <= 1 or resource_cost < 0:
            raise ValueError("invalid alpha or resource cost")
        if any(not isfinite(x) for x in (*utilities, *harms)):
            raise ValueError("utilities and harms must be finite")
        expected = sum(p * u for p, u in zip(probabilities, utilities)) - resource_cost
        worst = min(utilities) - resource_cost
        expected_harm = sum(p * h for p, h in zip(probabilities, harms))
        regret = 0.0 if maximum_regret is None else maximum_regret
        pairs = sorted(zip(utilities, probabilities), key=lambda x: x[0])
        tail_mass = 1.0 - cvar_alpha
        if tail_mass <= 1e-15:
            cvar = worst
        else:
            remaining = tail_mass
            weighted = 0.0
            for utility, probability in pairs:
                take = min(probability, remaining)
                weighted += take * utility
                remaining -= take
                if remaining <= 1e-15:
                    break
            cvar = weighted / tail_mass - resource_cost
        feasible = max_harm is None or expected_harm <= max_harm
        return DecisionScore(option_id, expected, worst, expected_harm, regret, cvar, feasible)

    @staticmethod
    def select(scores: Sequence[DecisionScore], objective: str = "expected_utility") -> DecisionScore:
        feasible = [s for s in scores if s.feasible]
        if not feasible:
            raise ValueError("no feasible decision")
        if objective == "expected_utility":
            return max(feasible, key=lambda s: s.expected_utility)
        if objective == "robust":
            return max(feasible, key=lambda s: s.worst_case_utility)
        if objective == "cvar":
            return max(feasible, key=lambda s: s.cvar_utility)
        if objective == "harm":
            return min(feasible, key=lambda s: s.expected_harm)
        if objective == "regret":
            return min(feasible, key=lambda s: (s.maximum_regret, -s.expected_utility))
        raise ValueError(f"unknown objective: {objective}")

    @staticmethod
    def evsi(prior_scores: Sequence[float], sampled_scores: Sequence[Sequence[float]],
             acquisition_cost: float, *, question: str, assumptions: Sequence[str]) -> ValueOfInformation:
        if not prior_scores or not sampled_scores:
            raise ValueError("prior and sampled scores are required")
        if acquisition_cost < 0 or not isfinite(acquisition_cost):
            raise ValueError("acquisition cost must be finite and non-negative")
        if any(len(row) != len(prior_scores) for row in sampled_scores):
            raise ValueError("sampled score rows must match the number of options")
        prior_optimum = max(prior_scores)
        posterior_optimum = sum(max(row) for row in sampled_scores) / len(sampled_scores)
        evsi = posterior_optimum - prior_optimum
        return ValueOfInformation(question, evsi, acquisition_cost, evsi - acquisition_cost,
                                  tuple(assumptions))
