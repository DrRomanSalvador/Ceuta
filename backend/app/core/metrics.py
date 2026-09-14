"""Catálogo matemático y motor de métricas de CeutIA.

Este módulo concentra las métricas, índices, escalas y primitivas matemáticas
que pueden utilizar los componentes analíticos de CeutIA. El registro distingue
entre metodologías validadas, indicadores oficiales, metodologías validadas en
otros contextos y capacidades todavía no autorizadas para producir riesgo.

Principios:
- una fórmula matemáticamente correcta no equivale a una métrica validada;
- una escala validada no equivale a un diagnóstico;
- discriminación no equivale a calibración ni a causalidad;
- un modelo publicado no se considera automáticamente validado para Ceuta;
- los índices oficiales se consumen según su definición oficial y no se
  reconstruyen con una fórmula aproximada bajo el mismo nombre;
- las señales de violencia/conflicto describen eventos observables y dinámica
  del sistema, no "peligrosidad" inherente de grupos o nacionalidades;
- ninguna probabilidad de riesgo estratégico se ejecuta sin outcome definido,
  datos apropiados, validación temporal/external, calibración y evaluación fuera
  de muestra.

El módulo no ingiere datos ni decide acciones. Es una capa determinista de
matemática, validación de entradas, metadatos epistemológicos y registro de
permisos. Los modelos estadísticos complejos pueden vivir posteriormente en
módulos de análisis, pero deben registrarse aquí si pretenden ser una métrica
oficial del sistema.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from math import erf, exp, isfinite, log, pi, sqrt
from statistics import NormalDist
from typing import Final, Iterable, Mapping, Sequence

import numpy as np


# ---------------------------------------------------------------------------
# Taxonomía
# ---------------------------------------------------------------------------


class MetricDomain(StrEnum):
    GENERAL_STATISTICS = "general_statistics"
    DISTRIBUTION = "distribution"
    PREDICTION = "prediction"
    CLASSIFICATION = "classification"
    CALIBRATION = "calibration"
    TIME_SERIES = "time_series"
    CHANGE_POINT = "change_point"
    EARLY_WARNING = "early_warning"
    BIOMEDICAL = "biomedical"
    EPIDEMIOLOGY = "epidemiology"
    CARDIOVASCULAR = "cardiovascular"
    MENTAL_HEALTH = "mental_health"
    TRAUMA = "trauma"
    SLEEP = "sleep"
    STRESS = "stress"
    WELLBEING = "wellbeing"
    ALLOSTATIC_LOAD = "allostatic_load"
    ENVIRONMENT = "environment"
    CLIMATE = "climate"
    DROUGHT = "drought"
    EXTREME_RAINFALL = "extreme_rainfall"
    HEAT = "heat"
    FIRE = "fire"
    AIR_QUALITY = "air_quality"
    WATER = "water"
    DEMOGRAPHY = "demography"
    MIGRATION = "migration"
    SOCIOLOGY = "sociology"
    SOCIAL_COHESION = "social_cohesion"
    VIOLENCE = "violence"
    POLITICAL_VIOLENCE = "political_violence"
    CONFLICT = "conflict"
    SECURITY = "security"
    STRATEGIC = "strategic"
    CAPACITY = "capacity"
    QUEUEING = "queueing"
    RESILIENCE = "resilience"
    NETWORK = "network"
    SYSTEM_DYNAMICS = "system_dynamics"
    CAUSAL_INFERENCE = "causal_inference"
    SCENARIO = "scenario"


class ValidationStatus(StrEnum):
    VALIDATED = "validated"
    VALIDATED_ELSEWHERE = "validated_elsewhere"
    OFFICIAL = "official"
    CATALOGUED = "catalogued"
    EXPERIMENTAL = "experimental"
    NOT_VALIDATED_FOR_CEUTA = "not_validated_for_ceuta"
    BLOCKED = "blocked"


class OutputChannel(StrEnum):
    INTERNAL = "internal"
    PRIVATE = "private"
    PUBLIC_USER = "public_user"


class MetricKind(StrEnum):
    FORMULA = "formula"
    SCORE = "score"
    SCALE = "scale"
    INDEX = "index"
    RATE = "rate"
    MODEL_EVALUATION = "model_evaluation"
    RISK_MODEL = "risk_model"
    EARLY_WARNING = "early_warning"
    MODEL_PRIMITIVE = "model_primitive"


class EvidenceLevel(StrEnum):
    PEER_REVIEWED = "peer_reviewed"
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    OFFICIAL = "official"
    METHODOLOGICAL_STANDARD = "methodological_standard"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class MetricDefinition:
    """Definición epistemológica y operativa de una métrica."""

    id: str
    name: str
    domain: MetricDomain
    kind: MetricKind
    status: ValidationStatus
    description: str
    unit: str
    output_type: str
    formula: str | None = None
    evidence_level: EvidenceLevel = EvidenceLevel.OTHER
    evidence_references: tuple[str, ...] = ()
    validated_population: str | None = None
    validated_context: str | None = None
    limitations: tuple[str, ...] = ()
    permitted_channels: frozenset[OutputChannel] = frozenset(
        {OutputChannel.INTERNAL}
    )
    individual_use: bool = False
    population_use: bool = True
    causal_interpretation_allowed: bool = False
    predictive_use_allowed: bool = False
    executable: bool = True


class MetricError(ValueError):
    """Error base del motor de métricas."""


class MetricInputError(MetricError):
    """Entradas ausentes, incompatibles o fuera de dominio."""


class MetricNotValidatedError(MetricError):
    """Intento de ejecutar una métrica no autorizada."""


class MetricNotPermittedError(MetricError):
    """Uso de una métrica fuera de su canal permitido."""


# ---------------------------------------------------------------------------
# Utilidades numéricas
# ---------------------------------------------------------------------------


def _as_float_array(values: Sequence[float] | np.ndarray, *, name: str) -> np.ndarray:
    arr = np.asarray(values, dtype=float)
    if arr.ndim != 1:
        raise MetricInputError(f"{name} debe ser un vector unidimensional")
    if arr.size == 0:
        raise MetricInputError(f"{name} no puede estar vacío")
    if not np.all(np.isfinite(arr)):
        raise MetricInputError(f"{name} contiene valores no finitos")
    return arr


def _validate_same_length(*arrays: np.ndarray) -> None:
    lengths = {a.size for a in arrays}
    if len(lengths) != 1:
        raise MetricInputError("Todos los vectores deben tener la misma longitud")


def _validate_probabilities(values: Sequence[float] | np.ndarray) -> np.ndarray:
    arr = _as_float_array(values, name="probabilidades")
    if np.any((arr < 0.0) | (arr > 1.0)):
        raise MetricInputError("Las probabilidades deben pertenecer a [0, 1]")
    return arr


def _validate_binary(values: Sequence[int] | np.ndarray, *, name: str) -> np.ndarray:
    arr = np.asarray(values)
    if arr.ndim != 1 or arr.size == 0:
        raise MetricInputError(f"{name} debe ser un vector no vacío")
    if not np.all(np.isin(arr, [0, 1])):
        raise MetricInputError(f"{name} debe contener exclusivamente 0 y 1")
    return arr.astype(int)


def _require_at_least_two(values: np.ndarray, name: str) -> None:
    if values.size < 2:
        raise MetricInputError(f"{name} requiere al menos dos observaciones")


# ---------------------------------------------------------------------------
# Estadística descriptiva y variación
# ---------------------------------------------------------------------------


def mean(values: Sequence[float] | np.ndarray) -> float:
    return float(np.mean(_as_float_array(values, name="values")))


def variance(values: Sequence[float] | np.ndarray, *, ddof: int = 1) -> float:
    arr = _as_float_array(values, name="values")
    if ddof < 0 or ddof >= arr.size:
        raise MetricInputError("ddof incompatible con el tamaño de la muestra")
    return float(np.var(arr, ddof=ddof))


def standard_deviation(values: Sequence[float] | np.ndarray, *, ddof: int = 1) -> float:
    return sqrt(variance(values, ddof=ddof))


def coefficient_of_variation(values: Sequence[float] | np.ndarray) -> float:
    arr = _as_float_array(values, name="values")
    _require_at_least_two(arr, "values")
    m = float(np.mean(arr))
    if m == 0.0:
        raise MetricInputError("El coeficiente de variación no está definido con media 0")
    return float(np.std(arr, ddof=1) / abs(m))


def quantile(values: Sequence[float] | np.ndarray, q: float) -> float:
    arr = _as_float_array(values, name="values")
    if not 0.0 <= q <= 1.0:
        raise MetricInputError("q debe estar en [0, 1]")
    return float(np.quantile(arr, q))


def median_absolute_deviation(values: Sequence[float] | np.ndarray) -> float:
    arr = _as_float_array(values, name="values")
    med = np.median(arr)
    return float(np.median(np.abs(arr - med)))


def z_score(value: float, baseline: Sequence[float] | np.ndarray) -> float:
    arr = _as_float_array(baseline, name="baseline")
    _require_at_least_two(arr, "baseline")
    sd = float(np.std(arr, ddof=1))
    if sd == 0.0:
        raise MetricInputError("No se puede estandarizar una línea basal constante")
    return float((value - np.mean(arr)) / sd)


def standardized_anomaly(value: float, baseline: Sequence[float] | np.ndarray) -> float:
    """Anomalía estandarizada; no debe llamarse SPI/SPEI."""
    return z_score(value, baseline)


def entropy(probabilities: Sequence[float] | np.ndarray, *, base: float = 2.0) -> float:
    p = _validate_probabilities(probabilities)
    if base <= 0.0 or base == 1.0:
        raise MetricInputError("La base logarítmica debe ser positiva y distinta de 1")
    positive = p[p > 0]
    return float(-np.sum(positive * np.log(positive)) / np.log(base))


# ---------------------------------------------------------------------------
# Tasas, diferencias, crecimiento y carga
# ---------------------------------------------------------------------------


def rate(events: float, exposure: float, *, scale: float = 1.0) -> float:
    if exposure <= 0.0 or scale <= 0.0:
        raise MetricInputError("exposure y scale deben ser positivos")
    if events < 0.0:
        raise MetricInputError("events no puede ser negativo")
    return float(events / exposure * scale)


def growth_rate(previous: float, current: float, *, duration: float = 1.0) -> float:
    if duration <= 0.0:
        raise MetricInputError("duration debe ser positiva")
    if previous == 0.0:
        raise MetricInputError("No existe tasa relativa definida desde un valor basal 0")
    return float((current - previous) / abs(previous) / duration)


def log_growth_rate(previous: float, current: float, *, duration: float = 1.0) -> float:
    if previous <= 0.0 or current <= 0.0 or duration <= 0.0:
        raise MetricInputError("Se requieren valores positivos y duration > 0")
    return float(np.log(current / previous) / duration)


def first_difference(values: Sequence[float] | np.ndarray) -> np.ndarray:
    return np.diff(_as_float_array(values, name="values"))


def second_difference(values: Sequence[float] | np.ndarray) -> np.ndarray:
    return np.diff(_as_float_array(values, name="values"), n=2)


def relative_change(previous: float, current: float) -> float:
    if previous == 0.0:
        raise MetricInputError("previous no puede ser 0")
    return float((current - previous) / abs(previous))


def demand_capacity_ratio(demand: float, capacity: float) -> float:
    if demand < 0.0 or capacity <= 0.0:
        raise MetricInputError("demand >= 0 y capacity > 0 son obligatorios")
    return float(demand / capacity)


def utilization(demand: float, capacity: float) -> float:
    """Utilización como demanda/capacidad. Puede superar 1 durante saturación."""
    return demand_capacity_ratio(demand, capacity)


def excess_demand(demand: float, capacity: float) -> float:
    if demand < 0.0 or capacity <= 0.0:
        raise MetricInputError("demand >= 0 y capacity > 0 son obligatorios")
    return float(max(0.0, demand - capacity))


def service_capacity_gap(arrival_rate: float, service_rate: float) -> float:
    if arrival_rate < 0.0 or service_rate <= 0.0:
        raise MetricInputError("arrival_rate >= 0 y service_rate > 0 son obligatorios")
    return float(service_rate - arrival_rate)


def cumulative_load(values: Sequence[float] | np.ndarray, *, dt: float = 1.0) -> float:
    arr = _as_float_array(values, name="values")
    if dt <= 0.0:
        raise MetricInputError("dt debe ser positivo")
    return float(np.sum(arr) * dt)


def exponential_moving_average(values: Sequence[float] | np.ndarray, alpha: float) -> np.ndarray:
    arr = _as_float_array(values, name="values")
    if not 0.0 < alpha <= 1.0:
        raise MetricInputError("alpha debe estar en (0, 1]")
    out = np.empty_like(arr)
    out[0] = arr[0]
    for i in range(1, arr.size):
        out[i] = alpha * arr[i] + (1.0 - alpha) * out[i - 1]
    return out


def autocorrelation(values: Sequence[float] | np.ndarray, lag: int = 1) -> float:
    arr = _as_float_array(values, name="values")
    if lag < 1 or lag >= arr.size:
        raise MetricInputError("lag debe estar entre 1 y n-1")
    if arr.size < lag + 2:
        raise MetricInputError("autocorrelation requiere al menos lag+2 observaciones")
    x = arr[:-lag]
    y = arr[lag:]
    sx = np.std(x, ddof=1)
    sy = np.std(y, ddof=1)
    if sx == 0.0 or sy == 0.0:
        raise MetricInputError("No se puede calcular correlación con varianza 0")
    return float(np.corrcoef(x, y)[0, 1])


# ---------------------------------------------------------------------------
# Evaluación de predicción y clasificación
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class ConfusionMatrix:
    true_positive: int
    false_positive: int
    true_negative: int
    false_negative: int

    @property
    def total(self) -> int:
        return (
            self.true_positive
            + self.false_positive
            + self.true_negative
            + self.false_negative
        )


def confusion_matrix_binary(
    y_true: Sequence[int] | np.ndarray,
    y_pred: Sequence[int] | np.ndarray,
) -> ConfusionMatrix:
    truth = _validate_binary(y_true, name="y_true")
    pred = _validate_binary(y_pred, name="y_pred")
    _validate_same_length(truth, pred)
    return ConfusionMatrix(
        true_positive=int(np.sum((truth == 1) & (pred == 1))),
        false_positive=int(np.sum((truth == 0) & (pred == 1))),
        true_negative=int(np.sum((truth == 0) & (pred == 0))),
        false_negative=int(np.sum((truth == 1) & (pred == 0))),
    )


def sensitivity(cm: ConfusionMatrix) -> float:
    denominator = cm.true_positive + cm.false_negative
    if denominator == 0:
        raise MetricInputError("Sensibilidad indefinida sin casos positivos reales")
    return cm.true_positive / denominator


def specificity(cm: ConfusionMatrix) -> float:
    denominator = cm.true_negative + cm.false_positive
    if denominator == 0:
        raise MetricInputError("Especificidad indefinida sin casos negativos reales")
    return cm.true_negative / denominator


def positive_predictive_value(cm: ConfusionMatrix) -> float:
    denominator = cm.true_positive + cm.false_positive
    if denominator == 0:
        raise MetricInputError("PPV indefinido sin predicciones positivas")
    return cm.true_positive / denominator


def negative_predictive_value(cm: ConfusionMatrix) -> float:
    denominator = cm.true_negative + cm.false_negative
    if denominator == 0:
        raise MetricInputError("NPV indefinido sin predicciones negativas")
    return cm.true_negative / denominator


def accuracy(cm: ConfusionMatrix) -> float:
    if cm.total == 0:
        raise MetricInputError("Matriz vacía")
    return (cm.true_positive + cm.true_negative) / cm.total


def balanced_accuracy(cm: ConfusionMatrix) -> float:
    return (sensitivity(cm) + specificity(cm)) / 2.0


def f1_score(cm: ConfusionMatrix) -> float:
    denominator = 2 * cm.true_positive + cm.false_positive + cm.false_negative
    if denominator == 0:
        raise MetricInputError("F1 indefinido sin positivos")
    return 2 * cm.true_positive / denominator


def matthews_correlation_coefficient(cm: ConfusionMatrix) -> float:
    numerator = cm.true_positive * cm.true_negative - cm.false_positive * cm.false_negative
    denominator = sqrt(
        (cm.true_positive + cm.false_positive)
        * (cm.true_positive + cm.false_negative)
        * (cm.true_negative + cm.false_positive)
        * (cm.true_negative + cm.false_negative)
    )
    if denominator == 0.0:
        raise MetricInputError("MCC indefinido para esta matriz")
    return numerator / denominator


def mse(y_true: Sequence[float] | np.ndarray, y_pred: Sequence[float] | np.ndarray) -> float:
    truth = _as_float_array(y_true, name="y_true")
    pred = _as_float_array(y_pred, name="y_pred")
    _validate_same_length(truth, pred)
    return float(np.mean((truth - pred) ** 2))


def rmse(y_true: Sequence[float] | np.ndarray, y_pred: Sequence[float] | np.ndarray) -> float:
    return sqrt(mse(y_true, y_pred))


def mae(y_true: Sequence[float] | np.ndarray, y_pred: Sequence[float] | np.ndarray) -> float:
    truth = _as_float_array(y_true, name="y_true")
    pred = _as_float_array(y_pred, name="y_pred")
    _validate_same_length(truth, pred)
    return float(np.mean(np.abs(truth - pred)))


def r_squared(y_true: Sequence[float] | np.ndarray, y_pred: Sequence[float] | np.ndarray) -> float:
    truth = _as_float_array(y_true, name="y_true")
    pred = _as_float_array(y_pred, name="y_pred")
    _validate_same_length(truth, pred)
    total = float(np.sum((truth - np.mean(truth)) ** 2))
    if total == 0.0:
        raise MetricInputError("R² indefinido para una variable observada constante")
    residual = float(np.sum((truth - pred) ** 2))
    return 1.0 - residual / total


def brier_score(
    y_true: Sequence[int] | np.ndarray,
    probabilities: Sequence[float] | np.ndarray,
) -> float:
    truth = _validate_binary(y_true, name="y_true")
    prob = _validate_probabilities(probabilities)
    _validate_same_length(truth, prob)
    return float(np.mean((prob - truth) ** 2))


def log_loss(
    y_true: Sequence[int] | np.ndarray,
    probabilities: Sequence[float] | np.ndarray,
    *,
    eps: float = 1e-15,
) -> float:
    truth = _validate_binary(y_true, name="y_true")
    prob = _validate_probabilities(probabilities)
    _validate_same_length(truth, prob)
    if not 0.0 < eps < 0.5:
        raise MetricInputError("eps debe estar entre 0 y 0.5")
    p = np.clip(prob, eps, 1.0 - eps)
    return float(-np.mean(truth * np.log(p) + (1 - truth) * np.log(1 - p)))


def roc_auc(
    y_true: Sequence[int] | np.ndarray,
    scores: Sequence[float] | np.ndarray,
) -> float:
    """AUC ROC mediante la probabilidad de concordancia de rangos.

    En empates se asigna 0.5. Requiere ambas clases presentes.
    """
    truth = _validate_binary(y_true, name="y_true")
    score = _as_float_array(scores, name="scores")
    _validate_same_length(truth, score)
    positives = score[truth == 1]
    negatives = score[truth == 0]
    if positives.size == 0 or negatives.size == 0:
        raise MetricInputError("ROC-AUC requiere ambas clases")
    comparisons = positives[:, None] - negatives[None, :]
    return float((np.sum(comparisons > 0) + 0.5 * np.sum(comparisons == 0)) / comparisons.size)


def precision_recall_auc(
    y_true: Sequence[int] | np.ndarray,
    scores: Sequence[float] | np.ndarray,
) -> float:
    """Área bajo la curva precision-recall por integración trapezoidal."""
    truth = _validate_binary(y_true, name="y_true")
    score = _as_float_array(scores, name="scores")
    _validate_same_length(truth, score)
    positives = int(np.sum(truth == 1))
    if positives == 0:
        raise MetricInputError("PR-AUC requiere al menos un positivo")
    order = np.argsort(-score, kind="mergesort")
    y = truth[order]
    tp = np.cumsum(y == 1)
    fp = np.cumsum(y == 0)
    recall = tp / positives
    precision = tp / np.maximum(tp + fp, 1)
    recall = np.concatenate(([0.0], recall, [1.0]))
    precision = np.concatenate(([1.0], precision, [precision[-1]]))
    return float(np.trapezoid(precision, recall))


@dataclass(frozen=True, slots=True)
class CalibrationBin:
    lower: float
    upper: float
    count: int
    mean_prediction: float
    observed_frequency: float


def calibration_bins(
    y_true: Sequence[int] | np.ndarray,
    probabilities: Sequence[float] | np.ndarray,
    *,
    bins: int = 10,
) -> tuple[CalibrationBin, ...]:
    truth = _validate_binary(y_true, name="y_true")
    prob = _validate_probabilities(probabilities)
    _validate_same_length(truth, prob)
    if bins < 2:
        raise MetricInputError("bins debe ser >= 2")
    edges = np.linspace(0.0, 1.0, bins + 1)
    result: list[CalibrationBin] = []
    for i in range(bins):
        lo, hi = float(edges[i]), float(edges[i + 1])
        mask = (prob >= lo) & ((prob < hi) if i < bins - 1 else (prob <= hi))
        if not np.any(mask):
            continue
        result.append(
            CalibrationBin(
                lower=lo,
                upper=hi,
                count=int(np.sum(mask)),
                mean_prediction=float(np.mean(prob[mask])),
                observed_frequency=float(np.mean(truth[mask])),
            )
        )
    return tuple(result)


def expected_calibration_error(
    y_true: Sequence[int] | np.ndarray,
    probabilities: Sequence[float] | np.ndarray,
    *,
    bins: int = 10,
) -> float:
    calibration = calibration_bins(y_true, probabilities, bins=bins)
    total = sum(b.count for b in calibration)
    if total == 0:
        raise MetricInputError("No hay observaciones para calibración")
    return float(
        sum(b.count / total * abs(b.mean_prediction - b.observed_frequency) for b in calibration)
    )


def calibration_in_the_large(
    y_true: Sequence[int] | np.ndarray,
    probabilities: Sequence[float] | np.ndarray,
) -> float:
    """Intercepto de calibración para un modelo con offset logit fijo."""
    truth = _validate_binary(y_true, name="y_true")
    p = _validate_probabilities(probabilities)
    _validate_same_length(truth, p)
    observed = float(np.mean(truth))
    if not 0.0 < observed < 1.0:
        raise MetricInputError(
            "calibration-in-the-large no está definida cuando la prevalencia observada es 0 o 1"
        )
    mean_logit = float(np.mean(np.log(np.clip(p, 1e-15, 1 - 1e-15) / np.clip(1 - p, 1e-15, 1 - 1e-15))))
    target_logit = log(observed / (1.0 - observed))
    return float(target_logit - mean_logit)


def calibration_slope(
    y_true: Sequence[int] | np.ndarray,
    probabilities: Sequence[float] | np.ndarray,
) -> float:
    """Pendiente de calibración aproximada mediante Newton-Raphson.

    Ajusta logit(P(Y=1)) = intercepto + slope * logit(predicción),
    preservando la interpretación habitual de slope=1 como calibración ideal.
    """
    truth = _validate_binary(y_true, name="y_true").astype(float)
    p = _validate_probabilities(probabilities)
    _validate_same_length(truth, p)
    prevalence = float(np.mean(truth))
    if not 0.0 < prevalence < 1.0:
        raise MetricInputError("calibration slope no está definida cuando la prevalencia observada es 0 o 1")
    x = np.log(np.clip(p, 1e-12, 1 - 1e-12) / np.clip(1 - p, 1e-12, 1 - 1e-12))
    if np.std(x) == 0.0:
        raise MetricInputError("Pendiente de calibración indefinida con predicciones constantes")
    beta = np.array([0.0, 1.0])
    design = np.column_stack((np.ones_like(x), x))
    for _ in range(50):
        eta = design @ beta
        mu = 1.0 / (1.0 + np.exp(-np.clip(eta, -35, 35)))
        weights = np.clip(mu * (1.0 - mu), 1e-12, None)
        hessian = design.T @ (weights[:, None] * design)
        gradient = design.T @ (truth - mu)
        try:
            step = np.linalg.solve(hessian, gradient)
        except np.linalg.LinAlgError as exc:
            raise MetricInputError("No se pudo estimar la pendiente de calibración") from exc
        beta += step
        if np.linalg.norm(step) < 1e-10:
            break
    return float(beta[1])


def decision_curve_net_benefit(
    y_true: Sequence[int] | np.ndarray,
    probabilities: Sequence[float] | np.ndarray,
    threshold: float,
) -> float:
    """Net benefit de decision-curve analysis para un umbral de probabilidad."""
    truth = _validate_binary(y_true, name="y_true")
    p = _validate_probabilities(probabilities)
    _validate_same_length(truth, p)
    if not 0.0 < threshold < 1.0:
        raise MetricInputError("threshold debe estar en (0,1)")
    predicted_positive = p >= threshold
    tp = int(np.sum(predicted_positive & (truth == 1)))
    fp = int(np.sum(predicted_positive & (truth == 0)))
    n = truth.size
    odds = threshold / (1.0 - threshold)
    return float(tp / n - fp / n * odds)


def integrated_brier_score(
    y_true: Sequence[float] | np.ndarray,
    predictions: Sequence[float] | np.ndarray,
) -> float:
    """Brier medio para una secuencia temporal discretizada."""
    truth = _as_float_array(y_true, name="y_true")
    pred = _as_float_array(predictions, name="predictions")
    _validate_same_length(truth, pred)
    return mse(truth, pred)


def prediction_interval_coverage(
    y_true: Sequence[float] | np.ndarray,
    lower: Sequence[float] | np.ndarray,
    upper: Sequence[float] | np.ndarray,
) -> float:
    truth = _as_float_array(y_true, name="y_true")
    lo = _as_float_array(lower, name="lower")
    hi = _as_float_array(upper, name="upper")
    _validate_same_length(truth, lo, hi)
    if np.any(lo > hi):
        raise MetricInputError("lower no puede superar upper")
    return float(np.mean((truth >= lo) & (truth <= hi)))


def pinball_loss(
    y_true: Sequence[float] | np.ndarray,
    prediction: Sequence[float] | np.ndarray,
    quantile_level: float,
) -> float:
    truth = _as_float_array(y_true, name="y_true")
    pred = _as_float_array(prediction, name="prediction")
    _validate_same_length(truth, pred)
    if not 0.0 < quantile_level < 1.0:
        raise MetricInputError("quantile_level debe estar en (0,1)")
    error = truth - pred
    return float(np.mean(np.maximum(quantile_level * error, (quantile_level - 1.0) * error)))


# ---------------------------------------------------------------------------
# Incertidumbre, intervalos y estandarización
# ---------------------------------------------------------------------------


def standard_error_mean(values: Sequence[float] | np.ndarray) -> float:
    arr = _as_float_array(values, name="values")
    _require_at_least_two(arr, "values")
    return float(np.std(arr, ddof=1) / sqrt(arr.size))


def normal_confidence_interval(
    values: Sequence[float] | np.ndarray,
    *,
    confidence: float = 0.95,
) -> tuple[float, float]:
    arr = _as_float_array(values, name="values")
    _require_at_least_two(arr, "values")
    if not 0.0 < confidence < 1.0:
        raise MetricInputError("confidence debe estar en (0,1)")
    z = NormalDist().inv_cdf((1.0 + confidence) / 2.0)
    margin = z * standard_error_mean(arr)
    m = float(np.mean(arr))
    return m - margin, m + margin


def relative_risk(exposed_events: float, exposed_total: float, unexposed_events: float, unexposed_total: float) -> float:
    if min(exposed_events, unexposed_events) < 0:
        raise MetricInputError("Los eventos no pueden ser negativos")
    if exposed_total <= 0 or unexposed_total <= 0:
        raise MetricInputError("Los denominadores deben ser positivos")
    risk_e = exposed_events / exposed_total
    risk_u = unexposed_events / unexposed_total
    if risk_u == 0.0:
        raise MetricInputError("RR indefinido con riesgo no expuesto 0")
    return float(risk_e / risk_u)


def odds_ratio(a: float, b: float, c: float, d: float) -> float:
    if min(a, b, c, d) < 0.0:
        raise MetricInputError("Las celdas no pueden ser negativas")
    if b * c == 0.0:
        raise MetricInputError("OR indefinido con producto de celdas 0")
    return float(a * d / (b * c))


# ---------------------------------------------------------------------------
# Epidemiología
# ---------------------------------------------------------------------------


def incidence_rate(new_cases: float, population_at_risk: float, person_time: float = 1.0) -> float:
    if new_cases < 0 or population_at_risk <= 0 or person_time <= 0:
        raise MetricInputError("Entradas epidemiológicas inválidas")
    return float(new_cases / population_at_risk / person_time)


def prevalence(cases: float, population: float) -> float:
    if cases < 0 or population <= 0 or cases > population:
        raise MetricInputError("cases debe estar entre 0 y population")
    return float(cases / population)


def attack_rate(cases: float, population_exposed: float) -> float:
    return prevalence(cases, population_exposed)


def case_fatality_ratio(deaths: float, cases: float) -> float:
    if deaths < 0 or cases <= 0 or deaths > cases:
        raise MetricInputError("CFR inválido")
    return float(deaths / cases)


def standardized_mortality_ratio(observed: float, expected: float) -> float:
    if observed < 0 or expected <= 0:
        raise MetricInputError("observed >= 0 y expected > 0 son obligatorios")
    return float(observed / expected)


def excess_mortality(observed: float, expected: float) -> float:
    if observed < 0 or expected < 0:
        raise MetricInputError("Las mortalidades deben ser no negativas")
    return float(observed - expected)


def epidemic_growth_rate(previous_cases: float, current_cases: float, duration: float = 1.0) -> float:
    return log_growth_rate(previous_cases, current_cases, duration=duration)


def effective_reproduction_number(
    incidence: Sequence[float] | np.ndarray,
    generation_interval_weights: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Estimación tipo renewal de Rt: I_t / sum_w w_s I_{t-s}.

    No sustituye un modelo epidemiológico completo ni una estimación oficial.
    """
    inc = _as_float_array(incidence, name="incidence")
    weights = _as_float_array(generation_interval_weights, name="generation_interval_weights")
    if np.any(inc < 0) or np.any(weights < 0):
        raise MetricInputError("Incidencia y pesos deben ser no negativos")
    if weights.sum() <= 0:
        raise MetricInputError("Los pesos deben sumar un valor positivo")
    weights = weights / weights.sum()
    out = np.full(inc.size, np.nan)
    for t in range(weights.size, inc.size):
        denominator = float(np.sum(weights * inc[t - weights.size : t][::-1]))
        if denominator > 0:
            out[t] = inc[t] / denominator
    return out


