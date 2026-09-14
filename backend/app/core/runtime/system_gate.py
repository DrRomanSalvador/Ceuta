"""Decision-runtime gate for system-level blind-spot controls."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from app.core.system_intelligence import SystemAssessment


class SystemGateDisposition(StrEnum):
    ALLOW = "allow"
    DEGRADED = "degraded"
    ABSTAIN = "abstain"


@dataclass(frozen=True, slots=True)
class SystemGateResult:
    disposition: SystemGateDisposition
    reasons: tuple[str, ...]
    confidence_multiplier: float


class SystemIntelligenceGate:
    """Translate system observability limits into an explicit runtime state.

    This gate never converts an association into a causal claim. It only
    constrains downstream use when observability, identifiability, measurement
    integrity, regime stability or model agreement is inadequate.
    """

    def evaluate(self, assessment: SystemAssessment) -> SystemGateResult:
        reasons = list(assessment.reasons)
        if assessment.abstain:
            return SystemGateResult(SystemGateDisposition.ABSTAIN, tuple(reasons), 0.0)
        degraded = assessment.missing_data_risk >= 0.35 or assessment.measurement_process_risk >= 0.35
        if degraded:
            reasons.append("system representation is usable but materially degraded")
            return SystemGateResult(SystemGateDisposition.DEGRADED, tuple(reasons), 0.5)
        return SystemGateResult(SystemGateDisposition.ALLOW, tuple(reasons), 1.0)


__all__ = ["SystemGateDisposition", "SystemGateResult", "SystemIntelligenceGate"]
