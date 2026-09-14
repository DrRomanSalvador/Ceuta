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


def sensitivity(y_true: Sequence[int] | np.ndarray, y_pred: Sequence[int] | np.ndarray) -> float:
    cm = confusion_matrix_binary(y_true, y_pred)
    denominator = cm.true_positive + cm.false_negative
    if denominator == 0:
        raise MetricInputError("sensibilidad indefinida sin positivos reales")
    return cm.true_positive / denominator


def specificity(y_true: Sequence[int] | np.ndarray, y_pred: Sequence[int] | np.ndarray) -> float:
    cm = confusion_matrix_binary(y_true, y_pred)
    denominator = cm.true_negative + cm.false_positive
    if denominator == 0:
        raise MetricInputError("especificidad indefinida sin negativos reales")
    return cm.true_negative / denominator


def positive_predictive_value(y_true: Sequence[int] | np.ndarray, y_pred: Sequence[int] | np.ndarray) -> float:
    cm = confusion_matrix_binary(y_true, y_pred)
    denominator = cm.true_positive + cm.false_positive
    if denominator == 0:
        raise MetricInputError("valor predictivo positivo indefinido sin positivos predichos")
    return cm.true_positive / denominator


def negative_predictive_value(y_true: Sequence[int] | np.ndarray, y_pred: Sequence[int] | np.ndarray) -> float:
    cm = confusion_matrix_binary(y_true, y_pred)
    denominator = cm.true_negative + cm.false_negative
    if denominator == 0:
        raise MetricInputError("valor predictivo negativo indefinido sin negativos predichos")
    return cm.true_negative / denominator


def accuracy(y_true: Sequence[int] | np.ndarray, y_pred: Sequence[int] | np.ndarray) -> float:
    cm = confusion_matrix_binary(y_true, y_pred)
    if cm.total == 0:
        raise MetricInputError("accuracy requiere observaciones")
    return (cm.true_positive + cm.true_negative) / cm.total


def balanced_accuracy(y_true: Sequence[int] | np.ndarray, y_pred: Sequence[int] | np.ndarray) -> float:
    return (sensitivity(y_true, y_pred) + specificity(y_true, y_pred)) / 2.0


def f1_score(y_true: Sequence[int] | np.ndarray, y_pred: Sequence[int] | np.ndarray) -> float:
    cm = confusion_matrix_binary(y_true, y_pred)
    denominator = 2 * cm.true_positive + cm.false_positive + cm.false_negative
    if denominator == 0:
        raise MetricInputError("F1 indefinido sin positivos reales ni predichos")
    return 2 * cm.true_positive / denominator


def matthews_correlation_coefficient(y_true: Sequence[int] | np.ndarray, y_pred: Sequence[int] | np.ndarray) -> float:
    cm = confusion_matrix_binary(y_true, y_pred)
    numerator = cm.true_positive * cm.true_negative - cm.false_positive * cm.false_negative
    denominator = sqrt(
        (cm.true_positive + cm.false_positive)
        * (cm.true_positive + cm.false_negative)
        * (cm.true_negative + cm.false_positive)
        * (cm.true_negative + cm.false_negative)
    )
    if denominator == 0.0:
        raise MetricInputError("MCC indefinido con una clase ausente en truth/prediction")
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
    denominator = float(np.sum((truth - np.mean(truth)) ** 2))
    if denominator == 0.0:
        raise MetricInputError("R² indefinido con outcome constante")
    return float(1.0 - np.sum((truth - pred) ** 2) / denominator)


def _validate_spatial_matrix(
    weights: Sequence[Sequence[float]] | np.ndarray,
    n: int,
) -> np.ndarray:
    w = np.asarray(weights, dtype=float)

    if n < 2:
        raise MetricInputError("Las métricas espaciales requieren al menos dos unidades")
    if w.ndim != 2 or w.shape != (n, n):
        raise MetricInputError("weights debe tener dimensión (n, n)")
    if not np.all(np.isfinite(w)):
        raise MetricInputError("weights contiene valores no finitos")
    if np.any(w < 0.0):
        raise MetricInputError("weights no puede contener valores negativos")
    row_sum = np.sum(w, axis=1)
    if np.any(row_sum <= 0.0):
        raise MetricInputError("Cada unidad territorial debe tener al menos una conexión espacial")
    if float(np.sum(w)) <= 0.0:
        raise MetricInputError("weights debe contener al menos una conexión")

    return w
