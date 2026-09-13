"""End-to-end decision engine with explicit epistemic gates and auditability.

The engine is deliberately conservative: it does not manufacture causal or
predictive validity. A recommendation is emitted only when the caller declares
the supplied model outputs calibrated/valid and all required identification
assumptions satisfied. Information acquisition can itself be the optimal action.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Mapping, Sequence

from .decision_system import DecisionDisposition, DecisionMode
from .optimization import DecisionOptimizer, DecisionScore, ValueOfInformation


class DecisionAction(str, Enum):
    RECOMMEND = "recommend"
    ACQUIRE_INFORMATION = "acquire_information"
    HUMAN_REVIEW = "human_review"
    ABSTAIN = "abstain"


@dataclass(frozen=True, slots=True)
class Scenario:
    scenario_id: str
    probability: float
    utility: float
    harm: float

    def __post_init__(self) -> None:
        if not self.scenario_id or not 0.0 <= self.probability <= 1.0:
            raise ValueError("invalid scenario")
        if not all(isfinite(float(x)) for x in (self.utility, self.harm)):
            raise ValueError("scenario values must be finite")


@dataclass(frozen=True, slots=True)
class ActionAlternative:
    option_id: str
    scenarios: tuple[Scenario, ...]
    resource_cost: float = 0.0
    uncertainty: float = 0.0

    def __post_init__(self) -> None:
        if not self.option_id or not self.scenarios:
            raise ValueError("action requires an id and scenarios")
        if self.resource_cost < 0 or not isfinite(self.resource_cost):
            raise ValueError("resource_cost must be finite and non-negative")
        if not 0.0 <= self.uncertainty <= 1.0:
            raise ValueError("uncertainty must be in [0, 1]")
        if abs(sum(s.probability for s in self.scenarios) - 1.0) > 1e-9:
            raise ValueError("scenario probabilities must sum to one")


@dataclass(frozen=True, slots=True)
class EpistemicGate:
    observable: bool
    identifiable: bool
    calibrated: bool
    model_valid: bool
    causal_identified: bool = True
    assumptions_satisfied: bool = True

    @property
    def passed(self) -> bool:
        return all((self.observable, self.identifiable, self.calibrated,
                    self.model_valid, self.causal_identified,
                    self.assumptions_satisfied))

    def failures(self) -> tuple[str, ...]:
        checks = (
            ("not_observable", self.observable),
            ("not_identifiable", self.identifiable),
            ("not_calibrated", self.calibrated),
            ("model_not_valid", self.model_valid),
            ("causal_effect_not_identified", self.causal_identified),
            ("causal_assumptions_not_satisfied", self.assumptions_satisfied),
        )
        return tuple(name for name, passed in checks if not passed)


@dataclass(frozen=True, slots=True)
class DecisionAudit:
    decision_id: str
    action: DecisionAction
    selected_option: str
    objective: str
    epistemic_failures: tuple[str, ...]
    expected_utility: float | None
    worst_case_utility: float | None
    expected_harm: float | None
    maximum_regret: float | None
    value_of_information: float
    assumptions: tuple[str, ...]
    provenance: tuple[str, ...]
    reevaluation_triggers: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DecisionCycleResult:
    audit: DecisionAudit
    score: DecisionScore | None
    information: ValueOfInformation | None


class DecisionEngine:
    """Decision-theoretic cycle: gate -> score -> compare -> act -> audit."""

    def __init__(self, optimizer: DecisionOptimizer | None = None):
        self.optimizer = optimizer or DecisionOptimizer()

    @staticmethod
    def _regret_by_scenario(options: Sequence[ActionAlternative]) -> Mapping[str, float]:
        best: dict[str, float] = {}
        for option in options:
            for scenario in option.scenarios:
                best[scenario.scenario_id] = max(best.get(scenario.scenario_id, float("-inf")), scenario.utility)
        return best

    def evaluate(
        self,
        *,
        decision_id: str,
        options: Sequence[ActionAlternative],
        gate: EpistemicGate,
        mode: DecisionMode = DecisionMode.ROBUST,
        max_harm: float | None = None,
        human_review_uncertainty: float = 0.35,
        information_request: ValueOfInformation | None = None,
        assumptions: Sequence[str] = (),
        provenance: Sequence[str] = (),
        reevaluation_triggers: Sequence[str] = (),
    ) -> DecisionCycleResult:
        if not decision_id:
            raise ValueError("decision_id is required")
        if not 0.0 <= human_review_uncertainty <= 1.0:
            raise ValueError("human_review_uncertainty must be in [0, 1]")

        if not gate.passed:
            audit = DecisionAudit(
                decision_id, DecisionAction.ABSTAIN, "ABSTAIN", mode.value,
                gate.failures(), None, None, None, None,
                information_request.net_value if information_request else 0.0,
                tuple(assumptions), tuple(provenance), tuple(reevaluation_triggers),
            )
            return DecisionCycleResult(audit, None, information_request)

        if not options:
            audit = DecisionAudit(
                decision_id, DecisionAction.ABSTAIN, "ABSTAIN", mode.value,
                ("no_admissible_actions",), None, None, None, None,
                information_request.net_value if information_request else 0.0,
                tuple(assumptions), tuple(provenance), tuple(reevaluation_triggers),
            )
            return DecisionCycleResult(audit, None, information_request)

        if information_request and information_request.net_value > 0:
            audit = DecisionAudit(
                decision_id, DecisionAction.ACQUIRE_INFORMATION, "INFORMATION_ACQUISITION", mode.value,
                (), None, None, None, None, information_request.net_value,
                tuple(assumptions), tuple(provenance), tuple(reevaluation_triggers),
            )
            return DecisionCycleResult(audit, None, information_request)

        regret_benchmark = self._regret_by_scenario(options)
        scores: list[DecisionScore] = []
        for option in options:
            probabilities = tuple(s.probability for s in option.scenarios)
            utilities = tuple(s.utility for s in option.scenarios)
            harms = tuple(s.harm for s in option.scenarios)
            regret = max(
                regret_benchmark[s.scenario_id] - s.utility
                for s in option.scenarios
            )
            base = self.optimizer.score(
                option.option_id, utilities, harms, probabilities,
                resource_cost=option.resource_cost, max_harm=max_harm,
            )
            scores.append(DecisionScore(
                base.option_id, base.expected_utility, base.worst_case_utility,
                base.expected_harm, regret, base.cvar_utility, base.feasible,
            ))

        objective = {
            DecisionMode.ROBUST: "robust",
            DecisionMode.UTILITY: "expected_utility",
            DecisionMode.REGRET: "regret",
            DecisionMode.HARM_MINIMIZATION: "harm",
        }[mode]
        try:
            selected = self.optimizer.select(scores, objective)
        except ValueError as exc:
            audit = DecisionAudit(
                decision_id, DecisionAction.ABSTAIN, "ABSTAIN", mode.value,
                (str(exc),), None, None, None, None, 0.0,
                tuple(assumptions), tuple(provenance), tuple(reevaluation_triggers),
            )
            return DecisionCycleResult(audit, None, None)

        option = next(o for o in options if o.option_id == selected.option_id)
        action = (DecisionAction.HUMAN_REVIEW
                  if option.uncertainty >= human_review_uncertainty
                  else DecisionAction.RECOMMEND)
        audit = DecisionAudit(
            decision_id, action, selected.option_id, mode.value, (),
            selected.expected_utility, selected.worst_case_utility,
            selected.expected_harm, selected.maximum_regret, 0.0,
            tuple(assumptions), tuple(provenance), tuple(reevaluation_triggers),
        )
        return DecisionCycleResult(audit, selected, None)
