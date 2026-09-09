"""
CeutIA - Scientific Metrics and Validated Risk Registry
========================================================

Motor cuantitativo para CeutIA.

PRINCIPIO CENTRAL
-----------------
Este módulo NO inventa índices de riesgo.

Solo permite ejecutar:

1. métricas matemáticas formalmente definidas;
2. instrumentos/índices con metodología publicada;
3. índices oficiales cuando la fuente oficial sea la autoridad competente;
4. métricas de validación de modelos;
5. modelos predictivos cuya implementación y dominio de aplicación
   estén explícitamente documentados.

Una métrica registrada no implica que sea apropiada para cualquier
población, territorio o finalidad.

Especialmente:

    PubMed != verdad
    AUC != utilidad clínica
    correlación != causalidad
    escala validada != diagnóstico
    índice ambiental != predicción individual
    modelo publicado != modelo validado para Ceuta

Una fórmula no puede producir una probabilidad de riesgo válida si
no existe una base empírica y un proceso de validación apropiado.

ARQUITECTURA DE SALIDA
----------------------
Las métricas pueden alimentar:

    INTERNAL
        motor de inteligencia de CeutIA

    PRIVATE
        inteligencia estratégica autorizada

    PUBLIC_USER
        recomendaciones personalizadas

Los objetos internos de inteligencia NO deben serializarse
directamente hacia PUBLIC_USER.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import log, sqrt
from typing import Callable, Final, Mapping, Sequence

import numpy as np


# ============================================================================
# ENUMS
# ============================================================================


class MetricDomain(StrEnum):
    """Scientific or operational domain."""

    GENERAL_STATISTICS = "general_statistics"
    PREDICTION = "prediction"
    CLASSIFICATION = "classification"
    CALIBRATION = "calibration"

    BIOMEDICAL = "biomedical"
    EPIDEMIOLOGY = "epidemiology"
    CARDIOVASCULAR = "cardiovascular"
    MENTAL_HEALTH = "mental_health"
    TRAUMA = "trauma"
    SLEEP = "sleep"
    STRESS = "stress"

    ENVIRONMENT = "environment"
    CLIMATE = "climate"
    DROUGHT = "drought"
    EXTREME_RAINFALL = "extreme_rainfall"
    HEAT = "heat"
    FIRE = "fire"
    AIR_QUALITY = "air_quality"
    WATER = "water"

    DEMOGRAPHY = "demography"
    SOCIOLOGY = "sociology"
    SOCIAL_COHESION = "social_cohesion"

    VIOLENCE = "violence"
    POLITICAL_VIOLENCE = "political_violence"
    CONFLICT = "conflict"
    SECURITY = "security"
    STRATEGIC = "strategic"

    CAPACITY = "capacity"
    QUEUEING = "queueing"
    NETWORK = "network"
    SYSTEM_DYNAMICS = "system_dynamics"


class ValidationStatus(StrEnum):
    """Scientific implementation status."""

    VALIDATED = "validated"
    VALIDATED_ELSEWHERE = "validated_elsewhere"
    OFFICIAL = "official"
    CATALOGUED = "catalogued"
    EXPERIMENTAL = "experimental"
    NOT_VALIDATED_FOR_CEUTA = "not_validated_for_ceuta"
    BLOCKED = "blocked"


class OutputChannel(StrEnum):
    """
    Permitted destination for a metric.

    This is an architectural boundary.
    """

    INTERNAL = "internal"
    PRIVATE = "private"
    PUBLIC_USER = "public_user"


class MetricKind(StrEnum):
    """Nature of the metric."""

    FORMULA = "formula"
    SCORE = "score"
    SCALE = "scale"
    INDEX = "index"
    MODEL_EVALUATION = "model_evaluation"
    RISK_MODEL = "risk_model"


class EvidenceLevel(StrEnum):
    """Evidence provenance level."""

    PEER_REVIEWED = "peer_reviewed"
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    OFFICIAL = "official"
    METHODOLOGICAL_STANDARD = "methodological_standard"
    OTHER = "other"


# ============================================================================
# METRIC REGISTRY
# ============================================================================


@dataclass(frozen=True, slots=True)
class MetricDefinition:
    """
    Formal registration of a metric/index/model.

    The registry is intentionally explicit. A metric cannot become
    operational merely because a developer added a Python function.
    """

    id: str
    name: str
    domain: MetricDomain
    kind: MetricKind
    status: ValidationStatus

    description: str

    unit: str
    output_type: str

    formula: str | None

    evidence_level: EvidenceLevel
    evidence_references: tuple[str, ...]

    validated_population: str | None
    validated_context: str | None

    limitations: tuple[str, ...]

    permitted_channels: frozenset[OutputChannel]

    individual_use: bool
    population_use: bool

    causal_interpretation_allowed: bool
    predictive_use_allowed: bool


# ============================================================================
# EXCEPTIONS
# ============================================================================


class MetricError(ValueError):
    """Base error for metric evaluation."""


class MetricInputError(MetricError):
    """Invalid metric inputs."""


class MetricNotValidatedError(MetricError):
    """Attempt to execute a non-validated metric."""


class MetricNotPermittedError(MetricError):
    """Metric is not permitted for the requested output channel."""


# ============================================================================
# BASIC VALIDATED STATISTICAL METRICS
# ============================================================================


def _validate_equal_length(
    y_true: Sequence[float],
    y_pred: Sequence[float],
) -> None:
    if len(y_true) != len(y_pred):
        raise MetricInputError("y_true y y_pred deben tener la misma longitud.")

    if len(y_true) == 0:
        raise MetricInputError("Las series no pueden estar vacías.")


def _as_float_array(values: Sequence[float]) -> np.ndarray:
    array = np.asarray(values, dtype=float)

    if not np.all(np.isfinite(array)):
        raise MetricInputError("Las entradas contienen valores no finitos.")

    return array


def mse(
    y_true: Sequence[float],
    y_pred: Sequence[float],
) -> float:
    """
    Mean Squared Error.

    MSE = mean((y - ŷ)^2)
    """
    _validate_equal_length(y_true, y_pred)

    actual = _as_float_array(y_true)
    predicted = _as_float_array(y_pred)

    return float(np.mean((actual - predicted) ** 2))


def rmse(
    y_true: Sequence[float],
    y_pred: Sequence[float],
) -> float:
    """
    Root Mean Squared Error.

    RMSE = sqrt(MSE)
    """
    return sqrt(mse(y_true, y_pred))


def mae(
    y_true: Sequence[float],
    y_pred: Sequence[float],
) -> float:
    """
    Mean Absolute Error.

    MAE = mean(|y - ŷ|)
    """
    _validate_equal_length(y_true, y_pred)

    actual = _as_float_array(y_true)
    predicted = _as_float_array(y_pred)

    return float(np.mean(np.abs(actual - predicted)))


def r_squared(
    y_true: Sequence[float],
    y_pred: Sequence[float],
) -> float:
    """
    Coefficient of determination.

    R² = 1 - SSE/SST

    Caution:
        R² is a goodness-of-fit statistic, not a causal measure
        and not a probability of prediction correctness.
    """
    _validate_equal_length(y_true, y_pred)

    actual = _as_float_array(y_true)
    predicted = _as_float_array(y_pred)

    denominator = float(np.sum((actual - np.mean(actual)) ** 2))

    if denominator == 0:
        raise MetricInputError(
            "R² no está definido cuando la varianza observada es cero."
        )

    numerator = float(np.sum((actual - predicted) ** 2))

    return 1.0 - numerator / denominator


# ============================================================================
# BINARY CLASSIFICATION
# ============================================================================


@dataclass(frozen=True, slots=True)
class ConfusionMatrix:
    true_positive: int
    true_negative: int
    false_positive: int
    false_negative: int


def confusion_matrix_binary(
    y_true: Sequence[int],
    y_pred: Sequence[int],
) -> ConfusionMatrix:
    _validate_equal_length(y_true, y_pred)

    actual = np.asarray(y_true, dtype=int)
    predicted = np.asarray(y_pred, dtype=int)

    if not np.isin(actual, [0, 1]).all():
        raise MetricInputError("y_true debe contener únicamente 0 y 1.")

    if not np.isin(predicted, [0, 1]).all():
        raise MetricInputError("y_pred debe contener únicamente 0 y 1.")

    return ConfusionMatrix(
        true_positive=int(np.sum((actual == 1) & (predicted == 1))),
        true_negative=int(np.sum((actual == 0) & (predicted == 0))),
        false_positive=int(np.sum((actual == 0) & (predicted == 1))),
        false_negative=int(np.sum((actual == 1) & (predicted == 0))),
    )


def sensitivity(cm: ConfusionMatrix) -> float:
    denominator = cm.true_positive + cm.false_negative

    if denominator == 0:
        raise MetricInputError("Sensibilidad indefinida: no hay positivos reales.")

    return cm.true_positive / denominator


def specificity(cm: ConfusionMatrix) -> float:
    denominator = cm.true_negative + cm.false_positive

    if denominator == 0:
        raise MetricInputError("Especificidad indefinida: no hay negativos reales.")

    return cm.true_negative / denominator


def positive_predictive_value(cm: ConfusionMatrix) -> float:
    denominator = cm.true_positive + cm.false_positive

    if denominator == 0:
        raise MetricInputError("PPV indefinido.")

    return cm.true_positive / denominator


def negative_predictive_value(cm: ConfusionMatrix) -> float:
    denominator = cm.true_negative + cm.false_negative

    if denominator == 0:
        raise MetricInputError("NPV indefinido.")

    return cm.true_negative / denominator


def accuracy(cm: ConfusionMatrix) -> float:
    total = (
        cm.true_positive
        + cm.true_negative
        + cm.false_positive
        + cm.false_negative
    )

    if total == 0:
        raise MetricInputError("Accuracy indefinida.")

    return (cm.true_positive + cm.true_negative) / total


def balanced_accuracy(cm: ConfusionMatrix) -> float:
    return (sensitivity(cm) + specificity(cm)) / 2.0


def f1_score(cm: ConfusionMatrix) -> float:
    precision = positive_predictive_value(cm)
    recall = sensitivity(cm)

    denominator = precision + recall

    if denominator == 0:
        return 0.0

    return 2.0 * precision * recall / denominator


def matthews_correlation_coefficient(cm: ConfusionMatrix) -> float:
    numerator = (
        cm.true_positive * cm.true_negative
        - cm.false_positive * cm.false_negative
    )

    denominator = sqrt(
        (cm.true_positive + cm.false_positive)
        * (cm.true_positive + cm.false_negative)
        * (cm.true_negative + cm.false_positive)
        * (cm.true_negative + cm.false_negative)
    )

    if denominator == 0:
        raise MetricInputError("MCC indefinido.")

    return numerator / denominator


# ============================================================================
# PROBABILISTIC PREDICTION
# ============================================================================


def _validate_probabilities(
    probabilities: Sequence[float],
) -> np.ndarray:
    values = _as_float_array(probabilities)

    if np.any(values < 0.0) or np.any(values > 1.0):
        raise MetricInputError(
            "Las probabilidades deben estar entre 0 y 1."
        )

    return values


def brier_score(
    y_true: Sequence[int],
    probabilities: Sequence[float],
) -> float:
    """
    Binary Brier score.

    BS = mean((p - y)^2)

    Lower is better.

    The Brier score is a proper scoring rule but does NOT by itself
    establish clinical or operational utility.
    """
    _validate_equal_length(y_true, probabilities)

    actual = np.asarray(y_true, dtype=float)
    if not np.isin(actual, [0, 1]).all():
        raise MetricInputError("y_true debe contener 0 y 1.")

    predicted = _validate_probabilities(probabilities)

    return float(np.mean((predicted - actual) ** 2))


def log_loss(
    y_true: Sequence[int],
    probabilities: Sequence[float],
    *,
    epsilon: float = 1e-15,
) -> float:
    """
    Binary logarithmic loss.

    LL = -mean(y log(p) + (1-y) log(1-p))
    """
    _validate_equal_length(y_true, probabilities)

    actual = np.asarray(y_true, dtype=float)
    if not np.isin(actual, [0, 1]).all():
        raise MetricInputError("y_true debe contener 0 y 1.")

    predicted = _validate_probabilities(probabilities)
    predicted = np.clip(predicted, epsilon, 1.0 - epsilon)

    value = -np.mean(
        actual * np.log(predicted)
        + (1.0 - actual) * np.log(1.0 - predicted)
    )

    return float(value)


@dataclass(frozen=True, slots=True)
class CalibrationBin:
    lower: float
    upper: float
    n: int
    mean_predicted: float
    observed_rate: float


def calibration_bins(
    y_true: Sequence[int],
    probabilities: Sequence[float],
    *,
    bins: int = 10,
) -> tuple[CalibrationBin, ...]:
    """
    Reliability/calibration bins.

    This describes calibration; it does not prove that a model is
    clinically useful.
    """
    if bins < 2:
        raise MetricInputError("Debe haber al menos dos bins.")

    _validate_equal_length(y_true, probabilities)

    actual = np.asarray(y_true, dtype=int)
    predicted = _validate_probabilities(probabilities)

    if not np.isin(actual, [0, 1]).all():
        raise MetricInputError("y_true debe contener 0 y 1.")

    edges = np.linspace(0.0, 1.0, bins + 1)
    result: list[CalibrationBin] = []

    for index in range(bins):
        lower = float(edges[index])
        upper = float(edges[index + 1])

        if index == bins - 1:
            mask = (predicted >= lower) & (predicted <= upper)
        else:
            mask = (predicted >= lower) & (predicted < upper)

        if not np.any(mask):
            continue

        result.append(
            CalibrationBin(
                lower=lower,
                upper=upper,
                n=int(np.sum(mask)),
                mean_predicted=float(np.mean(predicted[mask])),
                observed_rate=float(np.mean(actual[mask])),
            )
        )

    return tuple(result)


def expected_calibration_error(
    y_true: Sequence[int],
    probabilities: Sequence[float],
    *,
    bins: int = 10,
) -> float:
    """
    Expected Calibration Error.

    ECE is useful descriptively but is not a universal gold-standard
    calibration statistic. It must not be interpreted alone.
    """
    calibration = calibration_bins(
        y_true,
        probabilities,
        bins=bins,
    )

    total = len(y_true)

    if total == 0:
        raise MetricInputError("No hay observaciones.")

    return float(
        sum(
            (item.n / total)
            * abs(item.mean_predicted - item.observed_rate)
            for item in calibration
        )
    )


# ============================================================================
# RATE / FLOW / LOAD METRICS
# ============================================================================


def rate(
    events: float,
    exposure_time: float,
) -> float:
    """
    Generic event rate.

    rate = events / exposure_time

    Units are determined entirely by the caller.
    """
    if events < 0:
        raise MetricInputError("events no puede ser negativo.")

    if exposure_time <= 0:
        raise MetricInputError("exposure_time debe ser > 0.")

    return events / exposure_time


def growth_rate(
    current: float,
    previous: float,
) -> float:
    """
    Relative growth rate:

        (current - previous) / previous

    The result is dimensionless.
    """
    if previous == 0:
        raise MetricInputError(
            "No puede calcularse crecimiento relativo con baseline cero."
        )

    return (current - previous) / previous


def first_difference(
    current: float,
    previous: float,
    delta_t: float,
) -> float:
    """Approximate dx/dt."""
    if delta_t <= 0:
        raise MetricInputError("delta_t debe ser > 0.")

    return (current - previous) / delta_t


def second_difference(
    current: float,
    previous: float,
    previous_previous: float,
    delta_t: float,
) -> float:
    """Approximate d²x/dt² using equally spaced observations."""
    if delta_t <= 0:
        raise MetricInputError("delta_t debe ser > 0.")

    return (
        current
        - 2.0 * previous
        + previous_previous
    ) / (delta_t**2)


def utilization(
    demand: float,
    effective_capacity: float,
) -> float:
    """
    Load/capacity ratio.

        utilization = demand / effective_capacity

    Unlike a probability, this value MAY exceed 1.

        < 1  -> demand below capacity
        = 1  -> demand equals capacity
        > 1  -> demand exceeds capacity
    """
    if demand < 0:
        raise MetricInputError("demand no puede ser negativa.")

    if effective_capacity <= 0:
        raise MetricInputError(
            "effective_capacity debe ser > 0."
        )

    return demand / effective_capacity


# ============================================================================
# DROUGHT
# ============================================================================


def standardized_anomaly(
    value: float,
    mean: float,
    standard_deviation: float,
) -> float:
    """
    Standardized anomaly.

        z = (x - μ) / σ

    This is NOT SPI/SPEI.

    It must not be labelled as a drought index without the required
    distributional methodology.
    """
    if standard_deviation <= 0:
        raise MetricInputError(
            "standard_deviation debe ser > 0."
        )

    return (value - mean) / standard_deviation


# ============================================================================
# VALIDATED INSTRUMENT REGISTRY
# ============================================================================

# References are deliberately explicit.
# PubMed IDs/DOIs are recorded where the scientific evidence was verified.
#
# This registry does NOT claim that every instrument is validated
# specifically for Ceuta. That distinction is essential.

VALIDATED_METRICS: Final[
    Mapping[str, MetricDefinition]
] = {
    "mse": MetricDefinition(
        id="mse",
        name="Mean Squared Error",
        domain=MetricDomain.PREDICTION,
        kind=MetricKind.MODEL_EVALUATION,
        status=ValidationStatus.VALIDATED,
        description="Mean squared prediction error.",
        unit="squared outcome unit",
        output_type="continuous",
        formula="mean((y - y_hat)^2)",
        evidence_level=EvidenceLevel.METHODOLOGICAL_STANDARD,
        evidence_references=(),
        validated_population=None,
        validated_context="General statistical prediction evaluation.",
        limitations=(
            "Sensitive to large errors.",
            "Not directly interpretable as probability.",
        ),
        permitted_channels=frozenset(
            {OutputChannel.INTERNAL, OutputChannel.PRIVATE}
        ),
        individual_use=False,
        population_use=True,
        causal_interpretation_allowed=False,
        predictive_use_allowed=True,
    ),
    "rmse": MetricDefinition(
        id="rmse",
        name="Root Mean Squared Error",
        domain=MetricDomain.PREDICTION,
        kind=MetricKind.MODEL_EVALUATION,
        status=ValidationStatus.VALIDATED,
        description="Root mean squared prediction error.",
        unit="outcome unit",
        output_type="continuous",
        formula="sqrt(mean((y - y_hat)^2))",
        evidence_level=EvidenceLevel.METHODOLOGICAL_STANDARD,
        evidence_references=(),
        validated_population=None,
        validated_context="General statistical prediction evaluation.",
        limitations=(
            "Sensitive to outliers.",
            "Must be interpreted in the scale of the outcome.",
        ),
        permitted_channels=frozenset(
            {OutputChannel.INTERNAL, OutputChannel.PRIVATE}
        ),
        individual_use=False,
        population_use=True,
        causal_interpretation_allowed=False,
        predictive_use_allowed=True,
    ),
    "mae": MetricDefinition(
        id="mae",
        name="Mean Absolute Error",
        domain=MetricDomain.PREDICTION,
        kind=MetricKind.MODEL_EVALUATION,
        status=ValidationStatus.VALIDATED,
        description="Mean absolute prediction error.",
        unit="outcome unit",
        output_type="continuous",
        formula="mean(|y - y_hat|)",
        evidence_level=EvidenceLevel.METHODOLOGICAL_STANDARD,
        evidence_references=(),
        validated_population=None,
        validated_context="General statistical prediction evaluation.",
        limitations=(
            "Does not describe calibration of probabilistic predictions.",
        ),
        permitted_channels=frozenset(
            {OutputChannel.INTERNAL, OutputChannel.PRIVATE}
        ),
        individual_use=False,
        population_use=True,
        causal_interpretation_allowed=False,
        predictive_use_allowed=True,
    ),
    "brier_score": MetricDefinition(
        id="brier_score",
        name="Brier Score",
        domain=MetricDomain.CALIBRATION,
        kind=MetricKind.MODEL_EVALUATION,
        status=ValidationStatus.VALIDATED,
        description="Proper scoring rule for probabilistic binary predictions.",
        unit="dimensionless",
        output_type="continuous",
        formula="mean((p - y)^2)",
        evidence_level=EvidenceLevel.PEER_REVIEWED,
        evidence_references=(
            "PMID:31093548",
            "PMID:31093557",
        ),
        validated_population=None,
        validated_context="Probabilistic binary prediction.",
        limitations=(
            "Depends on outcome prevalence.",
            "Does not establish clinical or operational utility.",
        ),
        permitted_channels=frozenset(
            {OutputChannel.INTERNAL, OutputChannel.PRIVATE}
        ),
        individual_use=False,
        population_use=True,
        causal_interpretation_allowed=False,
        predictive_use_allowed=True,
    ),
    "sensitivity": MetricDefinition(
        id="sensitivity",
        name="Sensitivity",
        domain=MetricDomain.CLASSIFICATION,
        kind=MetricKind.MODEL_EVALUATION,
        status=ValidationStatus.VALIDATED,
        description="Probability of a positive classification among true positives.",
        unit="proportion",
        output_type="continuous",
        formula="TP / (TP + FN)",
        evidence_level=EvidenceLevel.METHODOLOGICAL_STANDARD,
        evidence_references=(),
        validated_population=None,
        validated_context="Binary classification.",
        limitations=(
            "Depends on the selected classification threshold.",
        ),
        permitted_channels=frozenset(
            {OutputChannel.INTERNAL, OutputChannel.PRIVATE}
        ),
        individual_use=False,
        population_use=True,
        causal_interpretation_allowed=False,
        predictive_use_allowed=True,
    ),
    "specificity": MetricDefinition(
        id="specificity",
        name="Specificity",
        domain=MetricDomain.CLASSIFICATION,
        kind=MetricKind.MODEL_EVALUATION,
        status=ValidationStatus.VALIDATED,
        description="Probability of a negative classification among true negatives.",
        unit="proportion",
        output_type="continuous",
        formula="TN / (TN + FP)",
        evidence_level=EvidenceLevel.METHODOLOGICAL_STANDARD,
        evidence_references=(),
        validated_population=None,
        validated_context="Binary classification.",
        limitations=(
            "Depends on the selected classification threshold.",
        ),
        permitted_channels=frozenset(
            {OutputChannel.INTERNAL, OutputChannel.PRIVATE}
        ),
        individual_use=False,
        population_use=True,
        causal_interpretation_allowed=False,
        predictive_use_allowed=True,
    ),
    "mcc": MetricDefinition(
        id="mcc",
        name="Matthews Correlation Coefficient",
        domain=MetricDomain.CLASSIFICATION,
        kind=MetricKind.MODEL_EVALUATION,
        status=ValidationStatus.VALIDATED,
        description="Correlation-based binary classification metric.",
        unit="dimensionless",
        output_type="continuous",
        formula=(
            "(TP*TN-FP*FN) / "
            "sqrt((TP+FP)(TP+FN)(TN+FP)(TN+FN))"
        ),
        evidence_level=EvidenceLevel.METHODOLOGICAL_STANDARD,
        evidence_references=(),
        validated_population=None,
        validated_context="Binary classification.",
        limitations=(
            "Undefined for degenerate confusion matrices.",
        ),
        permitted_channels=frozenset(
            {OutputChannel.INTERNAL, OutputChannel.PRIVATE}
        ),
        individual_use=False,
        population_use=True,
        causal_interpretation_allowed=False,
        predictive_use_allowed=True,
    ),
    "phq9": MetricDefinition(
        id="phq9",
        name="Patient Health Questionnaire-9",
        domain=MetricDomain.MENTAL_HEALTH,
        kind=MetricKind.SCALE,
        status=ValidationStatus.VALIDATED_ELSEWHERE,
        description=(
            "Validated symptom severity/screening instrument for "
            "depressive symptoms."
        ),
        unit="score",
        output_type="ordinal_score",
        formula="sum of 9 item scores",
        evidence_level=EvidenceLevel.PEER_REVIEWED,
        evidence_references=(
            "PMID:37264532",
            "PMID:33601674",
        ),
        validated_population=(
            "Multiple populations; performance varies by setting."
        ),
        validated_context="Depressive symptom screening/severity assessment.",
        limitations=(
            "Screening instrument; not by itself a psychiatric diagnosis.",
            "Cut-points depend on context and intended use.",
            "Should not be interpreted independently of clinical context.",
        ),
        permitted_channels=frozenset(
            {OutputChannel.INTERNAL, OutputChannel.PRIVATE, OutputChannel.PUBLIC_USER}
        ),
        individual_use=True,
        population_use=True,
        causal_interpretation_allowed=False,
        predictive_use_allowed=False,
    ),
    "gad7": MetricDefinition(
        id="gad7",
        name="Generalized Anxiety Disorder-7",
        domain=MetricDomain.MENTAL_HEALTH,
        kind=MetricKind.SCALE,
        status=ValidationStatus.VALIDATED_ELSEWHERE,
        description="Validated anxiety symptom screening instrument.",
        unit="score",
        output_type="ordinal_score",
        formula="sum of 7 item scores",
        evidence_level=EvidenceLevel.PEER_REVIEWED,
        evidence_references=(
            "PMID:37264532",
            "PMID:33601674",
        ),
        validated_population=(
            "Multiple populations; performance varies by setting."
        ),
        validated_context="Anxiety symptom screening.",
        limitations=(
            "Screening instrument; not by itself a diagnosis.",
            "Cut-points are context-dependent.",
        ),
        permitted_channels=frozenset(
            {OutputChannel.INTERNAL, OutputChannel.PRIVATE, OutputChannel.PUBLIC_USER}
        ),
        individual_use=True,
        population_use=True,
        causal_interpretation_allowed=False,
        predictive_use_allowed=False,
    ),
    "pcl5": MetricDefinition(
        id="pcl5",
        name="PTSD Checklist for DSM-5",
        domain=MetricDomain.TRAUMA,
        kind=MetricKind.SCALE,
        status=ValidationStatus.VALIDATED_ELSEWHERE,
        description="Validated PTSD symptom assessment instrument.",
        unit="score",
        output_type="ordinal_score",
        formula="sum of 20 item scores",
        evidence_level=EvidenceLevel.PEER_REVIEWED,
        evidence_references=(
            "PMID:37264532",
            "PMID:36843081",
            "PMID:38911962",
        ),
        validated_population=(
            "Multiple populations; Spanish validation evidence exists "
            "in specific clinical samples."
        ),
        validated_context="PTSD symptom assessment/screening.",
        limitations=(
            "Not equivalent to a clinical diagnosis.",
            "Performance depends on population and context.",
        ),
        permitted_channels=frozenset(
            {OutputChannel.INTERNAL, OutputChannel.PRIVATE, OutputChannel.PUBLIC_USER}
        ),
        individual_use=True,
        population_use=True,
        causal_interpretation_allowed=False,
        predictive_use_allowed=False,
    ),
    "aemet_ipif": MetricDefinition(
        id="aemet_ipif",
        name="IPIF - Índice de Peligro de Incendios Forestales",
        domain=MetricDomain.FIRE,
        kind=MetricKind.INDEX,
        status=ValidationStatus.OFFICIAL,
        description=(
            "Índice oficial de AEMET para caracterizar el peligro "
            "de incendios forestales."
        ),
        unit="official categorical/index output",
        output_type="official_index",
        formula=None,
        evidence_level=EvidenceLevel.OFFICIAL,
        evidence_references=(
            "AEMET: IPIF, 28-05-2026",
        ),
        validated_population="Territory covered by AEMET operational system.",
        validated_context="Operational wildfire danger assessment in Spain.",
        limitations=(
            "No debe transformarse en probabilidad de incendio sin "
            "un modelo de calibración específico.",
            "No es una predicción individual de comportamiento humano.",
        ),
        permitted_channels=frozenset(
            {OutputChannel.INTERNAL, OutputChannel.PRIVATE, OutputChannel.PUBLIC_USER}
        ),
        individual_use=False,
        population_use=True,
        causal_interpretation_allowed=False,
        predictive_use_allowed=True,
    ),
}


# ============================================================================
# REGISTRY ACCESS
# ============================================================================


def get_metric_definition(metric_id: str) -> MetricDefinition:
    """Return a registered metric or raise."""
    try:
        return VALIDATED_METRICS[metric_id]
    except KeyError as exc:
        raise MetricError(
            f"Métrica no registrada: {metric_id}"
        ) from exc


def assert_metric_executable(metric_id: str) -> MetricDefinition:
    """
    Hard gate preventing execution of non-validated metrics.
    """
    definition = get_metric_definition(metric_id)

    allowed_statuses = {
        ValidationStatus.VALIDATED,
        ValidationStatus.VALIDATED_ELSEWHERE,
        ValidationStatus.OFFICIAL,
    }

    if definition.status not in allowed_statuses:
        raise MetricNotValidatedError(
            f"La métrica '{metric_id}' no está autorizada para ejecución: "
            f"{definition.status}."
        )

    return definition


def assert_output_permitted(
    metric_id: str,
    channel: OutputChannel,
) -> MetricDefinition:
    """
    Prevent internal intelligence objects from being exposed
    through an unauthorized output channel.
    """
    definition = assert_metric_executable(metric_id)

    if channel not in definition.permitted_channels:
        raise MetricNotPermittedError(
            f"La métrica '{metric_id}' no puede utilizarse en "
            f"el canal '{channel}'."
        )

    return definition


# ============================================================================
# SCIENTIFIC SAFETY GATES
# ============================================================================


def require_validated_metric(
    metric_id: str,
    *,
    channel: OutputChannel = OutputChannel.INTERNAL,
) -> MetricDefinition:
    """
    Public entry point for metric execution.

    Every production calculation should pass this gate.
    """
    return assert_output_permitted(
        metric_id,
        channel,
    )


def require_population_context(
    metric_id: str,
    *,
    intended_population: str,
) -> None:
    """
    Prevent silent extrapolation from a validated population to
    an unrelated population.

    This function intentionally does not attempt automatic
    transportability inference.
    """
    definition = get_metric_definition(metric_id)

    if not intended_population.strip():
        raise MetricInputError(
            "Debe especificarse la población de aplicación."
        )

    if definition.validated_population is None:
        return

    # Transportability must be explicitly assessed elsewhere.
    raise MetricNotValidatedError(
        f"La métrica '{metric_id}' tiene una población/contexto "
        "de validación documentado. Su transferencia a una nueva "
        "población requiere evaluación explícita de transportabilidad."
    )


def prohibit_unvalidated_risk_probability(
    *,
    metric_id: str,
    calibrated: bool,
) -> None:
    """
    A score/index cannot be silently converted into a probability.
    """
    if not calibrated:
        raise MetricNotValidatedError(
            f"'{metric_id}' no puede expresarse como probabilidad "
            "de riesgo sin calibración empírica."
        )


# ============================================================================
# CEUTIA STRATEGIC-RISK REGISTRY
# ============================================================================

# IMPORTANT:
#
# These entries are intentionally CATALOGUED rather than VALIDATED.
#
# CeutIA must be capable of representing these risks:
#
# - intergroup violence;
# - riots;
# - political violence;
# - armed conflict;
# - institutional destabilization;
# - military uprising;
# - external escalation;
# - new border-entry/invasion events.
#
# But no arbitrary "Ceuta civil-war formula" is invented here.
#
# A future model may be registered only after:
#   1. explicit outcome definition;
#   2. historical dataset;
#   3. reproducible predictors;
#   4. temporal validation;
#   5. calibration;
#   6. out-of-sample evaluation;
#   7. uncertainty estimation;
#   8. bias assessment;
#   9. transportability assessment;
#   10. documented scientific/operational methodology.

STRATEGIC_RISK_REGISTRY: Final[
    Mapping[str, MetricDefinition]
] = {
    "intergroup_violence_early_warning": MetricDefinition(
        id="intergroup_violence_early_warning",
        name="Intergroup Violence Early Warning",
        domain=MetricDomain.VIOLENCE,
        kind=MetricKind.RISK_MODEL,
        status=ValidationStatus.CATALOGUED,
        description=(
            "Future calibrated event-prediction model for changes in "
            "intergroup violence."
        ),
        unit="probability only after calibration",
        output_type="probability",
        formula=None,
        evidence_level=EvidenceLevel.PEER_REVIEWED,
        evidence_references=(),
        validated_population=None,
        validated_context=None,
        limitations=(
            "No probability may be generated until a validated model exists.",
            "Must predict events, not group-based dangerousness.",
        ),
        permitted_channels=frozenset(
            {OutputChannel.INTERNAL, OutputChannel.PRIVATE}
        ),
        individual_use=False,
        population_use=True,
        causal_interpretation_allowed=False,
        predictive_use_allowed=False,
    ),
    "political_violence_early_warning": MetricDefinition(
        id="political_violence_early_warning",
        name="Political Violence Early Warning",
        domain=MetricDomain.POLITICAL_VIOLENCE,
        kind=MetricKind.RISK_MODEL,
        status=ValidationStatus.CATALOGUED,
        description=(
            "Future event-based model for political violence escalation."
        ),
        unit="probability only after calibration",
        output_type="probability",
        formula=None,
        evidence_level=EvidenceLevel.PEER_REVIEWED,
        evidence_references=(),
        validated_population=None,
        validated_context=None,
        limitations=(
            "No arbitrary risk score is permitted.",
            "Requires retrospective and out-of-sample validation.",
        ),
        permitted_channels=frozenset(
            {OutputChannel.INTERNAL, OutputChannel.PRIVATE}
        ),
        individual_use=False,
        population_use=True,
        causal_interpretation_allowed=False,
        predictive_use_allowed=False,
    ),
    "armed_conflict_early_warning": MetricDefinition(
        id="armed_conflict_early_warning",
        name="Armed Conflict Early Warning",
        domain=MetricDomain.CONFLICT,
        kind=MetricKind.RISK_MODEL,
        status=ValidationStatus.CATALOGUED,
        description="Event-level early-warning model.",
        unit="probability only after calibration",
        output_type="probability",
        formula=None,
        evidence_level=EvidenceLevel.PEER_REVIEWED,
        evidence_references=(),
        validated_population=None,
        validated_context=None,
        limitations=(
            "Rare-event prediction requires careful calibration.",
            "No deterministic threshold may be interpreted as certainty.",
        ),
        permitted_channels=frozenset(
            {OutputChannel.INTERNAL, OutputChannel.PRIVATE}
        ),
        individual_use=False,
        population_use=True,
        causal_interpretation_allowed=False,
        predictive_use_allowed=False,
    ),
    "external_escalation": MetricDefinition(
        id="external_escalation",
        name="External Strategic Escalation",
        domain=MetricDomain.STRATEGIC,
        kind=MetricKind.RISK_MODEL,
        status=ValidationStatus.CATALOGUED,
        description=(
            "Future model for observable external escalation events."
        ),
        unit="probability only after calibration",
        output_type="probability",
        formula=None,
        evidence_level=EvidenceLevel.PEER_REVIEWED,
        evidence_references=(),
        validated_population=None,
        validated_context=None,
        limitations=(
            "Requires explicit event definition.",
            "Geopolitical hypotheses must remain hypotheses until corroborated.",
        ),
        permitted_channels=frozenset(
            {OutputChannel.INTERNAL, OutputChannel.PRIVATE}
        ),
        individual_use=False,
        population_use=True,
        causal_interpretation_allowed=False,
        predictive_use_allowed=False,
    ),
    "border_entry_event": MetricDefinition(
        id="border_entry_event",
        name="Border Entry Event Risk",
        domain=MetricDomain.SECURITY,
        kind=MetricKind.RISK_MODEL,
        status=ValidationStatus.CATALOGUED,
        description=(
            "Future calibrated prediction of defined border-entry events."
        ),
        unit="probability only after calibration",
        output_type="probability",
        formula=None,
        evidence_level=EvidenceLevel.OFFICIAL,
        evidence_references=(),
        validated_population=None,
        validated_context=None,
        limitations=(
            "Must define the event operationally.",
            "Cannot infer hostile intent from nationality or ethnicity.",
        ),
        permitted_channels=frozenset(
            {OutputChannel.INTERNAL, OutputChannel.PRIVATE}
        ),
        individual_use=False,
        population_use=True,
        causal_interpretation_allowed=False,
        predictive_use_allowed=False,
    ),
}


# ============================================================================
# REGISTRY INTEGRITY
# ============================================================================


def validate_registry_integrity() -> tuple[str, ...]:
    """
    Validate structural invariants of the registry.

    Returns an empty tuple when valid.
    """
    errors: list[str] = []

    all_metrics = {
        **VALIDATED_METRICS,
        **STRATEGIC_RISK_REGISTRY,
    }

    for key, definition in all_metrics.items():
        if key != definition.id:
            errors.append(
                f"Registry key '{key}' != metric id '{definition.id}'."
            )

        if definition.status in {
            ValidationStatus.VALIDATED,
            ValidationStatus.VALIDATED_ELSEWHERE,
            ValidationStatus.OFFICIAL,
        }:
            if not definition.description.strip():
                errors.append(
                    f"{definition.id}: missing description."
                )

            if not definition.unit.strip():
                errors.append(
                    f"{definition.id}: missing unit."
                )

            if not definition.evidence_references:
                errors.append(
                    f"{definition.id}: validated/official metric "
                    "requires evidence references."
                )

    return tuple(errors)


# ============================================================================
# SCIENTIFIC INVARIANTS
# ============================================================================


SCIENTIFIC_METRIC_INVARIANTS: Final[tuple[str, ...]] = (
    "Ninguna fórmula se considera válida únicamente por ser matemáticamente elegante.",
    "Ninguna métrica puede convertirse en probabilidad de riesgo sin calibración.",
    "Una escala validada no equivale automáticamente a un diagnóstico.",
    "Una métrica de discriminación no demuestra causalidad.",
    "AUC no sustituye a la calibración.",
    "Brier score no demuestra utilidad clínica ni operativa.",
    "Un índice oficial no debe modificarse silenciosamente.",
    "Un modelo publicado no se considera validado para Ceuta sin evaluar transportabilidad.",
    "Las métricas deben conservar sus unidades y contexto de aplicación.",
    "Los modelos de eventos raros requieren validación temporal y calibración específica.",
    "La incertidumbre no puede eliminarse mediante redondeo.",
    "La falta de datos no debe convertirse en una puntuación artificial de riesgo.",
    "Una señal social no constituye por sí misma evidencia causal.",
    "Una métrica de riesgo debe predecir eventos o estados definidos, no la peligrosidad inherente de grupos humanos.",
    "No se permite inferir riesgo individual a partir de nacionalidad, origen étnico u otros atributos protegidos.",
    "Las predicciones estratégicas deben permanecer en INTERNAL/PRIVATE salvo que una política posterior autorice una salida pública específica.",
    "PUBLIC_USER recibe recomendaciones derivadas, no los objetos internos de inteligencia.",
)


def get_scientific_metric_invariants() -> tuple[str, ...]:
    """Return the immutable metric-science invariants."""
    return SCIENTIFIC_METRIC_INVARIANTS


# ============================================================================
# EXPORTS
# ============================================================================


__all__ = [
    "CalibrationBin",
    "ConfusionMatrix",
    "EvidenceLevel",
    "MetricDefinition",
    "MetricDomain",
    "MetricError",
    "MetricInputError",
    "MetricKind",
    "MetricNotPermittedError",
    "MetricNotValidatedError",
    "OutputChannel",
    "STRATEGIC_RISK_REGISTRY",
    "SCIENTIFIC_METRIC_INVARIANTS",
    "VALIDATED_METRICS",
    "accuracy",
    "balanced_accuracy",
    "brier_score",
    "calibration_bins",
    "confusion_matrix_binary",
    "expected_calibration_error",
    "f1_score",
    "first_difference",
    "get_metric_definition",
    "get_scientific_metric_invariants",
    "growth_rate",
    "log_loss",
    "mae",
    "matthews_correlation_coefficient",
    "mse",
    "negative_predictive_value",
    "positive_predictive_value",
    "prohibit_unvalidated_risk_probability",
    "rate",
    "require_population_context",
    "require_validated_metric",
    "r_squared",
    "rmse",
    "second_difference",
    "sensitivity",
    "specificity",
    "standardized_anomaly",
    "utilization",
    "validate_registry_integrity",
]