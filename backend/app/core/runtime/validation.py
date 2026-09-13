"""Prospective scientific validation primitives for longitudinal models."""
from __future__ import annotations
from dataclasses import dataclass
from math import sqrt
from typing import Sequence

@dataclass(frozen=True, slots=True)
class ValidationResult:
    n: int
    mae: float
    rmse: float
    mean_error: float
    passed: bool

class ProspectiveValidator:
    def regression(self, observed: Sequence[float], predicted: Sequence[float], tolerance: float)->ValidationResult:
        if len(observed)!=len(predicted) or not observed: raise ValueError("paired non-empty samples required")
        errors=[float(p)-float(o) for o,p in zip(observed,predicted)]
        mae=sum(abs(e) for e in errors)/len(errors); rmse=sqrt(sum(e*e for e in errors)/len(errors)); bias=sum(errors)/len(errors)
        return ValidationResult(len(errors),mae,rmse,bias,mae<=tolerance)
