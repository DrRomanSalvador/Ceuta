"""
CeutIA - Evidence Policy
========================

Política ejecutable para gobernar el uso de fuentes y evidencia.

Objetivo
--------
Impedir que CeutIA convierta automáticamente:

    fuente -> evidencia
    evidencia -> verdad
    correlación -> causalidad
    señal -> hecho
    opinión -> conocimiento científico

Este módulo NO determina si una afirmación es verdadera.

Determina qué tipo de soporte epistemológico puede recibir una
afirmación según:

- dominio;
- tipo de fuente;
- tipo de estudio;
- naturaleza de la afirmación;
- fuerza de la inferencia;
- falsabilidad;
- independencia de las fuentes.

Principio fundamental
---------------------
Una fuente puede ser útil como señal sin ser admisible como evidencia
científica.

Una fuente científica tampoco convierte automáticamente una afirmación
en verdadera: el diseño del estudio, sus resultados, limitaciones,
calidad, aplicabilidad e independencia deben evaluarse por separado.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import FrozenSet


class EvidenceDomain(StrEnum):
    """Domain in which an assertion is being evaluated."""

    BIOMEDICAL = "biomedical"
    EPIDEMIOLOGY = "epidemiology"
    PSYCHOLOGY = "psychology"
    PUBLIC_HEALTH = "public_health"
    ENVIRONMENT = "environment"
    DEMOGRAPHY = "demography"
    SOCIAL = "social"
    SECURITY = "security"
    ECONOMICS = "economics"
    GENERAL = "general"


class SourceClass(StrEnum):
    """
    Epistemic classification of the origin of information.

    This is intentionally independent from URL/domain names.
    A source's website does not by itself determine the quality
    of a specific claim.
    """

    PUBMED = "pubmed"
    PEER_REVIEWED = "peer_reviewed"
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    CLINICAL_TRIAL = "clinical_trial"

    OFFICIAL_INSTITUTION = "official_institution"
    INTERNATIONAL_ORGANIZATION = "international_organization"

    REPUTABLE_MEDIA = "reputable_media"
    SOCIAL_MEDIA = "social_media"
    CITIZEN_TESTIMONY = "citizen_testimony"

    BLOG = "blog"
    COMMERCIAL = "commercial"
    AI_GENERATED = "ai_generated"

    UNKNOWN = "unknown"


class StudyType(StrEnum):
    """Study or evidence design."""

    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    RANDOMIZED_CONTROLLED_TRIAL = "randomized_controlled_trial"
    COHORT = "cohort"
    CASE_CONTROL = "case_control"
    CROSS_SECTIONAL = "cross_sectional"
    CASE_SERIES = "case_series"
    CASE_REPORT = "case_report"
    QUALITATIVE = "qualitative"
    ECOLOGICAL = "ecological"
    EXPERT_OPINION = "expert_opinion"
    ADMINISTRATIVE_DATA = "administrative_data"
    SURVEILLANCE = "surveillance"
    DESCRIPTIVE = "descriptive"
    MODELLING = "modelling"
    UNKNOWN = "unknown"


class ClaimType(StrEnum):
    """Nature of the proposition being evaluated."""

    DESCRIPTIVE = "descriptive"
    ASSOCIATIONAL = "associational"
    CAUSAL = "causal"
    PREDICTIVE = "predictive"
    MECHANISTIC = "mechanistic"
    DIAGNOSTIC = "diagnostic"
    INTERVENTIONAL = "interventional"
    PREVALENCE = "prevalence"
    PROGNOSTIC = "prognostic"


class SupportLevel(StrEnum):
    """Maximum epistemic role permitted by the policy."""

    SCIENTIFIC_EVIDENCE = "scientific_evidence"
    INSTITUTIONAL_EVIDENCE = "institutional_evidence"
    CONTEXTUAL_EVIDENCE = "contextual_evidence"
    SIGNAL_ONLY = "signal_only"
    NOT_ADMISSIBLE = "not_admissible"


class PolicySeverity(StrEnum):
    """Severity of a policy violation."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    BLOCK = "block"