# ---------------------------------------------------------------------------
# Modelos de capacidad y colas: métricas matemáticas, no predicciones clínicas
# ---------------------------------------------------------------------------


def little_law_waiting_time(number_in_system: float, arrival_rate: float) -> float:
    if number_in_system < 0 or arrival_rate <= 0:
        raise MetricInputError("L >= 0 y lambda > 0 son obligatorios")
    return float(number_in_system / arrival_rate)


def little_law_number_in_system(arrival_rate: float, waiting_time: float) -> float:
    if arrival_rate < 0 or waiting_time < 0:
        raise MetricInputError("lambda y W deben ser no negativos")
    return float(arrival_rate * waiting_time)


def mm1_utilization(arrival_rate: float, service_rate: float) -> float:
    if arrival_rate < 0 or service_rate <= 0:
        raise MetricInputError("lambda >= 0 y mu > 0 son obligatorios")
    return float(arrival_rate / service_rate)


def mm1_mean_number_in_system(arrival_rate: float, service_rate: float) -> float:
    rho = mm1_utilization(arrival_rate, service_rate)
    if rho >= 1.0:
        raise MetricInputError("M/M/1 no tiene estado estacionario cuando rho >= 1")
    return float(rho / (1.0 - rho))


def mm1_mean_waiting_time(arrival_rate: float, service_rate: float) -> float:
    rho = mm1_utilization(arrival_rate, service_rate)
    if rho >= 1.0:
        raise MetricInputError("M/M/1 no tiene espera estacionaria cuando rho >= 1")
    return float(1.0 / (service_rate - arrival_rate))


def mm1_mean_queue_length(arrival_rate: float, service_rate: float) -> float:
    rho = mm1_utilization(arrival_rate, service_rate)
    if rho >= 1.0:
        raise MetricInputError("M/M/1 no tiene cola estacionaria cuando rho >= 1")
    return float(rho * rho / (1.0 - rho))


def capacity_headroom(capacity: float, demand: float) -> float:
    if capacity <= 0 or demand < 0:
        raise MetricInputError("capacity > 0 y demand >= 0 son obligatorios")
    return float((capacity - demand) / capacity)


def recovery_ratio(pre_event_capacity: float, post_event_capacity: float) -> float:
    if pre_event_capacity <= 0 or post_event_capacity < 0:
        raise MetricInputError("Capacidades inválidas")
    return float(post_event_capacity / pre_event_capacity)


# ---------------------------------------------------------------------------
# Redes y difusión
# ---------------------------------------------------------------------------


def network_density(node_count: int, edge_count: int, *, directed: bool = False) -> float:
    if node_count < 0 or edge_count < 0:
        raise MetricInputError("Los tamaños de red no pueden ser negativos")
    if node_count < 2:
        raise MetricInputError("Se requieren al menos dos nodos")
    max_edges = node_count * (node_count - 1) if directed else node_count * (node_count - 1) / 2
    return float(edge_count / max_edges)


def degree_centralization(degrees: Sequence[float] | np.ndarray) -> float:
    arr = _as_float_array(degrees, name="degrees")
    _require_at_least_two(arr, "degrees")
    maximum = float(np.max(arr))
    denominator = float((arr.size - 1) * (arr.size - 2))
    if denominator <= 0:
        raise MetricInputError("Red demasiado pequeña")
    numerator = float(np.sum(maximum - arr))
    return numerator / denominator


def jaccard_similarity(a: Iterable[str], b: Iterable[str]) -> float:
    left, right = set(a), set(b)
    union = left | right
    if not union:
        return 1.0
    return float(len(left & right) / len(union))


def normalized_entropy(counts: Sequence[float] | np.ndarray) -> float:
    arr = _as_float_array(counts, name="counts")
    if np.any(arr < 0) or np.sum(arr) <= 0:
        raise MetricInputError("counts debe ser no negativo y tener suma positiva")
    h = entropy(arr / np.sum(arr), base=np.e)
    maximum = log(arr.size)
    return 0.0 if maximum == 0 else float(h / maximum)


def concentration_hhi(shares: Sequence[float] | np.ndarray) -> float:
    arr = _as_float_array(shares, name="shares")
    if np.any(arr < 0) or not np.isclose(np.sum(arr), 1.0, atol=1e-6):
        raise MetricInputError("shares deben ser no negativas y sumar 1")
    return float(np.sum(arr**2))


# ---------------------------------------------------------------------------
# Dinámica de sistemas y early warning
# ---------------------------------------------------------------------------


def finite_difference_velocity(values: Sequence[float] | np.ndarray, dt: float = 1.0) -> np.ndarray:
    arr = _as_float_array(values, name="values")
    if dt <= 0:
        raise MetricInputError("dt debe ser positivo")
    return np.gradient(arr, dt)


def finite_difference_acceleration(values: Sequence[float] | np.ndarray, dt: float = 1.0) -> np.ndarray:
    arr = _as_float_array(values, name="values")
    if dt <= 0:
        raise MetricInputError("dt debe ser positivo")
    return np.gradient(np.gradient(arr, dt), dt)


def rolling_variance(values: Sequence[float] | np.ndarray, window: int) -> np.ndarray:
    arr = _as_float_array(values, name="values")
    if window < 2 or window > arr.size:
        raise MetricInputError("window incompatible con la serie")
    return np.asarray([np.var(arr[i - window + 1 : i + 1], ddof=1) for i in range(window - 1, arr.size)])


def rolling_autocorrelation(values: Sequence[float] | np.ndarray, window: int, lag: int = 1) -> np.ndarray:
    arr = _as_float_array(values, name="values")
    if window < lag + 2 or window > arr.size:
        raise MetricInputError("window/lag incompatibles")
    out: list[float] = []
    for i in range(window - 1, arr.size):
        segment = arr[i - window + 1 : i + 1]
        out.append(autocorrelation(segment, lag=lag))
    return np.asarray(out)


def coefficient_of_variation_of_residuals(
    observed: Sequence[float] | np.ndarray,
    fitted: Sequence[float] | np.ndarray,
) -> float:
    obs = _as_float_array(observed, name="observed")
    fit = _as_float_array(fitted, name="fitted")
    _validate_same_length(obs, fit)
    _require_at_least_two(obs, "observed")
    residual = obs - fit
    mean_obs = float(np.mean(obs))
    if mean_obs == 0:
        raise MetricInputError("Media observada 0")
    return float(np.std(residual, ddof=1) / abs(mean_obs))


def threshold_exceedance_rate(values: Sequence[float] | np.ndarray, threshold: float) -> float:
    arr = _as_float_array(values, name="values")
    return float(np.mean(arr >= threshold))


def persistence_probability(values: Sequence[float] | np.ndarray, threshold: float) -> float:
    """Proporción de pares consecutivos que permanecen sobre el umbral."""
    arr = _as_float_array(values, name="values")
    _require_at_least_two(arr, "values")
    above = arr >= threshold
    starts = above[:-1]
    if not np.any(starts):
        return 0.0
    return float(np.sum(starts & above[1:]) / np.sum(starts))


def early_warning_variance_trend(values: Sequence[float] | np.ndarray, window: int) -> float:
    """Pendiente OLS de la varianza móvil; indicador exploratorio de EWS.

    No constituye por sí solo evidencia de una transición crítica.
    """
    variances = rolling_variance(values, window)
    x = np.arange(variances.size, dtype=float)
    slope, _ = np.polyfit(x, variances, 1)
    return float(slope)


def early_warning_autocorrelation_trend(
    values: Sequence[float] | np.ndarray,
    window: int,
    lag: int = 1,
) -> float:
    ac = rolling_autocorrelation(values, window, lag=lag)
    x = np.arange(ac.size, dtype=float)
    slope, _ = np.polyfit(x, ac, 1)
    return float(slope)


def changepoint_mean_shift(values: Sequence[float] | np.ndarray) -> int | None:
    """Punto de cambio que maximiza la diferencia estandarizada de medias.

    Es una prueba exploratoria simple; no sustituye métodos específicos de
    change-point con control de error ni validación retrospectiva.
    """
    arr = _as_float_array(values, name="values")
    if arr.size < 4:
        raise MetricInputError("Se requieren al menos cuatro observaciones")
    best_index: int | None = None
    best_score = -np.inf
    for i in range(2, arr.size - 1):
        left, right = arr[:i], arr[i:]
        pooled = np.sqrt((np.var(left, ddof=1) + np.var(right, ddof=1)) / 2.0)
        if pooled == 0:
            continue
        score = abs(np.mean(left) - np.mean(right)) / pooled
        if score > best_score:
            best_score = score
            best_index = i
    return best_index


# ---------------------------------------------------------------------------
# Clima y medio ambiente
# ---------------------------------------------------------------------------


