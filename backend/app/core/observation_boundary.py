"""CeutIA observation boundary.

Controlled boundary between retrieval/ingestion and downstream analysis.
Evidence is admitted only with provenance-preserving, point-in-time availability.
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
    """Return the availability time of the exact evidence version.

    Revision time has precedence because a corrected version cannot be treated as
    if it had existed in its corrected form at the original publication time.
    Event time is never an availability marker.
    """
    return evidence.available_at


def validate_observation_for_analysis(
    evidence: EvidenceContract,
    *,
    evaluation_time: datetime,
) -> TemporalEligibility:
    """Validate point-in-time admissibility without changing epistemic state."""
    available = available_at(evidence)
    eligibility = evaluate_temporal_eligibility(
        evidence_id=evidence.evidence_id,
        available_at=available,
        evaluation_time=evaluation_time,
    )
    if not eligibility.eligible:
        raise ObservationBoundaryError(  # noqa: TRY003
            f"Evidence {evidence.evidence_id} is not eligible at "
            f"{evaluation_time.isoformat()}: {eligibility.reason}"
        )
    return eligibility


def admit_observation(
    evidence: EvidenceContract,
    *,
    evaluation_time: datetime,
) -> tuple[EvidenceContract, TemporalEligibility]:
    """Admit an observation without upgrading, resolving or rewriting it."""
    eligibility = validate_observation_for_analysis(
        evidence,
        evaluation_time=evaluation_time,
    )
    return evidence, eligibility