class EvidencePolicyError(ValueError):
    """Raised when an evidence-policy rule is violated."""


@dataclass(frozen=True, slots=True)
class EvidencePolicyFinding:
    """Single finding produced by policy evaluation."""

    code: str
    message: str
    severity: PolicySeverity


@dataclass(frozen=True, slots=True)
class EvidencePolicyResult:
    """Result of an evidence-policy evaluation."""

    admissible: bool
    support_level: SupportLevel
    findings: tuple[EvidencePolicyFinding, ...]

    @property
    def blocked(self) -> bool:
        """Whether the evidence is explicitly blocked."""
        return not self.admissible


# ---------------------------------------------------------------------------
# Source classes
# ---------------------------------------------------------------------------

SCIENTIFIC_SOURCE_CLASSES: FrozenSet[SourceClass] = frozenset(
    {
        SourceClass.PUBMED,
        SourceClass.PEER_REVIEWED,
        SourceClass.SYSTEMATIC_REVIEW,
        SourceClass.META_ANALYSIS,
        SourceClass.CLINICAL_TRIAL,
    }
)

INSTITUTIONAL_SOURCE_CLASSES: FrozenSet[SourceClass] = frozenset(
    {
        SourceClass.OFFICIAL_INSTITUTION,
        SourceClass.INTERNATIONAL_ORGANIZATION,
    }
)

SIGNAL_SOURCE_CLASSES: FrozenSet[SourceClass] = frozenset(
    {
        SourceClass.REPUTABLE_MEDIA,
        SourceClass.SOCIAL_MEDIA,
        SourceClass.CITIZEN_TESTIMONY,
    }
)

NON_ADMISSIBLE_SOURCE_CLASSES: FrozenSet[SourceClass] = frozenset(
    {
        SourceClass.AI_GENERATED,
        SourceClass.UNKNOWN,
    }
)


# ---------------------------------------------------------------------------
# Study designs
# ---------------------------------------------------------------------------

CAUSAL_DESIGNS: FrozenSet[StudyType] = frozenset(
    {
        StudyType.RANDOMIZED_CONTROLLED_TRIAL,
    }
)

STRONG_SYNTHESIS_DESIGNS: FrozenSet[StudyType] = frozenset(
    {
        StudyType.SYSTEMATIC_REVIEW,
        StudyType.META_ANALYSIS,
    }
)

OBSERVATIONAL_DESIGNS: FrozenSet[StudyType] = frozenset(
    {
        StudyType.COHORT,
        StudyType.CASE_CONTROL,
        StudyType.CROSS_SECTIONAL,
        StudyType.ECOLOGICAL,
    }
)


# ---------------------------------------------------------------------------
# Basic source-policy functions
# ---------------------------------------------------------------------------

def is_scientific_source(source: SourceClass) -> bool:
    """
    Return whether a source class belongs to the scientific evidence layer.

    This does NOT imply that a particular article is methodologically sound
    or that its conclusions are correct.
    """
    return source in SCIENTIFIC_SOURCE_CLASSES


def is_institutional_source(source: SourceClass) -> bool:
    """Return whether a source belongs to the institutional layer."""
    return source in INSTITUTIONAL_SOURCE_CLASSES


def can_be_signal(source: SourceClass) -> bool:
    """
    Return whether information can be retained as a signal.

    Social media, reputable media and citizen testimony may be valuable
    as signals of events, perceptions or emerging phenomena without
    becoming scientific evidence.
    """
    return source in SIGNAL_SOURCE_CLASSES


def can_support_scientific_claim(source: SourceClass) -> bool:
    """
    Return whether a source class can directly support a scientific claim.

    AI-generated content, social media, citizen testimony, media and
    commercial material cannot independently establish scientific evidence.
    """
    return source in SCIENTIFIC_SOURCE_CLASSES


# ---------------------------------------------------------------------------
# Permitted inference
# ---------------------------------------------------------------------------

