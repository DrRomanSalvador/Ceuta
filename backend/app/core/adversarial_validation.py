"""CeutIA — Adversarial Validation Gate
====================================

Sistema de validación adversarial multidisciplinar para CeutIA.

Propósito
---------
Este módulo convierte las seis perspectivas expertas de revisión de CeutIA
en controles ejecutables. Su función no es demostrar que un modelo "funciona",
sino intentar encontrar condiciones bajo las cuales sus resultados dejan de ser
fiables, interpretables, útiles o admisibles.

Los seis dominios de revisión son:

1. Strategic intelligence / OSINT
2. Operational security / emergency management
3. Epidemiology / public health
4. Geospatial / border / population analysis
5. Technology law / privacy / cybersecurity
6. Statistics / ML / predictive validation

Principio rector
---------------
Una capacidad predictiva no se considera operacionalmente válida porque:

- produzca una puntuación;
- tenga una métrica favorable;
- utilice machine learning;
- combine muchas fuentes;
- produzca alertas plausibles;
- o coincida retrospectivamente con algunos acontecimientos.

Debe superar controles independientes sobre:

    provenance
    independence
    corroboration
    contradiction
    temporal validity
    spatial validity
    uncertainty
    calibration
    discrimination
    false positives
    false negatives
    lead time
    utility
    drift
    missingness
    subgroup robustness
    privacy
    security
    human oversight
    reproducibility

Este módulo NO autoriza vigilancia individual ni predicción de peligrosidad
individual o colectiva basada en nacionalidad, origen u otros atributos
protegidos.

La unidad primaria de predicción de seguridad debe ser un fenómeno observable
del sistema, evento, flujo, infraestructura o entorno, no la identidad de una
persona o grupo.

Arquitectura de decisión
------------------------

    candidate
        |
        v
    six-domain validation
        |
        +---- critical failure ----> BLOCK
        |
        +---- major unresolved ----> SHADOW_ONLY
        |
        +---- all mandatory gates ----> PASS
        |
        v
    operational eligibility

"SHADOW_ONLY" significa que el componente puede ejecutarse para evaluación
retrospectiva/prospectiva sin que su salida pueda activar decisiones
operacionales.

Diseño
------
- stdlib only;
- immutable result objects;
- fail-closed;
- deterministic;
- auditable;
- no acceso a bases de datos;
- no acceso a red;
- no ejecución de modelos;
- no inferencia automática de identidad;
- no decisión operativa.

El módulo valida las condiciones bajo las cuales otro componente puede ser
considerado apto para operar.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from math import isfinite
from typing import Final, Mapping, Sequence


class ValidationDecision(str, Enum):
    """Resultado final del gate adversarial."""

    PASS = "pass"
    SHADOW_ONLY = "shadow_only"
    BLOCK = "block"


class FindingSeverity(str, Enum):
    """Severidad de una deficiencia encontrada durante la validación."""

    INFO = "info"
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class ExpertDomain(str, Enum):
    """Los seis dominios expertos que deben poder auditar CeutIA."""

    STRATEGIC_INTELLIGENCE = "strategic_intelligence"
    OPERATIONAL_SECURITY = "operational_security"
    EPIDEMIOLOGY_PUBLIC_HEALTH = "epidemiology_public_health"
    GEOSPATIAL_POPULATION = "geospatial_population"
    LAW_PRIVACY_CYBERSECURITY = "law_privacy_cybersecurity"
    STATISTICS_ML = "statistics_ml"


class ValidationDimension(str, Enum):
    """Dimensiones transversales examinadas por los expertos."""

    PROVENANCE = "provenance"
    SOURCE_INDEPENDENCE = "source_independence"
    CORROBORATION = "corroboration"
    CONTRADICTION = "contradiction"
    TEMPORAL_VALIDITY = "temporal_validity"
    SPATIAL_VALIDITY = "spatial_validity"
    EPISTEMIC_SEPARATION = "epistemic_separation"
    UNCERTAINTY = "uncertainty"
    CALIBRATION = "calibration"
    DISCRIMINATION = "discrimination"
    FALSE_POSITIVES = "false_positives"
    FALSE_NEGATIVES = "false_negatives"
    LEAD_TIME = "lead_time"
    OPERATIONAL_UTILITY = "operational_utility"
    MISSINGNESS = "missingness"
    DRIFT = "drift"
    ROBUSTNESS = "robustness"
    SUBGROUP_ROBUSTNESS = "subgroup_robustness"
    PRIVACY = "privacy"
    SECURITY = "security"
    HUMAN_OVERSIGHT = "human_oversight"
    REPRODUCIBILITY = "reproducibility"
    IDENTITY_INFERENCE = "identity_inference"
    AUTOMATED_ACTION = "automated_action"


class TargetLevel(str, Enum):
    """
    Unidad sobre la que opera la capacidad evaluada.

    SYSTEM:
        territorio, infraestructura, capacidad, flujo o sistema.

    EVENT:
        acontecimiento observable.

    POPULATION:
        agregado poblacional.

    INDIVIDUAL:
        persona identificable o potencialmente identificable.

    GROUP:
        colectivo definido por identidad/procedencia/atributos.

    CeutIA puede analizar sistemas, eventos y agregados.
    La predicción de peligrosidad individual/grupal requiere un gate
    explícito y queda bloqueada por defecto.
    """

    SYSTEM = "system"
    EVENT = "event"
    POPULATION = "population"
    INDIVIDUAL = "individual"
    GROUP = "group"


class EvidenceMaturity(str, Enum):
    """Madurez de la evidencia que sustenta una capacidad."""

    UNASSESSED = "unassessed"
    EXPLORATORY = "exploratory"
    RETROSPECTIVELY_VALIDATED = "retrospectively_validated"
    TEMPORALLY_VALIDATED = "temporally_validated"
    EXTERNALLY_VALIDATED = "externally_validated"
    PROSPECTIVELY_VALIDATED = "prospectively_validated"


class DataUseMode(str, Enum):
    """Modo de utilización de datos."""

    PUBLIC = "public"
    INTERNAL = "internal"
    PRIVATE = "private"
    RESTRICTED = "restricted"


class FindingCode(str, Enum):
    """Códigos normalizados para problemas detectados."""

    MISSING_PROVENANCE = "missing_provenance"
    DEPENDENT_SOURCES = "dependent_sources"
    INSUFFICIENT_CORROBORATION = "insufficient_corroboration"
    UNRESOLVED_CONTRADICTION = "unresolved_contradiction"
    NO_TEMPORAL_VALIDATION = "no_temporal_validation"
    NO_SPATIAL_VALIDATION = "no_spatial_validation"
    EPISTEMIC_COLLAPSE = "epistemic_collapse"
    UNCERTAINTY_MISSING = "uncertainty_missing"
    UNCALIbrATED_PROBABILITY = "uncalibrated_probability"
    DISCRIMINATION_UNASSESSED = "discrimination_unassessed"
    FALSE_POSITIVE_COST_UNKNOWN = "false_positive_cost_unknown"
    FALSE_NEGATIVE_COST_UNKNOWN = "false_negative_cost_unknown"
    LEAD_TIME_UNKNOWN = "lead_time_unknown"
    UTILITY_UNASSESSED = "utility_unassessed"
    MISSINGNESS_UNASSESSED = "missingness_unassessed"
    DRIFT_UNASSESSED = "drift_unassessed"
    ROBUSTNESS_UNASSESSED = "robustness_unassessed"
    SUBGROUP_ROBUSTNESS_UNASSESSED = "subgroup_robustness_unassessed"
    PRIVACY_VIOLATION = "privacy_violation"
    SECURITY_VIOLATION = "security_violation"
    HUMAN_OVERSIGHT_MISSING = "human_oversight_missing"
    REPRODUCIBILITY_MISSING = "reproducibility_missing"
    IDENTITY_BASED_INFERENCE = "identity_based_inference"
    AUTOMATED_OPERATIONAL_ACTION = "automated_operational_action"
    INDIVIDUAL_DANGEROUSNESS = "individual_dangerousness"
    GROUP_DANGEROUSNESS = "group_dangerousness"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    INVALID_TARGET = "invalid_target"
    INVALID_THRESHOLD = "invalid_threshold"
    OUTCOME_UNDEFINED = "outcome_undefined"
    HORIZON_UNDEFINED = "horizon_undefined"


@dataclass(frozen=True, slots=True)
class ValidationFinding:
    """Hallazgo individual producido por un gate."""

    code: FindingCode
    severity: FindingSeverity
    domain: ExpertDomain
    dimension: ValidationDimension
    message: str
    evidence: tuple[str, ...] = ()
    remediation: str | None = None


@dataclass(frozen=True, slots=True)
class ExpertGateResult:
    """Resultado de un dominio experto."""

    domain: ExpertDomain
    passed: bool
    findings: tuple[ValidationFinding, ...] = ()

    @property
    def critical_count(self) -> int:
        return sum(
            finding.severity is FindingSeverity.CRITICAL
            for finding in self.findings
        )

    @property
    def major_count(self) -> int:
        return sum(
            finding.severity is FindingSeverity.MAJOR
            for finding in self.findings
        )


@dataclass(frozen=True, slots=True)
class ValidationDataset:
    """
    Describe el conjunto utilizado para validar una capacidad.

    No contiene los datos. Solo registra las propiedades necesarias para
    determinar si el proceso de validación es suficientemente fuerte.
    """

    dataset_id: str
    sample_size: int
    positive_events: int
    negative_events: int
    temporal_split: bool
    external_dataset: bool
    prospective_evaluation: bool
    independent_test_set: bool
    missingness_assessed: bool
    subgroup_evaluation: bool
    drift_assessed: bool

    def validate(self) -> tuple[str, ...]:
        errors: list[str] = []

        if not self.dataset_id.strip():
            errors.append("dataset_id must not be empty")

        if self.sample_size <= 0:
            errors.append("sample_size must be positive")

        if self.positive_events < 0 or self.negative_events < 0:
            errors.append("event counts must not be negative")

        if self.positive_events + self.negative_events > self.sample_size:
            errors.append("event counts cannot exceed sample_size")

        return tuple(errors)


@dataclass(frozen=True, slots=True)
class PredictivePerformance:
    """
    Rendimiento predictivo observado.

    Los campos son opcionales porque no todos los modelos necesitan todas
    las métricas. Sin embargo, los gates correspondientes exigirán las que
    sean necesarias para el tipo de capacidad evaluada.
    """

    roc_auc: float | None = None
    pr_auc: float | None = None
    brier_score: float | None = None
    calibration_in_the_large: float | None = None
    calibration_slope: float | None = None
    sensitivity: float | None = None
    specificity: float | None = None
    false_positive_rate: float | None = None
    false_negative_rate: float | None = None
    decision_curve_net_benefit: float | None = None
    lead_time_minutes: float | None = None

    def validate_ranges(self) -> tuple[str, ...]:
        errors: list[str] = []

        bounded = {
            "roc_auc": self.roc_auc,
            "pr_auc": self.pr_auc,
            "brier_score": self.brier_score,
            "sensitivity": self.sensitivity,
            "specificity": self.specificity,
            "false_positive_rate": self.false_positive_rate,
            "false_negative_rate": self.false_negative_rate,
        }

        for name, value in bounded.items():
            if value is None:
                continue

            if not isfinite(value):
                errors.append(f"{name} must be finite")

            if not 0.0 <= value <= 1.0:
                errors.append(f"{name} must be between 0 and 1")

        if self.calibration_slope is not None and not isfinite(
            self.calibration_slope
        ):
            errors.append("calibration_slope must be finite")

        if self.calibration_in_the_large is not None and not isfinite(
            self.calibration_in_the_large
        ):
            errors.append("calibration_in_the_large must be finite")

        if self.decision_curve_net_benefit is not None and not isfinite(
            self.decision_curve_net_benefit
        ):
            errors.append("decision_curve_net_benefit must be finite")

        if self.lead_time_minutes is not None:
            if not isfinite(self.lead_time_minutes):
                errors.append("lead_time_minutes must be finite")
            elif self.lead_time_minutes < 0:
                errors.append("lead_time_minutes must not be negative")

        return tuple(errors)


@dataclass(frozen=True, slots=True)
class CandidateCapability:
    """
    Especificación de una capacidad que quiere pasar a producción.

    Esta estructura describe el objeto que será atacado por los seis gates.
    """

    capability_id: str
    name: str
    target_level: TargetLevel
    data_mode: DataUseMode
    evidence_maturity: EvidenceMaturity

    scientific_references: tuple[str, ...] = ()
    provenance_complete: bool = False
    source_independence_assessed: bool = False
    corroboration_assessed: bool = False
    contradiction_handling: bool = False

    temporal_validation: bool = False
    spatial_validation: bool = False
    uncertainty_quantified: bool = False
    epistemic_separation: bool = False

    produces_probability: bool = False
    calibration_assessed: bool = False
    discrimination_assessed: bool = False
    false_positive_cost_assessed: bool = False
    false_negative_cost_assessed: bool = False
    lead_time_assessed: bool = False
    operational_utility_assessed: bool = False

    missingness_assessed: bool = False
    drift_assessed: bool = False
    robustness_assessed: bool = False
    subgroup_robustness_assessed: bool = False

    privacy_reviewed: bool = False
    cybersecurity_reviewed: bool = False
    human_oversight_required: bool = True
    human_oversight_implemented: bool = False
    reproducibility_verified: bool = False

    uses_identity_attributes: bool = False
    predicts_individual_dangerousness: bool = False
    predicts_group_dangerousness: bool = False
    automated_operational_action: bool = False

    event_definition: str | None = None
    prediction_horizon_minutes: float | None = None
    threshold_definition: str | None = None

    validation_dataset: ValidationDataset | None = None
    performance: PredictivePerformance | None = None

    metadata: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class AdversarialValidationReport:
    """Informe completo producido por el proceso adversarial."""

    capability_id: str
    decision: ValidationDecision
    generated_at: datetime

    expert_results: tuple[ExpertGateResult, ...]
    findings: tuple[ValidationFinding, ...]

    mandatory_failures: tuple[FindingCode, ...]
    unresolved_major_failures: tuple[FindingCode, ...]

    @property
    def passed(self) -> bool:
        return self.decision is ValidationDecision.PASS

    @property
    def blocked(self) -> bool:
        return self.decision is ValidationDecision.BLOCK

    @property
    def shadow_only(self) -> bool:
        return self.decision is ValidationDecision.SHADOW_ONLY


# ---------------------------------------------------------------------------
# Common helpers
# ---------------------------------------------------------------------------


def _finding(
    code: FindingCode,
    severity: FindingSeverity,
    domain: ExpertDomain,
    dimension: ValidationDimension,
    message: str,
    *,
    evidence: Sequence[str] = (),
    remediation: str | None = None,
) -> ValidationFinding:
    return ValidationFinding(
        code=code,
        severity=severity,
        domain=domain,
        dimension=dimension,
        message=message,
        evidence=tuple(evidence),
        remediation=remediation,
    )


def _missing(
    condition: bool,
    *,
    code: FindingCode,
    severity: FindingSeverity,
    domain: ExpertDomain,
    dimension: ValidationDimension,
    message: str,
    remediation: str,
) -> ValidationFinding | None:
    if condition:
        return None

    return _finding(
        code,
        severity,
        domain,
        dimension,
        message,
        remediation=remediation,
    )


def _validate_dataset(
    candidate: CandidateCapability,
    domain: ExpertDomain,
) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []

    dataset = candidate.validation_dataset

    if dataset is None:
        findings.append(
            _finding(
                FindingCode.INSUFFICIENT_EVIDENCE,
                FindingSeverity.MAJOR,
                domain,
                ValidationDimension.REPRODUCIBILITY,
                "No validation dataset has been declared.",
                remediation=(
                    "Declare the dataset, event counts, temporal split and "
                    "validation strategy."
                ),
            )
        )
        return findings

    for error in dataset.validate():
        findings.append(
            _finding(
                FindingCode.INSUFFICIENT_EVIDENCE,
                FindingSeverity.CRITICAL,
                domain,
                ValidationDimension.REPRODUCIBILITY,
                error,
            )
        )

    return findings


# ---------------------------------------------------------------------------
# Gate 1 — Strategic intelligence / OSINT
# ---------------------------------------------------------------------------


def validate_strategic_intelligence(
    candidate: CandidateCapability,
) -> ExpertGateResult:
    """
    Evalúa si una capacidad puede distinguir información de señal.

    Particular atención a:

    - ruido digital;
    - dependencia entre fuentes;
    - corroboración;
    - contradicciones;
    - temporalidad;
    - desinformación;
    - señales débiles;
    - separación entre existencia de contenido y verdad de su afirmación.
    """

    domain = ExpertDomain.STRATEGIC_INTELLIGENCE
    findings: list[ValidationFinding] = []

    required = (
        (
            candidate.provenance_complete,
            FindingCode.MISSING_PROVENANCE,
            ValidationDimension.PROVENANCE,
            "Source provenance is incomplete.",
            "Register source, acquisition time, transformation lineage and integrity.",
        ),
        (
            candidate.source_independence_assessed,
            FindingCode.DEPENDENT_SOURCES,
            ValidationDimension.SOURCE_INDEPENDENCE,
            "Source independence has not been assessed.",
            "Assess common-origin, syndication and coordinated-source dependency.",
        ),
        (
            candidate.corroboration_assessed,
            FindingCode.INSUFFICIENT_CORROBORATION,
            ValidationDimension.CORROBORATION,
            "Corroboration has not been assessed.",
            "Evaluate independent corroboration rather than source count.",
        ),
        (
            candidate.contradiction_handling,
            FindingCode.UNRESOLVED_CONTRADICTION,
            ValidationDimension.CONTRADICTION,
            "Contradictory observations are not explicitly represented.",
            "Preserve contradictions and expose their effect on confidence.",
        ),
        (
            candidate.temporal_validation,
            FindingCode.NO_TEMPORAL_VALIDATION,
            ValidationDimension.TEMPORAL_VALIDITY,
            "Temporal validity has not been demonstrated.",
            "Evaluate performance on future periods not used for model fitting.",
        ),
        (
            candidate.epistemic_separation,
            FindingCode.EPISTEMIC_COLLAPSE,
            ValidationDimension.EPISTEMIC_SEPARATION,
            "Epistemic states are not explicitly separated.",
            "Separate observation, signal, inference, hypothesis, prediction and scenario.",
        ),
    )

    for (
        condition,
        code,
        dimension,
        message,
        remediation,
    ) in required:
        result = _missing(
            condition,
            code=code,
            severity=FindingSeverity.MAJOR,
            domain=domain,
            dimension=dimension,
            message=message,
            remediation=remediation,
        )
        if result is not None:
            findings.append(result)

    if candidate.uses_identity_attributes:
        findings.append(
            _finding(
                FindingCode.IDENTITY_BASED_INFERENCE,
                FindingSeverity.CRITICAL,
                domain,
                ValidationDimension.IDENTITY_INFERENCE,
                "Identity attributes are used as predictive risk features.",
                remediation=(
                    "Replace identity-based predictors with validated "
                    "observable system/event variables and document the causal "
                    "or predictive justification."
                ),
            )
        )

    return ExpertGateResult(
        domain=domain,
        passed=not any(
            finding.severity in {
                FindingSeverity.MAJOR,
                FindingSeverity.CRITICAL,
            }
            for finding in findings
        ),
        findings=tuple(findings),
    )


# ---------------------------------------------------------------------------
# Gate 2 — Operational security / emergency management
# ---------------------------------------------------------------------------


def validate_operational_security(
    candidate: CandidateCapability,
) -> ExpertGateResult:
    """
    Evalúa utilidad operacional y coste de error.

    Una alerta sin horizonte temporal, sin outcome definido o sin evaluación
    de falsos positivos/falsos negativos no se considera operacionalmente
    madura.
    """

    domain = ExpertDomain.OPERATIONAL_SECURITY
    findings: list[ValidationFinding] = []

    if not candidate.event_definition:
        findings.append(
            _finding(
                FindingCode.OUTCOME_UNDEFINED,
                FindingSeverity.MAJOR,
                domain,
                ValidationDimension.OPERATIONAL_UTILITY,
                "The predicted outcome/event is not explicitly defined.",
                remediation=(
                    "Define an observable outcome with objective inclusion "
                    "and exclusion criteria."
                ),
            )
        )

    if (
        candidate.prediction_horizon_minutes is None
        or candidate.prediction_horizon_minutes <= 0
    ):
        findings.append(
            _finding(
                FindingCode.HORIZON_UNDEFINED,
                FindingSeverity.MAJOR,
                domain,
                ValidationDimension.LEAD_TIME,
                "The prediction horizon is undefined or invalid.",
                remediation=(
                    "Declare the prediction horizon and evaluate warning "
                    "lead time against the actual event."
                ),
            )
        )

    required = (
        (
            candidate.false_positive_cost_assessed,
            FindingCode.FALSE_POSITIVE_COST_UNKNOWN,
            ValidationDimension.FALSE_POSITIVES,
            "False-positive consequences have not been assessed.",
            "Quantify alert burden and operational cost of false alarms.",
        ),
        (
            candidate.false_negative_cost_assessed,
            FindingCode.FALSE_NEGATIVE_COST_UNKNOWN,
            ValidationDimension.FALSE_NEGATIVES,
            "False-negative consequences have not been assessed.",
            "Quantify missed-event consequences and asymmetry of error costs.",
        ),
        (
            candidate.lead_time_assessed,
            FindingCode.LEAD_TIME_UNKNOWN,
            ValidationDimension.LEAD_TIME,
            "Actual warning lead time has not been evaluated.",
            "Measure the distribution of warning time before observed outcomes.",
        ),
        (
            candidate.operational_utility_assessed,
            FindingCode.UTILITY_UNASSESSED,
            ValidationDimension.OPERATIONAL_UTILITY,
            "Operational utility has not been evaluated.",
            "Evaluate whether alerts change decisions or improve outcomes.",
        ),
        (
            candidate.human_oversight_implemented,
            FindingCode.HUMAN_OVERSIGHT_MISSING,
            ValidationDimension.HUMAN_OVERSIGHT,
            "Required human oversight is not implemented.",
            "Route operational decisions through an authorized human reviewer.",
        ),
    )

    for (
        condition,
        code,
        dimension,
        message,
        remediation,
    ) in required:
        result = _missing(
            condition,
            code=code,
            severity=FindingSeverity.MAJOR,
            domain=domain,
            dimension=dimension,
            message=message,
            remediation=remediation,
        )
        if result is not None:
            findings.append(result)

    if candidate.automated_operational_action:
        findings.append(
            _finding(
                FindingCode.AUTOMATED_OPERATIONAL_ACTION,
                FindingSeverity.CRITICAL,
                domain,
                ValidationDimension.AUTOMATED_ACTION,
                "The capability can directly trigger an operational action.",
                remediation=(
                    "Separate detection and recommendation from the human "
                    "decision and action layer."
                ),
            )
        )

    return ExpertGateResult(
        domain=domain,
        passed=not any(
            finding.severity in {
                FindingSeverity.MAJOR,
                FindingSeverity.CRITICAL,
            }
            for finding in findings
        ),
        findings=tuple(findings),
    )


# ---------------------------------------------------------------------------
# Gate 3 — Epidemiology / public health
# ---------------------------------------------------------------------------


def validate_epidemiology(
    candidate: CandidateCapability,
) -> ExpertGateResult:
    """
    Evalúa validez epidemiológica y sanitaria.

    El gate obliga a diferenciar:

    - casos;
    - tasas;
    - prevalencia;
    - incidencia;
    - flujos;
    - capacidad;
    - ocupación;
    - carga acumulada;
    - y eventos extremos.

    También exige control temporal y de missingness.
    """

    domain = ExpertDomain.EPIDEMIOLOGY_PUBLIC_HEALTH
    findings: list[ValidationFinding] = []

    required = (
        (
            candidate.temporal_validation,
            FindingCode.NO_TEMPORAL_VALIDATION,
            ValidationDimension.TEMPORAL_VALIDITY,
            "Health/system performance has not been temporally validated.",
            "Use temporal holdout evaluation and preserve chronological ordering.",
        ),
        (
            candidate.uncertainty_quantified,
            FindingCode.UNCERTAINTY_MISSING,
            ValidationDimension.UNCERTAINTY,
            "Health risk output lacks quantified uncertainty.",
            "Propagate measurement, sampling and model uncertainty.",
        ),
        (
            candidate.missingness_assessed,
            FindingCode.MISSINGNESS_UNASSESSED,
            ValidationDimension.MISSINGNESS,
            "Missing-data mechanisms have not been assessed.",
            "Evaluate MCAR/MAR/MNAR plausibility and sensitivity to missingness.",
        ),
        (
            candidate.robustness_assessed,
            FindingCode.ROBUSTNESS_UNASSESSED,
            ValidationDimension.ROBUSTNESS,
            "Robustness has not been evaluated.",
            "Test alternative plausible specifications and perturbations.",
        ),
    )

    for (
        condition,
        code,
        dimension,
        message,
        remediation,
    ) in required:
        result = _missing(
            condition,
            code=code,
            severity=FindingSeverity.MAJOR,
            domain=domain,
            dimension=dimension,
            message=message,
            remediation=remediation,
        )
        if result is not None:
            findings.append(result)

    if candidate.validation_dataset is not None:
        if candidate.validation_dataset.positive_events == 0:
            findings.append(
                _finding(
                    FindingCode.INSUFFICIENT_EVIDENCE,
                    FindingSeverity.MAJOR,
                    domain,
                    ValidationDimension.ROBUSTNESS,
                    "The validation dataset contains no positive outcomes.",
                    remediation=(
                        "Obtain an evaluation period containing observed "
                        "events before claiming predictive performance."
                    ),
                )
            )

    return ExpertGateResult(
        domain=domain,
        passed=not any(
            finding.severity in {
                FindingSeverity.MAJOR,
                FindingSeverity.CRITICAL,
            }
            for finding in findings
        ),
        findings=tuple(findings),
    )


# ---------------------------------------------------------------------------
# Gate 4 — Geospatial / border / population
# ---------------------------------------------------------------------------


def validate_geospatial(
    candidate: CandidateCapability,
) -> ExpertGateResult:
    """
    Evalúa la dimensión espacial.

    El objetivo es impedir que un resultado agregado se interprete como si
    tuviera validez individual o que un modelo espacial se despliegue fuera
    de la escala para la que fue validado.
    """

    domain = ExpertDomain.GEOSPATIAL_POPULATION
    findings: list[ValidationFinding] = []

    result = _missing(
        candidate.spatial_validation,
        code=FindingCode.NO_SPATIAL_VALIDATION,
        severity=FindingSeverity.MAJOR,
        domain=domain,
        dimension=ValidationDimension.SPATIAL_VALIDITY,
        message="Spatial validity has not been demonstrated.",
        remediation=(
            "Validate the model at the spatial resolution and aggregation "
            "level at which it will actually be used."
        ),
    )

    if result is not None:
        findings.append(result)

    if candidate.target_level is TargetLevel.INDIVIDUAL:
        findings.append(
            _finding(
                FindingCode.INVALID_TARGET,
                FindingSeverity.MAJOR,
                domain,
                ValidationDimension.SPATIAL_VALIDITY,
                "Individual targeting is outside the default system-level "
                "geospatial monitoring scope.",
                remediation=(
                    "Use system/event/population aggregates and apply a "
                    "separate legal and privacy authorization for any "
                    "individual-level processing."
                ),
            )
        )

    if candidate.target_level is TargetLevel.GROUP:
        if candidate.predicts_group_dangerousness:
            findings.append(
                _finding(
                    FindingCode.GROUP_DANGEROUSNESS,
                    FindingSeverity.CRITICAL,
                    domain,
                    ValidationDimension.IDENTITY_INFERENCE,
                    "The capability predicts dangerousness of a group.",
                    remediation=(
                        "Reformulate the target as an observable event, "
                        "system state or environmental condition."
                    ),
                )
            )

    return ExpertGateResult(
        domain=domain,
        passed=not any(
            finding.severity in {
                FindingSeverity.MAJOR,
                FindingSeverity.CRITICAL,
            }
            for finding in findings
        ),
        findings=tuple(findings),
    )


# ---------------------------------------------------------------------------
# Gate 5 — Law / privacy / cybersecurity
# ---------------------------------------------------------------------------


def validate_law_privacy_cybersecurity(
    candidate: CandidateCapability,
) -> ExpertGateResult:
    """
    Evalúa las barreras de información.

    El gate no sustituye una evaluación jurídica profesional. Comprueba que
    las condiciones técnicas mínimas para una revisión jurídica existan y que
    ciertas arquitecturas intrínsecamente incompatibles con el diseño seguro
    de CeutIA sean bloqueadas.
    """

    domain = ExpertDomain.LAW_PRIVACY_CYBERSECURITY
    findings: list[ValidationFinding] = []

    required = (
        (
            candidate.privacy_reviewed,
            FindingCode.PRIVACY_VIOLATION,
            ValidationDimension.PRIVACY,
            "Privacy review has not been completed.",
            "Document data minimization, purpose limitation, retention and access controls.",
        ),
        (
            candidate.cybersecurity_reviewed,
            FindingCode.SECURITY_VIOLATION,
            ValidationDimension.SECURITY,
            "Cybersecurity review has not been completed.",
            "Review authentication, authorization, secrets, isolation, auditability and attack surface.",
        ),
        (
            candidate.reproducibility_verified,
            FindingCode.REPRODUCIBILITY_MISSING,
            ValidationDimension.REPRODUCIBILITY,
            "Reproducibility has not been verified.",
            "Record versions, parameters, data lineage and execution configuration.",
        ),
    )

    for (
        condition,
        code,
        dimension,
        message,
        remediation,
    ) in required:
        result = _missing(
            condition,
            code=code,
            severity=FindingSeverity.MAJOR,
            domain=domain,
            dimension=dimension,
            message=message,
            remediation=remediation,
        )
        if result is not None:
            findings.append(result)

    if candidate.uses_identity_attributes:
        findings.append(
            _finding(
                FindingCode.IDENTITY_BASED_INFERENCE,
                FindingSeverity.CRITICAL,
                domain,
                ValidationDimension.IDENTITY_INFERENCE,
                "Identity attributes are used as predictive risk variables.",
                remediation=(
                    "Remove identity-based risk inference and substitute "
                    "validated observable system variables."
                ),
            )
        )

    if candidate.predicts_individual_dangerousness:
        findings.append(
            _finding(
                FindingCode.INDIVIDUAL_DANGEROUSNESS,
                FindingSeverity.CRITICAL,
                domain,
                ValidationDimension.IDENTITY_INFERENCE,
                "The capability predicts individual dangerousness.",
                remediation=(
                    "Target observable events or system states instead of "
                    "inherent dangerousness of a person."
                ),
            )
        )

    if candidate.predicts_group_dangerousness:
        findings.append(
            _finding(
                FindingCode.GROUP_DANGEROUSNESS,
                FindingSeverity.CRITICAL,
                domain,
                ValidationDimension.IDENTITY_INFERENCE,
                "The capability predicts group dangerousness.",
                remediation=(
                    "Replace group-dangerousness prediction with "
                    "event/system-level monitoring."
                ),
            )
        )

    if candidate.automated_operational_action:
        findings.append(
            _finding(
                FindingCode.AUTOMATED_OPERATIONAL_ACTION,
                FindingSeverity.CRITICAL,
                domain,
                ValidationDimension.AUTOMATED_ACTION,
                "Automated operational action is connected directly to the capability.",
                remediation=(
                    "Require explicit human review and separate the alert "
                    "layer from the action layer."
                ),
            )
        )

    return ExpertGateResult(
        domain=domain,
        passed=not any(
            finding.severity in {
                FindingSeverity.MAJOR,
                FindingSeverity.CRITICAL,
            }
            for finding in findings
        ),
        findings=tuple(findings),
    )


# ---------------------------------------------------------------------------
# Gate 6 — Statistics / ML / predictive validation
# ---------------------------------------------------------------------------


def validate_statistics_ml(
    candidate: CandidateCapability,
) -> ExpertGateResult:
    """
    Evalúa la validez estadística y predictiva.

    Especial atención a:

    - calibration;
    - discrimination;
    - temporal/external validation;
    - rare-event behaviour;
    - uncertainty;
    - missingness;
    - drift;
    - subgroup robustness;
    - operational thresholding.
    """

    domain = ExpertDomain.STATISTICS_ML
    findings: list[ValidationFinding] = []

    if candidate.produces_probability and not candidate.calibration_assessed:
        findings.append(
            _finding(
                FindingCode.UNCALIbrATED_PROBABILITY,
                FindingSeverity.CRITICAL,
                domain,
                ValidationDimension.CALIBRATION,
                "A probability is produced without demonstrated calibration.",
                remediation=(
                    "Evaluate calibration-in-the-large, calibration slope "
                    "and reliability on data not used for fitting."
                ),
            )
        )

    if candidate.produces_probability and not candidate.discrimination_assessed:
        findings.append(
            _finding(
                FindingCode.DISCRIMINATION_UNASSESSED,
                FindingSeverity.MAJOR,
                domain,
                ValidationDimension.DISCRIMINATION,
                "Predictive discrimination has not been evaluated.",
                remediation=(
                    "Evaluate discrimination using metrics appropriate to "
                    "the event prevalence and decision problem."
                ),
            )
        )

    required = (
        (
            candidate.temporal_validation,
            FindingCode.NO_TEMPORAL_VALIDATION,
            ValidationDimension.TEMPORAL_VALIDITY,
            "Temporal validation is missing.",
            "Perform chronological out-of-sample evaluation.",
        ),
        (
            candidate.uncertainty_quantified,
            FindingCode.UNCERTAINTY_MISSING,
            ValidationDimension.UNCERTAINTY,
            "Predictive uncertainty is missing.",
            "Quantify and propagate uncertainty through the prediction pipeline.",
        ),
        (
            candidate.drift_assessed,
            FindingCode.DRIFT_UNASSESSED,
            ValidationDimension.DRIFT,
            "Distribution/model drift has not been assessed.",
            "Monitor covariate, concept and performance drift.",
        ),
        (
            candidate.robustness_assessed,
            FindingCode.ROBUSTNESS_UNASSESSED,
            ValidationDimension.ROBUSTNESS,
            "Robustness has not been assessed.",
            "Run sensitivity and perturbation analyses.",
        ),
        (
            candidate.subgroup_robustness_assessed,
            FindingCode.SUBGROUP_ROBUSTNESS_UNASSESSED,
            ValidationDimension.SUBGROUP_ROBUSTNESS,
            "Subgroup robustness has not been assessed.",
            "Evaluate performance heterogeneity where legally and scientifically appropriate.",
        ),
    )

    for (
        condition,
        code,
        dimension,
        message,
        remediation,
    ) in required:
        result = _missing(
            condition,
            code=code,
            severity=FindingSeverity.MAJOR,
            domain=domain,
            dimension=dimension,
            message=message,
            remediation=remediation,
        )
        if result is not None:
            findings.append(result)

    findings.extend(_validate_dataset(candidate, domain))

    if candidate.performance is not None:
        findings.extend(
            _performance_findings(
                candidate.performance,
                domain,
            )
        )

    return ExpertGateResult(
        domain=domain,
        passed=not any(
            finding.severity in {
                FindingSeverity.MAJOR,
                FindingSeverity.CRITICAL,
            }
            for finding in findings
        ),
        findings=tuple(findings),
    )


def _performance_findings(
    performance: PredictivePerformance,
    domain: ExpertDomain,
) -> list[ValidationFinding]:
    findings: list[ValidationFinding] = []

    for error in performance.validate_ranges():
        findings.append(
            _finding(
                FindingCode.INSUFFICIENT_EVIDENCE,
                FindingSeverity.CRITICAL,
                domain,
                ValidationDimension.ROBUSTNESS,
                error,
            )
        )

    return findings


# ---------------------------------------------------------------------------
# Cross-domain invariants
# ---------------------------------------------------------------------------


def validate_target_safety(
    candidate: CandidateCapability,
) -> tuple[ValidationFinding, ...]:
    """Aplica restricciones que ningún dominio puede sobrescribir."""

    findings: list[ValidationFinding] = []

    if candidate.predicts_individual_dangerousness:
        findings.append(
            _finding(
                FindingCode.INDIVIDUAL_DANGEROUSNESS,
                FindingSeverity.CRITICAL,
                ExpertDomain.LAW_PRIVACY_CYBERSECURITY,
                ValidationDimension.IDENTITY_INFERENCE,
                "Individual dangerousness prediction is prohibited by the "
                "CeutIA system-level monitoring boundary.",
            )
        )

    if candidate.predicts_group_dangerousness:
        findings.append(
            _finding(
                FindingCode.GROUP_DANGEROUSNESS,
                FindingSeverity.CRITICAL,
                ExpertDomain.STRATEGIC_INTELLIGENCE,
                ValidationDimension.IDENTITY_INFERENCE,
                "Group dangerousness prediction is prohibited.",
            )
        )

    if candidate.uses_identity_attributes:
        findings.append(
            _finding(
                FindingCode.IDENTITY_BASED_INFERENCE,
                FindingSeverity.CRITICAL,
                ExpertDomain.LAW_PRIVACY_CYBERSECURITY,
                ValidationDimension.IDENTITY_INFERENCE,
                "Identity-based predictive inference is prohibited.",
            )
        )

    if candidate.automated_operational_action:
        findings.append(
            _finding(
                FindingCode.AUTOMATED_OPERATIONAL_ACTION,
                FindingSeverity.CRITICAL,
                ExpertDomain.OPERATIONAL_SECURITY,
                ValidationDimension.AUTOMATED_ACTION,
                "Direct automated operational action is prohibited.",
            )
        )

    return tuple(findings)


def validate_evidence_maturity(
    candidate: CandidateCapability,
) -> tuple[ValidationFinding, ...]:
    """Comprueba que la madurez declarada sea coherente con la evidencia."""

    findings: list[ValidationFinding] = []

    if not candidate.scientific_references:
        findings.append(
            _finding(
                FindingCode.INSUFFICIENT_EVIDENCE,
                FindingSeverity.MAJOR,
                ExpertDomain.STATISTICS_ML,
                ValidationDimension.REPRODUCIBILITY,
                "No scientific or methodological references are declared.",
                remediation=(
                    "Attach the scientific/methodological basis for the "
                    "specific metric or model."
                ),
            )
        )

    if candidate.evidence_maturity in {
        EvidenceMaturity.TEMPORALLY_VALIDATED,
        EvidenceMaturity.EXTERNALLY_VALIDATED,
        EvidenceMaturity.PROSPECTIVELY_VALIDATED,
    } and not candidate.temporal_validation:
        findings.append(
            _finding(
                FindingCode.NO_TEMPORAL_VALIDATION,
                (
                    FindingSeverity.CRITICAL
                    if candidate.evidence_maturity
                    in {
                        EvidenceMaturity.TEMPORALLY_VALIDATED,
                        EvidenceMaturity.EXTERNALLY_VALIDATED,
                    }
                    else FindingSeverity.MAJOR
                ),
                ExpertDomain.STATISTICS_ML,
                ValidationDimension.TEMPORAL_VALIDITY,
                "Declared evidence maturity exceeds the demonstrated validation.",
            )
        )

    if candidate.evidence_maturity is EvidenceMaturity.EXTERNALLY_VALIDATED:
        dataset = candidate.validation_dataset
        if dataset is None or not dataset.external_dataset:
            findings.append(
                _finding(
                    FindingCode.INSUFFICIENT_EVIDENCE,
                    FindingSeverity.CRITICAL,
                    ExpertDomain.STATISTICS_ML,
                    ValidationDimension.ROBUSTNESS,
                    "External validation is declared without an external dataset.",
                )
            )

    if candidate.evidence_maturity is EvidenceMaturity.PROSPECTIVELY_VALIDATED:
        dataset = candidate.validation_dataset
        if dataset is None or not dataset.prospective_evaluation:
            findings.append(
                _finding(
                    FindingCode.INSUFFICIENT_EVIDENCE,
                    (
                        FindingSeverity.MAJOR
                        if dataset is None
                        else FindingSeverity.CRITICAL
                    ),
                    ExpertDomain.STATISTICS_ML,
                    ValidationDimension.TEMPORAL_VALIDITY,
                    "Prospective validation is declared without prospective evaluation.",
                )
            )

    return tuple(findings)


# ---------------------------------------------------------------------------
# Global adversarial validator
# ---------------------------------------------------------------------------


EXPERT_GATES: Final[tuple[ExpertDomain, ...]] = (
    ExpertDomain.STRATEGIC_INTELLIGENCE,
    ExpertDomain.OPERATIONAL_SECURITY,
    ExpertDomain.EPIDEMIOLOGY_PUBLIC_HEALTH,
    ExpertDomain.GEOSPATIAL_POPULATION,
    ExpertDomain.LAW_PRIVACY_CYBERSECURITY,
    ExpertDomain.STATISTICS_ML,
)


def run_adversarial_validation(
    candidate: CandidateCapability,
    *,
    now: datetime | None = None,
) -> AdversarialValidationReport:
    """
    Ejecuta los seis gates y determina elegibilidad operacional.

    Regla de decisión:

    CRITICAL
        => BLOCK

    MAJOR unresolved
        => SHADOW_ONLY

    Sin MAJOR/CRITICAL
        => PASS

    Los hallazgos INFO/MINOR no bloquean por sí mismos.

    El resultado es deliberadamente fail-closed.
    """

    timestamp = now or datetime.now().astimezone()

    expert_results = (
        validate_strategic_intelligence(candidate),
        validate_operational_security(candidate),
        validate_epidemiology(candidate),
        validate_geospatial(candidate),
        validate_law_privacy_cybersecurity(candidate),
        validate_statistics_ml(candidate),
    )

    cross_domain_findings = (
        *validate_target_safety(candidate),
        *validate_evidence_maturity(candidate),
    )

    all_findings = tuple(
        finding
        for result in expert_results
        for finding in result.findings
    ) + tuple(cross_domain_findings)

    critical = tuple(
        finding.code
        for finding in all_findings
        if finding.severity is FindingSeverity.CRITICAL
    )

    major = tuple(
        finding.code
        for finding in all_findings
        if finding.severity is FindingSeverity.MAJOR
    )

    if critical:
        decision = ValidationDecision.BLOCK
    elif major:
        decision = ValidationDecision.SHADOW_ONLY
    else:
        decision = ValidationDecision.PASS

    return AdversarialValidationReport(
        capability_id=candidate.capability_id,
        decision=decision,
        generated_at=timestamp,
        expert_results=expert_results,
        findings=all_findings,
        mandatory_failures=critical,
        unresolved_major_failures=major,
    )


def assert_operationally_eligible(
    report: AdversarialValidationReport,
) -> None:
    """
    Impide que una capacidad no aprobada continúe hacia producción.

    Raises
    ------
    RuntimeError
        Si el resultado es BLOCK o SHADOW_ONLY.
    """

    if report.decision is ValidationDecision.PASS:
        return

    if report.decision is ValidationDecision.BLOCK:
        raise RuntimeError(
            "CeutIA adversarial validation BLOCKED capability "
            f"{report.capability_id}: "
            f"{len(report.mandatory_failures)} critical finding(s)."
        )

    raise RuntimeError(
        "CeutIA capability "
        f"{report.capability_id} is SHADOW_ONLY and cannot be used "
        "for operational decisions."
    )


# ---------------------------------------------------------------------------
# Deterministic summary for APIs / audit
# ---------------------------------------------------------------------------


def summarize_report(
    report: AdversarialValidationReport,
) -> dict[str, object]:
    """
    Genera una representación serializable y segura del resultado.

    No incluye datos personales, fuentes privadas ni contenido operacional.
    """

    by_domain: dict[str, dict[str, int]] = {}

    for result in report.expert_results:
        by_domain[result.domain.value] = {
            "findings": len(result.findings),
            "major": result.major_count,
            "critical": result.critical_count,
            "passed": int(result.passed),
        }

    severity_counts = {
        severity.value: sum(
            finding.severity is severity
            for finding in report.findings
        )
        for severity in FindingSeverity
    }

    return {
        "capability_id": report.capability_id,
        "decision": report.decision.value,
        "generated_at": report.generated_at.isoformat(),
        "severity_counts": severity_counts,
        "domains": by_domain,
        "mandatory_failures": tuple(
            code.value for code in report.mandatory_failures
        ),
        "unresolved_major_failures": tuple(
            code.value for code in report.unresolved_major_failures
        ),
    }


# ---------------------------------------------------------------------------
# Invariants
# ---------------------------------------------------------------------------


SCIENTIFIC_INVARIANTS: Final[tuple[str, ...]] = (
    "A mathematically valid formula is not automatically operationally valid.",
    "A published model is not automatically validated for CeutIA.",
    "Retrospective fit is not prospective validation.",
    "Discrimination is not calibration.",
    "Calibration is not causal validity.",
    "Prediction is not explanation.",
    "Correlation is not causation.",
    "Source count is not source independence.",
    "Viral content is evidence that content exists, not evidence that its claim is true.",
    "Contradictory evidence must remain representable.",
    "Unknown must remain distinguishable from zero.",
    "Missing data must not silently become risk.",
    "Probability requires calibration evidence.",
    "Rare-event prediction requires explicit evaluation of class imbalance and calibration.",
    "Spatial aggregation does not justify individual inference.",
    "Population-level association does not justify individual-level prediction.",
    "Nationality or origin must not be used as a proxy for dangerousness.",
    "Group identity must not become a dangerousness score.",
    "CeutIA detects system/event signals; authorized humans interpret operational consequences.",
    "An alert is not an instruction to act.",
    "An operational decision must not be generated solely by an automated alert.",
    "Every production capability must have an auditable validation history.",
    "Every prediction must be retrospectively comparable with an observed outcome.",
    "Every model must have an explicit failure boundary.",
    "Every public output must be independently authorized by the information boundary.",
)


def validate_invariants() -> tuple[str, ...]:
    """
    Validación estática de las invariantes fundamentales.

    Returns an empty tuple when the invariant registry is structurally valid.
    """

    errors: list[str] = []

    if len(SCIENTIFIC_INVARIANTS) != len(set(SCIENTIFIC_INVARIANTS)):
        errors.append("Duplicate scientific invariant detected.")

    if len(EXPERT_GATES) != len(set(EXPERT_GATES)):
        errors.append("Duplicate expert gate detected.")

    if set(EXPERT_GATES) != set(ExpertDomain):
        errors.append(
            "The adversarial validator must cover exactly all six expert domains."
        )

    return tuple(errors)


_INVARIANT_ERRORS = validate_invariants()

if _INVARIANT_ERRORS:
    raise RuntimeError(
        "CeutIA adversarial validation invariant failure: "
        + "; ".join(_INVARIANT_ERRORS)
    )


__all__ = [
    "AdversarialValidationReport",
    "CandidateCapability",
    "DataUseMode",
    "EvidenceMaturity",
    "ExpertDomain",
    "ExpertGateResult",
    "FindingCode",
    "FindingSeverity",
    "PredictivePerformance",
    "SCIENTIFIC_INVARIANTS",
    "TargetLevel",
    "ValidationDataset",
    "ValidationDecision",
    "ValidationDimension",
    "ValidationFinding",
    "assert_operationally_eligible",
    "run_adversarial_validation",
    "summarize_report",
    "validate_epidemiology",
    "validate_geospatial",
    "validate_invariants",
    "validate_law_privacy_cybersecurity",
    "validate_operational_security",
    "validate_statistics_ml",
    "validate_strategic_intelligence",
    "validate_target_safety",
]
