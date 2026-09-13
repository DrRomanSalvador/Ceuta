"""Unified scientific inference boundary for CeutIA.

The purpose of this module is to make sophisticated mathematics operationally
simple without making the assumptions invisible. Specialist estimators remain
specialists; this layer selects an appropriate inferential regime, records why
it was selected, propagates epistemic state, and abstains when the declared
problem cannot support a defensible answer.

This is an orchestration contract, not a universal theorem prover. The engine
never infers causality from association, never treats model disagreement as
noise, and never converts missing identifiability into numerical confidence.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from ..decision.control_plane import UncertaintyState
from ..errors import ContractViolation


class InferenceRegime(str, Enum):
    LINEAR_GAUSSIAN = "LINEAR_GAUSSIAN"
    NONLINEAR_LOCAL = "NONLINEAR_LOCAL"
    NONLINEAR_NON_GAUSSIAN = "NONLINEAR_NON_GAUSSIAN"
    SWITCHING_REGIME = "SWITCHING_REGIME"
    HIERARCHICAL = "HIERARCHICAL"
    SPATIOTEMPORAL = "SPATIOTEMPORAL"
    NETWORK = "NETWORK"
    CAUSAL = "CAUSAL"
    ROBUST_NONPARAMETRIC = "ROBUST_NONPARAMETRIC"
    ABSTAIN = "ABSTAIN"


class EpistemicLevel(str, Enum):
    OBSERVED = "OBSERVED"
    ESTIMATED = "ESTIMATED"
    PREDICTIVE = "PREDICTIVE"
    CAUSAL = "CAUSAL"
    DECISIONAL = "DECISIONAL"


@dataclass(frozen=True, slots=True)
class InferenceProblem:
    """Declared structure of an inference problem."""

    dimension: int
    nonlinear: bool = False
    non_gaussian: bool = False
    regime_switching: bool = False
    hierarchical: bool = False
    spatial_dependence: bool = False
    network_dependence: bool = False
    causal_estimand: bool = False
    missing_not_at_random_possible: bool = False
    measurement_error: bool = False
    heavy_tails: bool = False
    irregular_sampling: bool = False
    delayed_observation: bool = False
    identifiable: bool = True
    sufficient_observation_model: bool = True
    sufficient_covariance_model: bool = True
    sample_size: int | None = None

    def __post_init__(self) -> None:
        if self.dimension < 1:
            raise ContractViolation("dimension must be positive")
        if self.sample_size is not None and self.sample_size < 1:
            raise ContractViolation("sample_size must be positive when provided")


@dataclass(frozen=True, slots=True)
class InferencePlan:
    primary: InferenceRegime
    required_methods: tuple[InferenceRegime, ...]
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    assumptions: tuple[str, ...]
    rationale: tuple[str, ...]
    abstain: bool


@dataclass(frozen=True, slots=True)
class EvidenceContribution:
    evidence_id: str
    source_ids: tuple[str, ...]
    independent_origin_count: int
    epistemic_status: str
    supports: bool | None
    weight: float

    def __post_init__(self) -> None:
        if not self.evidence_id or not self.source_ids:
            raise ContractViolation("evidence requires identity and source IDs")
        if self.independent_origin_count < 0:
            raise ContractViolation("independent_origin_count cannot be negative")
        if self.weight < 0.0:
            raise ContractViolation("evidence weight cannot be negative")


@dataclass(frozen=True, slots=True)
class InferenceResult:
    problem: InferenceProblem
    plan: InferencePlan
    epistemic_level: EpistemicLevel
    evidence: tuple[EvidenceContribution, ...]
    uncertainty_summary: str
    uncertainty_state: UncertaintyState
    claims: tuple[str, ...]
    limitations: tuple[str, ...]

    @property
    def usable(self) -> bool:
        return not self.plan.abstain and bool(self.claims)


class ScientificInferenceEngine:
    """Routes declared problems to the least-assumption-compatible regime."""

    def plan(self, problem: InferenceProblem) -> InferencePlan:
        blockers: list[str] = []
        warnings: list[str] = []
        rationale: list[str] = []
        required: list[InferenceRegime] = []

        if not problem.identifiable:
            blockers.append("the declared estimand/state is not identifiable")
        if not problem.sufficient_observation_model:
            blockers.append("observation process is insufficiently specified")
        if problem.missing_not_at_random_possible and not problem.sufficient_observation_model:
            blockers.append("MNAR is possible but the selection/observation mechanism is unspecified")
        if not problem.sufficient_covariance_model:
            blockers.append("dependence/covariance structure is insufficiently specified")

        if blockers:
            return InferencePlan(InferenceRegime.ABSTAIN, (), tuple(blockers), tuple(warnings), (), tuple(rationale), True)

        if problem.causal_estimand:
            required.append(InferenceRegime.CAUSAL)
            rationale.append("causal estimand requires an identification/causal-inference layer")
        if problem.spatial_dependence:
            required.append(InferenceRegime.SPATIOTEMPORAL)
            rationale.append("spatial dependence prevents treating observations as independent")
        if problem.network_dependence:
            required.append(InferenceRegime.NETWORK)
            rationale.append("network dependence requires explicit relational structure")
        if problem.hierarchical:
            required.append(InferenceRegime.HIERARCHICAL)
            rationale.append("nested units require multilevel structure")
        if problem.regime_switching:
            required.append(InferenceRegime.SWITCHING_REGIME)
            rationale.append("state dynamics are not assumed stationary across regimes")
        if problem.nonlinear and problem.non_gaussian:
            required.append(InferenceRegime.NONLINEAR_NON_GAUSSIAN)
            rationale.append("both nonlinear dynamics and non-Gaussian uncertainty are declared")
        elif problem.nonlinear:
            required.append(InferenceRegime.NONLINEAR_LOCAL)
            rationale.append("nonlinear dynamics require local or nonlinear state estimation")
        elif problem.non_gaussian:
            required.append(InferenceRegime.NONLINEAR_NON_GAUSSIAN)
            rationale.append("non-Gaussian uncertainty invalidates a default Gaussian filter")
        else:
            required.append(InferenceRegime.LINEAR_GAUSSIAN)
            rationale.append("declared linear/Gaussian assumptions permit the simpler exact state-space regime")

        if problem.heavy_tails or problem.measurement_error or problem.missing_not_at_random_possible:
            required.append(InferenceRegime.ROBUST_NONPARAMETRIC)
            rationale.append("measurement/selection/heavy-tail risk requires robustness or sensitivity analysis")
        if problem.irregular_sampling:
            warnings.append("time intervals must enter the transition/noise model; equal-step assumptions are prohibited")
        if problem.delayed_observation:
            warnings.append("observation delay requires an explicit delay/nowcasting model; filtering alone is insufficient")
        if problem.sample_size is not None and problem.sample_size < max(20, 5 * problem.dimension):
            warnings.append("finite-sample uncertainty may dominate asymptotic approximations")

        unique = tuple(dict.fromkeys(required))
        primary = unique[0] if unique else InferenceRegime.ABSTAIN
        assumptions = (
            "model assumptions are explicit rather than inferred silently",
            "uncertainty is carried separately from the point state",
            "observations are not treated as causal effects",
            "model selection does not constitute scientific validation",
        )
        return InferencePlan(primary, unique, tuple(blockers), tuple(warnings), assumptions, tuple(rationale), False)

    def compose(
        self,
        problem: InferenceProblem,
        *,
        evidence: Iterable[EvidenceContribution] = (),
        epistemic_level: EpistemicLevel = EpistemicLevel.ESTIMATED,
        claims: Iterable[str] = (),
        uncertainty_summary: str = "uncertainty not yet quantified",
        uncertainty_state: UncertaintyState | None = None,
        limitations: Iterable[str] = (),
    ) -> InferenceResult:
        plan = self.plan(problem)
        evidence_tuple = tuple(evidence)
        claims_tuple = tuple(claims)
        limitations_tuple = tuple(limitations)
        if plan.abstain:
            claims_tuple = ()
            limitations_tuple = tuple(dict.fromkeys((*plan.blockers, *limitations_tuple)))
        state = uncertainty_state or UncertaintyState(
            1.0,
            source_refs=tuple(item.evidence_id for item in evidence_tuple),
            method="unquantified-inference-uncertainty",
        )
        return InferenceResult(
            problem=problem,
            plan=plan,
            epistemic_level=epistemic_level,
            evidence=evidence_tuple,
            uncertainty_summary=uncertainty_summary,
            uncertainty_state=state,
            claims=claims_tuple,
            limitations=limitations_tuple,
        )

    def evidence_independence(self, evidence: Iterable[EvidenceContribution]) -> float:
        """Return effective independent evidence count, not raw source count."""
        items = tuple(evidence)
        if not items:
            return 0.0
        return float(sum(min(item.independent_origin_count, len(item.source_ids)) for item in items))


__all__ = [
    "EpistemicLevel", "EvidenceContribution", "InferencePlan", "InferenceProblem",
    "InferenceRegime", "InferenceResult", "ScientificInferenceEngine",
]
