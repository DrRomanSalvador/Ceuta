"""CeutIA observation boundary.

This is the controlled boundary between retrieval/ingestion and downstream
analysis. Retrieved material is preserved as evidence with provenance and
point-in-time availability; downstream dynamic models must consume only the
validated representation.
"""

from __future__ import annotations

from datetime import datetime

from app.core.p0_contracts import (
    EvidenceContract,
    TemporalEligibility,
    evaluate_temporal_eligibility,
)


class ObservationBoundaryError(ValueError):
    """Raised when an observation cannot safely enter the analytical layer."""


def available_at(evidence: EvidenceContract) -> datetime:
    """Return the earliest defensible time at which evidence was available.

    The event time describes when the underlying event occurred and is therefore
    not a point-in-time availability marker. Published evidence becomes
    available at publication time; otherwise the observed time is used.
    """
    if evidence.publication_time is not None:
        return evidence.publication_time
    return evidence.observed_at


def validate_observation_for_analysis(
    evidence: EvidenceContract,
    *,
    evaluation_time: datetime,
) -> TemporalEligibility:
    """Validate that evidence is admissible for an analysis at ``evaluation_time``.

    This function does not upgrade epistemic status, resolve contradictions or
    infer causality. It only enforces provenance-preserving temporal eligibility.
    """
    available = available_at(evidence)
    eligibility = evaluate_temporal_eligibility(
        evidence_id=evidence.evidence_id,
        available_at=available,
        evaluation_time=evaluation_time,
    )
    if not eligibility.eligible:
        raise ObservationBoundaryError(
            f"Evidence {evidence.evidence_id} is not eligible at "
            f"{evaluation_time.isoformat()}: {eligibility.reason}"
        )
    return eligibility


def admit_observation(
    evidence: EvidenceContract,
    *,
    evaluation_time: datetime,
) -> tuple[EvidenceContract, TemporalEligibility]:
    """Admit an observation to the analytical layer without changing its state."""
    eligibility = validate_observation_for_analysis(
        evidence,
        evaluation_time=evaluation_time,
    )
    return evidence, eligibility