def permitted_support_level(
    source: SourceClass,
    *,
    domain: EvidenceDomain,
) -> SupportLevel:
    """
    Determine the maximum epistemic role allowed for a source.

    The result is deliberately conservative.
    """

    if source in NON_ADMISSIBLE_SOURCE_CLASSES:
        return SupportLevel.NOT_ADMISSIBLE

    if source in SCIENTIFIC_SOURCE_CLASSES:
        return SupportLevel.SCIENTIFIC_EVIDENCE

    if source in INSTITUTIONAL_SOURCE_CLASSES:
        return SupportLevel.INSTITUTIONAL_EVIDENCE

    if source in SIGNAL_SOURCE_CLASSES:
        return SupportLevel.SIGNAL_ONLY

    if source in {
        SourceClass.BLOG,
        SourceClass.COMMERCIAL,
    }:
        return SupportLevel.CONTEXTUAL_EVIDENCE

    return SupportLevel.NOT_ADMISSIBLE


def validate_scientific_claim_source(
    source: SourceClass,
    *,
    domain: EvidenceDomain,
) -> EvidencePolicyResult:
    """
    Validate whether a source may be used as scientific support.

    For biomedical, epidemiological, psychological and public-health
    assertions, scientific literature is required for scientific claims.
    """

    if domain in {
        EvidenceDomain.BIOMEDICAL,
        EvidenceDomain.EPIDEMIOLOGY,
        EvidenceDomain.PSYCHOLOGY,
        EvidenceDomain.PUBLIC_HEALTH,
    }:
        if not is_scientific_source(source):
            return EvidencePolicyResult(
                admissible=False,
                support_level=permitted_support_level(
                    source,
                    domain=domain,
                ),
                findings=(
                    EvidencePolicyFinding(
                        code="SCIENTIFIC_SOURCE_REQUIRED",
                        message=(
                            "La afirmación pertenece a un dominio científico "
                            "y la fuente no pertenece a la capa de evidencia "
                            "científica admisible."
                        ),
                        severity=PolicySeverity.BLOCK,
                    ),
                ),
            )

    if source in NON_ADMISSIBLE_SOURCE_CLASSES:
        return EvidencePolicyResult(
            admissible=False,
            support_level=SupportLevel.NOT_ADMISSIBLE,
            findings=(
                EvidencePolicyFinding(
                    code="SOURCE_NOT_ADMISSIBLE",
                    message=(
                        "La fuente no es admisible como soporte epistemológico."
                    ),
                    severity=PolicySeverity.BLOCK,
                ),
            ),
        )

    return EvidencePolicyResult(
        admissible=True,
        support_level=permitted_support_level(
            source,
            domain=domain,
        ),
        findings=(),
    )


# ---------------------------------------------------------------------------
# Study-design rules
# ---------------------------------------------------------------------------

