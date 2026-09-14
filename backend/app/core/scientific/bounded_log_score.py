"""Bounded-exposure variant of the logarithmic scoring rule.

A raw logarithmic score has unbounded loss as a forecast approaches zero or
one. This module makes the exposure policy explicit by restricting the report
domain to [epsilon, 1-epsilon]. Within that admissible domain, expected log
loss remains strictly proper: truthful reporting is still uniquely optimal when
the true belief is itself admissible.

This is an exposure policy, not an arbitrary payout cap. A post-hoc transfer
cap would generally alter incentives and is therefore intentionally absent.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, log


@dataclass(frozen=True, slots=True)
class BoundedLogScorePolicy:
    epsilon: float = 1e-6
    stake: float = 1.0

    def __post_init__(self) -> None:
        if not isfinite(self.epsilon) or not 0.0 < self.epsilon < 0.5:
            raise ValueError("epsilon must be finite and in (0, 0.5)")
        if not isfinite(self.stake) or self.stake <= 0:
            raise ValueError("stake must be positive and finite")

    @property
    def maximum_loss(self) -> float:
        return self.stake * -log(self.epsilon)

    def validate_report(self, probability: float) -> None:
        if not isfinite(probability) or not self.epsilon <= probability <= 1.0 - self.epsilon:
            raise ValueError("probability is outside the bounded scoring domain")

    def expected_log_loss(self, probability: float, belief: float) -> float:
        self.validate_report(probability)
        if not isfinite(belief) or not self.epsilon <= belief <= 1.0 - self.epsilon:
            raise ValueError("belief is outside the bounded scoring domain")
        return -(belief * log(probability) + (1.0 - belief) * log(1.0 - probability))

    def truthful_report_gap(self, *, belief: float, report_probability: float) -> float:
        return self.expected_log_loss(report_probability, belief) - self.expected_log_loss(belief, belief)

    def strictly_proper(self, *, belief: float, candidate_reports: tuple[float, ...], tolerance: float = 1e-12) -> bool:
        if not candidate_reports:
            return False
        self.validate_report(belief)
        for candidate in candidate_reports:
            self.validate_report(candidate)
        truthful = self.expected_log_loss(belief, belief)
        return all(
            truthful < self.expected_log_loss(candidate, belief) - tolerance
            for candidate in candidate_reports
            if candidate != belief
        )


__all__ = ["BoundedLogScorePolicy"]