def heat_index_fahrenheit(temperature_f: float, relative_humidity_pct: float) -> float:
    """NOAA/NWS Rothfusz heat index en °F para condiciones donde es aplicable."""
    rh = relative_humidity_pct
    t = temperature_f
    if not 0.0 <= rh <= 100.0:
        raise MetricInputError("Humedad relativa debe estar entre 0 y 100 %")
    if not -100.0 <= t <= 160.0:
        raise MetricInputError("Temperatura fuera de rango operativo")
    hi = (
        -42.379
        + 2.04901523 * t
        + 10.14333127 * rh
        - 0.22475541 * t * rh
        - 0.00683783 * t**2
        - 0.05481717 * rh**2
        + 0.00122874 * t**2 * rh
        + 0.00085282 * t * rh**2
        - 0.00000199 * t**2 * rh**2
    )
    return float(hi)


def heat_index_celsius(temperature_c: float, relative_humidity_pct: float) -> float:
    t_f = temperature_c * 9.0 / 5.0 + 32.0
    hi_f = heat_index_fahrenheit(t_f, relative_humidity_pct)
    return float((hi_f - 32.0) * 5.0 / 9.0)


def vapor_pressure_saturation_kpa(temperature_c: float) -> float:
    """Magnus/Tetens form para presión de vapor de saturación."""
    return float(0.6108 * exp((17.27 * temperature_c) / (temperature_c + 237.3)))


def relative_humidity_from_vapor_pressure(vapor_pressure_kpa: float, temperature_c: float) -> float:
    if vapor_pressure_kpa < 0:
        raise MetricInputError("Presión de vapor no puede ser negativa")
    es = vapor_pressure_saturation_kpa(temperature_c)
    if es <= 0:
        raise MetricInputError("Presión de saturación inválida")
    return float(100.0 * vapor_pressure_kpa / es)


def pet_thornthwaite(
    mean_monthly_temperature_c: Sequence[float] | np.ndarray,
    annual_heat_index: float,
    latitude_factor: float = 1.0,
) -> np.ndarray:
    """PET mensual de Thornthwaite en mm/mes.

    Requiere temperaturas medias mensuales no negativas para la formulación
    estándar y un factor astronómico mensual calculado externamente.
    ``latitude_factor`` permite inyectar la corrección mensual; no representa
    automáticamente una latitud concreta.
    """
    temp = _as_float_array(mean_monthly_temperature_c, name="temperature")
    if temp.size != 12:
        raise MetricInputError("Thornthwaite requiere 12 meses")
    if annual_heat_index <= 0 or latitude_factor <= 0:
        raise MetricInputError("annual_heat_index y latitude_factor deben ser positivos")
    positive = np.maximum(temp, 0.0)
    exponent = 6.75e-7 * annual_heat_index**3 - 7.71e-5 * annual_heat_index**2 + 1.792e-2 * annual_heat_index + 0.49239
    pet = 16.0 * ((10.0 * positive / annual_heat_index) ** exponent)
    return pet * latitude_factor


def spi_from_accumulated_precipitation(
    accumulated_precipitation: Sequence[float] | np.ndarray,
    *,
    minimum_observations: int = 30,
) -> np.ndarray:
    """SPI aproximado mediante transformación empírica normal.

    La función implementa una estandarización no paramétrica útil como
    indicador operativo interno. Para un SPI oficial/científico reproducible
    debe fijarse explícitamente periodo climatológico, distribución, ceros,
    escala y método de estimación; este resultado NO se etiqueta como SPI
    oficial sin ese contrato metodológico.
    """
    arr = _as_float_array(accumulated_precipitation, name="accumulated_precipitation")
    if np.any(arr < 0) or arr.size < minimum_observations:
        raise MetricInputError("Precipitación no negativa y muestra insuficiente")
    ranks = np.argsort(np.argsort(arr, kind="mergesort"), kind="mergesort") + 1
    probabilities = (ranks - 0.44) / (arr.size + 0.12)
    nd = NormalDist()
    return np.asarray([nd.inv_cdf(float(np.clip(p, 1e-10, 1 - 1e-10))) for p in probabilities])


def climatic_water_balance(precipitation: Sequence[float] | np.ndarray, pet: Sequence[float] | np.ndarray) -> np.ndarray:
    p = _as_float_array(precipitation, name="precipitation")
    e = _as_float_array(pet, name="pet")
    _validate_same_length(p, e)
    if np.any(p < 0) or np.any(e < 0):
        raise MetricInputError("precipitación y PET deben ser no negativas")
    return p - e


def standardized_water_balance(values: Sequence[float] | np.ndarray) -> np.ndarray:
    """Estandarización simple de P-PET; no se etiqueta como SPEI oficial."""
    arr = _as_float_array(values, name="water_balance")
    _require_at_least_two(arr, "water_balance")
    sd = float(np.std(arr, ddof=1))
    if sd == 0:
        raise MetricInputError("Balance hídrico constante")
    return (arr - np.mean(arr)) / sd


def precipitation_intensity(total_mm: float, duration_hours: float) -> float:
    if total_mm < 0 or duration_hours <= 0:
        raise MetricInputError("total_mm >= 0 y duration_hours > 0 son obligatorios")
    return float(total_mm / duration_hours)


def rainfall_accumulation_intensity(values_mm: Sequence[float] | np.ndarray, duration_hours: float) -> float:
    return precipitation_intensity(float(np.sum(_as_float_array(values_mm, name="values_mm"))), duration_hours)


def standardized_anomaly_series(values: Sequence[float] | np.ndarray) -> np.ndarray:
    arr = _as_float_array(values, name="values")
    _require_at_least_two(arr, "values")
    sd = float(np.std(arr, ddof=1))
    if sd == 0:
        raise MetricInputError("Serie constante")
    return (arr - np.mean(arr)) / sd


def return_period_from_exceedance_probability(probability: float) -> float:
    if not 0.0 < probability <= 1.0:
        raise MetricInputError("probability debe estar en (0,1]")
    return float(1.0 / probability)


def exceedance_probability_from_return_period(return_period: float) -> float:
    if return_period < 1.0:
        raise MetricInputError("return_period debe ser >= 1")
    return float(1.0 / return_period)


# ---------------------------------------------------------------------------
# Incendios y calidad ambiental
# ---------------------------------------------------------------------------


def fine_fuel_moisture_code_proxy(relative_humidity_pct: float, temperature_c: float) -> float:
    """No es FFMC oficial: utilidad para normalización exploratoria únicamente."""
    if not 0 <= relative_humidity_pct <= 100:
        raise MetricInputError("Humedad inválida")
    if not -50 <= temperature_c <= 60:
        raise MetricInputError("Temperatura inválida")
    dryness = (temperature_c + 20.0) * (1.0 - relative_humidity_pct / 100.0)
    return float(dryness)


def air_pollution_exposure(concentration: Sequence[float] | np.ndarray, duration: Sequence[float] | np.ndarray) -> float:
    c = _as_float_array(concentration, name="concentration")
    d = _as_float_array(duration, name="duration")
    _validate_same_length(c, d)
    if np.any(c < 0) or np.any(d < 0) or np.sum(d) <= 0:
        raise MetricInputError("Concentraciones/duraciones inválidas")
    return float(np.sum(c * d) / np.sum(d))


def official_index_passthrough(value: float) -> float:
    """Entrada de un índice oficial ya calculado por la autoridad competente."""
    if not isfinite(value):
        raise MetricInputError("El índice oficial debe ser finito")
    return float(value)


# ---------------------------------------------------------------------------
# Escalas de salud validadas: puntuación, no diagnóstico
# ---------------------------------------------------------------------------


def phq9_score(items: Sequence[int] | np.ndarray) -> int:
    arr = np.asarray(items, dtype=int)
    if arr.shape != (9,) or np.any((arr < 0) | (arr > 3)):
        raise MetricInputError("PHQ-9 requiere 9 ítems puntuados 0-3")
    return int(np.sum(arr))


def gad7_score(items: Sequence[int] | np.ndarray) -> int:
    arr = np.asarray(items, dtype=int)
    if arr.shape != (7,) or np.any((arr < 0) | (arr > 3)):
        raise MetricInputError("GAD-7 requiere 7 ítems puntuados 0-3")
    return int(np.sum(arr))


def pcl5_score(items: Sequence[int] | np.ndarray) -> int:
    arr = np.asarray(items, dtype=int)
    if arr.shape != (20,) or np.any((arr < 0) | (arr > 4)):
        raise MetricInputError("PCL-5 requiere 20 ítems puntuados 0-4")
    return int(np.sum(arr))


def who5_score(items: Sequence[int] | np.ndarray) -> int:
    arr = np.asarray(items, dtype=int)
    if arr.shape != (5,) or np.any((arr < 0) | (arr > 5)):
        raise MetricInputError("WHO-5 requiere 5 ítems puntuados 0-5")
    return int(np.sum(arr) * 4)


def isi_score(items: Sequence[int] | np.ndarray) -> int:
    arr = np.asarray(items, dtype=int)
    if arr.shape != (7,) or np.any((arr < 0) | (arr > 4)):
        raise MetricInputError("ISI requiere 7 ítems puntuados 0-4")
    return int(np.sum(arr))


def audit_c_score(items: Sequence[int] | np.ndarray) -> int:
    arr = np.asarray(items, dtype=int)
    if arr.shape != (3,) or np.any((arr < 0) | (arr > 4)):
        raise MetricInputError("AUDIT-C requiere 3 ítems puntuados 0-4")
    return int(np.sum(arr))


def pss10_score(items: Sequence[int] | np.ndarray) -> int:
    arr = np.asarray(items, dtype=int)
    if arr.shape != (10,) or np.any((arr < 0) | (arr > 4)):
        raise MetricInputError("PSS-10 requiere 10 ítems puntuados 0-4")
    reverse_indices = (4, 5, 7, 8)
    corrected = arr.copy()
    corrected[list(reverse_indices)] = 4 - corrected[list(reverse_indices)]
    return int(np.sum(corrected))


# ---------------------------------------------------------------------------
# Riesgo cardiovascular: solo funciones matemáticas simples y metadatos de
# modelos externos; no se inventan coeficientes SCORE2/ASCVD/Framingham.
# ---------------------------------------------------------------------------


def bmi(weight_kg: float, height_m: float) -> float:
    if weight_kg <= 0 or height_m <= 0:
        raise MetricInputError("Peso y talla deben ser positivos")
    return float(weight_kg / height_m**2)


def mean_arterial_pressure(systolic_mmhg: float, diastolic_mmhg: float) -> float:
    if systolic_mmhg <= 0 or diastolic_mmhg <= 0 or systolic_mmhg < diastolic_mmhg:
        raise MetricInputError("Presiones arteriales inválidas")
    return float((systolic_mmhg + 2.0 * diastolic_mmhg) / 3.0)


def pulse_pressure(systolic_mmhg: float, diastolic_mmhg: float) -> float:
    if systolic_mmhg <= 0 or diastolic_mmhg <= 0 or systolic_mmhg < diastolic_mmhg:
        raise MetricInputError("Presiones arteriales inválidas")
    return float(systolic_mmhg - diastolic_mmhg)


# ---------------------------------------------------------------------------
# Allostatic load: infraestructura para composites, no score universal.
# ---------------------------------------------------------------------------


def standardized_component(values: Sequence[float] | np.ndarray, *, higher_is_worse: bool = True) -> np.ndarray:
    z = standardized_anomaly_series(values)
    return z if higher_is_worse else -z


def allostatic_load_count_thresholds(
    standardized_components: Sequence[float] | np.ndarray,
    thresholds: Sequence[float] | np.ndarray,
) -> int:
    components = _as_float_array(standardized_components, name="standardized_components")
    limits = _as_float_array(thresholds, name="thresholds")
    _validate_same_length(components, limits)
    return int(np.sum(components >= limits))


def allostatic_load_mean_z(standardized_components: Sequence[float] | np.ndarray) -> float:
    components = _as_float_array(standardized_components, name="standardized_components")
    return float(np.mean(components))


# ---------------------------------------------------------------------------
# Supervivencia / hazard y utilidad probabilística
# ---------------------------------------------------------------------------


def hazard_rate(events: float, person_time: float) -> float:
    return rate(events, person_time)


def survival_from_hazard(hazard: Sequence[float] | np.ndarray, dt: float = 1.0) -> np.ndarray:
    h = _as_float_array(hazard, name="hazard")
    if np.any(h < 0) or dt <= 0:
        raise MetricInputError("hazard >= 0 y dt > 0 son obligatorios")
    cumulative = np.cumsum(h) * dt
    return np.exp(-cumulative)


def hazard_ratio_from_coefficients(coefficient: float) -> float:
    return float(np.exp(coefficient))


# ---------------------------------------------------------------------------
# Modelos compuestos / escenarios
# ---------------------------------------------------------------------------


def weighted_index(values: Sequence[float] | np.ndarray, weights: Sequence[float] | np.ndarray) -> float:
    x = _as_float_array(values, name="values")
    w = _as_float_array(weights, name="weights")
    _validate_same_length(x, w)
    if np.sum(w) == 0:
        raise MetricInputError("Los pesos no pueden sumar 0")
    return float(np.sum(x * w) / np.sum(w))


def geometric_weighted_index(values: Sequence[float] | np.ndarray, weights: Sequence[float] | np.ndarray) -> float:
    x = _as_float_array(values, name="values")
    w = _as_float_array(weights, name="weights")
    _validate_same_length(x, w)
    if np.any(x < 0) or np.any(w < 0) or np.sum(w) <= 0:
        raise MetricInputError("Valores y pesos deben ser no negativos; pesos con suma positiva")
    return float(np.exp(np.sum(w * np.log(np.clip(x, 1e-15, None))) / np.sum(w)))


def monte_carlo_mean(samples: Sequence[float] | np.ndarray) -> float:
    return mean(samples)


def monte_carlo_quantile(samples: Sequence[float] | np.ndarray, q: float) -> float:
    return quantile(samples, q)


def probability_of_exceedance(samples: Sequence[float] | np.ndarray, threshold: float) -> float:
    arr = _as_float_array(samples, name="samples")
    return float(np.mean(arr >= threshold))


def sensitivity_to_parameter(
    baseline_output: float,
    perturbed_output: float,
    baseline_parameter: float,
    perturbed_parameter: float,
) -> float:
    if baseline_parameter == perturbed_parameter:
        raise MetricInputError("Los parámetros deben diferir")
    return float((perturbed_output - baseline_output) / (perturbed_parameter - baseline_parameter))


# ---------------------------------------------------------------------------
# Catálogo científico/operacional
# ---------------------------------------------------------------------------


PUBMED_PREDICTION_METHODS: Final[tuple[str, ...]] = (
    "PMID:36510134",  # model evaluation: discrimination, calibration, utility, updating
    "PMID:25560730",  # TRIPOD
    "PMID:41643238",  # prediction models / reporting / bias / fairness review
    "PMID:40599890",  # model updating review
)

ALLOSTATIC_LOAD_REFERENCES: Final[tuple[str, ...]] = (
    "PMID:32799204",
    "PMID:36113380",
    "PMID:35393143",
    "PMID:35704985",
    "PMID:40892605",
)

TRAUMA_REFERENCES: Final[tuple[str, ...]] = (
    "PMID:37264532",
    "PMID:36843081",
    "PMID:38911962",
    "PMID:34649684",
    "PMID:40968484",
    "PMID:37143625",
)

DROUGHT_REFERENCES: Final[tuple[str, ...]] = ("PMID:32842642",)

AEMET_OFFICIAL_REFERENCES: Final[tuple[str, ...]] = (
    "AEMET:IPIF:2026",
)


