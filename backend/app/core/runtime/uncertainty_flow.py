"""Traceable uncertainty propagation across the longitudinal decision chain."""
from __future__ import annotations
from dataclasses import dataclass
from math import sqrt

_COMPONENTS=("measurement","process","parameter","structural","selection","dependence")

@dataclass(frozen=True, slots=True)
class UncertaintyFlow:
    measurement: float=0.0
    process: float=0.0
    parameter: float=0.0
    structural: float=0.0
    selection: float=0.0
    dependence: float=0.0
    def __post_init__(self):
        if any(value < 0 for value in (self.measurement,self.process,self.parameter,self.structural,self.selection,self.dependence)):
            raise ValueError("uncertainty components cannot be negative")
    @property
    def total(self)->float:
        return sqrt(sum(getattr(self,k)**2 for k in _COMPONENTS))
    def combine(self, other:"UncertaintyFlow", dependent:bool=False)->"UncertaintyFlow":
        if dependent:
            values=tuple(getattr(self,k)+getattr(other,k) for k in _COMPONENTS)
        else:
            values=tuple(sqrt(getattr(self,k)**2+getattr(other,k)**2) for k in _COMPONENTS)
        return UncertaintyFlow(*values)
