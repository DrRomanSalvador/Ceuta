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
    abstain_from_phenomenon_claim: bool


class ChangeAttributionEngine:
    def assess(self, *, phenomenon_evidence: tuple[str, ...] = (), process_evidence: tuple[str, ...] = ()) -> ChangeAttributionAssessment:
        if phenomenon_evidence and process_evidence:
            attribution = ChangeAttribution.BOTH_PLAUSIBLE
        elif phenomenon_evidence:
            attribution = ChangeAttribution.PHENOMENON_SUPPORTED
        elif process_evidence:
            attribution = ChangeAttribution.MEASUREMENT_PROCESS_SUPPORTED
        else:
            attribution = ChangeAttribution.INSUFFICIENT_INFORMATION
        return ChangeAttributionAssessment(
            attribution,
            phenomenon_evidence,
            process_evidence,
            attribution is not ChangeAttribution.PHENOMENON_SUPPORTED,
        )


__all__ = ["ChangeAttribution", "ChangeAttributionAssessment", "ChangeAttributionEngine"]