METRIC_REGISTRY: Final[dict[str, MetricDefinition]] = {
    "mean": MetricDefinition(
        "mean", "Media aritmética", MetricDomain.GENERAL_STATISTICS, MetricKind.FORMULA,
        ValidationStatus.VALIDATED, "Media aritmética de una muestra", "input_units", "float",
        "Σxᵢ/n", EvidenceLevel.METHODOLOGICAL_STANDARD,
    ),
    "variance": MetricDefinition(
        "variance", "Varianza muestral", MetricDomain.DISTRIBUTION, MetricKind.FORMULA,
        ValidationStatus.VALIDATED, "Dispersión cuadrática muestral", "units²", "float",
        "Σ(xᵢ-x̄)²/(n-1)", EvidenceLevel.METHODOLOGICAL_STANDARD,
    ),
    "mse": MetricDefinition(
        "mse", "Mean Squared Error", MetricDomain.PREDICTION, MetricKind.MODEL_EVALUATION,
        ValidationStatus.VALIDATED, "Error cuadrático medio", "squared_output_units", "float",
        "mean((y-yhat)²)", EvidenceLevel.METHODOLOGICAL_STANDARD,
        predictive_use_allowed=True,
    ),
    "rmse": MetricDefinition(
        "rmse", "Root Mean Squared Error", MetricDomain.PREDICTION, MetricKind.MODEL_EVALUATION,
        ValidationStatus.VALIDATED, "Raíz del error cuadrático medio", "output_units", "float",
        "sqrt(MSE)", EvidenceLevel.METHODOLOGICAL_STANDARD, predictive_use_allowed=True,
    ),
    "mae": MetricDefinition(
        "mae", "Mean Absolute Error", MetricDomain.PREDICTION, MetricKind.MODEL_EVALUATION,
        ValidationStatus.VALIDATED, "Error absoluto medio", "output_units", "float",
        "mean(|y-yhat|)", EvidenceLevel.METHODOLOGICAL_STANDARD, predictive_use_allowed=True,
    ),
    "r_squared": MetricDefinition(
        "r_squared", "R²", MetricDomain.PREDICTION, MetricKind.MODEL_EVALUATION,
        ValidationStatus.VALIDATED, "Coeficiente de determinación", "dimensionless", "float",
        "1-SSE/SST", EvidenceLevel.METHODOLOGICAL_STANDARD, predictive_use_allowed=True,
    ),
    "roc_auc": MetricDefinition(
        "roc_auc", "ROC-AUC", MetricDomain.CLASSIFICATION, MetricKind.MODEL_EVALUATION,
        ValidationStatus.VALIDATED, "Discriminación binaria por área ROC", "dimensionless", "float",
        "P(score_positive > score_negative)", EvidenceLevel.METHODOLOGICAL_STANDARD,
        predictive_use_allowed=True,
        limitations=("No mide calibración ni utilidad clínica/operativa.",),
    ),
    "pr_auc": MetricDefinition(
        "pr_auc", "PR-AUC", MetricDomain.CLASSIFICATION, MetricKind.MODEL_EVALUATION,
        ValidationStatus.VALIDATED, "Área precision-recall", "dimensionless", "float",
        "∫ precision d(recall)", EvidenceLevel.METHODOLOGICAL_STANDARD, predictive_use_allowed=True,
    ),
    "sensitivity": MetricDefinition(
        "sensitivity", "Sensibilidad", MetricDomain.CLASSIFICATION, MetricKind.MODEL_EVALUATION,
        ValidationStatus.VALIDATED, "Proporción de positivos correctamente detectados", "dimensionless", "float",
        "TP/(TP+FN)", EvidenceLevel.METHODOLOGICAL_STANDARD, predictive_use_allowed=True,
    ),
    "specificity": MetricDefinition(
        "specificity", "Especificidad", MetricDomain.CLASSIFICATION, MetricKind.MODEL_EVALUATION,
        ValidationStatus.VALIDATED, "Proporción de negativos correctamente identificados", "dimensionless", "float",
        "TN/(TN+FP)", EvidenceLevel.METHODOLOGICAL_STANDARD, predictive_use_allowed=True,
    ),
    "mcc": MetricDefinition(
        "mcc", "Matthews correlation coefficient", MetricDomain.CLASSIFICATION, MetricKind.MODEL_EVALUATION,
        ValidationStatus.VALIDATED, "Correlación entre clasificación observada y predicha", "dimensionless", "float",
        "(TP·TN-FP·FN)/sqrt(...)", EvidenceLevel.METHODOLOGICAL_STANDARD, predictive_use_allowed=True,
    ),
    "brier_score": MetricDefinition(
        "brier_score", "Brier score", MetricDomain.CALIBRATION, MetricKind.MODEL_EVALUATION,
        ValidationStatus.VALIDATED, "Error cuadrático medio de probabilidades binarias", "dimensionless", "float",
        "mean((p-y)²)", EvidenceLevel.PEER_REVIEWED,
        evidence_references=("PMID:31093548", "PMID:31093557"), predictive_use_allowed=True,
        limitations=("No debe interpretarse aisladamente como utilidad operativa.",),
    ),
    "calibration_in_the_large": MetricDefinition(
        "calibration_in_the_large", "Calibration-in-the-large", MetricDomain.CALIBRATION,
        MetricKind.MODEL_EVALUATION, ValidationStatus.VALIDATED,
        "Desplazamiento global entre riesgo predicho y observado", "log_odds", "float",
        "intercept calibration model", EvidenceLevel.PEER_REVIEWED,
        evidence_references=PUBMED_PREDICTION_METHODS, predictive_use_allowed=True,
    ),
    "calibration_slope": MetricDefinition(
        "calibration_slope", "Calibration slope", MetricDomain.CALIBRATION,
        MetricKind.MODEL_EVALUATION, ValidationStatus.VALIDATED,
        "Pendiente de calibración", "dimensionless", "float", "slope of observed logit on predicted logit",
        EvidenceLevel.PEER_REVIEWED, evidence_references=PUBMED_PREDICTION_METHODS,
        predictive_use_allowed=True,
    ),
    "decision_curve_net_benefit": MetricDefinition(
        "decision_curve_net_benefit", "Decision-curve net benefit", MetricDomain.CALIBRATION,
        MetricKind.MODEL_EVALUATION, ValidationStatus.VALIDATED,
        "Beneficio neto según umbral de decisión", "net_benefit", "float",
        "TP/n - FP/n·pt/(1-pt)", EvidenceLevel.PEER_REVIEWED,
        predictive_use_allowed=True,
    ),
    "phq9": MetricDefinition(
        "phq9", "PHQ-9", MetricDomain.MENTAL_HEALTH, MetricKind.SCALE,
        ValidationStatus.VALIDATED_ELSEWHERE, "Puntuación de síntomas depresivos", "score 0-27", "integer",
        "Σ9 items", EvidenceLevel.PEER_REVIEWED, evidence_references=TRAUMA_REFERENCES,
        individual_use=True, population_use=True,
        limitations=("Instrumento de cribado/medición de síntomas; no constituye diagnóstico autónomo.",),
    ),
    "gad7": MetricDefinition(
        "gad7", "GAD-7", MetricDomain.MENTAL_HEALTH, MetricKind.SCALE,
        ValidationStatus.VALIDATED_ELSEWHERE, "Puntuación de síntomas de ansiedad", "score 0-21", "integer",
        "Σ7 items", EvidenceLevel.PEER_REVIEWED, evidence_references=TRAUMA_REFERENCES,
        individual_use=True, population_use=True,
        limitations=("Instrumento de medición/cribado; no equivale a diagnóstico.",),
    ),
    "pcl5": MetricDefinition(
        "pcl5", "PCL-5", MetricDomain.TRAUMA, MetricKind.SCALE,
        ValidationStatus.VALIDATED_ELSEWHERE, "Puntuación de síntomas relacionados con TEPT", "score 0-80", "integer",
        "Σ20 items", EvidenceLevel.PEER_REVIEWED, evidence_references=TRAUMA_REFERENCES,
        individual_use=True, population_use=True,
        limitations=("No es diagnóstico autónomo; requiere interpretación clínica/contextual.",),
    ),
    "who5": MetricDefinition(
        "who5", "WHO-5 Well-Being Index", MetricDomain.WELLBEING, MetricKind.SCALE,
        ValidationStatus.VALIDATED_ELSEWHERE, "Índice de bienestar subjetivo", "0-100", "integer",
        "4·Σ5 items", EvidenceLevel.PEER_REVIEWED,
        individual_use=True, population_use=True,
        limitations=("No es una escala diagnóstica específica.",),
    ),
    "isi": MetricDefinition(
        "isi", "Insomnia Severity Index", MetricDomain.SLEEP, MetricKind.SCALE,
        ValidationStatus.VALIDATED_ELSEWHERE, "Severidad percibida del insomnio", "score 0-28", "integer",
        "Σ7 items", EvidenceLevel.PEER_REVIEWED,
        individual_use=True, population_use=True,
    ),
    "audit_c": MetricDefinition(
        "audit_c", "AUDIT-C", MetricDomain.MENTAL_HEALTH, MetricKind.SCALE,
        ValidationStatus.VALIDATED_ELSEWHERE, "Cribado de consumo de alcohol", "score 0-12", "integer",
        "Σ3 items", EvidenceLevel.PEER_REVIEWED,
        individual_use=True, population_use=True,
    ),
    "pss10": MetricDefinition(
        "pss10", "Perceived Stress Scale-10", MetricDomain.STRESS, MetricKind.SCALE,
        ValidationStatus.VALIDATED_ELSEWHERE, "Percepción de estrés", "score 0-40", "integer",
        "Σ10 corrected items", EvidenceLevel.PEER_REVIEWED,
        individual_use=True, population_use=True,
    ),
    "bmi": MetricDefinition(
        "bmi", "Índice de masa corporal", MetricDomain.BIOMEDICAL, MetricKind.FORMULA,
        ValidationStatus.VALIDATED, "Peso dividido por talla al cuadrado", "kg/m²", "float",
        "kg/m²", EvidenceLevel.METHODOLOGICAL_STANDARD, individual_use=True, population_use=True,
    ),
    "relative_risk": MetricDefinition(
        "relative_risk", "Riesgo relativo", MetricDomain.EPIDEMIOLOGY, MetricKind.FORMULA,
        ValidationStatus.VALIDATED, "Razón de riesgos entre dos grupos definidos", "ratio", "float",
        "(a/n1)/(c/n0)", EvidenceLevel.METHODOLOGICAL_STANDARD,
    ),
    "odds_ratio": MetricDefinition(
        "odds_ratio", "Odds ratio", MetricDomain.EPIDEMIOLOGY, MetricKind.FORMULA,
        ValidationStatus.VALIDATED, "Razón de odds", "ratio", "float", "ad/bc",
        EvidenceLevel.METHODOLOGICAL_STANDARD,
    ),
    "effective_reproduction_number": MetricDefinition(
        "effective_reproduction_number", "Rt tipo renewal", MetricDomain.EPIDEMIOLOGY, MetricKind.MODEL_PRIMITIVE,
        ValidationStatus.VALIDATED_ELSEWHERE, "Razón de incidencia actual respecto a incidencia infecciosa esperada por intervalos de generación", "ratio", "vector",
        "I_t/Σ w_s I_{t-s}", EvidenceLevel.PEER_REVIEWED,
        limitations=("Muy sensible a datos de incidencia, retrasos, intervalos de generación y supuestos de observación.",),
        predictive_use_allowed=True,
    ),
    "demand_capacity_ratio": MetricDefinition(
        "demand_capacity_ratio", "Ratio demanda/capacidad", MetricDomain.CAPACITY, MetricKind.RATE,
        ValidationStatus.VALIDATED, "Presión instantánea sobre capacidad", "ratio", "float", "D/C",
        EvidenceLevel.METHODOLOGICAL_STANDARD,
    ),
    "little_law_waiting_time": MetricDefinition(
        "little_law_waiting_time", "Ley de Little", MetricDomain.QUEUEING, MetricKind.FORMULA,
        ValidationStatus.VALIDATED, "Relación entre población media, tasa de llegada y tiempo medio", "time", "float",
        "W=L/λ", EvidenceLevel.METHODOLOGICAL_STANDARD,
        limitations=("La interpretación estacionaria exige condiciones de aplicabilidad de la ley.",),
    ),
    "mm1_waiting_time": MetricDefinition(
        "mm1_waiting_time", "M/M/1 mean waiting time", MetricDomain.QUEUEING, MetricKind.FORMULA,
        ValidationStatus.VALIDATED, "Espera media M/M/1 estacionaria", "time", "float",
        "W=1/(μ-λ)", EvidenceLevel.METHODOLOGICAL_STANDARD,
        limitations=("Modelo M/M/1; no debe confundirse con capacidad real de un servicio complejo.",),
    ),
    "early_warning_variance_trend": MetricDefinition(
        "early_warning_variance_trend", "Tendencia de varianza móvil", MetricDomain.EARLY_WARNING,
        MetricKind.EARLY_WARNING, ValidationStatus.VALIDATED_ELSEWHERE,
        "Cambio temporal de la varianza como posible indicador de pérdida de resiliencia", "variance/time", "float",
        "slope(Var_window)", EvidenceLevel.PEER_REVIEWED,
        evidence_references=("PMID:23087241",), predictive_use_allowed=True,
        limitations=("Indicador temprano no específico; puede aparecer por múltiples mecanismos y ruido.",),
    ),
    "early_warning_autocorrelation_trend": MetricDefinition(
        "early_warning_autocorrelation_trend", "Tendencia de autocorrelación", MetricDomain.EARLY_WARNING,
        MetricKind.EARLY_WARNING, ValidationStatus.VALIDATED_ELSEWHERE,
        "Cambio temporal de autocorrelación como posible indicador de desaceleración crítica", "correlation/time", "float",
        "slope(AC_window)", EvidenceLevel.PEER_REVIEWED,
        evidence_references=("PMID:23087241",), predictive_use_allowed=True,
    ),
    "spi": MetricDefinition(
        "spi", "Standardized Precipitation Index", MetricDomain.DROUGHT, MetricKind.INDEX,
        ValidationStatus.VALIDATED_ELSEWHERE, "Índice estandarizado de precipitación a una escala temporal definida", "standardized", "vector",
        "distributional standardization of accumulated precipitation", EvidenceLevel.PEER_REVIEWED,
        evidence_references=DROUGHT_REFERENCES,
        limitations=("La función simplificada incluida no sustituye una implementación climatológica completa con distribución, ceros, periodo base y escala definidos.",),
    ),
    "spei": MetricDefinition(
        "spei", "Standardized Precipitation Evapotranspiration Index", MetricDomain.DROUGHT, MetricKind.INDEX,
        ValidationStatus.CATALOGUED, "Índice estandarizado del balance climático P-PET", "standardized", "vector",
        "standardization of accumulated (P-PET)", EvidenceLevel.PEER_REVIEWED,
        evidence_references=DROUGHT_REFERENCES,
        limitations=("Requiere especificación completa de PET, distribución, escala y periodo climatológico.",),
        executable=False,
    ),
    "aemet_ipif": MetricDefinition(
        "aemet_ipif", "Índice de Peligro de Incendios Forestales de AEMET", MetricDomain.FIRE,
        MetricKind.INDEX, ValidationStatus.OFFICIAL,
        "Índice operativo oficial de peligro de incendios forestales de AEMET", "official_index", "float",
        formula=None, evidence_level=EvidenceLevel.OFFICIAL, evidence_references=AEMET_OFFICIAL_REFERENCES,
        limitations=("CeutIA no reconstruye ni modifica la fórmula oficial; debe consumir el producto oficial o una implementación oficialmente documentada.",),
    ),
    "heat_index": MetricDefinition(
        "heat_index", "Heat Index", MetricDomain.HEAT, MetricKind.INDEX,
        ValidationStatus.VALIDATED_ELSEWHERE, "Índice biometeorológico basado en temperatura y humedad", "°C equivalent", "float",
        "NOAA/NWS Rothfusz regression", EvidenceLevel.OFFICIAL,
        limitations=("Tiene dominio de aplicabilidad y no sustituye los sistemas oficiales españoles de vigilancia y alerta por calor.",),
    ),
    "air_pollution_exposure": MetricDefinition(
        "air_pollution_exposure", "Exposición media ponderada por tiempo", MetricDomain.AIR_QUALITY,
        MetricKind.FORMULA, ValidationStatus.VALIDATED,
        "Concentración media ponderada por duración de exposición", "concentration_units", "float",
        "Σ(cᵢ·Δtᵢ)/ΣΔtᵢ", EvidenceLevel.METHODOLOGICAL_STANDARD,
    ),
    "allostatic_load_count": MetricDefinition(
        "allostatic_load_count", "Allostatic load threshold count", MetricDomain.ALLOSTATIC_LOAD,
        MetricKind.SCORE, ValidationStatus.VALIDATED_ELSEWHERE,
        "Número de biomarcadores/componentes que superan umbrales definidos por el protocolo", "count", "integer",
        "Σ I(zᵢ≥thresholdᵢ)", EvidenceLevel.SYSTEMATIC_REVIEW,
        evidence_references=ALLOSTATIC_LOAD_REFERENCES,
        limitations=("No existe un único score universal; la selección de biomarcadores y umbrales debe declararse.",),
    ),
    "allostatic_load_mean_z": MetricDefinition(
        "allostatic_load_mean_z", "Media de componentes estandarizados de carga alostática", MetricDomain.ALLOSTATIC_LOAD,
        MetricKind.SCORE, ValidationStatus.VALIDATED_ELSEWHERE,
        "Composición continua de componentes estandarizados", "z-score", "float",
        "mean(zᵢ)", EvidenceLevel.SYSTEMATIC_REVIEW,
        evidence_references=ALLOSTATIC_LOAD_REFERENCES,
        limitations=("No debe presentarse como un estándar clínico universal.",),
    ),
    "territorial_share": MetricDefinition(
        "territorial_share", "Participación territorial", MetricDomain.DEMOGRAPHY, MetricKind.INDEX,
        ValidationStatus.VALIDATED, "Participación de cada unidad territorial sobre el total observado", "share", "vector",
        "x_i / Σ_j x_j", EvidenceLevel.METHODOLOGICAL_STANDARD,
        permitted_channels=frozenset({OutputChannel.INTERNAL, OutputChannel.PRIVATE}),
        limitations=("Es descriptiva; depende de la unidad espacial y del denominador observado.",),
    ),
    "territorial_morans_i": MetricDefinition(
        "territorial_morans_i", "Moran's I territorial", MetricDomain.SYSTEM_DYNAMICS, MetricKind.INDEX,
        ValidationStatus.VALIDATED_ELSEWHERE, "Autocorrelación espacial global de una variable territorial", "dimensionless", "float",
        "(n/S0)·Σij(wij zi zj)/Σi zi²", EvidenceLevel.METHODOLOGICAL_STANDARD,
        permitted_channels=frozenset({OutputChannel.INTERNAL, OutputChannel.PRIVATE}),
        limitations=("Requiere W explícita, vecinos por unidad y una hipótesis espacial; no implica causalidad.", "Resultados con muestras espaciales pequeñas pueden ser inestables."),
    ),
    "territorial_gearys_c": MetricDefinition(
        "territorial_gearys_c", "Geary's C territorial", MetricDomain.SYSTEM_DYNAMICS, MetricKind.INDEX,
        ValidationStatus.VALIDATED_ELSEWHERE, "Autocorrelación espacial basada en diferencias locales", "dimensionless", "float",
        "((n-1)/(2S0))·Σij wij(xi-xj)²/Σi(xi-x̄)²", EvidenceLevel.METHODOLOGICAL_STANDARD,
        permitted_channels=frozenset({OutputChannel.INTERNAL, OutputChannel.PRIVATE}),
        limitations=("Requiere W explícita y contexto espacial; no implica causalidad.",),
    ),
    "territorial_demand_per_capacity": MetricDefinition(
        "territorial_demand_per_capacity", "Demanda/capacidad territorial", MetricDomain.CAPACITY, MetricKind.RATE,
        ValidationStatus.VALIDATED, "Presión de demanda sobre capacidad en cada unidad territorial", "ratio", "vector",
        "D_i/C_i", EvidenceLevel.METHODOLOGICAL_STANDARD,
        permitted_channels=frozenset({OutputChannel.INTERNAL, OutputChannel.PRIVATE}),
        limitations=("La comparabilidad exige que demanda y capacidad compartan definición y horizonte temporal.",),
    ),
    "territorial_capacity_reserve": MetricDefinition(
        "territorial_capacity_reserve", "Reserva territorial de capacidad", MetricDomain.CAPACITY, MetricKind.FORMULA,
        ValidationStatus.VALIDATED, "Diferencia entre capacidad y demanda observadas", "capacity_units", "vector",
        "C_i-D_i", EvidenceLevel.METHODOLOGICAL_STANDARD,
        permitted_channels=frozenset({OutputChannel.INTERNAL, OutputChannel.PRIVATE}),
    ),
    "territorial_bottleneck_migration": MetricDefinition(
        "territorial_bottleneck_migration", "Cambio de localización del cuello de botella", MetricDomain.SYSTEM_DYNAMICS, MetricKind.INDEX,
        ValidationStatus.EXPERIMENTAL, "Detecta cambio de la unidad territorial con mayor utilización", "territorial_index_or_none", "integer|null",
        "argmax(D_t/C_t) != argmax(D_t-1/C_t-1)", EvidenceLevel.OTHER,
        permitted_channels=frozenset({OutputChannel.INTERNAL, OutputChannel.PRIVATE}),
        limitations=("Describe cambio de localización; no implica transferencia causal de carga.",),
        executable=False,
    ),
    "territorial_load_transfer": MetricDefinition(
        "territorial_load_transfer", "Cambio territorial de carga", MetricDomain.SYSTEM_DYNAMICS, MetricKind.FORMULA,
        ValidationStatus.VALIDATED, "Diferencia entre carga territorial en dos instantes", "input_units", "vector",
        "L_i(t)-L_i(t-1)", EvidenceLevel.METHODOLOGICAL_STANDARD,
        permitted_channels=frozenset({OutputChannel.INTERNAL, OutputChannel.PRIVATE}),
    ),
    "territorial_spatial_propagation": MetricDefinition(
        "territorial_spatial_propagation", "Propagación espacial descriptiva", MetricDomain.SYSTEM_DYNAMICS, MetricKind.INDEX,
        ValidationStatus.EXPERIMENTAL, "Asociación entre incrementos locales y señal espacial previa de vecinos", "normalized_signal", "float",
        "Σ Δx_i+·L_i(x_prev)/ΣΔx_i+", EvidenceLevel.OTHER,
        permitted_channels=frozenset({OutputChannel.INTERNAL, OutputChannel.PRIVATE}),
        limitations=("Es descriptiva; no identifica dirección causal ni mecanismo de transmisión.",),
        executable=False,
    ),
    "territorial_cascade_depth": MetricDefinition(
        "territorial_cascade_depth", "Profundidad de capas de propagación observadas", MetricDomain.SYSTEM_DYNAMICS, MetricKind.EARLY_WARNING,
        ValidationStatus.EXPERIMENTAL, "Número de generaciones/capas de activación observadas, cuando se proporciona una secuencia temporal explícita", "layers", "integer",
        "max observed activation layer", EvidenceLevel.OTHER,
        permitted_channels=frozenset({OutputChannel.INTERNAL, OutputChannel.PRIVATE}),
        limitations=("No representa profundidad causal; simultaneidad o correlación no constituyen cascada causal.",),
        executable=False,
    ),
    "territorial_observation_coverage": MetricDefinition(
        "territorial_observation_coverage", "Cobertura territorial de observación", MetricDomain.SYSTEM_DYNAMICS, MetricKind.RATE,
        ValidationStatus.VALIDATED, "Fracción observada sobre el universo potencialmente observable", "share", "vector",
        "observed_i/possible_i", EvidenceLevel.METHODOLOGICAL_STANDARD,
        permitted_channels=frozenset({OutputChannel.INTERNAL, OutputChannel.PRIVATE}),
        limitations=("La cobertura no demuestra ausencia del fenómeno en unidades no observadas.",),
    ),
    "territorial_signal_to_noise": MetricDefinition(
        "territorial_signal_to_noise", "Relación señal/ruido territorial", MetricDomain.SYSTEM_DYNAMICS, MetricKind.RATE,
        ValidationStatus.VALIDATED, "Relación descriptiva entre señal y ruido definidos en la misma escala", "ratio", "vector",
        "signal_i/noise_i", EvidenceLevel.METHODOLOGICAL_STANDARD,
        permitted_channels=frozenset({OutputChannel.INTERNAL, OutputChannel.PRIVATE}),
        limitations=("Requiere una definición explícita y compatible de señal y ruido; no equivale a evidencia causal.",),
    ),
    "score2": MetricDefinition(
        "score2", "SCORE2", MetricDomain.CARDIOVASCULAR, MetricKind.RISK_MODEL,
        ValidationStatus.VALIDATED_ELSEWHERE, "Modelo de riesgo cardiovascular de la ESC", "probability", "float",
        formula=None, evidence_level=EvidenceLevel.PEER_REVIEWED,
        limitations=("Los coeficientes no se reconstruyen aquí sin especificación/versionado del modelo; requiere población y región de riesgo apropiadas.",),
        executable=False,
        predictive_use_allowed=True,
    ),
    "score2_op": MetricDefinition(
        "score2_op", "SCORE2-OP", MetricDomain.CARDIOVASCULAR, MetricKind.RISK_MODEL,
        ValidationStatus.VALIDATED_ELSEWHERE, "Modelo SCORE2 para personas mayores", "probability", "float",
        formula=None, evidence_level=EvidenceLevel.PEER_REVIEWED,
        limitations=("No se ejecuta sin versión oficial y parámetros completos.",),
        executable=False, predictive_use_allowed=True,
    ),
}