def validate_claim_design(
    claim_type: ClaimType,
    study_type: StudyType,
) -> EvidencePolicyResult:
    """
    Validate whether the study design is compatible with the claimed
    strength of inference.

    Particularly important:
        association != causation
        temporal precedence != causation
        mechanism != demonstrated clinical effect
    """

    findings: list[EvidencePolicyFinding] = []

    if claim_type == ClaimType.CAUSAL:
        if study_type in OBSERVATIONAL_DESIGNS:
            findings.append(
                EvidencePolicyFinding(
                    code="CAUSAL_OVERREACH",
                    message=(
                        "Un diseño observacional no permite por sí solo "
                        "elevar una asociación a causalidad."
                    ),
                    severity=PolicySeverity.BLOCK,
                )
            )

        elif study_type in {
            StudyType.CASE_REPORT,
            StudyType.CASE_SERIES,
            StudyType.EXPERT_OPINION,
            StudyType.UNKNOWN,
        }:
            findings.append(
                EvidencePolicyFinding(
                    code="INSUFFICIENT_CAUSAL_DESIGN",
                    message=(
                        "El diseño indicado no proporciona por sí mismo "
                        "base suficiente para una inferencia causal."
                    ),
                    severity=PolicySeverity.BLOCK,
                )
            )

    if claim_type == ClaimType.INTERVENTIONAL:
        if study_type in {
            StudyType.CROSS_SECTIONAL,
            StudyType.CASE_REPORT,
            StudyType.CASE_SERIES,
            StudyType.ECOLOGICAL,
            StudyType.EXPERT_OPINION,
            StudyType.UNKNOWN,
        }:
            findings.append(
                EvidencePolicyFinding(
                    code="INTERVENTIONAL_OVERREACH",
                    message=(
                        "El diseño indicado no permite demostrar por sí mismo "
                        "la eficacia de una intervención."
                    ),
                    severity=PolicySeverity.BLOCK,
                )
            )

    if claim_type == ClaimType.PREVALENCE:
        if study_type == StudyType.CASE_REPORT:
            findings.append(
                EvidencePolicyFinding(
                    code="PREVALENCE_DESIGN_MISMATCH",
                    message=(
                        "Un caso individual no permite estimar prevalencia "
                        "poblacional."
                    ),
                    severity=PolicySeverity.BLOCK,
                )
            )

    if findings:
        return EvidencePolicyResult(
            admissible=False,
            support_level=SupportLevel.SCIENTIFIC_EVIDENCE,
            findings=tuple(findings),
        )

    return EvidencePolicyResult(
        admissible=True,
        support_level=SupportLevel.SCIENTIFIC_EVIDENCE,
        findings=(),
    )


# ---------------------------------------------------------------------------
# Anti-pseudoscience controls
# ---------------------------------------------------------------------------

def validate_scientific_hypothesis(
    *,
    falsifiable: bool,
    empirical_basis: bool,
    source_classes: set[SourceClass],
) -> EvidencePolicyResult:
    """
    Apply minimum scientific admissibility criteria.

    This function deliberately does not attempt to identify
    "pseudoscience" linguistically. It enforces structural properties
    that scientific hypotheses must satisfy.
    """

    findings: list[EvidencePolicyFinding] = []

    if not falsifiable:
        findings.append(
            EvidencePolicyFinding(
                code="NON_FALSIFIABLE",
                message=(
                    "La hipótesis no es falsable y no puede tratarse "
                    "como hipótesis científica validada."
                ),
                severity=PolicySeverity.BLOCK,
            )
        )

    if not empirical_basis:
        findings.append(
            EvidencePolicyFinding(
                code="NO_EMPIRICAL_BASIS",
                message=(
                    "No se ha identificado una base empírica suficiente "
                    "para tratar la proposición como evidencia científica."
                ),
                severity=PolicySeverity.BLOCK,
            )
        )

    if not any(
        is_scientific_source(source)
        for source in source_classes
    ):
        findings.append(
            EvidencePolicyFinding(
                code="NO_SCIENTIFIC_SOURCE",
                message=(
                    "No existe una fuente científica admisible entre "
                    "las fuentes aportadas."
                ),
                severity=PolicySeverity.BLOCK,
            )
        )

    return EvidencePolicyResult(
        admissible=not findings,
        support_level=(
            SupportLevel.SCIENTIFIC_EVIDENCE
            if not findings
            else SupportLevel.NOT_ADMISSIBLE
        ),
        findings=tuple(findings),
    )


# ---------------------------------------------------------------------------
# Independence and corroboration
# ---------------------------------------------------------------------------

