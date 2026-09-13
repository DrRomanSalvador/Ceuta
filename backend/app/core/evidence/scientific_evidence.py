"""Scientific evidence quality, validation and decision-safety gate."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Sequence

from .scientific_assurance import GradeAssessment, GradeRating


class EvidenceClass(StrEnum):
    STANDARD = "standard"
    GUIDELINE = "guideline"
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    METHODOLOGICAL = "methodological"
    EMPIRICAL_VALIDATION = "empirical_validation"
    PROSPECTIVE_VALIDATION = "prospective_validation"
    OBSERVATIONAL = "observational"
    PREPRINT = "preprint"
    NARRATIVE_REVIEW = "narrative_review"
    BLOG = "blog"
    COMMERCIAL = "commercial"
    WIKIPEDIA = "wikipedia"


class ValidationLevel(StrEnum):
    NONE = "none"
    APPARENT = "apparent"
    INTERNAL = "internal"
    TEMPORAL = "temporal"
    GEOGRAPHIC = "geographic"
    EXTERNAL = "external"
    PROSPECTIVE = "prospective"


class Certainty(StrEnum):
    HIGH = "high"
    MODERATE = "moderate"
    LOW = "low"
    VERY_LOW = "very_low"
    UNRATED = "unrated"


class Missingness(StrEnum):
    NONE = "none"
    MCAR = "mcar"
    MAR = "mar"
    MNAR = "mnar"
    UNKNOWN = "unknown"


class GateDisposition(StrEnum):
    ALLOW = "allow"
    HUMAN_REVIEW = "human_review"
    ABSTAIN = "abstain"


@dataclass(frozen=True, slots=True)
class ScientificEvidence:
    evidence_id: str
    evidence_class: EvidenceClass
    peer_reviewed: bool
    doi_verified: bool
    certainty: Certainty = Certainty.UNRATED
    risk_of_bias: float | None = None
    applicability: float | None = None
    independence: float = 1.0
    validation_level: ValidationLevel = ValidationLevel.NONE
    calibrated: bool | None = None
    decision_utility_evaluated: bool = False
    harms_evaluated: bool = False
    human_factors_evaluated: bool = False
    missingness: Missingness = Missingness.NONE
    missingness_sensitivity: bool = False
    high_impact: bool = False
    prediction_model: bool = False
    primary_source_verified: bool = True
    grade: GradeAssessment | None = None
    common_origin_id: str | None = None

    def __post_init__(self) -> None:
        if not self.evidence_id:
            raise ValueError("evidence_id is required")
        for name in ("risk_of_bias", "applicability"):
            value = getattr(self, name)
            if value is not None and not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0,1]")
        if not 0.0 <= self.independence <= 1.0:
            raise ValueError("independence must be in [0,1]")


@dataclass(frozen=True, slots=True)
class EvidenceGateResult:
    disposition: GateDisposition
    epistemic_uncertainty: float
    reasons: tuple[str, ...]
    required_controls: tuple[str, ...]


class ScientificEvidenceGate:
    """Applies evidence controls conditionally on the evidence type and use."""

    _BLOCKED_CLASSES = {EvidenceClass.BLOG, EvidenceClass.COMMERCIAL, EvidenceClass.WIKIPEDIA}

    def evaluate(self, evidence: Sequence[ScientificEvidence]) -> EvidenceGateResult:
        if not evidence:
            return EvidenceGateResult(GateDisposition.ABSTAIN, 1.0, ("no_scientific_evidence_declared",), ("declare_evidence_provenance",))
        reasons: list[str] = []
        controls: list[str] = []
        uncertainty = 0.0
        disposition = GateDisposition.ALLOW
        origins: dict[str, int] = {}

        for item in evidence:
            if item.common_origin_id:
                origins[item.common_origin_id] = origins.get(item.common_origin_id, 0) + 1
            if item.evidence_class in self._BLOCKED_CLASSES:
                reasons.append(f"{item.evidence_id}:inadmissible_source_class")
                uncertainty = max(uncertainty, 1.0)
                disposition = GateDisposition.ABSTAIN
                continue
            if item.evidence_class is EvidenceClass.PREPRINT or not item.peer_reviewed:
                reasons.append(f"{item.evidence_id}:not_peer_reviewed")
                controls.append(f"{item.evidence_id}:independent_review")
                uncertainty = max(uncertainty, 0.60)
                disposition = max_disposition(disposition, GateDisposition.HUMAN_REVIEW)
            if item.evidence_class in {EvidenceClass.GUIDELINE, EvidenceClass.STANDARD} and not item.primary_source_verified:
                reasons.append(f"{item.evidence_id}:primary_source_not_verified")
                controls.append(f"{item.evidence_id}:verify_primary_source")
                uncertainty = max(uncertainty, 0.55)
                disposition = max_disposition(disposition, GateDisposition.HUMAN_REVIEW)

            # External validation and calibration are conditional on actual
            # prediction-model use. A methodological or validation paper can
            # legitimately be evidence about methods without itself being a
            # deployed prediction model.
            if item.prediction_model:
                if item.validation_level in {ValidationLevel.NONE, ValidationLevel.APPARENT, ValidationLevel.INTERNAL}:
                    reasons.append(f"{item.evidence_id}:no_external_validation")
                    controls.append(f"{item.evidence_id}:external_validation")
                    uncertainty = max(uncertainty, 0.65)
                    disposition = max_disposition(disposition, GateDisposition.HUMAN_REVIEW)
                if item.calibrated is False or (item.high_impact and item.calibrated is None):
                    reasons.append(f"{item.evidence_id}:calibration_not_established")
                    controls.append(f"{item.evidence_id}:calibration_assessment")
                    uncertainty = max(uncertainty, 0.70)
                    disposition = max_disposition(disposition, GateDisposition.HUMAN_REVIEW)

            if item.missingness is Missingness.MNAR and not item.missingness_sensitivity:
                reasons.append(f"{item.evidence_id}:mnar_without_sensitivity_analysis")
                controls.append(f"{item.evidence_id}:mnar_sensitivity_analysis")
                uncertainty = max(uncertainty, 0.75)
                disposition = max_disposition(disposition, GateDisposition.HUMAN_REVIEW)
            elif item.missingness is Missingness.UNKNOWN:
                reasons.append(f"{item.evidence_id}:missingness_mechanism_unknown")
                controls.append(f"{item.evidence_id}:assess_mcar_mar_mnar")
                uncertainty = max(uncertainty, 0.70)
                disposition = max_disposition(disposition, GateDisposition.HUMAN_REVIEW)

            if item.high_impact:
                required = (("decision_utility_evaluated", item.decision_utility_evaluated), ("harms_evaluated", item.harms_evaluated), ("human_factors_evaluated", item.human_factors_evaluated))
                for name, satisfied in required:
                    if not satisfied:
                        reasons.append(f"{item.evidence_id}:{name}_missing")
                        controls.append(f"{item.evidence_id}:{name}")
                        uncertainty = max(uncertainty, 0.80)
                        disposition = max_disposition(disposition, GateDisposition.HUMAN_REVIEW)

            if item.certainty in {Certainty.LOW, Certainty.VERY_LOW}:
                uncertainty = max(uncertainty, 0.75)
                reasons.append(f"{item.evidence_id}:low_certainty")
                disposition = max_disposition(disposition, GateDisposition.HUMAN_REVIEW)
            if item.grade is not None:
                if not item.grade.complete:
                    reasons.append(f"{item.evidence_id}:grade_assessment_incomplete")
                    controls.append(f"{item.evidence_id}:complete_grade_domains")
                    uncertainty = max(uncertainty, 0.65)
                    disposition = max_disposition(disposition, GateDisposition.HUMAN_REVIEW)
                if item.grade.certainty in {GradeRating.LOW, GradeRating.VERY_LOW}:
                    uncertainty = max(uncertainty, 0.75)
                    reasons.append(f"{item.evidence_id}:grade_low_certainty")
                    disposition = max_disposition(disposition, GateDisposition.HUMAN_REVIEW)
            if item.risk_of_bias is not None and item.risk_of_bias >= 0.75:
                uncertainty = max(uncertainty, 0.80)
                reasons.append(f"{item.evidence_id}:high_risk_of_bias")
                disposition = max_disposition(disposition, GateDisposition.HUMAN_REVIEW)
            if item.independence < 0.50:
                uncertainty = max(uncertainty, 0.65)
                reasons.append(f"{item.evidence_id}:low_independence")
                controls.append(f"{item.evidence_id}:independent_corroboration")
                disposition = max_disposition(disposition, GateDisposition.HUMAN_REVIEW)

        for origin, count in origins.items():
            if count > 1:
                reasons.append(f"common_origin:{origin}:duplicate_evidence_cluster")
                controls.append(f"common_origin:{origin}:dependency_adjustment")
                uncertainty = max(uncertainty, 0.55)
                disposition = max_disposition(disposition, GateDisposition.HUMAN_REVIEW)
        if uncertainty >= 0.90:
            disposition = GateDisposition.ABSTAIN
        return EvidenceGateResult(disposition, min(1.0, uncertainty), tuple(dict.fromkeys(reasons)), tuple(dict.fromkeys(controls)))


def max_disposition(left: GateDisposition, right: GateDisposition) -> GateDisposition:
    rank = {GateDisposition.ALLOW: 0, GateDisposition.HUMAN_REVIEW: 1, GateDisposition.ABSTAIN: 2}
    return left if rank[left] >= rank[right] else right


__all__ = ["Certainty", "EvidenceClass", "EvidenceGateResult", "GateDisposition", "Missingness", "ScientificEvidence", "ScientificEvidenceGate", "ValidationLevel"]