# Modelos estratégicos: deliberadamente no ejecutables hasta validación específica.
STRATEGIC_RISK_REGISTRY: Final[dict[str, MetricDefinition]] = {
    "intergroup_violence_early_warning": MetricDefinition(
        "intergroup_violence_early_warning", "Early warning de violencia intergrupal",
        MetricDomain.VIOLENCE, MetricKind.RISK_MODEL, ValidationStatus.CATALOGUED,
        "Modelo de riesgo de eventos observables de violencia intergrupal y escalada",
        "probability", "float", evidence_level=EvidenceLevel.OTHER,
        limitations=(
            "No debe inferir peligrosidad por nacionalidad, origen o grupo protegido.",
            "Requiere outcome operacional, datos históricos, validación temporal/external y calibración.",
        ),
        permitted_channels=frozenset({OutputChannel.INTERNAL, OutputChannel.PRIVATE}),
        predictive_use_allowed=False, executable=False,
    ),
    "political_violence_early_warning": MetricDefinition(
        "political_violence_early_warning", "Early warning de violencia política",
        MetricDomain.POLITICAL_VIOLENCE, MetricKind.RISK_MODEL, ValidationStatus.CATALOGUED,
        "Predicción de eventos observables de violencia política", "probability", "float",
        evidence_level=EvidenceLevel.OTHER,
        limitations=("No existe una ecuación universal validada para Ceuta; requiere dataset y validación específicos.",),
        permitted_channels=frozenset({OutputChannel.INTERNAL, OutputChannel.PRIVATE}),
        executable=False,
    ),
    "armed_conflict_early_warning": MetricDefinition(
        "armed_conflict_early_warning", "Early warning de conflicto armado",
        MetricDomain.CONFLICT, MetricKind.RISK_MODEL, ValidationStatus.CATALOGUED,
        "Riesgo de eventos de conflicto armado definido operacionalmente", "probability", "float",
        evidence_level=EvidenceLevel.OTHER,
        limitations=("No debe producirse una probabilidad sin outcome, horizonte y validación explícitos.",),
        permitted_channels=frozenset({OutputChannel.INTERNAL, OutputChannel.PRIVATE}),
        executable=False,
    ),
    "external_escalation": MetricDefinition(
        "external_escalation", "Escalada externa/estratégica",
        MetricDomain.STRATEGIC, MetricKind.RISK_MODEL, ValidationStatus.CATALOGUED,
        "Modelo de escenarios/eventos de escalada externa", "probability", "float",
        evidence_level=EvidenceLevel.OTHER,
        limitations=("Hipótesis y escenarios no equivalen a hechos ni a probabilidades calibradas.",),
        permitted_channels=frozenset({OutputChannel.INTERNAL, OutputChannel.PRIVATE}),
        executable=False,
    ),
    "border_entry_event": MetricDefinition(
        "border_entry_event", "Evento de entrada fronteriza",
        MetricDomain.MIGRATION, MetricKind.EARLY_WARNING, ValidationStatus.CATALOGUED,
        "Modelización de flujos/eventos fronterizos observables", "count/rate", "float",
        evidence_level=EvidenceLevel.OTHER,
        limitations=("La entrada de personas no equivale a criminalidad ni a peligrosidad.",),
        permitted_channels=frozenset({OutputChannel.INTERNAL, OutputChannel.PRIVATE}),
        predictive_use_allowed=False, executable=False,
    ),
    "military_uprising": MetricDefinition(
        "military_uprising", "Riesgo de levantamiento militar",
        MetricDomain.STRATEGIC, MetricKind.RISK_MODEL, ValidationStatus.CATALOGUED,
        "Escenario de ruptura institucional/militar definido por eventos observables",
        "probability", "float", evidence_level=EvidenceLevel.OTHER,
        limitations=("No existe fórmula universal validada para convertir señales heterogéneas en una probabilidad Ceuta-específica.",),
        permitted_channels=frozenset({OutputChannel.INTERNAL, OutputChannel.PRIVATE}),
        executable=False,
    ),
    "invasion_event": MetricDefinition(
        "invasion_event", "Riesgo de incursión/invasión como evento",
        MetricDomain.SECURITY, MetricKind.RISK_MODEL, ValidationStatus.CATALOGUED,
        "Escenario de evento externo definido operacionalmente, no predicción de personas o grupos",
        "probability", "float", evidence_level=EvidenceLevel.OTHER,
        limitations=("Requiere definición del evento, horizonte, datos y validación retrospectiva.",),
        permitted_channels=frozenset({OutputChannel.INTERNAL, OutputChannel.PRIVATE}),
        executable=False,
    ),
}


# ---------------------------------------------------------------------------
# Registro y controles epistemológicos
# ---------------------------------------------------------------------------


def get_metric_definition(metric_id: str) -> MetricDefinition:
    try:
        return {**METRIC_REGISTRY, **STRATEGIC_RISK_REGISTRY}[metric_id]
    except KeyError as exc:
        raise MetricError(f"Métrica no registrada: {metric_id}") from exc


def assert_metric_executable(metric_id: str) -> MetricDefinition:
    definition = get_metric_definition(metric_id)
    if not definition.executable or definition.status in {
        ValidationStatus.CATALOGUED,
        ValidationStatus.EXPERIMENTAL,
        ValidationStatus.BLOCKED,
        ValidationStatus.NOT_VALIDATED_FOR_CEUTA,
    }:
        raise MetricNotValidatedError(
            f"La métrica '{metric_id}' no está autorizada para ejecución: {definition.status}"
        )
    return definition


def assert_output_permitted(metric_id: str, channel: OutputChannel) -> None:
    definition = get_metric_definition(metric_id)
    if channel not in definition.permitted_channels:
        raise MetricNotPermittedError(
            f"'{metric_id}' no está permitido en el canal {channel}"
        )


def require_validated_metric(metric_id: str) -> MetricDefinition:
    definition = get_metric_definition(metric_id)
    if definition.status not in {
        ValidationStatus.VALIDATED,
        ValidationStatus.VALIDATED_ELSEWHERE,
        ValidationStatus.OFFICIAL,
    }:
        raise MetricNotValidatedError(
            f"'{metric_id}' no tiene estado de validación suficiente: {definition.status}"
        )
    return definition


def require_population_context(metric_id: str, *, individual: bool = False) -> MetricDefinition:
    definition = require_validated_metric(metric_id)
    if individual and not definition.individual_use:
        raise MetricNotPermittedError(f"'{metric_id}' no está autorizado para uso individual")
    return definition


def prohibit_unvalidated_risk_probability(metric_id: str) -> None:
    definition = get_metric_definition(metric_id)
    if definition.kind == MetricKind.RISK_MODEL and not definition.predictive_use_allowed:
        raise MetricNotValidatedError(
            f"No se puede emitir una probabilidad de riesgo con '{metric_id}' sin validación y calibración"
        )


def validate_registry_integrity() -> None:
    registry = {**METRIC_REGISTRY, **STRATEGIC_RISK_REGISTRY}
    for metric_id, definition in registry.items():
        if metric_id != definition.id:
            raise MetricError(f"ID inconsistente en registro: {metric_id}")
        if not definition.description.strip():
            raise MetricError(f"Descripción vacía: {metric_id}")
        if definition.status == ValidationStatus.OFFICIAL and definition.formula is not None:
            raise MetricError(
                f"Índice oficial '{metric_id}' no debe inventar una fórmula local en el registro"
            )
        if definition.kind == MetricKind.RISK_MODEL and definition.status == ValidationStatus.CATALOGUED:
            if definition.executable:
                raise MetricError(f"Riesgo catalogado no puede ser ejecutable: {metric_id}")
        if definition.status == ValidationStatus.BLOCKED and definition.executable:
            raise MetricError(f"Métrica bloqueada marcada como ejecutable: {metric_id}")


def validate_probability_output(
    metric_id: str,
    probabilities: Sequence[float] | np.ndarray,
    *,
    calibrated: bool,
    externally_validated: bool,
) -> np.ndarray:
    definition = get_metric_definition(metric_id)
    if definition.kind != MetricKind.RISK_MODEL:
        raise MetricError(f"'{metric_id}' no está registrado como risk model")
    if not definition.predictive_use_allowed:
        raise MetricNotValidatedError(f"Predicción no autorizada para '{metric_id}'")
    if not calibrated or not externally_validated:
        raise MetricNotValidatedError(
            "Una probabilidad de riesgo requiere calibración y validación fuera de muestra/external"
        )
    return _validate_probabilities(probabilities)


# ---------------------------------------------------------------------------
# Invariantes científicos de CeutIA
# ---------------------------------------------------------------------------

SCIENTIFIC_METRIC_INVARIANTS: Final[tuple[str, ...]] = (
    "Una fórmula matemáticamente válida no es automáticamente una métrica validada.",
    "Una métrica validada en otra población no se considera automáticamente validada para Ceuta.",
    "Una escala validada no equivale a un diagnóstico.",
    "Discriminación no equivale a calibración.",
    "Calibración no equivale a causalidad.",
    "AUC no mide calibración.",
    "Brier score no mide por sí solo utilidad clínica u operativa.",
    "La precisión aparente no debe utilizarse como sustituto de validación temporal/external.",
    "Los modelos de eventos raros requieren especial atención a prevalencia, calibración y validación temporal.",
    "La incertidumbre no debe eliminarse mediante redondeo o puntuaciones arbitrarias.",
    "Los datos faltantes no deben convertirse silenciosamente en riesgo.",
    "La correlación temporal no demuestra causalidad.",
    "Una señal de red social o testimonio ciudadano es una señal epistemológica, no prueba causal por sí sola.",
    "La entrada migratoria no debe convertirse en un proxy automático de criminalidad o peligrosidad.",
    "Los modelos de violencia deben predecir eventos observables, no atributos peligrosos de grupos.",
    "Nacionalidad, origen u otro atributo protegido no puede utilizarse como sustituto de evidencia conductual relevante.",
    "Los índices oficiales no deben reconstruirse con aproximaciones y presentarse como equivalentes oficiales.",
    "Un índice ambiental debe conservar unidad, escala temporal, periodo de referencia y contexto espacial.",
    "SPI y SPEI requieren especificación completa de escala, climatología y método de estandarización.",
    "Un indicador de early warning no demuestra por sí mismo que vaya a producirse una transición crítica.",
    "La ausencia de eventos observados no equivale necesariamente a ausencia de riesgo.",
    "Una predicción debe registrarse y compararse posteriormente con el outcome real.",
    "Toda probabilidad operativa debe poder auditarse hasta su modelo, versión, datos y validación.",
    "La complejidad del modelo no justifica por sí misma mejor capacidad predictiva.",
    "CeutIA debe conservar la distinción entre observación, señal, inferencia, hipótesis, predicción, escenario y decisión.",
)


validate_registry_integrity()


__all__ = [
    "MetricDomain",
    "ValidationStatus",
    "OutputChannel",
    "MetricKind",
    "EvidenceLevel",
    "MetricDefinition",
    "MetricError",
    "MetricInputError",
    "MetricNotValidatedError",
    "MetricNotPermittedError",
    "ConfusionMatrix",
    "CalibrationBin",
    "mean",
    "variance",
    "standard_deviation",
    "coefficient_of_variation",
    "quantile",
    "median_absolute_deviation",
    "z_score",
    "standardized_anomaly",
    "entropy",
    "rate",
    "growth_rate",
    "log_growth_rate",
    "first_difference",
    "second_difference",
    "relative_change",
    "demand_capacity_ratio",
    "utilization",
    "excess_demand",
    "service_capacity_gap",
    "cumulative_load",
    "exponential_moving_average",
    "autocorrelation",
    "confusion_matrix_binary",
    "sensitivity",
    "specificity",
    "positive_predictive_value",
    "negative_predictive_value",
    "accuracy",
    "balanced_accuracy",
    "f1_score",
    "matthews_correlation_coefficient",
    "mse",
    "rmse",
    "mae",
    "r_squared",
    "brier_score",
    "log_loss",
    "roc_auc",
    "precision_recall_auc",
    "calibration_bins",
    "expected_calibration_error",
    "calibration_in_the_large",
    "calibration_slope",
    "decision_curve_net_benefit",
    "integrated_brier_score",
    "prediction_interval_coverage",
    "pinball_loss",
    "standard_error_mean",
    "normal_confidence_interval",
    "relative_risk",
    "odds_ratio",
    "incidence_rate",
    "prevalence",
    "attack_rate",
    "case_fatality_ratio",
    "standardized_mortality_ratio",
    "excess_mortality",
    "epidemic_growth_rate",
    "effective_reproduction_number",
    "little_law_waiting_time",
    "little_law_number_in_system",
    "mm1_utilization",
    "mm1_mean_number_in_system",
    "mm1_mean_waiting_time",
    "mm1_mean_queue_length",
    "capacity_headroom",
    "recovery_ratio",
    "network_density",
    "degree_centralization",
    "jaccard_similarity",
    "normalized_entropy",
    "concentration_hhi",
    "finite_difference_velocity",
    "finite_difference_acceleration",
    "rolling_variance",
    "rolling_autocorrelation",
    "threshold_exceedance_rate",
    "persistence_probability",
    "early_warning_variance_trend",
    "early_warning_autocorrelation_trend",
    "changepoint_mean_shift",
    "heat_index_fahrenheit",
    "heat_index_celsius",
    "vapor_pressure_saturation_kpa",
    "relative_humidity_from_vapor_pressure",
    "pet_thornthwaite",
    "spi_from_accumulated_precipitation",
    "climatic_water_balance",
    "standardized_water_balance",
    "precipitation_intensity",
    "rainfall_accumulation_intensity",
    "standardized_anomaly_series",
    "return_period_from_exceedance_probability",
    "exceedance_probability_from_return_period",
    "fine_fuel_moisture_code_proxy",
    "air_pollution_exposure",
    "official_index_passthrough",
    "phq9_score",
    "gad7_score",
    "pcl5_score",
    "who5_score",
    "isi_score",
    "audit_c_score",
    "pss10_score",
    "bmi",
    "mean_arterial_pressure",
    "pulse_pressure",
    "standardized_component",
    "allostatic_load_count_thresholds",
    "allostatic_load_mean_z",
    "hazard_rate",
    "survival_from_hazard",
    "hazard_ratio_from_coefficients",
    "weighted_index",
    "geometric_weighted_index",
    "monte_carlo_mean",
    "monte_carlo_quantile",
    "probability_of_exceedance",
    "sensitivity_to_parameter",
    "PUBMED_PREDICTION_METHODS",
    "ALLOSTATIC_LOAD_REFERENCES",
    "TRAUMA_REFERENCES",
    "DROUGHT_REFERENCES",
    "AEMET_OFFICIAL_REFERENCES",
    "METRIC_REGISTRY",
    "STRATEGIC_RISK_REGISTRY",
    "get_metric_definition",
    "assert_metric_executable",
    "assert_output_permitted",
    "require_validated_metric",
    "require_population_context",
    "prohibit_unvalidated_risk_probability",
    "validate_registry_integrity",
    "validate_probability_output",
    "SCIENTIFIC_METRIC_INVARIANTS",
]
def get_scientific_metric_invariants() -> tuple[str, ...]:
    """Return the immutable metric-science invariants."""
    return SCIENTIFIC_METRIC_INVARIANTS


# ============================================================================
# EXPORTS
# ============================================================================



# =============================================================================
# CEUTIA — MÉTRICAS TERRITORIALES, MULTIESCALA Y DE SENSIBILIDAD SISTÉMICA
# =============================================================================
#
# Esta sección amplía la capa matemática con:
#
#   1. distribución espacial
#   2. concentración y desigualdad territorial
#   3. dependencia espacial
#   4. co-localización de fenómenos
#   5. presión multidimensional
#   6. capacidad y reserva locales
#   7. cuellos de botella territoriales
#   8. propagación y difusión
#   9. perturbaciones compuestas
#  10. sensibilidad y elasticidad
#  11. amplificación y amortiguación
#  12. no linealidad
#  13. umbrales y proximidad crítica
#  14. persistencia y turnover de hotspots
#  15. heterogeneidad de recuperación
#  16. métricas espacio-temporales
#  17. desigualdad de distribución
#  18. métricas de exposición y accesibilidad
#  19. información espacial
#  20. métricas de cascada territorial
#
# Convenciones:
#
#   x_i       = magnitud en unidad territorial i
#   x_it      = magnitud en unidad i en tiempo t
#   W_ij      = peso espacial entre i y j
#   D_i       = demanda local
#   C_i       = capacidad local
#   R_i       = reserva local
#   P_ik      = presión k en unidad i
#
# Estas métricas describen estados y relaciones observables.
# No constituyen por sí mismas modelos causales ni predicciones individuales.
# =============================================================================


def _validate_territorial_vector(
    values: Sequence[float] | np.ndarray,
    *,
    name: str,
    nonnegative: bool = False,
) -> np.ndarray:
    arr = _as_float_array(values, name=name)
    if nonnegative and np.any(arr < 0.0):
        raise MetricInputError(f"{name} debe ser no negativo")
    return arr


def _validate_spatial_matrix(
    weights: Sequence[Sequence[float]] | np.ndarray,
    n: int,
) -> np.ndarray:
    if n < 2:
        raise MetricInputError("Se requieren al menos dos unidades territoriales para una operación espacial")
    w = np.asarray(weights, dtype=float)

    if w.ndim != 2 or w.shape != (n, n):
        raise MetricInputError("weights debe tener dimensión (n, n)")
    if not np.all(np.isfinite(w)):
        raise MetricInputError("weights contiene valores no finitos")
    if np.any(w < 0.0):
        raise MetricInputError("weights no puede contener valores negativos")

    w = w.copy()
    np.fill_diagonal(w, 0.0)

    row_sum = np.sum(w, axis=1)
    if np.any(row_sum <= 0.0):
        raise MetricInputError("Cada unidad territorial debe tener al menos un vecino con peso positivo")
    if float(np.sum(row_sum)) <= 0.0:
        raise MetricInputError("weights debe contener al menos una conexión")

    return w


