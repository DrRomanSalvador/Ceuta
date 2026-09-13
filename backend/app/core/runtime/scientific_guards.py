"""Scientific gates preventing unsupported transitions in the inference chain."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence

@dataclass(frozen=True, slots=True)
class ScientificGate:
    allowed: bool
    reasons: tuple[str,...]
    epistemic_ceiling: str

class ScientificIntegrityEngine:
    def evaluate(self, *, observed: bool, estimated: bool, identifiable: bool, predictive_calibrated: bool, causal_identified: bool, intervention_validated: bool, contradictions: int=0)->ScientificGate:
        reasons=[]
        if not observed: reasons.append("no valid observation")
        if not estimated: reasons.append("state not estimated")
        if not identifiable: reasons.append("non-identifiable state")
        ceiling="observed"
        if estimated and identifiable: ceiling="estimated"
        if predictive_calibrated and estimated and identifiable: ceiling="predictive"
        if causal_identified and predictive_calibrated and estimated and identifiable: ceiling="causal"
        if intervention_validated and causal_identified and predictive_calibrated and estimated and identifiable: ceiling="decision-supported"
        if contradictions: reasons.append("unresolved contradictions")
        return ScientificGate(not reasons,tuple(reasons),ceiling)

    @staticmethod
    def require_assumptions(assumptions: Sequence[str], required: Sequence[str]) -> tuple[str,...]:
        missing=tuple(sorted(set(required)-set(assumptions)))
        if missing: raise ValueError("missing scientific assumptions: "+", ".join(missing))
        return tuple(assumptions)
