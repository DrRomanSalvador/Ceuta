"""Explicit intervention semantics: observational conditioning is never an intervention."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class Intervention:
    variable: str
    value: object
    operator: str = "do"
    mechanism: str | None = None

    def __post_init__(self) -> None:
        if self.operator != "do":
            raise ValueError("Causal intervention must use the explicit do operator")
        if not self.variable:
            raise ValueError("Intervention variable is required")


@dataclass(frozen=True)
class CounterfactualQuery:
    outcome: str
    factual_state_id: str
    intervention: Intervention
    reference_intervention: Intervention | None = None


class InterventionGate:
    """Rejects decision claims that attempt to use observational probability as causal effect."""

    @staticmethod
    def require_intervention(query: CounterfactualQuery) -> None:
        if query.intervention.operator != "do":
            raise ValueError("Counterfactual decisions require an explicit causal intervention")

    @staticmethod
    def observational_vs_interventional(
        observational_probability: float,
        interventional_probability: float | None,
    ) -> str:
        if interventional_probability is None:
            return "observational_only"
        if observational_probability == interventional_probability:
            return "no_identified_difference"
        return "interventional_effect_requires_causal_assumptions"
