"""Advanced causal reasoning primitives for CeutIA.

This module is deliberately conservative: it can generate, compare, stress-test and
validate causal models, but it never upgrades association to causation by itself.
All numerical estimators are represented as auditable contracts; production
estimators must provide their own data, identification assumptions and validation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from math import isfinite
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class TemporalObservation:
    variable: str
    time: float
    value: float
    available_at: float | None = None
    domain: str = "unknown"
    regime: str | None = None

    def __post_init__(self) -> None:
        if not self.variable or not isfinite(self.time) or not isfinite(self.value):
            raise ValueError("Temporal observations require finite variable, time and value")
        if self.available_at is not None and self.available_at < self.time:
            raise ValueError("available_at cannot precede event time")


@dataclass(frozen=True)
class TemporalRelation:
    cause: str
    effect: str
    lag: float
    support: float
    stability: float
    regime: str | None = None
    mechanism: str | None = None

    def __post_init__(self) -> None:
        if self.lag < 0 or not 0 <= self.support <= 1 or not 0 <= self.stability <= 1:
            raise ValueError("Invalid temporal relation")


@dataclass(frozen=True)
class CausalModel:
    model_id: str
    edges: tuple[tuple[str, str], ...]
    assumptions: tuple[str, ...]
    weight: float = 1.0
    regime: str | None = None

    def __post_init__(self) -> None:
        if not self.model_id or not self.assumptions:
            raise ValueError("A causal model requires an id and explicit assumptions")
        if not 0 <= self.weight <= 1:
            raise ValueError("Model weight must be in [0,1]")


@dataclass(frozen=True)
class CausalEffect:
    exposure: str
    outcome: str
    estimand: str
    estimate: float | None
    lower: float | None
    upper: float | None
    identified: bool
    assumptions: tuple[str, ...]
    subgroup: str | None = None
    regime: str | None = None
    lag: float | None = None

    def __post_init__(self) -> None:
        if self.lower is not None and self.upper is not None and self.lower > self.upper:
            raise ValueError("Effect interval is invalid")
        if not self.assumptions:
            raise ValueError("Causal effects require explicit assumptions")


@dataclass(frozen=True)
class HeterogeneousEffect:
    effect: CausalEffect
    effect_modifier: str
    stratum: str
    estimate: float | None
    sample_support: float


@dataclass(frozen=True)
class CounterfactualResult:
    outcome: str
    factual_value: float
    counterfactual_value: float | None
    effect: float | None
    identified: bool
    assumptions: tuple[str, ...]
    uncertainty: tuple[str, ...] = ()


@dataclass(frozen=True)
class FalsificationChallenge:
    name: str
    target_assumption: str
    expected_result: str
    observed_result: str | None = None
    passed: bool | None = None


@dataclass(frozen=True)
class CausalValidation:
    hypothesis_id: str
    predicted_effect: float
    observed_effect: float | None
    error: float | None
    validated: bool
    explanation: str
    intervention_id: str | None = None


@dataclass(frozen=True)
class ActiveCausalQuery:
    query_id: str
    observation: str
    target_uncertainty: str
    expected_information_gain: float
    cost: float
    feasibility: float
    rationale: str

    @property
    def priority(self) -> float:
        if self.cost <= 0:
            return self.expected_information_gain * self.feasibility
        return self.expected_information_gain * self.feasibility / self.cost


@dataclass(frozen=True)
class CausalLoopAssessment:
    nodes: tuple[str, ...]
    lagged: bool
    feedback_strength: float
    regime_sensitive: bool
    tipping_threshold: float | None = None
    hysteresis: bool = False


class TemporalCausalAnalyzer:
    """Detects temporal precedence, lag structure and regime instability without causal promotion."""

    def relations(
        self,
        observations: Sequence[TemporalObservation],
        max_lag: float = 30.0,
    ) -> tuple[TemporalRelation, ...]:
        grouped: dict[str, list[TemporalObservation]] = {}
        for obs in observations:
            grouped.setdefault(obs.variable, []).append(obs)
        variables = sorted(grouped)
        result: list[TemporalRelation] = []
        for cause in variables:
            for effect in variables:
                if cause == effect:
                    continue
                pairs = [(a, b) for a in grouped[cause] for b in grouped[effect] if 0 < b.time - a.time <= max_lag]
                if not pairs:
                    continue
                lags = [b.time - a.time for a, b in pairs]
                support = min(1.0, len(pairs) / max(1, min(len(grouped[cause]), len(grouped[effect]))))
                result.append(TemporalRelation(cause, effect, sum(lags) / len(lags), support, 1.0))
        return tuple(result)


class ConfoundingAnalyzer:
    """Makes confounding and collider risks explicit rather than silently adjusting them."""

    @staticmethod
    def candidates(parents_of_exposure: Iterable[str], declared: Iterable[str]) -> tuple[str, ...]:
        declared_set = set(declared)
        return tuple(sorted(set(parents_of_exposure) - declared_set))

    @staticmethod
    def adjustment_status(candidates: Iterable[str], adjustment: Iterable[str]) -> str:
        c, a = set(candidates), set(adjustment)
        if not c:
            return "no_known_backdoor_candidates"
        if c <= a:
            return "known_backdoor_candidates_addressed"
        return "unresolved_confounding"

    @staticmethod
    def collider_warning(node: str, causes: Sequence[str]) -> str:
        return f"Do not condition on {node}: candidate collider of {', '.join(sorted(causes))}"


class InteractionAnalyzer:
    @staticmethod
    def candidates(exposure: str, modifiers: Sequence[str]) -> tuple[str, ...]:
        return tuple(f"{exposure}*{m}" for m in sorted(set(modifiers)) if m != exposure)

    @staticmethod
    def classify(effect_main: float | None, interaction: float | None) -> str:
        if interaction is None:
            return "untested"
        if effect_main is None:
            return "interaction_without_main_effect"
        if interaction == 0:
            return "no_detected_interaction"
        return "effect_modification_candidate"


class CausalModelEnsemble:
    """Preserves disagreement between structurally distinct causal models."""

    @staticmethod
    def normalize(models: Sequence[CausalModel]) -> tuple[CausalModel, ...]:
        total = sum(m.weight for m in models)
        if total <= 0:
            raise ValueError("At least one model must carry positive weight")
        return tuple(CausalModel(m.model_id, m.edges, m.assumptions, m.weight / total, m.regime) for m in models)

    @staticmethod
    def disagreement(models: Sequence[CausalModel]) -> frozenset[tuple[str, str]]:
        normalized = CausalModelEnsemble.normalize(models)
        all_edges = {edge for m in normalized for edge in m.edges}
        return frozenset(edge for edge in all_edges if len({edge in m.edges for m in normalized}) > 1)


class CounterfactualEngine:
    @staticmethod
    def require_identification(identified: bool, assumptions: Sequence[str]) -> None:
        if not identified:
            raise ValueError("Counterfactual effect requires an identified causal model")
        if not assumptions:
            raise ValueError("Counterfactual effect requires explicit assumptions")

    @staticmethod
    def compute(factual: float, counterfactual: float, identified: bool, assumptions: Sequence[str]) -> CounterfactualResult:
        CounterfactualEngine.require_identification(identified, assumptions)
        return CounterfactualResult("outcome", factual, counterfactual, counterfactual - factual, True, tuple(assumptions))


class CausalStressTester:
    @staticmethod
    def challenge(model: CausalModel, alternative_assumptions: Sequence[str]) -> tuple[FalsificationChallenge, ...]:
        return tuple(
            FalsificationChallenge(
                name=f"break:{assumption}",
                target_assumption=assumption,
                expected_result="model remains coherent only if assumption is unnecessary",
            )
            for assumption in alternative_assumptions
            if assumption not in model.assumptions
        )


class ActiveCausalLearning:
    @staticmethod
    def rank(queries: Sequence[ActiveCausalQuery]) -> tuple[ActiveCausalQuery, ...]:
        return tuple(sorted(queries, key=lambda q: (-q.priority, q.query_id)))


class CrossDomainCausalEngine:
    @staticmethod
    def connect(edges: Sequence[tuple[str, str, str, str]]) -> tuple[tuple[str, str, str, str], ...]:
        """Return only explicit cross-domain mechanisms: source domain, variable, target domain, variable."""
        result = []
        for source_domain, source, target_domain, target in edges:
            if source_domain != target_domain and source != target:
                result.append((source_domain, source, target_domain, target))
        return tuple(sorted(set(result)))


class RegimeCausalEngine:
    @staticmethod
    def compare(effects: Sequence[CausalEffect]) -> Mapping[str, tuple[float | None, ...]]:
        result: dict[str, list[float | None]] = {}
        for effect in effects:
            result.setdefault(effect.regime or "unknown", []).append(effect.estimate)
        return {key: tuple(values) for key, values in sorted(result.items())}


class FeedbackAnalyzer:
    @staticmethod
    def assess(nodes: Sequence[str], strength: float, lagged: bool, threshold: float | None = None, hysteresis: bool = False) -> CausalLoopAssessment:
        if not nodes or len(set(nodes)) < 2:
            raise ValueError("A feedback loop requires at least two distinct nodes")
        if not 0 <= strength <= 1:
            raise ValueError("Feedback strength must be in [0,1]")
        if not lagged:
            raise ValueError("Feedback in a dynamic causal system must be temporally lagged")
        return CausalLoopAssessment(tuple(nodes), True, strength, threshold is not None, threshold, hysteresis)


class ProspectiveCausalValidator:
    @staticmethod
    def validate(hypothesis_id: str, predicted: float, observed: float | None, tolerance: float, intervention_id: str | None = None) -> CausalValidation:
        if tolerance < 0:
            raise ValueError("Tolerance cannot be negative")
        if observed is None:
            return CausalValidation(hypothesis_id, predicted, None, None, False, "outcome_not_observed", intervention_id)
        error = observed - predicted
        passed = abs(error) <= tolerance
        explanation = "prospective_prediction_within_tolerance" if passed else "prospective_prediction_outside_tolerance"
        return CausalValidation(hypothesis_id, predicted, observed, error, passed, explanation, intervention_id)
