"""Proper scoring rules for prospective binary forecast evaluation.

These scores are evaluation primitives, not evidence of calibration or truthful
reporting by themselves. They become scientifically meaningful only when paired
with outcome data that were available after the forecast origin.
"""
from __future__ import annotations

from math import isfinite, log


def _validate_probability(probability: float) -> None:
    if not isfinite(probability) or not 0.0 <= probability <= 1.0:
        raise ValueError("probability must be finite and in [0,1]")


def _validate_binary_outcome(outcome: int) -> None:
    if outcome not in (0, 1):
        raise ValueError("binary outcome must be 0 or 1")


def brier_score(probability: float, outcome: int) -> float:
    """Return the binary Brier score; lower is better."""
    _validate_probability(probability)
    _validate_binary_outcome(outcome)
    return (probability - outcome) ** 2


def logarithmic_score(probability: float, outcome: int) -> float:
    """Return the positive log loss; lower is better.

    The log score is strictly proper for binary probabilistic forecasts, but
    that property alone does not establish truthful reporting in a strategic
    multi-agent environment: observability, payoffs, verification and collusion
    assumptions still matter.
    """
    _validate_probability(probability)
    _validate_binary_outcome(outcome)
    # Keep the score finite while retaining the usual limiting penalty at 0/1.
    epsilon = 1e-15
    p = min(max(probability, epsilon), 1.0 - epsilon)
    return -(outcome * log(p) + (1 - outcome) * log(1.0 - p))


def mean_brier_score(
    probabilities: tuple[float, ...], outcomes: tuple[int, ...]
) -> float:
    """Return the mean Brier score for aligned prospective observations."""
    if not probabilities or len(probabilities) != len(outcomes):
        raise ValueError("probabilities and outcomes must be non-empty and aligned")
    return sum(brier_score(p, y) for p, y in zip(probabilities, outcomes)) / len(probabilities)


__all__ = ["brier_score", "logarithmic_score", "mean_brier_score"]