def validate_source_independence(
    source_ids: list[str],
    independent_source_ids: set[str],
) -> EvidencePolicyResult:
    """
    Prevent duplicated reporting from being counted as independent
    corroboration.

    Multiple articles reproducing the same original source do not
    constitute multiple independent observations.
    """

    unique_ids = set(source_ids)

    if not unique_ids:
        return EvidencePolicyResult(
            admissible=False,
            support_level=SupportLevel.NOT_ADMISSIBLE,
            findings=(
                EvidencePolicyFinding(
                    code="NO_SOURCES",
                    message="No se han proporcionado fuentes.",
                    severity=PolicySeverity.BLOCK,
                ),
            ),
        )

    independent_count = len(unique_ids & independent_source_ids)

    if independent_count <= 1 and len(unique_ids) > 1:
        return EvidencePolicyResult(
            admissible=True,
            support_level=SupportLevel.CONTEXTUAL_EVIDENCE,
            findings=(
                EvidencePolicyFinding(
                    code="DEPENDENT_CORROBORATION",
                    message=(
                        "Las múltiples fuentes no demuestran independencia "
                        "epistémica suficiente para considerarse corroboración "
                        "independiente."
                    ),
                    severity=PolicySeverity.WARNING,
                ),
            ),
        )

    return EvidencePolicyResult(
        admissible=True,
        support_level=SupportLevel.CONTEXTUAL_EVIDENCE,
        findings=(),
    )


# ---------------------------------------------------------------------------
# Evidence aggregation
# ---------------------------------------------------------------------------

def validate_evidence_bundle(
    *,
    domain: EvidenceDomain,
    source_classes: set[SourceClass],
    claim_type: ClaimType,
    study_types: set[StudyType],
    falsifiable: bool,
    empirical_basis: bool,
) -> EvidencePolicyResult:
    """
    Evaluate an evidence bundle conservatively.

    Important:
    - More sources do not automatically mean stronger evidence.
    - A weak source cannot be upgraded merely by repetition.
    - A scientific source does not override an incompatible study design.
    """

    findings: list[EvidencePolicyFinding] = []

    if not source_classes:
        return EvidencePolicyResult(
            admissible=False,
            support_level=SupportLevel.NOT_ADMISSIBLE,
            findings=(
                EvidencePolicyFinding(
                    code="EMPTY_EVIDENCE_BUNDLE",
                    message="El conjunto de evidencia no contiene fuentes.",
                    severity=PolicySeverity.BLOCK,
                ),
            ),
        )

    scientific_sources = {
        source
        for source in source_classes
        if is_scientific_source(source)
    }

    if domain in {
        EvidenceDomain.BIOMEDICAL,
        EvidenceDomain.EPIDEMIOLOGY,
        EvidenceDomain.PSYCHOLOGY,
        EvidenceDomain.PUBLIC_HEALTH,
    } and not scientific_sources:
        findings.append(
            EvidencePolicyFinding(
                code="SCIENTIFIC_EVIDENCE_MISSING",
                message=(
                    "Para este dominio no existe evidencia científica "
                    "admisible en el conjunto proporcionado."
                ),
                severity=PolicySeverity.BLOCK,
            )
        )

    if claim_type in {
        ClaimType.CAUSAL,
        ClaimType.INTERVENTIONAL,
    }:
        if not study_types:
            findings.append(
                EvidencePolicyFinding(
                    code="STUDY_DESIGN_MISSING",
                    message=(
                        "Una inferencia causal o interventional requiere "
                        "conocer el diseño de los estudios utilizados."
                    ),
                    severity=PolicySeverity.BLOCK,
                )
            )

        if study_types and all(
            study_type in OBSERVATIONAL_DESIGNS
            for study_type in study_types
        ):
            findings.append(
                EvidencePolicyFinding(
                    code="OBSERVATIONAL_ONLY",
                    message=(
                        "El conjunto está compuesto exclusivamente por "
                        "diseños observacionales; no debe presentarse "
                        "como demostración causal."
                    ),
                    severity=PolicySeverity.BLOCK,
                )
            )

    hypothesis_result = validate_scientific_hypothesis(
        falsifiable=falsifiable,
        empirical_basis=empirical_basis,
        source_classes=source_classes,
    )

    findings.extend(hypothesis_result.findings)

    if findings:
        return EvidencePolicyResult(
            admissible=False,
            support_level=SupportLevel.NOT_ADMISSIBLE,
            findings=tuple(findings),
        )

    return EvidencePolicyResult(
        admissible=True,
        support_level=SupportLevel.SCIENTIFIC_EVIDENCE,
        findings=(),
    )


