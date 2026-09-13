"""Fail-closed boundary between observed association and causal claims."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite


class InteractionStatus(StrEnum):
    OBSERVED_ASSOCIATION = "OBSERVED_ASSOCIATION"
    PROSPECTIVELY_SUPPORTED = "PROSPECTIVELY_SUPPORTED"
    CAUSAL = "CAUSAL"
    REJECTED = "REJECTED"


@dataclass(frozen=True, slots=True)
class AssociationEvidence:
    upstream: str
    downstream: str
    observations: int
    prospective_evaluations: int
    directional_accuracy: float
    baseline_improvement: float
    status: InteractionStatus = InteractionStatus.OBSERVED_ASSOCIATION

    def __post_init__(self) -> None:
        if not self.upstream or not self.downstream:
            raise ValueError("interaction endpoints are required")
        if self.observations < 0 or self.prospective_evaluations < 0:
            raise ValueError("counts must be non-negative")
        for name in ("directional_accuracy", "baseline_improvement"):
            value = float(getattr(self, name))
            if not isfinite(value):
                raise ValueError(f"{name} must be finite")
        if not 0.0 <= self.directional_accuracy <= 1.0:
            raise ValueError("directional_accuracy must be between 0 and 1")


@dataclass(frozen=True, slots=True)
class CausalityDecision:
    status: InteractionStatus
    allowed_in_scenarios: bool
    reason: str


class CausalityGuard:
    """Require prospective evidence before an interaction can affect regimes."""

    def __init__(
        self,
        *,
        min_prospective_evaluations: int = 30,
        min_directional_accuracy: float = 0.60,
        min_baseline_improvement: float = 0.0,
        causal_requires_explicit_design: bool = True,
    ) -> None:
        if min_prospective_evaluations < 1:
            raise ValueError("min_prospective_evaluations must be positive")
        if not 0.0 <= min_directional_accuracy <= 1.0:
            raise ValueError("min_directional_accuracy must be between 0 and 1")
        if not isfinite(min_baseline_improvement):
            raise ValueError("min_baseline_improvement must be finite")
        self._min_evaluations = min_prospective_evaluations
        self._min_accuracy = min_directional_accuracy
        self._min_improvement = min_baseline_improvement
        self._causal_requires_explicit_design = causal_requires_explicit_design

    def evaluate(self, evidence: AssociationEvidence) -> CausalityDecision:
        if evidence.status is not InteractionStatus.OBSERVED_ASSOCIATION:
            return CausalityDecision(
                InteractionStatus.REJECTED,
                False,
                "only OBSERVED_ASSOCIATION may enter the causal gate",
            )
        if evidence.prospective_evaluations < self._min_evaluations:
            return CausalityDecision(
                InteractionStatus.OBSERVED_ASSOCIATION,
                False,
                "insufficient prospective ledger history",
            )
        if evidence.directional_accuracy < self._min_accuracy:
            return CausalityDecision(
                InteractionStatus.REJECTED,
                False,
                "directional prospective accuracy below threshold",
            )
        if evidence.baseline_improvement < self._min_improvement:
            return CausalityDecision(
                InteractionStatus.REJECTED,
                False,
                "no demonstrated improvement over baseline",
            )
        if self._causal_requires_explicit_design:
            return CausalityDecision(
                InteractionStatus.PROSPECTIVELY_SUPPORTED,
                True,
                "prospectively supported association; causal status still unestablished",
            )
        return CausalityDecision(
            InteractionStatus.PROSPECTIVELY_SUPPORTED,
            True,
            "prospectively supported interaction",
        )
