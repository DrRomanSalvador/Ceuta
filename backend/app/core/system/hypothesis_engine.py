"""Competing hypotheses and discriminating evidence."""
from dataclasses import dataclass
from ..errors import ContractViolation

@dataclass(frozen=True, slots=True)
class Hypothesis:
    hypothesis_id: str
    statement: str
    status: str = "UNRESOLVED"
    evidence_for: tuple[str, ...] = ()
    evidence_against: tuple[str, ...] = ()
    discriminators: tuple[str, ...] = ()
    alternatives: tuple[str, ...] = ()
    def __post_init__(self):
        if not self.hypothesis_id or not self.statement: raise ContractViolation("hypothesis identity and statement required")
        if self.status not in {"UNRESOLVED","SUPPORTED","FALSIFIED","INCONCLUSIVE"}: raise ContractViolation("invalid hypothesis status")

@dataclass(frozen=True, slots=True)
class HypothesisLedger:
    hypotheses: tuple[Hypothesis, ...]
    def unresolved(self): return tuple(h for h in self.hypotheses if h.status == "UNRESOLVED")
    def falsified(self): return tuple(h for h in self.hypotheses if h.status == "FALSIFIED")
