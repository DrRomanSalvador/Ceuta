"""P0 contracts for epistemic state, temporal eligibility and provenance.

This module deliberately separates epistemic status from implementation/validation
status. It is conservative: missing, dependent or future information cannot silently
upgrade a claim.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from typing import Iterable

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ImplementationStatus(StrEnum):
    EXISTING_VERIFIED = "EXISTENTE_VERIFICADO"
    PROPOSED = "PROPUESTO"
    PENDING = "PENDIENTE"
    NOT_VERIFIED = "NO_VERIFICADO"
    UNKNOWN = "UNKNOWN"


class EpistemicStatus(StrEnum):
    OBSERVED_FACT = "OBSERVED_FACT"
    CORROBORATED_FACT = "CORROBORATED_FACT"
    ATTRIBUTED_CLAIM = "ATTRIBUTED_CLAIM"
    INFERENCE = "INFERENCE"
    HYPOTHESIS = "HYPOTHESIS"
    UNVERIFIED = "UNVERIFIED"
    CONTRADICTED = "CONTRADICTED"
    DISPROVEN = "DISPROVEN"
    UNKNOWN = "UNKNOWN"


class SourceRelation(StrEnum):
    INDEPENDENT = "INDEPENDENT"
    DEPENDENT = "DEPENDENT"
    COPY = "COPY"
    AMPLIFIER = "AMPLIFIER"
    UNKNOWN = "UNKNOWN"


class Uncertainty(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: str = Field(min_length=1)
    lower: float | None = None
    upper: float | None = None
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    description: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_interval(self) -> "Uncertainty":
        if (self.lower is None) != (self.upper is None):
            raise ValueError("lower and upper must be supplied together")
        if self.lower is not None and self.upper is not None and self.lower > self.upper:
            raise ValueError("uncertainty lower bound cannot exceed upper bound")
        return self


class ProvenanceLink(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str = Field(min_length=1)
    source_version: str = Field(min_length=1)
    relation: SourceRelation
    parent_evidence_ids: tuple[str, ...] = ()
    transformation: str = Field(min_length=1)


class EvidenceContract(BaseModel):
    """Evidence record with explicit availability and epistemic semantics."""

    model_config = ConfigDict(extra="forbid")

    evidence_id: str = Field(min_length=1)
    claim: str = Field(min_length=1)
    source_id: str = Field(min_length=1)
    publication_time: datetime | None = None
    event_time: datetime | None = None
    observed_at: datetime = Field(description="When the evidence was observed/available")
    ingestion_time: datetime
    uncertainty: Uncertainty
    epistemic_status: EpistemicStatus
    source_relation: SourceRelation
    provenance: tuple[ProvenanceLink, ...] = ()
    corroborating_evidence_ids: tuple[str, ...] = ()
    independent_source_count: int = Field(default=0, ge=0)
    limitations: tuple[str, ...] = ()
    schema_version: str = Field(default="1.0.0", min_length=1)

    @model_validator(mode="after")
    def validate_temporal_order(self) -> "EvidenceContract":
        for name, value in (
            ("observed_at", self.observed_at),
            ("publication_time", self.publication_time),
        ):
            if value is not None and value.tzinfo is None:
                raise ValueError(f"{name} must be timezone-aware")
        if self.ingestion_time.tzinfo is None:
            raise ValueError("ingestion_time must be timezone-aware")
        if self.publication_time is not None and self.ingestion_time < self.publication_time:
            raise ValueError("ingestion_time cannot precede publication_time")
        if self.observed_at > self.ingestion_time:
            raise ValueError("observed_at cannot be later than ingestion_time")
        if self.epistemic_status == EpistemicStatus.CORROBORATED_FACT:
            if self.independent_source_count < 2:
                raise ValueError("CORROBORATED_FACT requires at least two independent sources")
            if not self.corroborating_evidence_ids:
                raise ValueError("CORROBORATED_FACT requires corroborating evidence IDs")
        return self


class TemporalEligibility(BaseModel):
    model_config = ConfigDict(extra="forbid")

    evaluation_time: datetime
    evidence_id: str = Field(min_length=1)
    available_at: datetime
    eligible: bool
    reason: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_eligibility(self) -> "TemporalEligibility":
        if self.evaluation_time.tzinfo is None or self.available_at.tzinfo is None:
            raise ValueError("evaluation_time and available_at must be timezone-aware")
        expected = self.available_at <= self.evaluation_time
        if self.eligible != expected:
            raise ValueError("eligible must equal available_at <= evaluation_time")
        return self


def evaluate_temporal_eligibility(
    *, evidence_id: str, available_at: datetime, evaluation_time: datetime
) -> TemporalEligibility:
    """Return deterministic feature eligibility for a point-in-time evaluation."""
    if available_at.tzinfo is None or evaluation_time.tzinfo is None:
        raise ValueError("timestamps must be timezone-aware")
    eligible = available_at <= evaluation_time
    return TemporalEligibility(
        evidence_id=evidence_id,
        available_at=available_at,
        evaluation_time=evaluation_time,
        eligible=eligible,
        reason=(
            "available_at is on or before evaluation_time"
            if eligible
            else "available_at is after evaluation_time; future information is prohibited"
        ),
    )


def independent_source_count(relations: Iterable[SourceRelation]) -> int:
    """Count only explicitly independent sources; unknown is never independent."""
    return sum(relation == SourceRelation.INDEPENDENT for relation in relations)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)
