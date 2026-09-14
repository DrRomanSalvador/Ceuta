"""Controls for interpreting changes in observed series.

A series break is not automatically a phenomenon break. This module requires
explicit evidence about the observation process before classifying a change.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class ChangeAttribution(StrEnum):
    PHENOMENON_SUPPORTED = "phenomenon_supported"
    MEASUREMENT_PROCESS_SUPPORTED = "measurement_process_supported"
    BOTH_PLAUSIBLE = "both_plausible"
    INSUFFICIENT_INFORMATION = "insufficient_information"


@dataclass(frozen=True, slots=True)
class ChangeAttributionAssessment:
    attribution: ChangeAttribution
    phenomenon_evidence: tuple[str, ...]
    process_evidence: tuple[str, ...]
    confidence: float
    abstain_from_phenomenon_claim: bool

    def __post_init__(self) -> None:
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be in [0,1]")


class ChangeAttributionEngine:
    def assess(self, *, phenomenon_evidence: tuple[str, ...] = (), process_evidence: tuple[str, ...] = ()) -> ChangeAttributionAssessment:
        if phenomenon_evidence and process_evidence:
            attribution = ChangeAttribution.BOTH_PLAUSIBLE
            confidence = 0.5
        elif phenomenon_evidence:
            attribution = ChangeAttribution.PHENOMENON_SUPPORTED
            confidence = 0.7
        elif process_evidence:
            attribution = ChangeAttribution.MEASUREMENT_PROCESS_SUPPORTED
            confidence = 0.8
        else:
            attribution = ChangeAttribution.INSUFFICIENT_INFORMATION
            confidence = 0.0
        abstain = attribution is not ChangeAttribution.PHENOMENON_SUPPORTED
        return ChangeAttributionAssessment(attribution, phenomenon_evidence, process_evidence, confidence, abstain)


__all__ = ["ChangeAttribution", "ChangeAttributionAssessment", "ChangeAttributionEngine"]
