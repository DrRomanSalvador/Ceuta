"""Integrated decision analysis with explicit alternatives, constraints and epistemic gates."""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Sequence


@dataclass(frozen=True, slots=True)
class Alternative:
    option_id: str
    scenario_utilities: Mapping[str, float]
    scenario_harms: Mapping[str, float]
    resource_cost: float = 0.0

    def __post_init__(self) -> None:
        if not self.option_id or not self.scenario_utilities:
            raise ValueError("alternative requires an id and scenario utilities")
        if set(self.scenario_utilities) != set(self.scenario_harms):
            raise ValueError("utility and harm scenarios must match")
        if self.resource_cost < 0 or not isfinite(self.resource_cost):
            raise ValueError("resource cost must be finite and non-negative")
        if any(not isfinite(float(v)) for v in (*self.scenario_utilities.values(), *self.scenario_harms.values())):
            raise ValueError("scenario values must be finite")


@dataclass(frozen=True, slots=True)
class DecisionAnalysis:
    option_id: str
    expected_utility: float
    worst_case_utility: float
    expected_harm: float
    cvar_utility: float
    maximum_regret: float
    feasible: bool
    objective: str
    rationale: tuple[str, ...]


class RigorousDecisionEngine:
    """Decision engine for finite, explicitly specified scenario spaces.

    It is deliberately fail-closed: missing scenarios, invalid probability mass,
    non-finite values and infeasible alternatives prevent a recommendation.
    """

    def analyze(
        self,
        alternatives: Sequence[Alternative],
        probabilities: Mapping[str, float],
        *,
        objective: str = "expected_utility",
        max_expected_harm: float | None = None,
        cvar_alpha: float = 0.95,
        minimum_expected_utility: float | None = None,
    ) -> tuple[DecisionAnalysis, ...]:
        self._validate_probability_space(probabilities)
        if not alternatives:
            raise ValueError("at least one alternative is required")
        if not 0 < cvar_alpha <= 1:
            raise ValueError("cvar_alpha must be in (0, 1]")
        if max_expected_harm is not None and not isfinite(max_expected_harm):
            raise ValueError("max_expected_harm must be finite")
        if minimum_expected_utility is not None and not isfinite(minimum_expected_utility):
            raise ValueError("minimum_expected_utility must be finite")
        scenario_ids = set(probabilities)
        analyses: list[DecisionAnalysis] = []
        for alternative in alternatives:
            if set(alternative.scenario_utilities) != scenario_ids:
                raise ValueError("every alternative must define every decision scenario")
            expected = sum(probabilities[s] * alternative.scenario_utilities[s] for s in scenario_ids) - alternative.resource_cost
            expected_harm = sum(probabilities[s] * alternative.scenario_harms[s] for s in scenario_ids)
            worst = min(alternative.scenario_utilities.values()) - alternative.resource_cost
            cvar = self._lower_tail_cvar(alternative.scenario_utilities, probabilities, cvar_alpha) - alternative.resource_cost
            feasible = (max_expected_harm is None or expected_harm <= max_expected_harm) and (minimum_expected_utility is None or expected >= minimum_expected_utility)
            analyses.append(DecisionAnalysis(alternative.option_id, expected, worst, expected_harm, cvar, 0.0, feasible, objective, ()))
        for index, analysis in enumerate(analyses):
            alternative = alternatives[index]
            regret = max(
                max(other.scenario_utilities[s] - other.resource_cost for other in alternatives)
                - (alternative.scenario_utilities[s] - alternative.resource_cost)
                for s in scenario_ids
            )
            rationale = (
                f"objective={objective}",
                f"expected_harm={analysis.expected_harm:.6g}",
                f"worst_case_utility={analysis.worst_case_utility:.6g}",
                f"cvar_{cvar_alpha:.6g}={analysis.cvar_utility:.6g}",
                f"maximum_regret={regret:.6g}",
                "recommendation is conditional on the supplied scenario model and probabilities",
            )
            analyses[index] = DecisionAnalysis(analysis.option_id, analysis.expected_utility, analysis.worst_case_utility,
                                               analysis.expected_harm, analysis.cvar_utility, regret,
                                               analysis.feasible, objective, rationale)
        return tuple(analyses)

    def select(self, analyses: Sequence[DecisionAnalysis]) -> DecisionAnalysis:
        feasible = [a for a in analyses if a.feasible]
        if not feasible:
            raise ValueError("no feasible alternative")
        objective = analyses[0].objective
        if any(a.objective != objective for a in analyses):
            raise ValueError("analysis objective mismatch")
        if objective == "expected_utility":
            return max(feasible, key=lambda a: a.expected_utility)
        if objective == "robust":
            return max(feasible, key=lambda a: a.worst_case_utility)
        if objective == "cvar":
            return max(feasible, key=lambda a: a.cvar_utility)
        if objective == "harm":
            return min(feasible, key=lambda a: a.expected_harm)
        if objective == "regret":
            return min(feasible, key=lambda a: a.maximum_regret)
        raise ValueError(f"unknown decision objective: {objective}")

    @staticmethod
    def _validate_probability_space(probabilities: Mapping[str, float]) -> None:
        if not probabilities or any(not key or not isfinite(float(value)) or value < 0 for key, value in probabilities.items()):
            raise ValueError("scenario probabilities must be finite and non-negative")
        if abs(sum(probabilities.values()) - 1.0) > 1e-9:
            raise ValueError("scenario probabilities must sum to one")

    @staticmethod
    def _lower_tail_cvar(values: Mapping[str, float], probabilities: Mapping[str, float], alpha: float) -> float:
        tail = 1.0 - alpha
        if tail <= 1e-15:
            return min(values.values())
        remaining = tail
        weighted = 0.0
        for scenario, value in sorted(values.items(), key=lambda item: item[1]):
            mass = min(probabilities[scenario], remaining)
            weighted += mass * value
            remaining -= mass
            if remaining <= 1e-15:
                break
        return weighted / tail
