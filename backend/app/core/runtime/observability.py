"""Observability and identifiability gates for the live inference loop."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Sequence

@dataclass(frozen=True, slots=True)
class ObservabilityAssessment:
    observed_fraction: float
    identifiable: bool
    missing_components: tuple[str,...]
    warnings: tuple[str,...]

class ObservabilityEngine:
    def assess(self, required: Sequence[str], observed: Sequence[str], identifiable: bool=True) -> ObservabilityAssessment:
        req=set(required); obs=set(observed); missing=tuple(sorted(req-obs)); fraction=len(req&obs)/len(req) if req else 1.0
        return ObservabilityAssessment(fraction,identifiable and not missing,missing,tuple((["partial observability"] if missing else []) + (["structural non-identifiability"] if not identifiable else [])))
