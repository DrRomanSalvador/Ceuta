"""State-engine facade over specialist estimators."""
from dataclasses import dataclass
from typing import Mapping
from ..inference.inference_engine import InferencePlan, InferenceProblem, ScientificInferenceEngine

@dataclass(frozen=True, slots=True)
class StateInferenceRequest:
    problem: InferenceProblem
    observations: tuple[str, ...]
    model_version: str

@dataclass(frozen=True, slots=True)
class StateInferenceOutcome:
    plan: InferencePlan
    state_record_id: str | None
    method: str
    diagnostics: Mapping[str, object]
    abstained: bool

class StateInferenceEngine:
    """Selects the appropriate estimator without hiding its assumptions."""
    def __init__(self, selector: ScientificInferenceEngine | None = None):
        self.selector = selector or ScientificInferenceEngine()
    def prepare(self, request: StateInferenceRequest) -> StateInferenceOutcome:
        plan = self.selector.plan(request.problem)
        return StateInferenceOutcome(plan, None if plan.abstain else "pending", plan.primary.value, {"warnings": plan.warnings}, plan.abstain)