# ---------------------------------------------------------------------------
# Explicit prohibitions
# ---------------------------------------------------------------------------

def prohibit_causal_language_from_association(
    *,
    observed_association: bool,
    causal_design: bool,
) -> None:
    """
    Raise if causal language is attempted without causal support.
    """

    if observed_association and not causal_design:
        raise EvidencePolicyError(
            "No puede transformarse una asociación observada "
            "en una afirmación causal sin soporte metodológico adecuado."
        )


def prohibit_truth_claim_from_source(
    *,
    source: SourceClass,
) -> None:
    """
    A source can support an epistemic claim; it cannot itself establish
    absolute truth.
    """

    if source in NON_ADMISSIBLE_SOURCE_CLASSES:
        raise EvidencePolicyError(
            "Una fuente no admisible no puede utilizarse para establecer "
            "una afirmación como conocimiento."
        )


def prohibit_identity_based_inference(
    *,
    protected_attribute_used: bool,
    individual_risk_inference: bool,
) -> None:
    """
    Prevent individual risk inference based on protected attributes.

    This is a hard architectural boundary for CeutIA.
    """

    if protected_attribute_used and individual_risk_inference:
        raise EvidencePolicyError(
            "No se permite inferir riesgo individual a partir de "
            "atributos protegidos o de pertenencia grupal."
        )


# ---------------------------------------------------------------------------
# Public policy invariants
# ---------------------------------------------------------------------------

SCIENTIFIC_INVARIANTS: tuple[str, ...] = (
    "Una correlación no demuestra causalidad.",
    "La precedencia temporal no demuestra causalidad.",
    "Una narrativa coherente no constituye evidencia.",
    "La repetición de una misma fuente no constituye corroboración independiente.",
    "Una publicación científica no equivale automáticamente a evidencia de alta calidad.",
    "PubMed es un índice bibliográfico; la indexación no valida por sí sola las conclusiones de un artículo.",
    "Las redes sociales y testimonios ciudadanos pueden constituir señales, pero no evidencia científica por sí mismos.",
    "El contenido generado por IA no constituye evidencia primaria.",
    "Una hipótesis científica debe ser empíricamente contrastable y falsable.",
    "La ausencia de evidencia no equivale automáticamente a evidencia de ausencia.",
    "La evidencia contradictoria debe conservarse y evaluarse, no eliminarse.",
    "La incertidumbre debe conservarse en la cadena epistemológica.",
    "El número de fuentes no sustituye su independencia ni su calidad metodológica.",
    "Una métrica de rendimiento no es una probabilidad de verdad.",
    "Una alerta no constituye por sí misma una decisión.",
    "CeutIA no debe realizar inferencias individuales de peligrosidad basadas en nacionalidad, origen u otros atributos protegidos.",
)


def get_scientific_invariants() -> tuple[str, ...]:
    """Return immutable scientific invariants used by CeutIA."""
    return SCIENTIFIC_INVARIANTS


__all__ = [
    "ClaimType",
    "EvidenceDomain",
    "EvidencePolicyError",
    "EvidencePolicyFinding",
    "EvidencePolicyResult",
    "INSTITUTIONAL_SOURCE_CLASSES",
    "NON_ADMISSIBLE_SOURCE_CLASSES",
    "OBSERVATIONAL_DESIGNS",
    "PolicySeverity",
    "SCIENTIFIC_INVARIANTS",
    "SCIENTIFIC_SOURCE_CLASSES",
    "SIGNAL_SOURCE_CLASSES",
    "SourceClass",
    "StudyType",
    "SupportLevel",
    "can_be_signal",
    "can_support_scientific_claim",
    "get_scientific_invariants",
    "is_institutional_source",
    "is_scientific_source",
    "permitted_support_level",
    "prohibit_causal_language_from_association",
    "prohibit_identity_based_inference",
    "prohibit_truth_claim_from_source",
    "validate_claim_design",
    "validate_evidence_bundle",
    "validate_scientific_claim_source",
    "validate_scientific_hypothesis",
    "validate_source_independence",
]