def territorial_total(
    values: Sequence[float] | np.ndarray,
) -> float:
    """Carga, demanda, exposición o eventos territoriales totales."""
    arr = _validate_territorial_vector(values, name="values", nonnegative=True)
    return float(np.sum(arr))


def territorial_share(
    values: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Participación territorial:

        s_i = x_i / Σ_j x_j
    """
    arr = _validate_territorial_vector(values, name="values", nonnegative=True)
    total = float(np.sum(arr))

    if total <= 0.0:
        raise MetricInputError("El total territorial debe ser positivo")

    return arr / total


def territorial_concentration_hhi(
    values: Sequence[float] | np.ndarray,
) -> float:
    """
    Índice de concentración de Herfindahl-Hirschman:

        HHI = Σ_i s_i²
    """
    shares = territorial_share(values)
    return float(np.sum(shares**2))


def territorial_entropy(
    values: Sequence[float] | np.ndarray,
    *,
    base: float = np.e,
) -> float:
    """
    Entropía territorial:

        H = -Σ_i s_i log_b(s_i)
    """
    shares = territorial_share(values)

    if base <= 0.0 or base == 1.0:
        raise MetricInputError("base debe ser positiva y distinta de 1")

    positive = shares[shares > 0.0]

    return float(-np.sum(positive * np.log(positive)) / np.log(base))


def territorial_normalized_entropy(
    values: Sequence[float] | np.ndarray,
) -> float:
    """
    Entropía territorial normalizada:

        H_norm = H / log(n)

    No está definida para una única unidad porque log(1)=0.
    """
    arr = _validate_territorial_vector(values, name="values", nonnegative=True)

    if arr.size < 2:
        raise MetricInputError("La entropía territorial normalizada requiere al menos dos unidades")

    h = territorial_entropy(arr)

    return float(h / log(arr.size))


def territorial_effective_number_of_units(
    values: Sequence[float] | np.ndarray,
) -> float:
    """
    Número efectivo de unidades:

        N_eff = 1 / HHI
    """
    hhi = territorial_concentration_hhi(values)

    if hhi <= 0.0:
        raise MetricInputError("HHI inválido")

    return float(1.0 / hhi)


def territorial_max_share(
    values: Sequence[float] | np.ndarray,
) -> float:
    """Mayor participación territorial: max(s_i)."""
    return float(np.max(territorial_share(values)))


def territorial_top_k_share(
    values: Sequence[float] | np.ndarray,
    k: int,
) -> float:
    """
    Concentración acumulada de las k unidades principales:

        TopK = Σ_{i∈Top(k)} s_i
    """
    arr = _validate_territorial_vector(values, name="values", nonnegative=True)

    if k < 1 or k > arr.size:
        raise MetricInputError("k incompatible con el número de unidades")

    shares = np.sort(territorial_share(arr))[::-1]

    return float(np.sum(shares[:k]))


def territorial_gini(
    values: Sequence[float] | np.ndarray,
) -> float:
    """
    Coeficiente de Gini:

        G = Σ_i Σ_j |x_i-x_j| / (2 n Σ_i x_i)
    """
    arr = _validate_territorial_vector(values, name="values", nonnegative=True)

    total = float(np.sum(arr))

    if total <= 0.0:
        raise MetricInputError("La suma debe ser positiva")

    n = arr.size
    differences = np.abs(arr[:, None] - arr[None, :])

    return float(np.sum(differences) / (2.0 * n * total))


def territorial_theil(
    values: Sequence[float] | np.ndarray,
) -> float:
    """
    Índice de Theil T:

        T = (1/n) Σ_i (x_i/μ) log(x_i/μ)
    """
    arr = _validate_territorial_vector(values, name="values", nonnegative=True)

    mean_value = float(np.mean(arr))

    if mean_value <= 0.0:
        raise MetricInputError("La media debe ser positiva")

    ratio = arr / mean_value
    positive = ratio > 0.0
    terms = np.zeros_like(ratio)
    terms[positive] = ratio[positive] * np.log(ratio[positive])

    return float(np.mean(terms))


def territorial_mean(
    values: Sequence[float] | np.ndarray,
) -> float:
    """Media territorial."""
    return float(np.mean(_validate_territorial_vector(values, name="values")))


def territorial_variance(
    values: Sequence[float] | np.ndarray,
) -> float:
    """Varianza transversal entre unidades territoriales."""
    arr = _validate_territorial_vector(values, name="values")
    _require_at_least_two(arr, "values")
    return float(np.var(arr, ddof=1))


def territorial_coefficient_of_variation(
    values: Sequence[float] | np.ndarray,
) -> float:
    """CV territorial = σ / |μ|."""
    arr = _validate_territorial_vector(values, name="values")
    _require_at_least_two(arr, "values")
    mean_value = float(np.mean(arr))

    if mean_value == 0.0:
        raise MetricInputError("CV indefinido con media 0")

    return float(np.std(arr, ddof=1) / abs(mean_value))


def territorial_z_scores(
    values: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Estandarización transversal territorial."""
    arr = _validate_territorial_vector(values, name="values")
    _require_at_least_two(arr, "values")
    sd = float(np.std(arr, ddof=1))

    if sd == 0.0:
        raise MetricInputError("No se puede estandarizar una variable constante")

    return (arr - float(np.mean(arr))) / sd


def territorial_spatial_lag(
    values: Sequence[float] | np.ndarray,
    weights: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """
    Rezago espacial:

        L_i = Σ_j w_ij x_j / Σ_j w_ij
    """
    x = _validate_territorial_vector(values, name="values")
    w = _validate_spatial_matrix(weights, x.size)

    row_sum = np.sum(w, axis=1)

    return (w @ x) / row_sum


def territorial_spatial_gradient(
    values: Sequence[float] | np.ndarray,
    weights: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """
    Gradiente espacial:

        G_i = x_i - L_i
    """
    x = _validate_territorial_vector(values, name="values")

    return x - territorial_spatial_lag(x, weights)


def territorial_spatial_gradient_magnitude(
    values: Sequence[float] | np.ndarray,
    weights: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """Magnitud media |G_i|."""
    gradient = territorial_spatial_gradient(values, weights)

    return float(np.mean(np.abs(gradient)))


def territorial_morans_i(
    values: Sequence[float] | np.ndarray,
    weights: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    I de Moran global:

        I = (n / S0)
            · [Σ_i Σ_j w_ij z_i z_j]
            / [Σ_i z_i²]

    No implica causalidad.
    """
    x = _validate_territorial_vector(values, name="values")
    w = _validate_spatial_matrix(weights, x.size)

    z = x - float(np.mean(x))
    denominator = float(np.sum(z**2))

    if denominator == 0.0:
        raise MetricInputError("La variable territorial tiene varianza nula")

    s0 = float(np.sum(w))

    return float(
        (x.size / s0)
        * ((z @ w @ z) / denominator)
    )


def territorial_gearys_c(
    values: Sequence[float] | np.ndarray,
    weights: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    C de Geary:

        C =
        [(n-1)/(2S0)]
        · [Σ_i Σ_j w_ij (x_i-x_j)²]
        / [Σ_i (x_i-x̄)²]
    """
    x = _validate_territorial_vector(values, name="values")
    w = _validate_spatial_matrix(weights, x.size)

    denominator = float(np.sum((x - np.mean(x)) ** 2))

    if denominator == 0.0:
        raise MetricInputError("La variable territorial tiene varianza nula")

    differences = (x[:, None] - x[None, :]) ** 2
    numerator = float(np.sum(w * differences))
    s0 = float(np.sum(w))

    return float(
        ((x.size - 1.0) / (2.0 * s0))
        * (numerator / denominator)
    )


def territorial_local_spatial_association(
    values: Sequence[float] | np.ndarray,
    weights: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """
    Asociación espacial local simplificada:

        LISA_i = z_i · Σ_j w_ij z_j / Σ_j w_ij
    """
    z = territorial_z_scores(values)
    lag = territorial_spatial_lag(z, weights)

    return z * lag


def territorial_spatial_concentration(
    values: Sequence[float] | np.ndarray,
    weights: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    Concentración espacial basada en la diferencia entre unidades
    y sus vecinos.
    """
    gradient = territorial_spatial_gradient(values, weights)
    scale = float(np.std(values, ddof=0))

    if scale == 0.0:
        return 0.0

    return float(np.mean(np.abs(gradient)) / scale)


def territorial_distance_weighted_exposure(
    exposure: Sequence[float] | np.ndarray,
    distances: Sequence[float] | np.ndarray,
    *,
    decay: float = 1.0,
) -> float:
    """
    Exposición ponderada por distancia:

        E_d = Σ_i E_i exp(-α d_i) / Σ_i exp(-α d_i)
    """
    e = _validate_territorial_vector(exposure, name="exposure", nonnegative=True)
    d = _validate_territorial_vector(distances, name="distances", nonnegative=True)
    _validate_same_length(e, d)

    if decay < 0.0:
        raise MetricInputError("decay debe ser no negativo")

    weights = np.exp(-decay * d)

    if np.sum(weights) == 0.0:
        raise MetricInputError("Pesos espaciales inválidos")

    return float(np.sum(e * weights) / np.sum(weights))


def territorial_accessibility_index(
    population: Sequence[float] | np.ndarray,
    travel_time: Sequence[float] | np.ndarray,
    *,
    decay: float = 1.0,
) -> float:
    """
    Accesibilidad gravitacional simplificada:

        A = Σ_i P_i exp(-α t_i) / Σ_i P_i
    """
    p = _validate_territorial_vector(population, name="population", nonnegative=True)
    t = _validate_territorial_vector(travel_time, name="travel_time", nonnegative=True)
    _validate_same_length(p, t)

    if decay < 0.0:
        raise MetricInputError("decay debe ser no negativo")

    total_population = float(np.sum(p))

    if total_population <= 0.0:
        raise MetricInputError("population debe tener suma positiva")

    return float(np.sum(p * np.exp(-decay * t)) / total_population)


def territorial_service_coverage(
    population: Sequence[float] | np.ndarray,
    covered_population: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Cobertura local:

        Coverage_i = covered_i / population_i
    """
    p = _validate_territorial_vector(population, name="population", nonnegative=True)
    c = _validate_territorial_vector(
        covered_population,
        name="covered_population",
        nonnegative=True,
    )
    _validate_same_length(p, c)

    if np.any(c > p):
        raise MetricInputError("covered_population no puede superar population")

    if np.any(p <= 0.0):
        raise MetricInputError("population debe ser positiva en todas las unidades")

    return c / p


def territorial_coverage_gap(
    population: Sequence[float] | np.ndarray,
    covered_population: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Brecha local de cobertura = 1 - cobertura."""
    return 1.0 - territorial_service_coverage(population, covered_population)


def territorial_demand_per_capacity(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Utilización local:

        U_i = D_i / C_i
    """
    d = _validate_territorial_vector(demand, name="demand", nonnegative=True)
    c = _validate_territorial_vector(capacity, name="capacity", nonnegative=True)
    _validate_same_length(d, c)

    if np.any(c <= 0.0):
        raise MetricInputError("capacity debe ser positiva")

    return d / c


def territorial_capacity_reserve(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Reserva absoluta:

        R_i = C_i - D_i
    """
    d = _validate_territorial_vector(demand, name="demand", nonnegative=True)
    c = _validate_territorial_vector(capacity, name="capacity", nonnegative=True)
    _validate_same_length(d, c)

    return c - d


def territorial_capacity_reserve_fraction(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Reserva relativa:

        R_i* = (C_i-D_i)/C_i = 1-U_i
    """
    utilization_values = territorial_demand_per_capacity(demand, capacity)

    return 1.0 - utilization_values


def territorial_excess_demand(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Exceso local max(D_i-C_i, 0)."""
    reserve = territorial_capacity_reserve(demand, capacity)

    return np.maximum(-reserve, 0.0)


def territorial_capacity_debt(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
) -> float:
    """
    Deuda territorial de capacidad:

        CD = Σ_i max(D_i-C_i, 0)
    """
    return float(np.sum(territorial_excess_demand(demand, capacity)))


def territorial_bottleneck_index(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
) -> int | None:
    """Unidad territorial con mayor utilización cuando el máximo es único.

    Un empate no identifica un cuello de botella único y por tanto devuelve
    ``None`` en lugar de introducir un ordenamiento arbitrario.
    """
    utilization_values = territorial_demand_per_capacity(demand, capacity)
    maximum = float(np.max(utilization_values))
    candidates = np.flatnonzero(np.isclose(utilization_values, maximum, rtol=1e-12, atol=1e-12))
    if candidates.size != 1:
        return None
    return int(candidates[0])


def territorial_bottleneck_ratio(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
) -> float:
    """
    Presión del cuello de botella:

        B = max_i(D_i/C_i)
    """
    utilization_values = territorial_demand_per_capacity(demand, capacity)

    return float(np.max(utilization_values))


def territorial_bottleneck_share(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
) -> float:
    """
    Fracción del déficit total atribuible al mayor déficit:

        B_s = max(E_i) / Σ_i E_i
    """
    excess = territorial_excess_demand(demand, capacity)
    total = float(np.sum(excess))

    if total == 0.0:
        return 0.0

    return float(np.max(excess) / total)


def territorial_saturation_fraction(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
    *,
    threshold: float = 1.0,
) -> float:
    """Fracción de unidades con D_i/C_i >= threshold."""
    if threshold <= 0.0:
        raise MetricInputError("threshold debe ser positivo")

    utilization_values = territorial_demand_per_capacity(demand, capacity)

    return float(np.mean(utilization_values >= threshold))


def territorial_bottleneck_migration(
    previous_demand: Sequence[float] | np.ndarray,
    previous_capacity: Sequence[float] | np.ndarray,
    current_demand: Sequence[float] | np.ndarray,
    current_capacity: Sequence[float] | np.ndarray,
) -> int | None:
    """
    Detecta cambio de localización del cuello de botella.
    """
    previous = territorial_bottleneck_index(
        previous_demand,
        previous_capacity,
    )
    current = territorial_bottleneck_index(
        current_demand,
        current_capacity,
    )

    if previous is None or current is None:
        return None
    return None if previous == current else current


def territorial_load_transfer(
    previous: Sequence[float] | np.ndarray,
    current: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Cambio territorial:

        ΔL_i = L_i(t) - L_i(t-1)
    """
    old = _validate_territorial_vector(previous, name="previous")
    new = _validate_territorial_vector(current, name="current")
    _validate_same_length(old, new)

    return new - old


def territorial_positive_load_transfer(
    previous: Sequence[float] | np.ndarray,
    current: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Sólo incrementos positivos de carga."""
    return np.maximum(territorial_load_transfer(previous, current), 0.0)


def territorial_load_transfer_concentration(
    previous: Sequence[float] | np.ndarray,
    current: Sequence[float] | np.ndarray,
) -> float:
    """HHI de la transferencia positiva de carga."""
    transfer = territorial_positive_load_transfer(previous, current)
    total = float(np.sum(transfer))

    if total == 0.0:
        return 0.0

    return territorial_concentration_hhi(transfer)


def territorial_spatial_propagation(
    previous: Sequence[float] | np.ndarray,
    current: Sequence[float] | np.ndarray,
    weights: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    Propagación espacial descriptiva:

        Prop =
        Σ_i Δx_i^+ · L_i(x_t-1)
        /
        Σ_i Δx_i^+
    """
    old = _validate_territorial_vector(previous, name="previous", nonnegative=True)
    new = _validate_territorial_vector(current, name="current", nonnegative=True)
    _validate_same_length(old, new)

    increase = np.maximum(new - old, 0.0)
    total_increase = float(np.sum(increase))

    if total_increase == 0.0:
        return 0.0

    old_scale = max(float(np.max(old)), 1e-12)
    normalized_old = old / old_scale
    neighbor_signal = territorial_spatial_lag(normalized_old, weights)

    return float(np.sum(increase * neighbor_signal) / total_increase)


def territorial_spatial_synchronization(
    first: Sequence[float] | np.ndarray,
    second: Sequence[float] | np.ndarray,
) -> float:
    """Correlación transversal entre dos fenómenos territoriales."""
    a = _validate_territorial_vector(first, name="first")
    b = _validate_territorial_vector(second, name="second")
    _validate_same_length(a, b)

    if np.std(a, ddof=0) == 0.0 or np.std(b, ddof=0) == 0.0:
        raise MetricInputError("No existe variabilidad territorial suficiente")

    return float(np.corrcoef(a, b)[0, 1])


def territorial_cospatial_overlap(
    first: Sequence[float] | np.ndarray,
    second: Sequence[float] | np.ndarray,
    *,
    quantile: float = 0.90,
) -> float:
    """
    Jaccard de hotspots:

        J = |A ∩ B| / |A ∪ B|
    """
    a = _validate_territorial_vector(first, name="first")
    b = _validate_territorial_vector(second, name="second")
    _validate_same_length(a, b)

    if not 0.0 < quantile < 1.0:
        raise MetricInputError("quantile debe estar entre 0 y 1")

    hotspot_a = a >= np.quantile(a, quantile)
    hotspot_b = b >= np.quantile(b, quantile)

    union = hotspot_a | hotspot_b

    if not np.any(union):
        return 0.0

    return float(np.sum(hotspot_a & hotspot_b) / np.sum(union))


def territorial_cospatial_burden(
    first: Sequence[float] | np.ndarray,
    second: Sequence[float] | np.ndarray,
) -> float:
    """
    Co-localización ponderada:

        CB = Σ_i s_i · q_i
    """
    a = _validate_territorial_vector(first, name="first", nonnegative=True)
    b = _validate_territorial_vector(second, name="second", nonnegative=True)
    _validate_same_length(a, b)

    return float(np.sum(territorial_share(a) * territorial_share(b)))


def territorial_cross_pressure(
    first: Sequence[float] | np.ndarray,
    second: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Interacción multiplicativa normalizada:

        CP_i =
        (x_i / x̄) · (y_i / ȳ)
    """
    a = _validate_territorial_vector(first, name="first", nonnegative=True)
    b = _validate_territorial_vector(second, name="second", nonnegative=True)
    _validate_same_length(a, b)

    mean_a = float(np.mean(a))
    mean_b = float(np.mean(b))

    if mean_a <= 0.0 or mean_b <= 0.0:
        raise MetricInputError("Las medias deben ser positivas")

    return (a / mean_a) * (b / mean_b)


def territorial_cross_pressure_breadth(
    first: Sequence[float] | np.ndarray,
    second: Sequence[float] | np.ndarray,
    *,
    threshold: float = 1.0,
) -> float:
    """Fracción territorial con CP_i >= threshold."""
    if threshold <= 0.0:
        raise MetricInputError("threshold debe ser positivo")

    cross = territorial_cross_pressure(first, second)

    return float(np.mean(cross >= threshold))


def territorial_multi_pressure_matrix(
    pressures: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """
    Matriz territorial:

        P = [p_i,k]

    filas = unidades territoriales
    columnas = dimensiones de presión
    """
    matrix = np.asarray(pressures, dtype=float)

    if matrix.ndim != 2:
        raise MetricInputError("pressures debe ser una matriz 2D")
    if matrix.shape[0] == 0 or matrix.shape[1] == 0:
        raise MetricInputError("pressures no puede estar vacía")
    if not np.all(np.isfinite(matrix)):
        raise MetricInputError("pressures contiene valores no finitos")
    if np.any(matrix < 0.0):
        raise MetricInputError("pressures debe ser no negativa")

    return matrix


def territorial_multi_pressure_zscores(
    pressures: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """Z-score territorial independiente para cada dimensión."""
    matrix = territorial_multi_pressure_matrix(pressures)
    if matrix.shape[0] < 2:
        raise MetricInputError("Se requieren al menos dos unidades territoriales")
    mean_values = np.mean(matrix, axis=0)
    std_values = np.std(matrix, axis=0, ddof=1)

    if np.any(std_values == 0.0):
        raise MetricInputError("Una dimensión tiene varianza territorial nula")

    return (matrix - mean_values) / std_values


def territorial_multi_pressure_score(
    pressures: Sequence[Sequence[float]] | np.ndarray,
    weights: Sequence[float] | np.ndarray | None = None,
) -> np.ndarray:
    """
    Perfil integrado:

        S_i = Σ_k w_k z_i,k
        con Σ_k w_k = 1
    """
    z = territorial_multi_pressure_zscores(pressures)

    if weights is None:
        w = np.ones(z.shape[1], dtype=float) / z.shape[1]
    else:
        w = _as_float_array(weights, name="weights")

        if w.size != z.shape[1]:
            raise MetricInputError("weights no coincide con las dimensiones")

        if np.any(w < 0.0):
            raise MetricInputError("weights debe ser no negativa")

        total = float(np.sum(w))

        if total <= 0.0:
            raise MetricInputError("weights debe tener suma positiva")

        w = w / total

    return z @ w


def territorial_pressure_breadth(
    pressures: Sequence[Sequence[float]] | np.ndarray,
    *,
    threshold: float = 1.0,
) -> np.ndarray:
    """
    Número de dimensiones que superan simultáneamente un umbral:

        B_i = Σ_k I(z_i,k >= θ)
    """
    if threshold < 0.0:
        raise MetricInputError("threshold debe ser no negativo")

    z = territorial_multi_pressure_zscores(pressures)

    return np.sum(z >= threshold, axis=1).astype(float)


def territorial_pressure_breadth_fraction(
    pressures: Sequence[Sequence[float]] | np.ndarray,
    *,
    threshold: float = 1.0,
) -> np.ndarray:
    """B_i / K."""
    z = territorial_multi_pressure_zscores(pressures)

    return territorial_pressure_breadth(
        z,
        threshold=threshold,
    ) / z.shape[1]


def territorial_pressure_dependence(
    pressures: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    Dependencia media absoluta entre dimensiones:

        D = mean(|r_jk|)
    """
    matrix = territorial_multi_pressure_matrix(pressures)

    if matrix.shape[1] < 2:
        return 0.0

    correlation = np.corrcoef(matrix, rowvar=False)
    upper = correlation[np.triu_indices(correlation.shape[0], k=1)]

    return float(np.mean(np.abs(upper)))


def territorial_pressure_concentration(
    pressures: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """Concentración territorial de la carga multidimensional."""
    score = territorial_multi_pressure_score(pressures)

    shifted = score - np.min(score) + 1e-12

    return territorial_concentration_hhi(shifted)


def territorial_pressure_hotspot(
    pressures: Sequence[Sequence[float]] | np.ndarray,
    *,
    threshold: float = 1.0,
) -> np.ndarray:
    """Fracción de dimensiones elevadas simultáneamente por unidad."""
    return territorial_pressure_breadth_fraction(
        pressures,
        threshold=threshold,
    )


def territorial_local_reserve(
    capacity: Sequence[float] | np.ndarray,
    load: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Reserva absoluta R_i = C_i-L_i."""
    return territorial_capacity_reserve(load, capacity)


def territorial_reserve_depletion(
    reserve_before: Sequence[float] | np.ndarray,
    reserve_after: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Depleción:

        ΔR_i = R_i(before) - R_i(after)
    """
    before = _validate_territorial_vector(
        reserve_before,
        name="reserve_before",
        nonnegative=True,
    )
    after = _validate_territorial_vector(
        reserve_after,
        name="reserve_after",
        nonnegative=True,
    )
    _validate_same_length(before, after)

    return before - after


def territorial_reserve_depletion_fraction(
    reserve_before: Sequence[float] | np.ndarray,
    reserve_after: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Depleción relativa de reserva."""
    before = _validate_territorial_vector(
        reserve_before,
        name="reserve_before",
        nonnegative=True,
    )
    after = _validate_territorial_vector(
        reserve_after,
        name="reserve_after",
        nonnegative=True,
    )
    _validate_same_length(before, after)

    if np.any(before <= 0.0):
        raise MetricInputError("reserve_before debe ser positiva")

    return (before - after) / before


def territorial_shock_intensity(
    baseline: Sequence[float] | np.ndarray,
    shocked: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Intensidad relativa del shock:

        S_i = |x_i^shock-x_i^base| / |x_i^base|
    """
    base = _validate_territorial_vector(
        baseline,
        name="baseline",
    )
    shock = _validate_territorial_vector(
        shocked,
        name="shocked",
    )
    _validate_same_length(base, shock)

    if np.any(base == 0.0):
        raise MetricInputError("baseline no puede contener ceros")

    return np.abs(shock - base) / np.abs(base)


def territorial_shock_direction(
    baseline: Sequence[float] | np.ndarray,
    shocked: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Dirección del shock: Δx_i."""
    return territorial_load_transfer(baseline, shocked)


def territorial_shock_breadth(
    baseline: Sequence[float] | np.ndarray,
    shocked: Sequence[float] | np.ndarray,
    *,
    threshold: float = 0.10,
) -> float:
    """Fracción territorial afectada por un shock >= threshold."""
    intensity = territorial_shock_intensity(baseline, shocked)

    if threshold < 0.0:
        raise MetricInputError("threshold debe ser no negativo")

    return float(np.mean(intensity >= threshold))


def territorial_compound_shock_breadth(
    shocks: Sequence[Sequence[float]] | np.ndarray,
    *,
    threshold: float = 1.0,
) -> np.ndarray:
    """
    Número de dimensiones de shock elevadas simultáneamente.
    """
    return territorial_pressure_breadth(
        shocks,
        threshold=threshold,
    )


def territorial_response_sensitivity(
    perturbation: Sequence[float] | np.ndarray,
    response: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Sensibilidad:

        χ_i = ΔR_i / ΔP_i
    """
    p = _validate_territorial_vector(
        perturbation,
        name="perturbation",
        nonnegative=True,
    )
    r = _validate_territorial_vector(
        response,
        name="response",
        nonnegative=True,
    )
    _validate_same_length(p, r)

    if np.any(p == 0.0):
        raise MetricInputError("perturbation no puede contener ceros")

    return r / p


def territorial_response_elasticity(
    baseline_perturbation: Sequence[float] | np.ndarray,
    perturbed_perturbation: Sequence[float] | np.ndarray,
    baseline_response: Sequence[float] | np.ndarray,
    perturbed_response: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Elasticidad:

        E_i =
        (%ΔR_i) / (%ΔP_i)
    """
    p0 = _validate_territorial_vector(
        baseline_perturbation,
        name="baseline_perturbation",
        nonnegative=True,
    )
    p1 = _validate_territorial_vector(
        perturbed_perturbation,
        name="perturbed_perturbation",
        nonnegative=True,
    )
    r0 = _validate_territorial_vector(
        baseline_response,
        name="baseline_response",
        nonnegative=True,
    )
    r1 = _validate_territorial_vector(
        perturbed_response,
        name="perturbed_response",
        nonnegative=True,
    )

    _validate_same_length(p0, p1, r0, r1)

    if np.any(p0 <= 0.0) or np.any(r0 <= 0.0):
        raise MetricInputError("Los valores basales deben ser positivos")

    dp = (p1 - p0) / p0
    dr = (r1 - r0) / r0

    if np.any(dp == 0.0):
        raise MetricInputError("La perturbación debe cambiar en todas las unidades")

    return dr / dp


def territorial_amplification_factor(
    perturbation: Sequence[float] | np.ndarray,
    response: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Amplificación:

        A_i = |ΔR_i| / |ΔP_i|
    """
    p = _validate_territorial_vector(
        perturbation,
        name="perturbation",
        nonnegative=True,
    )
    r = _validate_territorial_vector(
        response,
        name="response",
        nonnegative=True,
    )
    _validate_same_length(p, r)

    if np.any(p == 0.0):
        raise MetricInputError("perturbation no puede contener ceros")

    return np.abs(r) / np.abs(p)


def territorial_damping_factor(
    perturbation: Sequence[float] | np.ndarray,
    response: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Amortiguación:

        D_i = 1 / (1 + A_i)

    donde A_i es la amplificación absoluta.
    """
    amplification = territorial_amplification_factor(
        perturbation,
        response,
    )

    return 1.0 / (1.0 + amplification)


def territorial_small_stimulus_amplification(
    perturbation: Sequence[float] | np.ndarray,
    response: Sequence[float] | np.ndarray,
    *,
    quantile_level: float = 0.25,
) -> float:
    """
    Respuesta media relativa ante el cuarto inferior de perturbaciones.

    No es una probabilidad de evento.
    """
    p = _validate_territorial_vector(
        perturbation,
        name="perturbation",
        nonnegative=True,
    )
    r = _validate_territorial_vector(
        response,
        name="response",
        nonnegative=True,
    )
    _validate_same_length(p, r)

    if not 0.0 < quantile_level < 1.0:
        raise MetricInputError("quantile_level debe estar entre 0 y 1")

    threshold = float(np.quantile(p, quantile_level))
    mask = p <= threshold

    if not np.any(mask):
        raise MetricInputError("No existen observaciones de estímulo pequeño")

    p_mean = float(np.mean(p[mask]))
    r_mean = float(np.mean(r[mask]))

    if p_mean == 0.0:
        raise MetricInputError("La perturbación media no puede ser 0")

    return float(r_mean / p_mean)


def territorial_nonlinearity_residual_ratio(
    perturbation: Sequence[float] | np.ndarray,
    response: Sequence[float] | np.ndarray,
) -> float:
    """
    Ajuste lineal local:

        ΔR = β₀ + β₁ΔP + ε

    y calcula:

        NL = SD(ε) / SD(ΔR)

    Valores altos indican mayor desviación respecto al ajuste lineal.
    """
    p = _validate_territorial_vector(
        perturbation,
        name="perturbation",
    )
    r = _validate_territorial_vector(
        response,
        name="response",
    )
    _validate_same_length(p, r)

    if p.size < 3:
        raise MetricInputError("Se requieren al menos tres observaciones")

    dp = np.diff(p)
    dr = np.diff(r)

    if np.std(dp, ddof=0) == 0.0 or np.std(dr, ddof=0) == 0.0:
        raise MetricInputError("No existe variabilidad suficiente")

    beta = np.polyfit(dp, dr, 1)
    predicted = beta[0] * dp + beta[1]
    residual = dr - predicted

    denominator = float(np.std(dr, ddof=0))

    if denominator == 0.0:
        return 0.0

    return float(np.std(residual, ddof=0) / denominator)


def territorial_threshold_distance(
    values: Sequence[float] | np.ndarray,
    thresholds: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Distancia relativa al umbral:

        d_i = (T_i-x_i)/T_i

    d > 0: por debajo
    d = 0: umbral
    d < 0: superación
    """
    x = _validate_territorial_vector(values, name="values")
    t = _validate_territorial_vector(
        thresholds,
        name="thresholds",
        nonnegative=True,
    )
    _validate_same_length(x, t)

    if np.any(t <= 0.0):
        raise MetricInputError("thresholds debe ser positivo")

    return (t - x) / t


def territorial_threshold_breach_fraction(
    values: Sequence[float] | np.ndarray,
    thresholds: Sequence[float] | np.ndarray,
) -> float:
    """Fracción de unidades que supera su umbral."""
    distance = territorial_threshold_distance(values, thresholds)

    return float(np.mean(distance <= 0.0))


def territorial_threshold_margin(
    values: Sequence[float] | np.ndarray,
    thresholds: Sequence[float] | np.ndarray,
) -> float:
    """
    Margen mínimo territorial respecto al umbral:

        M = min_i d_i
    """
    distance = territorial_threshold_distance(values, thresholds)

    return float(np.min(distance))


def territorial_hotspot_share(
    values: Sequence[float] | np.ndarray,
    *,
    quantile_level: float = 0.90,
) -> float:
    """
    Participación de la magnitud total localizada en el hotspot superior.
    """
    arr = _validate_territorial_vector(values, name="values", nonnegative=True)

    if not 0.0 < quantile_level < 1.0:
        raise MetricInputError("quantile_level debe estar entre 0 y 1")

    threshold = float(np.quantile(arr, quantile_level))
    hotspot = arr[arr >= threshold]
    total = float(np.sum(arr))

    if total == 0.0:
        return 0.0

    return float(np.sum(hotspot) / total)


def territorial_hotspot_persistence(
    values_by_time: Sequence[Sequence[float]] | np.ndarray,
    *,
    quantile_level: float = 0.90,
) -> np.ndarray:
    """
    Persistencia de hotspot por unidad:

        H_i = (1/T) Σ_t I(x_it >= Q_t)
    """
    matrix = np.asarray(values_by_time, dtype=float)

    if matrix.ndim != 2:
        raise MetricInputError("values_by_time debe ser una matriz 2D")
    if not np.all(np.isfinite(matrix)):
        raise MetricInputError("values_by_time contiene valores no finitos")
    if not 0.0 < quantile_level < 1.0:
        raise MetricInputError("quantile_level debe estar entre 0 y 1")

    thresholds = np.quantile(matrix, quantile_level, axis=1)
    hotspot = matrix >= thresholds[:, None]

    return np.mean(hotspot, axis=0)


def territorial_hotspot_turnover(
    values_by_time: Sequence[Sequence[float]] | np.ndarray,
    *,
    quantile_level: float = 0.90,
) -> float:
    """
    Turnover de hotspots:

        TO = mean(
            |H_t Δ H_(t-1)|
            / |H_t ∪ H_(t-1)|
        )
    """
    matrix = np.asarray(values_by_time, dtype=float)

    if matrix.ndim != 2 or matrix.shape[0] < 2:
        raise MetricInputError("Se requieren al menos dos periodos")
    if not 0.0 < quantile_level < 1.0:
        raise MetricInputError("quantile_level debe estar entre 0 y 1")

    thresholds = np.quantile(matrix, quantile_level, axis=1)
    hotspot = matrix >= thresholds[:, None]

    turnovers: list[float] = []

    for t in range(1, matrix.shape[0]):
        previous = hotspot[t - 1]
        current = hotspot[t]

        union = previous | current

        if np.any(union):
            turnovers.append(float(np.sum(previous != current) / np.sum(union)))
        else:
            turnovers.append(0.0)

    return float(np.mean(turnovers))


def territorial_time_concentration(
    values_by_time: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """HHI territorial para cada instante."""
    matrix = np.asarray(values_by_time, dtype=float)

    if matrix.ndim != 2:
        raise MetricInputError("values_by_time debe ser una matriz 2D")

    return np.asarray(
        [territorial_concentration_hhi(row) for row in matrix],
        dtype=float,
    )


def territorial_time_entropy(
    values_by_time: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """Entropía territorial para cada instante."""
    matrix = np.asarray(values_by_time, dtype=float)

    if matrix.ndim != 2:
        raise MetricInputError("values_by_time debe ser una matriz 2D")

    return np.asarray(
        [territorial_normalized_entropy(row) for row in matrix],
        dtype=float,
    )


def territorial_spatiotemporal_breadth(
    values_by_time: Sequence[Sequence[float]] | np.ndarray,
    *,
    threshold: float,
) -> np.ndarray:
    """
    Número de unidades territoriales sobre el umbral en cada instante.
    """
    matrix = np.asarray(values_by_time, dtype=float)

    if matrix.ndim != 2:
        raise MetricInputError("values_by_time debe ser una matriz 2D")

    return np.sum(matrix >= threshold, axis=1).astype(float)


def territorial_spatiotemporal_breadth_fraction(
    values_by_time: Sequence[Sequence[float]] | np.ndarray,
    *,
    threshold: float,
) -> np.ndarray:
    """Fracción territorial sobre el umbral en cada instante."""
    matrix = np.asarray(values_by_time, dtype=float)

    return territorial_spatiotemporal_breadth(
        matrix,
        threshold=threshold,
    ) / matrix.shape[1]


def territorial_spatiotemporal_concentration(
    values_by_time: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    Concentración media espacio-temporal:

        C_ST = mean_t(HHI_t)
    """
    concentration = territorial_time_concentration(values_by_time)

    return float(np.mean(concentration))


def territorial_spatiotemporal_variability(
    values_by_time: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    Variabilidad espacio-temporal de la distribución:

        V_ST = SD(HHI_t)
    """
    concentration = territorial_time_concentration(values_by_time)

    if concentration.size < 2:
        raise MetricInputError("Se requieren al menos dos periodos para una desviación estándar muestral")
    if not np.all(np.isfinite(concentration)):
        raise MetricInputError("La concentración espacio-temporal contiene valores no finitos")

    return float(np.std(concentration, ddof=1))


def territorial_recovery_fraction(
    baseline: Sequence[float] | np.ndarray,
    nadir: Sequence[float] | np.ndarray,
    current: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Recuperación:

        R_i =
        (x_i,current - x_i,nadir)
        /
        (x_i,baseline - x_i,nadir)
    """
    b = _validate_territorial_vector(baseline, name="baseline")
    n = _validate_territorial_vector(nadir, name="nadir")
    c = _validate_territorial_vector(current, name="current")
    _validate_same_length(b, n, c)

    denominator = b - n

    if np.any(denominator <= 0.0):
        raise MetricInputError(
            "baseline debe ser mayor que nadir"
        )

    return (c - n) / denominator


def territorial_recovery_heterogeneity(
    baseline: Sequence[float] | np.ndarray,
    nadir: Sequence[float] | np.ndarray,
    current: Sequence[float] | np.ndarray,
) -> float:
    """Desviación estándar de la recuperación entre unidades."""
    recovery = territorial_recovery_fraction(
        baseline,
        nadir,
        current,
    )

    return float(np.std(recovery, ddof=0))


def territorial_recovery_concentration(
    baseline: Sequence[float] | np.ndarray,
    nadir: Sequence[float] | np.ndarray,
    current: Sequence[float] | np.ndarray,
) -> float:
    """
    Concentración de la recuperación positiva entre unidades.
    """
    recovery = np.maximum(
        territorial_recovery_fraction(
            baseline,
            nadir,
            current,
        ),
        0.0,
    )

    total = float(np.sum(recovery))

    if total == 0.0:
        return 0.0

    return territorial_concentration_hhi(recovery)


def territorial_recovery_asymmetry(
    recovery_times: Sequence[float] | np.ndarray,
) -> float:
    """
    Asimetría de tiempos de recuperación basada en skewness de Fisher.
    """
    arr = _validate_territorial_vector(
        recovery_times,
        name="recovery_times",
        nonnegative=True,
    )

    if arr.size < 3:
        raise MetricInputError("Se requieren al menos tres tiempos")

    mean_value = float(np.mean(arr))
    sd = float(np.std(arr, ddof=0))

    if sd == 0.0:
        return 0.0

    return float(np.mean(((arr - mean_value) / sd) ** 3))


def territorial_joint_threshold_breach(
    values: Sequence[Sequence[float]] | np.ndarray,
    thresholds: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Número de dimensiones que superan simultáneamente sus umbrales.
    """
    matrix = territorial_multi_pressure_matrix(values)
    t = _as_float_array(thresholds, name="thresholds")

    if t.size != matrix.shape[1]:
        raise MetricInputError("thresholds no coincide con las dimensiones")

    return np.sum(matrix >= t[None, :], axis=1).astype(float)


def territorial_joint_threshold_fraction(
    values: Sequence[Sequence[float]] | np.ndarray,
    thresholds: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Fracción de dimensiones que superan simultáneamente sus umbrales."""
    matrix = territorial_multi_pressure_matrix(values)

    return territorial_joint_threshold_breach(
        matrix,
        thresholds,
    ) / matrix.shape[1]


def territorial_cascade_depth(
    initial_signal: Sequence[float] | np.ndarray,
    final_signal: Sequence[float] | np.ndarray,
    *,
    threshold: float = 0.0,
    propagation_layers: Sequence[Sequence[float]] | np.ndarray | None = None,
) -> int:
    """Observed propagation-layer depth; not causal depth.

    With only initial/final states, the function can establish at most one
    observed transition. A multi-generation depth requires an explicit ordered
    sequence of observed activation layers. The metric never infers parent-child
    causal links from simultaneous or correlated activation.
    """
    initial = _validate_territorial_vector(
        initial_signal,
        name="initial_signal",
        nonnegative=True,
    )
    final = _validate_territorial_vector(
        final_signal,
        name="final_signal",
        nonnegative=True,
    )
    _validate_same_length(initial, final)

    if threshold < 0.0:
        raise MetricInputError("threshold debe ser no negativo")

    if propagation_layers is None:
        initial_active = initial > threshold
        final_active = final > threshold
        return int(np.any(final_active & ~initial_active))

    layers = np.asarray(propagation_layers, dtype=float)
    if layers.ndim != 2 or layers.shape[1] != initial.size or layers.shape[0] == 0:
        raise MetricInputError("propagation_layers debe tener forma (generaciones, unidades)")
    if not np.all(np.isfinite(layers)) or np.any(layers < 0.0):
        raise MetricInputError("propagation_layers contiene valores inválidos")

    active = layers > threshold
    if np.any(active[:-1] & ~active[1:]):
        raise MetricInputError("propagation_layers debe representar capas acumulativas sin desaparición de activaciones")
    return int(np.count_nonzero(np.any(active, axis=1)))


def territorial_cascade_amplification(
    baseline: Sequence[float] | np.ndarray,
    final: Sequence[float] | np.ndarray,
) -> float:
    """
    Amplificación territorial total:

        CA = Σ_i |Δx_i| / Σ_i |x_i,baseline|
    """
    base = _validate_territorial_vector(
        baseline,
        name="baseline",
        nonnegative=True,
    )
    end = _validate_territorial_vector(
        final,
        name="final",
        nonnegative=True,
    )
    _validate_same_length(base, end)

    denominator = float(np.sum(np.abs(base)))

    if denominator == 0.0:
        raise MetricInputError("baseline no puede tener suma 0")

    return float(np.sum(np.abs(end - base)) / denominator)


def territorial_systemic_sensitivity_matrix(
    perturbations: Sequence[Sequence[float]] | np.ndarray,
    responses: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """
    Matriz de sensibilidad:

        S_ij = Δresponse_i / Δperturbation_j

    La dimensión i corresponde a la respuesta territorial y j al estímulo.
    """
    p = np.asarray(perturbations, dtype=float)
    r = np.asarray(responses, dtype=float)

    if p.ndim != 2 or r.ndim != 2:
        raise MetricInputError("perturbations y responses deben ser matrices 2D")

    if p.shape[0] != r.shape[0]:
        raise MetricInputError(
            "perturbations y responses deben compartir unidades territoriales"
        )

    if p.shape[0] < 2:
        raise MetricInputError("Se requieren al menos dos unidades territoriales")

    p_scale = np.std(p, axis=0, ddof=1)

    if np.any(p_scale == 0.0):
        raise MetricInputError(
            "Una perturbación no presenta variabilidad territorial"
        )

    r_scale = np.std(r, axis=0, ddof=1)

    if np.any(r_scale == 0.0):
        raise MetricInputError(
            "Una respuesta no presenta variabilidad territorial"
        )

    standardized_p = (p - np.mean(p, axis=0)) / p_scale
    standardized_r = (r - np.mean(r, axis=0)) / r_scale

    return (standardized_p.T @ standardized_r) / max(p.shape[0] - 1, 1)


def territorial_dependency_matrix(
    variables: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """
    Matriz de dependencia empírica entre variables territoriales.

    La correlación muestral requiere al menos dos observaciones y no está
    definida para una dimensión territorial constante.
    """
    matrix = territorial_multi_pressure_matrix(variables)

    if matrix.shape[0] < 2:
        raise MetricInputError("Se requieren al menos dos observaciones territoriales")
    if matrix.shape[1] < 2:
        return np.ones((1, 1), dtype=float)
    if np.any(np.std(matrix, axis=0, ddof=1) == 0.0):
        raise MetricInputError("La matriz de dependencia no está definida para una variable constante")

    result = np.corrcoef(matrix, rowvar=False)
    if not np.all(np.isfinite(result)):
        raise MetricInputError("La matriz de dependencia contiene valores no finitos")
    return result


def territorial_effective_dimension(
    variables: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    Dimensión efectiva aproximada mediante eigenvalues de la matriz
    de correlación:

        D_eff =
        (Σ λ_i)² / Σ λ_i²
    """
    correlation = territorial_dependency_matrix(variables)
    eigenvalues = np.linalg.eigvalsh(correlation)
    eigenvalues = np.maximum(eigenvalues, 0.0)

    denominator = float(np.sum(eigenvalues**2))

    if denominator == 0.0:
        raise MetricInputError("Dimensión efectiva indefinida")

    return float(np.sum(eigenvalues) ** 2 / denominator)


def territorial_principal_component_concentration(
    variables: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    Proporción de varianza explicada por el primer componente principal:

        PC1 = λ_max / Σ_i λ_i
    """
    correlation = territorial_dependency_matrix(variables)
    eigenvalues = np.linalg.eigvalsh(correlation)
    eigenvalues = np.maximum(eigenvalues, 0.0)

    total = float(np.sum(eigenvalues))

    if total == 0.0:
        raise MetricInputError("Varianza total nula")

    return float(np.max(eigenvalues) / total)


def territorial_systemic_headroom(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
) -> float:
    """
    Margen sistémico mínimo:

        H = min_i(1-D_i/C_i)
    """
    reserve = territorial_capacity_reserve_fraction(
        demand,
        capacity,
    )

    return float(np.min(reserve))


def territorial_systemic_headroom_mean(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
) -> float:
    """Margen medio territorial."""
    reserve = territorial_capacity_reserve_fraction(
        demand,
        capacity,
    )

    return float(np.mean(reserve))


def territorial_capacity_inequality(
    capacity: Sequence[float] | np.ndarray,
) -> float:
    """Desigualdad territorial de capacidad mediante Gini."""
    return territorial_gini(
        _validate_territorial_vector(
            capacity,
            name="capacity",
            nonnegative=True,
        )
    )


def territorial_demand_inequality(
    demand: Sequence[float] | np.ndarray,
) -> float:
    """Desigualdad territorial de demanda mediante Gini."""
    return territorial_gini(
        _validate_territorial_vector(
            demand,
            name="demand",
            nonnegative=True,
        )
    )


def territorial_exposure_inequality(
    exposure: Sequence[float] | np.ndarray,
) -> float:
    """Desigualdad territorial de exposición mediante Gini."""
    return territorial_gini(
        _validate_territorial_vector(
            exposure,
            name="exposure",
            nonnegative=True,
        )
    )


def territorial_load_capacity_imbalance(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
) -> float:
    """
    Desviación territorial del ratio demanda/capacidad:

        I = SD(D_i/C_i)
    """
    utilization_values = territorial_demand_per_capacity(
        demand,
        capacity,
    )

    return float(np.std(utilization_values, ddof=0))


def territorial_load_capacity_tail(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
    *,
    quantile_level: float = 0.90,
) -> float:
    """Cuantil alto de utilización territorial."""
    if not 0.0 < quantile_level < 1.0:
        raise MetricInputError("quantile_level debe estar entre 0 y 1")

    utilization_values = territorial_demand_per_capacity(
        demand,
        capacity,
    )

    return float(np.quantile(utilization_values, quantile_level))


def territorial_capacity_redundancy(
    capacities: Sequence[float] | np.ndarray,
) -> float:
    """
    Redundancia relativa:

        R = 1 - max(C_i)/Σ_i C_i

    Describe distribución de capacidad, no sustituibilidad funcional.
    """
    c = _validate_territorial_vector(
        capacities,
        name="capacities",
        nonnegative=True,
    )

    total = float(np.sum(c))

    if total <= 0.0:
        raise MetricInputError("La capacidad total debe ser positiva")

    return float(1.0 - np.max(c) / total)


def territorial_single_point_dependency(
    capacities: Sequence[float] | np.ndarray,
) -> float:
    """
    Dependencia de la unidad dominante:

        SPD = max(C_i) / Σ_i C_i
    """
    return 1.0 - territorial_capacity_redundancy(capacities)


def territorial_observation_coverage(
    observed: Sequence[float] | np.ndarray,
    possible: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Cobertura de observación:

        O_i = observed_i / possible_i
    """
    obs = _validate_territorial_vector(
        observed,
        name="observed",
        nonnegative=True,
    )
    pos = _validate_territorial_vector(
        possible,
        name="possible",
        nonnegative=True,
    )
    _validate_same_length(obs, pos)

    if np.any(pos <= 0.0):
        raise MetricInputError("possible debe ser positiva")

    if np.any(obs > pos):
        raise MetricInputError("observed no puede superar possible")

    return obs / pos


def territorial_observation_gap(
    observed: Sequence[float] | np.ndarray,
    possible: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Brecha de observación = 1 - cobertura."""
    return 1.0 - territorial_observation_coverage(
        observed,
        possible,
    )


def territorial_signal_to_noise(
    signal: Sequence[float] | np.ndarray,
    noise: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Relación señal/ruido:

        SNR_i = signal_i / noise_i
    """
    s = _validate_territorial_vector(signal, name="signal", nonnegative=True)
    n = _validate_territorial_vector(noise, name="noise", nonnegative=True)
    _validate_same_length(s, n)

    if np.any(n <= 0.0):
        raise MetricInputError("noise debe ser positiva")

    return s / n


def territorial_information_concentration(
    information_volume: Sequence[float] | np.ndarray,
) -> float:
    """
    Concentración territorial de información observada mediante HHI.
    """
    return territorial_concentration_hhi(
        _validate_territorial_vector(
            information_volume,
            name="information_volume",
            nonnegative=True,
        )
    )


def territorial_data_coverage_weighted_mean(
    values: Sequence[float] | np.ndarray,
    coverage: Sequence[float] | np.ndarray,
) -> float:
    """
    Media ponderada por cobertura:

        μ_c = Σ_i x_i c_i / Σ_i c_i
    """
    x = _validate_territorial_vector(values, name="values")
    c = _validate_territorial_vector(
        coverage,
        name="coverage",
        nonnegative=True,
    )
    _validate_same_length(x, c)

    if np.sum(c) <= 0.0:
        raise MetricInputError("coverage debe tener suma positiva")

    return float(np.sum(x * c) / np.sum(c))


TERRITORIAL_SYSTEMIC_METRICS: Final[dict[str, object]] = {
    "territorial_total": territorial_total,
    "territorial_share": territorial_share,
    "territorial_concentration_hhi": territorial_concentration_hhi,
    "territorial_entropy": territorial_entropy,
    "territorial_normalized_entropy": territorial_normalized_entropy,
    "territorial_effective_number_of_units": territorial_effective_number_of_units,
    "territorial_max_share": territorial_max_share,
    "territorial_top_k_share": territorial_top_k_share,
    "territorial_gini": territorial_gini,
    "territorial_theil": territorial_theil,
    "territorial_mean": territorial_mean,
    "territorial_variance": territorial_variance,
    "territorial_coefficient_of_variation": territorial_coefficient_of_variation,
    "territorial_z_scores": territorial_z_scores,
    "territorial_spatial_lag": territorial_spatial_lag,
    "territorial_spatial_gradient": territorial_spatial_gradient,
    "territorial_spatial_gradient_magnitude": territorial_spatial_gradient_magnitude,
    "territorial_morans_i": territorial_morans_i,
    "territorial_gearys_c": territorial_gearys_c,
    "territorial_local_spatial_association": territorial_local_spatial_association,
    "territorial_spatial_concentration": territorial_spatial_concentration,
    "territorial_distance_weighted_exposure": territorial_distance_weighted_exposure,
    "territorial_accessibility_index": territorial_accessibility_index,
    "territorial_service_coverage": territorial_service_coverage,
    "territorial_coverage_gap": territorial_coverage_gap,
    "territorial_demand_per_capacity": territorial_demand_per_capacity,
    "territorial_capacity_reserve": territorial_capacity_reserve,
    "territorial_capacity_reserve_fraction": territorial_capacity_reserve_fraction,
    "territorial_excess_demand": territorial_excess_demand,
    "territorial_capacity_debt": territorial_capacity_debt,
    "territorial_bottleneck_index": territorial_bottleneck_index,
    "territorial_bottleneck_ratio": territorial_bottleneck_ratio,
    "territorial_bottleneck_share": territorial_bottleneck_share,
    "territorial_saturation_fraction": territorial_saturation_fraction,
    "territorial_bottleneck_migration": territorial_bottleneck_migration,
    "territorial_load_transfer": territorial_load_transfer,
    "territorial_positive_load_transfer": territorial_positive_load_transfer,
    "territorial_load_transfer_concentration": territorial_load_transfer_concentration,
    "territorial_spatial_propagation": territorial_spatial_propagation,
    "territorial_spatial_synchronization": territorial_spatial_synchronization,
    "territorial_cospatial_overlap": territorial_cospatial_overlap,
    "territorial_cospatial_burden": territorial_cospatial_burden,
    "territorial_cross_pressure": territorial_cross_pressure,
    "territorial_cross_pressure_breadth": territorial_cross_pressure_breadth,
    "territorial_multi_pressure_matrix": territorial_multi_pressure_matrix,
    "territorial_multi_pressure_zscores": territorial_multi_pressure_zscores,
    "territorial_multi_pressure_score": territorial_multi_pressure_score,
    "territorial_pressure_breadth": territorial_pressure_breadth,
    "territorial_pressure_breadth_fraction": territorial_pressure_breadth_fraction,
    "territorial_pressure_dependence": territorial_pressure_dependence,
    "territorial_pressure_concentration": territorial_pressure_concentration,
    "territorial_pressure_hotspot": territorial_pressure_hotspot,
    "territorial_local_reserve": territorial_local_reserve,
    "territorial_reserve_depletion": territorial_reserve_depletion,
    "territorial_reserve_depletion_fraction": territorial_reserve_depletion_fraction,
    "territorial_shock_intensity": territorial_shock_intensity,
    "territorial_shock_direction": territorial_shock_direction,
    "territorial_shock_breadth": territorial_shock_breadth,
    "territorial_compound_shock_breadth": territorial_compound_shock_breadth,
    "territorial_response_sensitivity": territorial_response_sensitivity,
    "territorial_response_elasticity": territorial_response_elasticity,
    "territorial_amplification_factor": territorial_amplification_factor,
    "territorial_damping_factor": territorial_damping_factor,
    "territorial_small_stimulus_amplification": territorial_small_stimulus_amplification,
    "territorial_nonlinearity_residual_ratio": territorial_nonlinearity_residual_ratio,
    "territorial_threshold_distance": territorial_threshold_distance,
    "territorial_threshold_breach_fraction": territorial_threshold_breach_fraction,
    "territorial_threshold_margin": territorial_threshold_margin,
    "territorial_hotspot_share": territorial_hotspot_share,
    "territorial_hotspot_persistence": territorial_hotspot_persistence,
    "territorial_hotspot_turnover": territorial_hotspot_turnover,
    "territorial_time_concentration": territorial_time_concentration,
    "territorial_time_entropy": territorial_time_entropy,
    "territorial_spatiotemporal_breadth": territorial_spatiotemporal_breadth,
    "territorial_spatiotemporal_breadth_fraction": territorial_spatiotemporal_breadth_fraction,
    "territorial_spatiotemporal_concentration": territorial_spatiotemporal_concentration,
    "territorial_spatiotemporal_variability": territorial_spatiotemporal_variability,
    "territorial_recovery_fraction": territorial_recovery_fraction,
    "territorial_recovery_heterogeneity": territorial_recovery_heterogeneity,
    "territorial_recovery_concentration": territorial_recovery_concentration,
    "territorial_recovery_asymmetry": territorial_recovery_asymmetry,
    "territorial_joint_threshold_breach": territorial_joint_threshold_breach,
    "territorial_joint_threshold_fraction": territorial_joint_threshold_fraction,
    "territorial_cascade_depth": territorial_cascade_depth,
    "territorial_cascade_amplification": territorial_cascade_amplification,
    "territorial_systemic_sensitivity_matrix": territorial_systemic_sensitivity_matrix,
    "territorial_dependency_matrix": territorial_dependency_matrix,
    "territorial_effective_dimension": territorial_effective_dimension,
    "territorial_principal_component_concentration": territorial_principal_component_concentration,
    "territorial_systemic_headroom": territorial_systemic_headroom,
    "territorial_systemic_headroom_mean": territorial_systemic_headroom_mean,
    "territorial_capacity_inequality": territorial_capacity_inequality,
    "territorial_demand_inequality": territorial_demand_inequality,
    "territorial_exposure_inequality": territorial_exposure_inequality,
    "territorial_load_capacity_imbalance": territorial_load_capacity_imbalance,
    "territorial_load_capacity_tail": territorial_load_capacity_tail,
    "territorial_capacity_redundancy": territorial_capacity_redundancy,
    "territorial_single_point_dependency": territorial_single_point_dependency,
    "territorial_observation_coverage": territorial_observation_coverage,
    "territorial_observation_gap": territorial_observation_gap,
    "territorial_signal_to_noise": territorial_signal_to_noise,
    "territorial_information_concentration": territorial_information_concentration,
    "territorial_data_coverage_weighted_mean": territorial_data_coverage_weighted_mean,
}


TERRITORIAL_SYSTEMIC_INVARIANTS: Final[tuple[str, ...]] = (
    "La concentración espacial describe la distribución de una variable, "
    "no una peligrosidad inherente de las personas residentes.",
    "La presencia de altercados, incendios, déficit de agua u otros eventos "
    "en una zona no convierte a esa zona en una categoría de personas.",
    "Co-localización no implica causalidad.",
    "Correlación espacial no implica causalidad.",
    "Moran y Geary dependen de la matriz W y de la definición de vecindad.",
    "La escala espacial modifica los resultados y debe conservarse explícitamente.",
    "La unidad territorial puede ser barrio, distrito, cuadrícula u otra unidad "
    "operativa; no debe asumirse que el barrio sea siempre la escala correcta.",
    "Los denominadores poblacionales y de exposición deben conservarse.",
    "Una perturbación pequeña no implica por sí misma un resultado grave.",
    "Una respuesta amplificada describe sensibilidad observada, no peligrosidad individual.",
    "Una cascada observada no demuestra que vaya a repetirse.",
    "Una presión multidimensional agregada no sustituye las variables originales.",
    "La incertidumbre, cobertura y calidad de observación deben acompañar a toda "
    "métrica territorial operacionalmente relevante.",
    "Las métricas de violencia deben referirse a eventos observables y no a "
    "nacionalidad, origen, etnia u otros atributos protegidos.",
    "Las métricas territoriales no deben utilizarse para inferir peligrosidad individual.",
    "Un hotspot depende de la variable, ventana temporal, umbral y escala espacial.",
    "La ausencia de observación no equivale automáticamente a ausencia del fenómeno.",
    "La amplificación no equivale a probabilidad.",
    "La sensibilidad no equivale a causalidad.",
    "La robustez de una métrica no implica verdad del mecanismo que pudiera explicarla.",
)


__all__.extend(TERRITORIAL_SYSTEMIC_METRICS.keys())
