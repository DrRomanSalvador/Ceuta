"""Uncertainty carried with every integrated system state."""
from dataclasses import dataclass
from ..errors import ContractViolation

@dataclass(frozen=True, slots=True)
class UncertaintyState:
    measurement: float = 0.0
    process: float = 0.0
    parameter: float = 0.0
    structural: float = 0.0
    selection: float = 0.0
    dependence: float = 0.0
    def __post_init__(self):
        values=(self.measurement,self.process,self.parameter,self.structural,self.selection,self.dependence)
        if any(x < 0 for x in values): raise ContractViolation("uncertainty components cannot be negative")
    @property
    def total_upper_bound(self) -> float:
        return sum((self.measurement,self.process,self.parameter,self.structural,self.selection,self.dependence))
    def as_mapping(self):
        return {"measurement":self.measurement,"process":self.process,"parameter":self.parameter,"structural":self.structural,"selection":self.selection,"dependence":self.dependence}
