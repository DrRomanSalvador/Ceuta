"""Advanced runtime contracts: adaptation, adversarial integrity, tail risk and simulation."""
from __future__ import annotations
from dataclasses import dataclass
from math import isfinite
from typing import Mapping, Sequence

@dataclass(frozen=True, slots=True)
class AdaptationState:
    system_id: str
    behaviour_change: float
    intervention_exposure: float
    feedback_strength: float

@dataclass(frozen=True, slots=True)
class AdversarialAssessment:
    integrity_score: float
    suspicious_sources: tuple[str,...]
    coordinated_pattern: bool
    action: str

@dataclass(frozen=True, slots=True)
class TailRisk:
    probability: float
    threshold: float
    expected_shortfall: float
    method: str

@dataclass(frozen=True, slots=True)
class SimulationPath:
    scenario_id: str
    states: tuple[Mapping[str,float],...]
    valid: bool
    assumptions: tuple[str,...]

class AdvancedRuntime:
    def adaptation(self, system_id:str, behaviour_change:float, intervention_exposure:float, feedback_strength:float)->AdaptationState:
        return AdaptationState(system_id,behaviour_change,intervention_exposure,feedback_strength)
    def adversarial(self, integrity_score:float, suspicious_sources:Sequence[str], coordinated:bool)->AdversarialAssessment:
        if not 0<=integrity_score<=1: raise ValueError("integrity score must be in [0,1]")
        return AdversarialAssessment(integrity_score,tuple(suspicious_sources),coordinated,"abstain" if integrity_score<.5 or coordinated else "continue")
    def tail_risk(self, losses:Sequence[float], threshold:float)->TailRisk:
        tail=[x for x in losses if x>=threshold]
        p=len(tail)/len(losses) if losses else 0.0
        es=sum(tail)/len(tail) if tail else 0.0
        return TailRisk(p,threshold,es,"empirical-tail")
