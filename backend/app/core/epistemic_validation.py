"""
CEUTIA PUBLIC — Epistemic Validation Engine.

Deterministic validation primitives for protecting the epistemic integrity
of CEUTIA PUBLIC.

This module does NOT determine whether a proposition is true.

Its purpose is to determine whether an epistemic object contains enough
documented structure to be:

    accepted
    accepted_with_warning
    quarantined
    rejected
    unknown

Core principles:

1. Correlation is not causation.
2. Repetition is not independence.
3. A model output is not an observation.
4. A scenario is not a prediction.
5. A prediction is not an outcome.
6. Missing evidence is not negative evidence.
7. Unknown must remain an explicit state.
8. Contradictions must be preserved.
9. Confidence must not exceed evidentiary support.
10. Complex models require explicit assumptions and validation.
11. Every prediction must be evaluable retrospectively.
12. Scientific validity and operational urgency are different dimensions.

This module is intentionally independent from SQLAlchemy and FastAPI.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from math import isfinite
from typing import Iterable
from uuid import UUID

from .models import (
    Claim,
    DataQualityGate,
    Evidence,
    EvidenceDirection,
    Hypothesis,
    HypothesisStatus,
    Prediction,
    PredictionStatus,
    QualityLevel,
    Signal,
    Source,
    SourceAuthenticity,
    UncertaintyType,
)


# ============================================================================
# ENUMERATIONS
# ============================================================================


class ValidationStatus(StrEnum):
    ACCEPT = "ACCEPT"
    ACCEPT_WITH_WARNING = "ACCEPT_WITH_WARNING"
    QUARANTINE = "QUARANTINE"
    REJECT = "REJECT"
    UNKNOWN = "UNKNOWN"


class ValidationCode(StrEnum):
    VALID = "VALID"

    MISSING_PROVENANCE = "MISSING_PROVENANCE"
    INVALID_PROVENANCE = "INVALID_PROVENANCE"

    LOW_SOURCE_QUALITY = "LOW_SOURCE_QUALITY"
    UNKNOWN_SOURCE_QUALITY = "UNKNOWN_SOURCE_QUALITY"
    UNVERIFIED_SOURCE = "UNVERIFIED_SOURCE"

    NO_EVIDENCE = "NO_EVIDENCE"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"

    CONTRADICTORY_EVIDENCE = "CONTRADICTORY_EVIDENCE"
    DEPENDENT_SOURCES = "DEPENDENT_SOURCES"

    EXCESSIVE_UNCERTAINTY = "EXCESSIVE_UNCERTAINTY"
    MISSING_UNCERTAINTY = "MISSING_UNCERTAINTY"

    TEMPORAL_INCONSISTENCY = "TEMPORAL_INCONSISTENCY"

    INVALID_CONFIDENCE = "INVALID_CONFIDENCE"
    UNSUPPORTED_CONFIDENCE = "UNSUPPORTED_CONFIDENCE"

    CAUSALITY_NOT_ESTABLISHED = "CAUSALITY_NOT_ESTABLISHED"

    MISSING_HYPOTHESIS_COMPETITION = "MISSING_HYPOTHESIS_COMPETITION"
    MISSING_FALSIFICATION_CRITERIA = "MISSING_FALSIFICATION_CRITERIA"

    MISSING_MODEL_VERSION = "MISSING_MODEL_VERSION"
    MISSING_VALIDATION = "MISSING_VALIDATION"

    PREDICTION_NOT_EVALUABLE = "PREDICTION_NOT_EVALUABLE"

    INVALID_DATA_QUALITY = "INVALID_DATA_QUALITY"

    UNKNOWN_STATE = "UNKNOWN_STATE"


class ValidationSeverity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class CausalStatus(StrEnum):
    NOT_ASSESSED = "NOT_ASSESSED"
    ASSOCIATIONAL = "ASSOCIATIONAL"
    TEMPORAL_ASSOCIATION = "TEMPORAL_ASSOCIATION"
    CAUSAL_HYPOTHESIS = "CAUSAL_HYPOTHESIS"
    CAUSAL_EFFECT_ESTIMATED = "CAUSAL_EFFECT_ESTIMATED"
    CAUSALITY_NOT_ESTABLISHED = "CAUSALITY_NOT_ESTABLISHED"


class ValidationMethod(StrEnum):
    NONE = "NONE"
    EXPERT_REVIEW = "EXPERT_REVIEW"
    INTERNAL_HOLDOUT = "INTERNAL_HOLDOUT"
    CROSS_VALIDATION = "CROSS_VALIDATION"
    TEMPORAL_VALIDATION = "TEMPORAL_VALIDATION"
    EXTERNAL_VALIDATION = "EXTERNAL_VALIDATION"
    PROSPECTIVE_VALIDATION = "PROSPECTIVE_VALIDATION"
    EXPERIMENTAL = "EXPERIMENTAL"
    QUASI_EXPERIMENTAL = "QUASI_EXPERIMENTAL"
    UNKNOWN = "UNKNOWN"


# ============================================================================
# RESULT TYPES
# ============================================================================


@dataclass(frozen=True, slots=True)
class ValidationFinding:
    """One deterministic epistemic validation finding."""

    code: ValidationCode
    severity: ValidationSeverity
    message: str
    object_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class ValidationResult:
    """Complete result of an epistemic validation operation."""

    status: ValidationStatus
    findings: tuple[ValidationFinding, ...]
    evaluated_at: datetime

    @property
    def valid(self) -> bool:
        """Return True only for fully accepted objects."""
        return self.status == ValidationStatus.ACCEPT

    @property
    def has_errors(self) -> bool:
        """Return True when at least one error or critical finding exists."""
        return any(
            finding.severity
            in {
                ValidationSeverity.ERROR,
                ValidationSeverity.CRITICAL,
            }
            for finding in self.findings
        )


# ============================================================================
# QUALITY MAPPINGS
# ============================================================================


_QUALITY_SCORE: dict[QualityLevel, float] = {
    QualityLevel.VERY_LOW: 0.10,
    QualityLevel.LOW: 0.30,
    QualityLevel.MODERATE: 0.55,
    QualityLevel.HIGH: 0.80,
    QualityLevel.VERY_HIGH: 0.95,
    QualityLevel.UNKNOWN: 0.0,
}


def quality_score(quality: QualityLevel) -> float:
    """
    Convert qualitative source/evidence quality to an internal score.

    This is an ordinal operational mapping, NOT a probability of truth.
    """
    return _QUALITY_SCORE[quality]


# ============================================================================
# GENERIC VALIDATION HELPERS
# ============================================================================


def _finding(
    code: ValidationCode,
    severity: ValidationSeverity,
    message: str,
    object_id: UUID | None = None,
) -> ValidationFinding:
    return ValidationFinding(
        code=code,
        severity=severity,
        message=message,
        object_id=object_id,
    )


def _status_from_findings(
    findings: Iterable[ValidationFinding],
) -> ValidationStatus:
    findings_list = tuple(findings)

    if not findings_list:
        return ValidationStatus.ACCEPT

    severities = {finding.severity for finding in findings_list}

    if ValidationSeverity.CRITICAL in severities:
        return ValidationStatus.REJECT

    if ValidationSeverity.ERROR in severities:
        return ValidationStatus.QUARANTINE

    if ValidationSeverity.WARNING in severities:
        return ValidationStatus.ACCEPT_WITH_WARNING

    return ValidationStatus.ACCEPT


def _result(
    findings: Iterable[ValidationFinding],
    *,
    evaluated_at: datetime,
) -> ValidationResult:
    if evaluated_at.tzinfo is None or evaluated_at.utcoffset() is None:
        raise ValueError("evaluated_at must be timezone-aware")

    findings_tuple = tuple(findings)

    return ValidationResult(
        status=_status_from_findings(findings_tuple),
        findings=findings_tuple,
        evaluated_at=evaluated_at,
    )


def _validate_probability(
    value: float | None,
    *,
    name: str,
    object_id: UUID | None,
) -> ValidationFinding | None:
    if value is None:
        return None

    if not isfinite(value) or not 0.0 <= value <= 1.0:
        return _finding(
            ValidationCode.INVALID_CONFIDENCE,
            ValidationSeverity.ERROR,
            f"{name} must be finite and between 0 and 1.",
            object_id,
        )

    return None


# ============================================================================
# SOURCE VALIDATION
# ============================================================================


def validate_source(
    source: Source,
    *,
    evaluated_at: datetime,
) -> ValidationResult:
    """
    Validate the epistemic metadata of a source.

    A verified source is not assumed to make every claim true.
    """

    findings: list[ValidationFinding] = []

    if source.authenticity == SourceAuthenticity.UNKNOWN:
        findings.append(
            _finding(
                ValidationCode.UNVERIFIED_SOURCE,
                ValidationSeverity.WARNING,
                "Source authenticity has not been established.",
                source.id,
            )
        )

    if source.authenticity == SourceAuthenticity.DISPUTED:
        findings.append(
            _finding(
                ValidationCode.UNVERIFIED_SOURCE,
                ValidationSeverity.ERROR,
                "Source authenticity is disputed.",
                source.id,
            )
        )

    if source.quality == QualityLevel.UNKNOWN:
        findings.append(
            _finding(
                ValidationCode.UNKNOWN_SOURCE_QUALITY,
                ValidationSeverity.WARNING,
                "Source quality has not been assessed.",
                source.id,
            )
        )

    elif source.quality in {
        QualityLevel.VERY_LOW,
        QualityLevel.LOW,
    }:
        findings.append(
            _finding(
                ValidationCode.LOW_SOURCE_QUALITY,
                ValidationSeverity.WARNING,
                "Source quality is low and requires cautious downstream use.",
                source.id,
            )
        )

    if source.independence_group is None:
        findings.append(
            _finding(
                ValidationCode.DEPENDENT_SOURCES,
                ValidationSeverity.WARNING,
                "No independence group has been assigned to the source.",
                source.id,
            )
        )

    return _result(findings, evaluated_at=evaluated_at)


# ============================================================================
# CLAIM VALIDATION
# ============================================================================


def validate_claim(
    claim: Claim,
    *,
    sources: Iterable[Source],
    evidence: Iterable[Evidence],
    evaluated_at: datetime,
) -> ValidationResult:
    """
    Validate whether a claim has sufficient epistemic structure.

    This function does not determine whether the claim is true.
    """

    source_list = tuple(sources)
    evidence_list = tuple(evidence)

    findings: list[ValidationFinding] = []

    if not claim.source_ids and not claim.evidence_ids:
        findings.append(
            _finding(
                ValidationCode.MISSING_PROVENANCE,
                ValidationSeverity.ERROR,
                "Claim has neither source references nor evidence references.",
                claim.id,
            )
        )

    if claim.evidence_ids and not evidence_list:
        findings.append(
            _finding(
                ValidationCode.INVALID_PROVENANCE,
                ValidationSeverity.ERROR,
                "Claim references evidence that was not supplied for validation.",
                claim.id,
            )
        )

    if not evidence_list:
        findings.append(
            _finding(
                ValidationCode.NO_EVIDENCE,
                ValidationSeverity.ERROR,
                "No evidence is available for the claim.",
                claim.id,
            )
        )

    probability_finding = _validate_probability(
        claim.confidence,
        name="claim confidence",
        object_id=claim.id,
    )

    if probability_finding is not None:
        findings.append(probability_finding)

    if claim.confidence is not None and not evidence_list:
        findings.append(
            _finding(
                ValidationCode.UNSUPPORTED_CONFIDENCE,
                ValidationSeverity.ERROR,
                "A confidence value cannot substitute for missing evidence.",
                claim.id,
            )
        )

    if source_list:
        unknown_sources = [
            source
            for source in source_list
            if source.authenticity == SourceAuthenticity.UNKNOWN
        ]

        if unknown_sources:
            findings.append(
                _finding(
                    ValidationCode.UNVERIFIED_SOURCE,
                    ValidationSeverity.WARNING,
                    "At least one supporting source has unknown authenticity.",
                    claim.id,
                )
            )

    independent_groups = {
        evidence_item.independence_group
        for evidence_item in evidence_list
        if evidence_item.independence_group is not None
    }

    if len(evidence_list) > 1 and len(independent_groups) < 2:
        findings.append(
            _finding(
                ValidationCode.DEPENDENT_SOURCES,
                ValidationSeverity.WARNING,
                "Multiple evidence items do not demonstrate multiple independent "
                "source groups.",
                claim.id,
            )
        )

    has_support = any(
        item.direction == EvidenceDirection.SUPPORTS
        for item in evidence_list
    )

    has_refutation = any(
        item.direction == EvidenceDirection.REFUTES
        for item in evidence_list
    )

    if has_support and has_refutation:
        findings.append(
            _finding(
                ValidationCode.CONTRADICTORY_EVIDENCE,
                ValidationSeverity.WARNING,
                "The evidence contains both supporting and refuting material. "
                "The contradiction must remain explicit.",
                claim.id,
            )
        )

    return _result(findings, evaluated_at=evaluated_at)


# ============================================================================
# EVIDENCE VALIDATION
# ============================================================================


def validate_evidence(
    evidence: Evidence,
    *,
    source: Source | None,
    evaluated_at: datetime,
) -> ValidationResult:
    """Validate one evidence item without assigning truth to it."""

    findings: list[ValidationFinding] = []

    if source is None:
        findings.append(
            _finding(
                ValidationCode.INVALID_PROVENANCE,
                ValidationSeverity.ERROR,
                "Evidence references a source that is unavailable.",
                evidence.id,
            )
        )

    if (
        evidence.artifact_id is None
        and evidence.observation_id is None
    ):
        findings.append(
            _finding(
                ValidationCode.MISSING_PROVENANCE,
                ValidationSeverity.ERROR,
                "Evidence must reference an artifact or observation.",
                evidence.id,
            )
        )

    probability_finding = _validate_probability(
        evidence.reliability,
        name="evidence reliability",
        object_id=evidence.id,
    )

    if probability_finding is not None:
        findings.append(probability_finding)

    if source is not None and source.quality == QualityLevel.UNKNOWN:
        findings.append(
            _finding(
                ValidationCode.UNKNOWN_SOURCE_QUALITY,
                ValidationSeverity.WARNING,
                "Evidence originates from a source whose quality is unknown.",
                evidence.id,
            )
        )

    if source is not None and source.authenticity in {
        SourceAuthenticity.UNVERIFIED,
        SourceAuthenticity.DISPUTED,
    }:
        findings.append(
            _finding(
                ValidationCode.UNVERIFIED_SOURCE,
                ValidationSeverity.WARNING,
                "Evidence originates from an unverified or disputed source.",
                evidence.id,
            )
        )

    return _result(findings, evaluated_at=evaluated_at)


# ============================================================================
# HYPOTHESIS VALIDATION
# ============================================================================


def validate_hypothesis(
    hypothesis: Hypothesis,
    *,
    evaluated_at: datetime,
) -> ValidationResult:
    """
    Validate whether a hypothesis is explicitly falsifiable.
    """

    findings: list[ValidationFinding] = []

    prior_finding = _validate_probability(
        hypothesis.prior_probability,
        name="prior probability",
        object_id=hypothesis.id,
    )

    posterior_finding = _validate_probability(
        hypothesis.posterior_probability,
        name="posterior probability",
        object_id=hypothesis.id,
    )

    if prior_finding is not None:
        findings.append(prior_finding)

    if posterior_finding is not None:
        findings.append(posterior_finding)

    if not hypothesis.falsification_criteria:
        findings.append(
            _finding(
                ValidationCode.MISSING_FALSIFICATION_CRITERIA,
                ValidationSeverity.WARNING,
                "Hypothesis has no explicit falsification criteria.",
                hypothesis.id,
            )
        )

    if not hypothesis.discriminating_predictions:
        findings.append(
            _finding(
                ValidationCode.MISSING_HYPOTHESIS_COMPETITION,
                ValidationSeverity.WARNING,
                "Hypothesis contains no discriminating predictions.",
                hypothesis.id,
            )
        )

    return _result(findings, evaluated_at=evaluated_at)


# ============================================================================
# HYPOTHESIS COMPETITION
# ============================================================================


def validate_hypothesis_competition(
    hypotheses: Iterable[Hypothesis],
    *,
    evaluated_at: datetime,
) -> ValidationResult:
    """
    Validate a set of competing hypotheses.

    The objective is not to force competition where scientifically
    inappropriate, but to prevent the first plausible narrative from
    automatically becoming the accepted explanation.
    """

    hypothesis_list = tuple(hypotheses)
    findings: list[ValidationFinding] = []

    if len(hypothesis_list) == 0:
        findings.append(
            _finding(
                ValidationCode.MISSING_HYPOTHESIS_COMPETITION,
                ValidationSeverity.WARNING,
                "No competing hypotheses were supplied.",
            )
        )

        return _result(findings, evaluated_at=evaluated_at)

    if len(hypothesis_list) == 1:
        findings.append(
            _finding(
                ValidationCode.MISSING_HYPOTHESIS_COMPETITION,
                ValidationSeverity.WARNING,
                "Only one hypothesis is represented. Alternative explanations "
                "have not been documented.",
                hypothesis_list[0].id,
            )
        )

    active_hypotheses = [
        hypothesis
        for hypothesis in hypothesis_list
        if hypothesis.status in {
            HypothesisStatus.ACTIVE,
            HypothesisStatus.SUPPORTED,
            HypothesisStatus.INCONCLUSIVE,
        }
    ]

    if not active_hypotheses:
        findings.append(
            _finding(
                ValidationCode.UNKNOWN_STATE,
                ValidationSeverity.WARNING,
                "No active or unresolved hypothesis remains.",
            )
        )

    return _result(findings, evaluated_at=evaluated_at)


# ============================================================================
# CAUSALITY VALIDATION
# ============================================================================


def validate_causal_interpretation(
    *,
    causal_status: CausalStatus,
    validation_method: ValidationMethod,
    object_id: UUID | None,
    evaluated_at: datetime,
) -> ValidationResult:
    """
    Prevent unsupported causal language.

    Association, temporal precedence and causality are deliberately
    represented as different epistemic states.
    """

    findings: list[ValidationFinding] = []

    if causal_status in {
        CausalStatus.ASSOCIATIONAL,
        CausalStatus.TEMPORAL_ASSOCIATION,
        CausalStatus.CAUSAL_HYPOTHESIS,
    }:
        if validation_method == ValidationMethod.NONE:
            findings.append(
                _finding(
                    ValidationCode.CAUSALITY_NOT_ESTABLISHED,
                    ValidationSeverity.WARNING,
                    "The relationship is not causally established. "
                    "It must not be presented as established causation.",
                    object_id,
                )
            )

    if (
        causal_status == CausalStatus.CAUSAL_EFFECT_ESTIMATED
        and validation_method
        not in {
            ValidationMethod.EXPERIMENTAL,
            ValidationMethod.QUASI_EXPERIMENTAL,
            ValidationMethod.EXTERNAL_VALIDATION,
            ValidationMethod.PROSPECTIVE_VALIDATION,
        }
    ):
        findings.append(
            _finding(
                ValidationCode.CAUSALITY_NOT_ESTABLISHED,
                ValidationSeverity.ERROR,
                "A causal effect cannot be represented as established without "
                "an appropriate causal identification and validation method.",
                object_id,
            )
        )

    return _result(findings, evaluated_at=evaluated_at)


# ============================================================================
# MODEL VALIDATION
# ============================================================================


@dataclass(frozen=True, slots=True)
class ModelValidationMetadata:
    """
    Minimum metadata required to treat a quantitative model output as
    scientifically evaluated rather than merely computationally generated.
    """

    model_name: str
    model_version: str | None

    validation_method: ValidationMethod

    validation_score: float | None = None
    baseline_score: float | None = None

    assumptions: tuple[str, ...] = ()
    sensitivity_analysis_completed: bool = False

    external_validation_completed: bool = False


def validate_model(
    metadata: ModelValidationMetadata,
    *,
    object_id: UUID | None,
    evaluated_at: datetime,
) -> ValidationResult:
    """
    Validate the methodological metadata surrounding a model.

    The function does not decide whether the model is scientifically good.
    It detects missing minimum safeguards.
    """

    findings: list[ValidationFinding] = []

    if not metadata.model_name.strip():
        findings.append(
            _finding(
                ValidationCode.INVALID_PROVENANCE,
                ValidationSeverity.ERROR,
                "Model name is required.",
                object_id,
            )
        )

    if not metadata.model_version:
        findings.append(
            _finding(
                ValidationCode.MISSING_MODEL_VERSION,
                ValidationSeverity.WARNING,
                "Model version is missing.",
                object_id,
            )
        )

    if metadata.validation_method == ValidationMethod.UNKNOWN:
        findings.append(
            _finding(
                ValidationCode.MISSING_VALIDATION,
                ValidationSeverity.WARNING,
                "Model validation method is unknown.",
                object_id,
            )
        )

    if metadata.validation_method == ValidationMethod.NONE:
        findings.append(
            _finding(
                ValidationCode.MISSING_VALIDATION,
                ValidationSeverity.ERROR,
                "Model has not been validated.",
                object_id,
            )
        )

    if not metadata.assumptions:
        findings.append(
            _finding(
                ValidationCode.MISSING_VALIDATION,
                ValidationSeverity.WARNING,
                "Model assumptions have not been documented.",
                object_id,
            )
        )

    if not metadata.sensitivity_analysis_completed:
        findings.append(
            _finding(
                ValidationCode.MISSING_VALIDATION,
                ValidationSeverity.WARNING,
                "Sensitivity analysis has not been documented.",
                object_id,
            )
        )

    if metadata.validation_score is not None:
        if not isfinite(metadata.validation_score):
            findings.append(
                _finding(
                    ValidationCode.INVALID_CONFIDENCE,
                    ValidationSeverity.ERROR,
                    "Validation score must be finite.",
                    object_id,
                )
            )

    return _result(findings, evaluated_at=evaluated_at)


# ============================================================================
# PREDICTION VALIDATION
# ============================================================================


def validate_prediction(
    prediction: Prediction,
    *,
    evaluated_at: datetime,
) -> ValidationResult:
    """
    Validate whether a prediction has been registered in a way that permits
    retrospective calibration.
    """

    findings: list[ValidationFinding] = []

    probability_finding = _validate_probability(
        prediction.probability,
        name="prediction probability",
        object_id=prediction.id,
    )

    if probability_finding is not None:
        findings.append(probability_finding)

    if not prediction.basis_ids:
        findings.append(
            _finding(
                ValidationCode.MISSING_PROVENANCE,
                ValidationSeverity.ERROR,
                "Prediction has no documented analytical basis.",
                prediction.id,
            )
        )

    if prediction.status == PredictionStatus.OPEN:
        if prediction.outcome_id is not None:
            findings.append(
                _finding(
                    ValidationCode.PREDICTION_NOT_EVALUABLE,
                    ValidationSeverity.ERROR,
                    "An open prediction cannot already reference an outcome.",
                    prediction.id,
                )
            )

    if prediction.status in {
        PredictionStatus.CONFIRMED,
        PredictionStatus.PARTIALLY_CONFIRMED,
        PredictionStatus.DISCONFIRMED,
    }:
        if prediction.outcome_id is None:
            findings.append(
                _finding(
                    ValidationCode.PREDICTION_NOT_EVALUABLE,
                    ValidationSeverity.ERROR,
                    "Evaluated predictions require an outcome reference.",
                    prediction.id,
                )
            )

    if prediction.evaluation_window_start is None:
        findings.append(
            _finding(
                ValidationCode.PREDICTION_NOT_EVALUABLE,
                ValidationSeverity.WARNING,
                "Prediction has no explicit evaluation-window start.",
                prediction.id,
            )
        )

    return _result(findings, evaluated_at=evaluated_at)


# ============================================================================
# SIGNAL VALIDATION
# ============================================================================


def validate_signal(
    signal: Signal,
    *,
    evaluated_at: datetime,
) -> ValidationResult:
    """
    Validate the minimum evidentiary structure of an analytical signal.
    """

    findings: list[ValidationFinding] = []

    if (
        not signal.observation_ids
        and not signal.evidence_ids
        and not signal.source_ids
    ):
        findings.append(
            _finding(
                ValidationCode.MISSING_PROVENANCE,
                ValidationSeverity.ERROR,
                "Signal has no observations, evidence or source references.",
                signal.id,
            )
        )

    strength_finding = _validate_probability(
        signal.strength,
        name="signal strength",
        object_id=signal.id,
    )

    uncertainty_finding = _validate_probability(
        signal.uncertainty,
        name="signal uncertainty",
        object_id=signal.id,
    )

    if strength_finding is not None:
        findings.append(strength_finding)

    if uncertainty_finding is not None:
        findings.append(uncertainty_finding)

    if signal.strength is not None and signal.uncertainty is None:
        findings.append(
            _finding(
                ValidationCode.MISSING_UNCERTAINTY,
                ValidationSeverity.WARNING,
                "Signal strength is provided without explicit uncertainty.",
                signal.id,
            )
        )

    return _result(findings, evaluated_at=evaluated_at)


# ============================================================================
# DATA QUALITY VALIDATION
# ============================================================================


def validate_data_quality_gate(
    gate: DataQualityGate,
    *,
    object_id: UUID | None,
    evaluated_at: datetime,
) -> ValidationResult:
    """
    Translate a data-quality gate into an epistemic processing decision.
    """

    findings: list[ValidationFinding] = []

    if gate == DataQualityGate.REJECT:
        findings.append(
            _finding(
                ValidationCode.INVALID_DATA_QUALITY,
                ValidationSeverity.CRITICAL,
                "Data-quality gate is REJECT. Object must not enter analytical "
                "processing.",
                object_id,
            )
        )

    elif gate == DataQualityGate.QUARANTINE:
        findings.append(
            _finding(
                ValidationCode.INVALID_DATA_QUALITY,
                ValidationSeverity.ERROR,
                "Data-quality gate is QUARANTINE. Object requires controlled "
                "review before analytical use.",
                object_id,
            )
        )

    elif gate == DataQualityGate.UNKNOWN:
        findings.append(
            _finding(
                ValidationCode.INVALID_DATA_QUALITY,
                ValidationSeverity.WARNING,
                "Data-quality state is unknown.",
                object_id,
            )
        )

    elif gate == DataQualityGate.ACCEPT_WITH_WARNING:
        findings.append(
            _finding(
                ValidationCode.INVALID_DATA_QUALITY,
                ValidationSeverity.WARNING,
                "Data accepted with documented quality limitations.",
                object_id,
            )
        )

    return _result(findings, evaluated_at=evaluated_at)


# ============================================================================
# SOURCE INDEPENDENCE
# ============================================================================


def assess_source_independence(
    sources: Iterable[Source],
    *,
    evaluated_at: datetime,
) -> ValidationResult:
    """
    Determine whether apparent source multiplicity represents genuine
    independence.

    This does not infer independence when metadata are absent.
    """

    source_list = tuple(sources)
    findings: list[ValidationFinding] = []

    if not source_list:
        findings.append(
            _finding(
                ValidationCode.NO_EVIDENCE,
                ValidationSeverity.ERROR,
                "No sources were supplied.",
            )
        )

        return _result(findings, evaluated_at=evaluated_at)

    groups = {
        source.independence_group
        for source in source_list
        if source.independence_group is not None
    }

    if len(source_list) > 1 and len(groups) < 2:
        findings.append(
            _finding(
                ValidationCode.DEPENDENT_SOURCES,
                ValidationSeverity.WARNING,
                "Multiple sources are present, but independent source groups "
                "have not been demonstrated.",
            )
        )

    missing_groups = [
        source
        for source in source_list
        if source.independence_group is None
    ]

    if missing_groups:
        findings.append(
            _finding(
                ValidationCode.DEPENDENT_SOURCES,
                ValidationSeverity.WARNING,
                "At least one source lacks an independence-group declaration.",
            )
        )

    return _result(findings, evaluated_at=evaluated_at)


# ============================================================================
# AGGREGATE VALIDATION
# ============================================================================


def validate_epistemic_chain(
    *,
    claim: Claim | None = None,
    sources: Iterable[Source] = (),
    evidence: Iterable[Evidence] = (),
    signal: Signal | None = None,
    hypothesis: Hypothesis | None = None,
    prediction: Prediction | None = None,
    evaluated_at: datetime,
) -> ValidationResult:
    """
    Validate a partial epistemic chain as a whole.

    This is the main deterministic gate for analytical services.

    It intentionally performs no statistical inference.
    """

    findings: list[ValidationFinding] = []

    source_list = tuple(sources)
    evidence_list = tuple(evidence)

    if claim is not None:
        claim_result = validate_claim(
            claim,
            sources=source_list,
            evidence=evidence_list,
            evaluated_at=evaluated_at,
        )
        findings.extend(claim_result.findings)

    if signal is not None:
        signal_result = validate_signal(
            signal,
            evaluated_at=evaluated_at,
        )
        findings.extend(signal_result.findings)

    if hypothesis is not None:
        hypothesis_result = validate_hypothesis(
            hypothesis,
            evaluated_at=evaluated_at,
        )
        findings.extend(hypothesis_result.findings)

    if prediction is not None:
        prediction_result = validate_prediction(
            prediction,
            evaluated_at=evaluated_at,
        )
        findings.extend(prediction_result.findings)

    if source_list:
        independence_result = assess_source_independence(
            source_list,
            evaluated_at=evaluated_at,
        )
        findings.extend(independence_result.findings)

    if not claim and not signal and not hypothesis and not prediction:
        findings.append(
            _finding(
                ValidationCode.UNKNOWN_STATE,
                ValidationSeverity.WARNING,
                "No epistemic object was supplied for validation.",
            )
        )

    return _result(findings, evaluated_at=evaluated_at)


# ============================================================================
# SCIENTIFIC INVARIANTS
# ============================================================================


SCIENTIFIC_INVARIANTS: tuple[str, ...] = (
    "correlation_is_not_causation",
    "temporal_precedence_is_not_causation",
    "repeated_sources_are_not_necessarily_independent",
    "model_output_is_not_observation",
    "scenario_is_not_prediction",
    "prediction_is_not_outcome",
    "absence_of_evidence_is_not_evidence_of_absence",
    "unknown_is_not_zero",
    "unknown_is_not_false",
    "confidence_is_not_truth",
    "complexity_does_not_establish_validity",
    "statistical_significance_does_not_establish_causality",
    "association_does_not_establish_mechanism",
    "one_model_does_not_establish_consensus",
    "publication_does_not_establish_validity",
)


def get_scientific_invariants() -> tuple[str, ...]:
    """Return the immutable scientific invariants enforced by the module."""
    return SCIENTIFIC_INVARIANTS


__all__ = [
    "CausalStatus",
    "ModelValidationMetadata",
    "SCIENTIFIC_INVARIANTS",
    "ValidationCode",
    "ValidationFinding",
    "ValidationMethod",
    "ValidationResult",
    "ValidationSeverity",
    "ValidationStatus",
    "assess_source_independence",
    "get_scientific_invariants",
    "quality_score",
    "validate_causal_interpretation",
    "validate_claim",
    "validate_data_quality_gate",
    "validate_epistemic_chain",
    "validate_evidence",
    "validate_hypothesis",
    "validate_hypothesis_competition",
    "validate_model",
    "validate_prediction",
    "validate_signal",
    "validate_source",
]