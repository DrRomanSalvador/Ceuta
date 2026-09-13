"""Contextual longitudinal baselines and deviation measures."""
from __future__ import annotations
from dataclasses import dataclass
from math import sqrt
from statistics import mean, pstdev
from typing import Sequence

@dataclass(frozen=True, slots=True)
class Baseline:
    center: float
    scale: float
    sample_size: int
    method: str

@dataclass(frozen=True, slots=True)
class Deviation:
    value: float
    z_like: float | None
    direction: int
    baseline: Baseline

class DynamicBaselineEngine:
    def baseline(self, values: Sequence[float], *, robust: bool = True) -> Baseline:
        if not values: raise ValueError("values cannot be empty")
        ordered = sorted(float(v) for v in values)
        if robust:
            mid = len(ordered)//2
            center = ordered[mid] if len(ordered)%2 else (ordered[mid-1]+ordered[mid])/2
            deviations = sorted(abs(v-center) for v in ordered)
            m = len(deviations)//2
            scale = deviations[m] if len(deviations)%2 else (deviations[m-1]+deviations[m])/2
            scale *= 1.4826
            method = "median_mad"
        else:
            center, scale, method = mean(ordered), pstdev(ordered) if len(ordered)>1 else 0.0, "mean_sd"
        return Baseline(center, max(scale, 1e-12), len(ordered), method)

    def deviation(self, value: float, baseline: Baseline) -> Deviation:
        delta = float(value)-baseline.center
        return Deviation(delta, delta/baseline.scale, 1 if delta>0 else -1 if delta<0 else 0, baseline)
