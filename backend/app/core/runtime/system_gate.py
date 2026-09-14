"""Decision-runtime gate for system-level epistemic and blind-spot controls."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite

from app.core.final_epistemic_control import (
    EpistemicIntegrityStatus,
    FinalEpistemicAssessment,
    SystemValidity,
)
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
    """Constrain downstream use when system or final epistemic controls are inadequate."""

    def evaluate(
        self,
        assessment: SystemAssessment,
        final_epistemic: FinalEpistemicAssessment | None = None,
    ) -> SystemGateResult:
        reasons = list(assessment.reasons)
        if (
            not isfinite(assessment.missing_data_risk)
            or not 0.0 <= assessment.missing_data_risk <= 1.0
            or not isfinite(assessment.measurement_process_risk)
            or not 0.0 <= assessment.measurement_process_risk <= 1.0
            or not isfinite(assessment.predictability.confidence)
            or not 0.0 <= assessment.predictability.confidence <= 1.0
        ):
            reasons.append("system assessment contains invalid non-finite or out-of-range risk/confidence values")
            return SystemGateResult(SystemGateDisposition.ABSTAIN, tuple(reasons), 0.0)
        if assessment.abstain:
            return SystemGateResult(SystemGateDisposition.ABSTAIN, tuple(reasons), 0.0)
        if final_epistemic is not None:
            reasons.extend(final_epistemic.reasons)
            if final_epistemic.validity in {SystemValidity.DOUBT, SystemValidity.ABSTAIN}:
                return SystemGateResult(SystemGateDisposition.ABSTAIN, tuple(reasons), 0.0)
            if final_epistemic.composition is EpistemicIntegrityStatus.BROKEN:
                reasons.append("epistemic composition is broken")
                return SystemGateResult(SystemGateDisposition.ABSTAIN, tuple(reasons), 0.0)
        degraded = assessment.missing_data_risk >= 0.35 or assessment.measurement_process_risk >= 0.35
        if final_epistemic is not None and final_epistemic.composition in {
            EpistemicIntegrityStatus.WEAKENED,
            EpistemicIntegrityStatus.UNKNOWN,
        }:
            degraded = True
            reasons.append("epistemic composition is weakened or unresolved")
        if degraded:
            reasons.append("system representation is usable but materially degraded")
            return SystemGateResult(SystemGateDisposition.DEGRADED, tuple(reasons), 0.5)
        return SystemGateResult(SystemGateDisposition.ALLOW, tuple(reasons), 1.0)


__all__ = ["SystemGateDisposition", "SystemGateResult", "SystemIntelligenceGate"]
