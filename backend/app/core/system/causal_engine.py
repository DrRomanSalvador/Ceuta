"""Causal layer boundary: estimands and identification status."""
from dataclasses import dataclass
from ..errors import ContractViolation

@dataclass(frozen=True, slots=True)
class CausalEstimand:
    estimand_id: str
    treatment: str
    outcome: str
    population: str
    contrast: str
    identification_assumptions: tuple[str, ...]
    identification_status: str = "UNASSESSED"
    sensitivity_analysis_ids: tuple[str, ...] = ()
    def __post_init__(self):
        if not all((self.estimand_id,self.treatment,self.outcome,self.population,self.contrast)): raise ContractViolation("causal estimand fields required")
        if self.identification_status not in {"UNASSESSED","IDENTIFIED","NOT_IDENTIFIED","SENSITIVITY_REQUIRED"}: raise ContractViolation("invalid identification status")

@dataclass(frozen=True, slots=True)
class CausalAssessment:
    estimand: CausalEstimand
    confounding_risks: tuple[str, ...] = ()
    positivity_risks: tuple[str, ...] = ()
    consistency_risks: tuple[str, ...] = ()
    interference_risks: tuple[str, ...] = ()
    negative_control_ids: tuple[str, ...] = ()
    def decision_usable(self) -> bool:
        return self.estimand.identification_status == "IDENTIFIED" and not self.positivity_risks
