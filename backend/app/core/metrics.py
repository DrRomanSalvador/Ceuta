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
    _require_at_least_two(arr, "values")
    if lag < 1 or lag >= arr.size:
        raise MetricInputError("lag debe estar entre 1 y n-1")
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
    mean_logit = float(np.mean(np.log(np.clip(p, 1e-15, 1 - 1e-15) / np.clip(1 - p, 1e-15, 1 - 1e-15))))
    target_logit = log(observed / (1.0 - observed)) if 0 < observed < 1 else float("inf")
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