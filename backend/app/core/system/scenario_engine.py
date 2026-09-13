"""Scenario and counterfactual representations with feasibility boundaries."""
from dataclasses import dataclass
from ..errors import ContractViolation

@dataclass(frozen=True, slots=True)
class Scenario:
    scenario_id: str
    interventions: tuple[str, ...]
    assumptions: tuple[str, ...]
    constraints: tuple[str, ...]
    horizon_seconds: float
    probability: float | None = None
    def __post_init__(self):
        if not self.scenario_id or self.horizon_seconds <= 0: raise ContractViolation("scenario identity/horizon invalid")
        if self.probability is not None and not 0 <= self.probability <= 1: raise ContractViolation("scenario probability invalid")

@dataclass(frozen=True, slots=True)
class ScenarioResult:
    scenario_id: str
    feasible: bool
    predicted_state_id: str | None
    uncertainty_summary: str
    invalidity_reasons: tuple[str, ...] = ()
