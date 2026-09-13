"""Traceable uncertainty propagation across the longitudinal decision chain."""
from __future__ import annotations
from dataclasses import dataclass
from math import sqrt
from typing import Mapping

@dataclass(frozen=True, slots=True)
class UncertaintyFlow:
    measurement: float=0.0
    process: float=0.0
    parameter: float=0.0
    structural: float=0.0
    selection: float=0.0
    dependence: float=0.0
    @property
    def total(self)->float:
        return sqrt(sum(x*x for x in (self.measurement,self.process,self.parameter,self.structural,self.selection,self.dependence)))
    def combine(self, other:"UncertaintyFlow", dependent:bool=False)->"UncertaintyFlow":
        vals=tuple(getattr(self,k)+getattr(other,k) for k in ("measurement","process","parameter","structural","selection","dependence"))
        if dependent:
            vals=tuple(getattr(self,k)+getattr(other,k) for k in ("measurement","process","parameter","structural","selection","dependence"))
        return UncertaintyFlow(*vals)
