from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import isfinite
from typing import Mapping, Sequence


class DecisionMode(str, Enum):
    ROBUST = "robust"
    UTILITY = "utility"
    REGRET = "regret"
    HARM_MINIMIZATION = "harm_minimization"


class DecisionDisposition(str, Enum):
    RECOMMEND = "recommend"
    ABSTAIN = "abstain"
    HUMAN_REVIEW = "human_review"


@dataclass(frozen=True, slots=True)
class DecisionObjective:
    name: str
    weight: float
    direction: int = 1

    def __post_init__(self) -> None:
        if not self.name or not isfinite(self.weight) or self.weight < 0:
            raise ValueError("invalid decision objective")
        if self.direction not in (-1, 1):
            raise ValueError("objective direction must be -1 or 1")


@dataclass(frozen=True, slots=True)
class DecisionContext:
    decision_id: str
    decision_maker: str
    horizon: str
    objectives: tuple[DecisionObjective, ...]
    constraints: Mapping[str, float] = field(default_factory=dict)
    assumptions: tuple[str, ...] = ()
    validity_window: str = ""

    def __post_init__(self) -> None:
        if not self.decision_id or not self.decision_maker or not self.horizon:
            raise ValueError("decision context requires identity, decision maker and horizon")
        if not self.objectives:
            raise ValueError("at least one decision objective is required")
        if any(not isfinite(float(v)) for v in self.constraints.values()):
            raise ValueError("decision constraints must be finite")


@dataclass(frozen=True, slots=True)
class ScenarioOutcome:
    scenario_id: str
    probability: float
    utility: float
    harm: float
    regret: float = 0.0

    def __post_init__(self) -> None:
        if not 0.0 <= self.probability <= 1.0:
            raise ValueError("scenario probability must be in [0, 1]")
        if not all(isfinite(float(x)) for x in (self.utility, self.harm, self.regret)):
            raise ValueError("scenario outcomes must be finite")


@dataclass(frozen=True, slots=True)
class DecisionOption:
    option_id: str
    outcomes: tuple[ScenarioOutcome, ...]
    resource_cost: float = 0.0
    uncertainty: float = 1.0
    policy: str = "default"

    def __post_init__(self) -> None:
        if not self.option_id or not self.outcomes:
            raise ValueError("decision option requires id and outcomes")
        if self.resource_cost < 0 or not isfinite(self.resource_cost):
            raise ValueError("resource cost must be finite and non-negative")
        if not 0.0 <= self.uncertainty <= 1.0:
            raise ValueError("uncertainty must be in [0, 1]")
        total = sum(x.probability for x in self.outcomes)
        if not 0.999999 <= total <= 1.000001:
            raise ValueError("scenario probabilities must sum to 1")


@dataclass(frozen=True, slots=True)
class InformationRequest:
    question: str
    expected_value: float
    acquisition_cost: float
    priority: float

    @property
    def net_value(self) -> float:
        return self.expected_value - self.acquisition_cost


@dataclass(frozen=True, slots=True)
class DecisionRecommendation:
    decision_id: str
    option_id: str
    disposition: DecisionDisposition
    mode: DecisionMode
    score: float
    worst_case_utility: float
    expected_utility: float
    expected_harm: float
    maximum_regret: float
    value_of_information: float
    reasons: tuple[str, ...]
    provenance: tuple[str, ...]
    reevaluation_triggers: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DecisionFeedback:
    decision_id: str
    option_id: str
    observed_utility: float
    expected_utility: float
    observed_harm: float
    expected_harm: float
    outcome_note: str = ""

    @property
    def utility_error(self) -> float:
        return self.observed_utility - self.expected_utility

    @property
    def harm_error(self) -> float:
        return self.observed_harm - self.expected_harm


class DecisionSystem:
    """Deterministic decision layer for closed-loop decision analysis.

    This layer does not claim causal identification. It consumes explicitly supplied
    scenario outcomes, uncertainty, assumptions and provenance, and fails closed when
    those contracts are incomplete.
    """

    def rank_information(self, requests: Sequence[InformationRequest]) -> tuple[InformationRequest, ...]:
        return tuple(sorted(requests, key=lambda r: (r.net_value, r.priority), reverse=True))

    def recommend(
        self,
        context: DecisionContext,
        options: Sequence[DecisionOption],
        *,
        mode: DecisionMode = DecisionMode.ROBUST,
        max_uncertainty: float = 0.5,
        human_review_threshold: float = 0.35,
        provenance: Sequence[str] = (),
        reevaluation_triggers: Sequence[str] = (),
    ) -> DecisionRecommendation:
        if not options:
            return self._abstain(context, mode, "no admissible options", provenance, reevaluation_triggers)
        eligible = tuple(o for o in options if o.uncertainty <= max_uncertainty)
        if not eligible:
            return self._abstain(context, mode, "all options exceed uncertainty threshold", provenance, reevaluation_triggers)

        scored = [(o, self._metrics(o)) for o in eligible]
        if mode is DecisionMode.ROBUST:
            chosen, metrics = max(scored, key=lambda item: item[1][0])
        elif mode is DecisionMode.HARM_MINIMIZATION:
            chosen, metrics = min(scored, key=lambda item: (item[1][2], -item[1][0]))
        elif mode is DecisionMode.REGRET:
            chosen, metrics = min(scored, key=lambda item: (item[1][3], -item[1][1]))
        else:
            chosen, metrics = max(scored, key=lambda item: item[1][1])

        worst, expected, harm, regret = metrics
        normalized_uncertainty = chosen.uncertainty
        disposition = (DecisionDisposition.HUMAN_REVIEW if normalized_uncertainty >= human_review_threshold
                       else DecisionDisposition.RECOMMEND)
        score = worst if mode is DecisionMode.ROBUST else expected if mode is DecisionMode.UTILITY else -regret if mode is DecisionMode.REGRET else -harm
        reasons = (
            f"policy={mode.value}",
            f"uncertainty={normalized_uncertainty:.6f}",
            "decision is conditional on supplied scenarios and assumptions",
        )
        return DecisionRecommendation(
            context.decision_id, chosen.option_id, disposition, mode, score,
            worst, expected, harm, regret, 0.0, reasons,
            tuple(provenance), tuple(reevaluation_triggers),
        )

    @staticmethod
    def _metrics(option: DecisionOption) -> tuple[float, float, float, float]:
        worst = min(x.utility for x in option.outcomes)
        expected = sum(x.probability * x.utility for x in option.outcomes) - option.resource_cost
        harm = sum(x.probability * x.harm for x in option.outcomes)
        regret = max(x.regret for x in option.outcomes)
        return worst, expected, harm, regret

    @staticmethod
    def _abstain(context: DecisionContext, mode: DecisionMode, reason: str, provenance: Sequence[str], triggers: Sequence[str]) -> DecisionRecommendation:
        return DecisionRecommendation(
            context.decision_id, "ABSTAIN", DecisionDisposition.ABSTAIN, mode,
            0.0, 0.0, 0.0, 0.0, 0.0, 0.0, (reason,), tuple(provenance), tuple(triggers)
        )
