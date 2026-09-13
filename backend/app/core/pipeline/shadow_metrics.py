"""Quantitative Shadow Mode gap and calibration metrics."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from math import isfinite
from statistics import mean

from .shadow_mode import ShadowEvaluation


@dataclass(frozen=True, slots=True)
class ShadowGapReport:
    sample_size: int
    model_mse: float
    baseline_mse: float
    mse_gap: float
    relative_mse_gap: float | None
    model_mae: float
    baseline_mae: float
    bias: float
    directional_accuracy: float | None

    @property
    def beats_baseline(self) -> bool:
        return self.model_mse < self.baseline_mse


def compute_shadow_gap(evaluations: Iterable[ShadowEvaluation]) -> ShadowGapReport:
    rows = tuple(evaluations)
    if not rows:
        raise ValueError("at least one shadow evaluation is required")
    model_errors = [item.error for item in rows]
    baseline_errors = [item.baseline_error for item in rows]
    model_squared = [item.squared_error for item in rows]
    baseline_squared = [item.baseline_squared_error for item in rows]
    values = (*model_errors, *baseline_errors, *model_squared, *baseline_squared)
    if any(not isfinite(value) for value in values):
        raise ValueError("shadow metrics require finite values")
    model_mse = mean(model_squared)
    baseline_mse = mean(baseline_squared)
    directional = [item.directional_hit for item in rows if item.directional_hit is not None]
    return ShadowGapReport(
        sample_size=len(rows),
        model_mse=model_mse,
        baseline_mse=baseline_mse,
        mse_gap=model_mse - baseline_mse,
        relative_mse_gap=(model_mse - baseline_mse) / baseline_mse if baseline_mse > 0 else None,
        model_mae=mean(abs(value) for value in model_errors),
        baseline_mae=mean(abs(value) for value in baseline_errors),
        bias=mean(model_errors),
        directional_accuracy=mean(bool(value) for value in directional) if directional else None,
    )
