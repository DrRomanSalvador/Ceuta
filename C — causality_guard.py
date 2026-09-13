from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import isfinite
from typing import Final
from uuid import UUID, uuid4


class CausalityValidationError(ValueError):
    """Base causal-validation error."""


class CausalityRejected(CausalityValidationError):
    """Raised when evidence is insufficient for a causal label."""


@dataclass(frozen=True, slots=True)
class ObservedAssociation:
    association_id: UUID
    source_variable: str
    target_variable: str
    coefficient: float
    sample_size: int
    temporal_lag_seconds: float
    evidence_ids: tuple[UUID, ...]
    evaluated_at: datetime

    def __post_init__(self) -> None:
        if not self.source_variable.strip():
            raise CausalityValidationError(
                "source_variable cannot be empty"
            )

        if not self.target_variable.strip():
            raise CausalityValidationError(
                "target_variable cannot be empty"
            )

        if not isfinite(self.coefficient):
            raise CausalityValidationError(
                "coefficient must be finite"
            )

        if not isfinite(self.temporal_lag_seconds):
            raise CausalityValidationError(
                "temporal_lag_seconds must be finite"
            )

        if self.sample_size < 1:
            raise CausalityValidationError(
                "sample_size must be positive"
            )

        if self.evaluated_at.tzinfo is None:
            raise CausalityValidationError(
                "evaluated_at must be timezone-aware"
            )

        if self.source_variable == self.target_variable:
            raise CausalityValidationError(
                "self-associations are not accepted"
            )


@dataclass(frozen=True, slots=True)
class ProspectiveValidationEvidence:
    validated: bool
    sample_size: int
    forecast_skill: float
    baseline_skill: float
    calibration_error: float
    validation_windows: int

    def __post_init__(self) -> None:
        if self.sample_size < 1:
            raise CausalityValidationError(
                "sample_size must be positive"
            )

        if self.validation_windows < 1:
            raise CausalityValidationError(
                "validation_windows must be positive"
            )

        for name, value in (
            ("forecast_skill", self.forecast_skill),
            ("baseline_skill", self.baseline_skill),
            ("calibration_error", self.calibration_error),
        ):
            if not isfinite(value):
                raise CausalityValidationError(
                    f"{name} must be finite"
                )

        if not 0.0 <= self.calibration_error <= 1.0:
            raise CausalityValidationError(
                "calibration_error must be within [0, 1]"
            )


@dataclass(frozen=True, slots=True)
class CausalValidationEvidence:
    design: str
    confounder_control: bool
    temporal_precedence: bool
    intervention_or_quasi_experiment: bool
    replication_count: int
    validated: bool

    def __post_init__(self) -> None:
        if not self.design.strip():
            raise CausalityValidationError(
                "causal design cannot be empty"
            )

        if self.replication_count < 1:
            raise CausalityValidationError(
                "replication_count must be positive"
            )


@dataclass(frozen=True, slots=True)
class CausalRelationship:
    relationship_id: UUID
    source_variable: str
    target_variable: str
    association_id: UUID
    causal_evidence: CausalValidationEvidence
    created_at: datetime


@dataclass(frozen=True, slots=True)
class CausalityDecision:
    accepted: bool
    reason: str
    relationship: CausalRelationship | None


class CausalityGuard:
    MIN_SAMPLE_SIZE: Final[int] = 100
    MIN_VALIDATION_WINDOWS: Final[int] = 5
    MIN_REPLICATIONS: Final[int] = 3
    MAX_CALIBRATION_ERROR: Final[float] = 0.20

    def validate(
        self,
        association: ObservedAssociation,
        prospective_validation: ProspectiveValidationEvidence,
        causal_validation: CausalValidationEvidence | None = None,
    ) -> CausalityDecision:
        if not prospective_validation.validated:
            return self._reject(
                "prospective validation has not been established"
            )

        if prospective_validation.sample_size < self.MIN_SAMPLE_SIZE:
            return self._reject(
                "insufficient prospective validation sample"
            )

        if (
            prospective_validation.validation_windows
            < self.MIN_VALIDATION_WINDOWS
        ):
            return self._reject(
                "insufficient independent validation windows"
            )

        if (
            prospective_validation.calibration_error
            > self.MAX_CALIBRATION_ERROR
        ):
            return self._reject(
                "prospective calibration error exceeds causal guard threshold"
            )

        if (
            prospective_validation.forecast_skill
            <= prospective_validation.baseline_skill
        ):
            return self._reject(
                "forecasting does not outperform the baseline"
            )

        if causal_validation is None:
            return self._reject(
                "predictive validation does not establish causality"
            )

        if not causal_validation.validated:
            return self._reject(
                "causal validation has not been established"
            )

        if not causal_validation.confounder_control:
            return self._reject(
                "confounder control is insufficient"
            )

        if not causal_validation.temporal_precedence:
            return self._reject(
                "temporal precedence has not been demonstrated"
            )

        if not causal_validation.intervention_or_quasi_experiment:
            return self._reject(
                "no intervention or quasi-experimental evidence is available"
            )

        if causal_validation.replication_count < self.MIN_REPLICATIONS:
            return self._reject(
                "insufficient causal replication"
            )

        relationship = CausalRelationship(
            relationship_id=uuid4(),
            source_variable=association.source_variable,
            target_variable=association.target_variable,
            association_id=association.association_id,
            causal_evidence=causal_validation,
            created_at=datetime.now(association.evaluated_at.tzinfo),
        )

        return CausalityDecision(
            accepted=True,
            reason="causal validation requirements satisfied",
            relationship=relationship,
        )

    @staticmethod
    def _reject(reason: str) -> CausalityDecision:
        return CausalityDecision(
            accepted=False,
            reason=reason,
            relationship=None,
        )