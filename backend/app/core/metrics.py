# Añadir al final de backend/app/core/metrics.py, antes de __all__ si existe.
# Si __all__ ya está al final, insertar este bloque antes de ella.

# ---------------------------------------------------------------------------
# Métricas dinámicas adicionales de CeutIA
# ---------------------------------------------------------------------------

def skewness(values: Sequence[float] | np.ndarray) -> float:
    """Asimetría de una distribución."""
    arr = _as_float_array(values, name="values")
    _require_at_least_two(arr, "values")
    mean = float(np.mean(arr))
    std = float(np.std(arr, ddof=0))
    if std == 0.0:
        raise MetricInputError("Skewness indefinida para una distribución constante")
    return float(np.mean(((arr - mean) / std) ** 3))


def kurtosis_excess(values: Sequence[float] | np.ndarray) -> float:
    """Curtosis en exceso (Fisher)."""
    arr = _as_float_array(values, name="values")
    _require_at_least_two(arr, "values")
    mean = float(np.mean(arr))
    std = float(np.std(arr, ddof=0))
    if std == 0.0:
        raise MetricInputError("Curtosis indefinida para una distribución constante")
    return float(np.mean(((arr - mean) / std) ** 4) - 3.0)


def coefficient_of_variation(
    values: Sequence[float] | np.ndarray,
) -> float:
    """Coeficiente de variación: desviación estándar / media."""
    arr = _as_float_array(values, name="values")
    _require_at_least_two(arr, "values")
    mean = float(np.mean(arr))
    if mean == 0.0:
        raise MetricInputError("Coeficiente de variación indefinido con media cero")
    return float(np.std(arr, ddof=1) / abs(mean))


def rolling_coefficient_of_variation(
    values: Sequence[float] | np.ndarray,
    window: int,
) -> np.ndarray:
    """Coeficiente de variación móvil para detectar cambios de estabilidad."""
    arr = _as_float_array(values, name="values")
    if window < 2:
        raise MetricInputError("window debe ser >= 2")
    if arr.size < window:
        raise MetricInputError("La serie es menor que window")

    result = np.empty(arr.size - window + 1, dtype=float)
    for i in range(result.size):
        result[i] = coefficient_of_variation(arr[i : i + window])
    return result


def recovery_time(
    times: Sequence[float] | np.ndarray,
    values: Sequence[float] | np.ndarray,
    *,
    baseline: float,
    tolerance: float,
    direction: str = "absolute",
) -> float | None:
    """
    Tiempo necesario para regresar al intervalo de recuperación alrededor
    del baseline después de una perturbación.

    Devuelve None si la recuperación no aparece en la serie.
    """
    t = _as_float_array(times, name="times")
    x = _as_float_array(values, name="values")
    _validate_same_length(t, x)

    if t.size < 2:
        raise MetricInputError("Se requieren al menos dos observaciones")
    if tolerance < 0:
        raise MetricInputError("tolerance debe ser >= 0")
    if np.any(np.diff(t) < 0):
        raise MetricInputError("times debe estar ordenado ascendentemente")

    deviation = np.abs(x - baseline)

    if direction == "absolute":
        outside = deviation > tolerance
    elif direction == "above":
        outside = x > baseline + tolerance
    elif direction == "below":
        outside = x < baseline - tolerance
    else:
        raise MetricInputError(
            "direction debe ser 'absolute', 'above' o 'below'"
        )

    disturbed = np.flatnonzero(outside)
    if disturbed.size == 0:
        return 0.0

    start = int(disturbed[0])
    for i in range(start, x.size):
        if not outside[i]:
            return float(t[i] - t[start])

    return None


def recovery_ratio_dynamic(
    baseline: float,
    minimum_after_event: float,
    recovered_value: float,
) -> float:
    """
    Recuperación relativa respecto a la pérdida producida por el evento.
    """
    loss = baseline - minimum_after_event
    if loss == 0.0:
        raise MetricInputError("No existe pérdida para calcular recuperación")
    return float((recovered_value - minimum_after_event) / loss)


def dynamic_slope(
    times: Sequence[float] | np.ndarray,
    values: Sequence[float] | np.ndarray,
) -> float:
    """Pendiente lineal global de una trayectoria."""
    t = _as_float_array(times, name="times")
    x = _as_float_array(values, name="values")
    _validate_same_length(t, x)

    if t.size < 2:
        raise MetricInputError("Se requieren al menos dos observaciones")

    centered_t = t - np.mean(t)
    denominator = float(np.sum(centered_t**2))
    if denominator == 0.0:
        raise MetricInputError("Los tiempos deben contener variación")

    return float(np.sum(centered_t * (x - np.mean(x))) / denominator)


def dynamic_acceleration(
    times: Sequence[float] | np.ndarray,
    values: Sequence[float] | np.ndarray,
) -> float:
    """Cambio de la velocidad de la trayectoria mediante ajuste cuadrático."""
    t = _as_float_array(times, name="times")
    x = _as_float_array(values, name="values")
    _validate_same_length(t, x)

    if t.size < 3:
        raise MetricInputError("Se requieren al menos tres observaciones")

    coefficients = np.polyfit(t, x, 2)
    return float(2.0 * coefficients[0])


def hysteresis_gap(
    upward_values: Sequence[float] | np.ndarray,
    downward_values: Sequence[float] | np.ndarray,
) -> float:
    """
    Diferencia media entre trayectorias de subida y bajada.

    No demuestra por sí misma histéresis causal; cuantifica separación
    entre trayectorias observadas.
    """
    up = _as_float_array(upward_values, name="upward_values")
    down = _as_float_array(downward_values, name="downward_values")
    _validate_same_length(up, down)
    return float(np.mean(np.abs(up - down)))


def covariance(
    x: Sequence[float] | np.ndarray,
    y: Sequence[float] | np.ndarray,
) -> float:
    """Covarianza muestral."""
    left = _as_float_array(x, name="x")
    right = _as_float_array(y, name="y")
    _validate_same_length(left, right)
    if left.size < 2:
        raise MetricInputError("Se requieren al menos dos observaciones")
    return float(np.cov(left, right, ddof=1)[0, 1])


def correlation(
    x: Sequence[float] | np.ndarray,
    y: Sequence[float] | np.ndarray,
) -> float:
    """Correlación de Pearson."""
    left = _as_float_array(x, name="x")
    right = _as_float_array(y, name="y")
    _validate_same_length(left, right)

    if left.size < 2:
        raise MetricInputError("Se requieren al menos dos observaciones")

    left_std = float(np.std(left, ddof=1))
    right_std = float(np.std(right, ddof=1))

    if left_std == 0.0 or right_std == 0.0:
        raise MetricInputError("Correlación indefinida para una variable constante")

    return float(np.corrcoef(left, right)[0, 1])


def lagged_correlation(
    x: Sequence[float] | np.ndarray,
    y: Sequence[float] | np.ndarray,
    lag: int,
) -> float:
    """
    Correlación entre x(t) e y(t+lag).

    lag > 0: x precede a y.
    """
    left = _as_float_array(x, name="x")
    right = _as_float_array(y, name="y")
    _validate_same_length(left, right)

    if lag >= left.size or lag <= -left.size:
        raise MetricInputError("lag fuera del rango de la serie")

    if lag > 0:
        return correlation(left[:-lag], right[lag:])
    if lag < 0:
        shift = abs(lag)
        return correlation(left[shift:], right[:-shift])
    return correlation(left, right)


def interaction_effect(
    observed_joint: float,
    expected_additive: float,
) -> float:
    """
    Desviación respecto a un efecto aditivo esperado.

    No constituye identificación causal por sí sola.
    """
    if not (isfinite(observed_joint) and isfinite(expected_additive)):
        raise MetricInputError("Los valores deben ser finitos")
    return float(observed_joint - expected_additive)


def coupling_strength(
    x: Sequence[float] | np.ndarray,
    y: Sequence[float] | np.ndarray,
    *,
    lag: int = 0,
) -> float:
    """Magnitud absoluta de la asociación temporal entre dos variables."""
    return abs(lagged_correlation(x, y, lag))


def synchronization_index(
    series: Sequence[Sequence[float] | np.ndarray],
) -> float:
    """
    Sincronización media absoluta entre múltiples series normalizadas.

    Devuelve 0 si no existe sincronización lineal y 1 si las trayectorias
    presentan correlación lineal perfecta en magnitud.
    """
    arrays = [_as_float_array(item, name="series") for item in series]

    if len(arrays) < 2:
        raise MetricInputError("Se requieren al menos dos series")

    length = arrays[0].size
    if length < 2:
        raise MetricInputError("Cada serie debe contener al menos dos observaciones")

    if any(item.size != length for item in arrays):
        raise MetricInputError("Todas las series deben tener la misma longitud")

    correlations: list[float] = []
    for i in range(len(arrays)):
        for j in range(i + 1, len(arrays)):
            correlations.append(abs(correlation(arrays[i], arrays[j])))

    return float(np.mean(correlations))


def effective_capacity(
    nominal_capacity: float,
    availability: float,
    efficiency: float,
) -> float:
    """
    Capacidad efectiva = capacidad nominal × disponibilidad × eficiencia.
    """
    if nominal_capacity < 0:
        raise MetricInputError("nominal_capacity debe ser >= 0")
    if not 0.0 <= availability <= 1.0:
        raise MetricInputError("availability debe estar entre 0 y 1")
    if not 0.0 <= efficiency <= 1.0:
        raise MetricInputError("efficiency debe estar entre 0 y 1")

    return float(nominal_capacity * availability * efficiency)


def capacity_reserve(
    effective_capacity_value: float,
    demand: float,
) -> float:
    """Reserva absoluta de capacidad."""
    if effective_capacity_value < 0 or demand < 0:
        raise MetricInputError("Capacidad y demanda deben ser >= 0")
    return float(effective_capacity_value - demand)


def time_to_exhaustion(
    current_reserve: float,
    depletion_rate: float,
) -> float | None:
    """
    Tiempo estimado hasta agotamiento de la reserva bajo tasa constante.

    No debe interpretarse como predicción si la tasa no es estable.
    """
    if current_reserve < 0:
        raise MetricInputError("current_reserve debe ser >= 0")
    if depletion_rate < 0:
        raise MetricInputError("depletion_rate debe ser >= 0")

    if depletion_rate == 0.0:
        return None

    return float(current_reserve / depletion_rate)


def amplification_gain(
    input_change: float,
    output_change: float,
) -> float:
    """Ganancia absoluta de una perturbación."""
    if input_change == 0.0:
        raise MetricInputError("input_change no puede ser cero")
    return float(abs(output_change / input_change))


def cascade_amplification(
    initial_impact: float,
    final_impact: float,
) -> float:
    """Relación entre impacto final e impacto inicial."""
    if initial_impact == 0.0:
        raise MetricInputError("initial_impact no puede ser cero")
    return float(final_impact / initial_impact)


def propagation_depth(
    graph,
    source,
    *,
    target=None,
) -> int | None:
    """
    Distancia mínima de propagación en un grafo NetworkX.

    Requiere un objeto compatible con NetworkX.
    """
    import networkx as nx

    if source not in graph:
        raise MetricInputError("source no existe en el grafo")

    if target is not None:
        if target not in graph:
            raise MetricInputError("target no existe en el grafo")
        try:
            return int(nx.shortest_path_length(graph, source, target))
        except nx.NetworkXNoPath:
            return None

    distances = nx.single_source_shortest_path_length(graph, source)
    if not distances:
        return 0

    return int(max(distances.values()))


def normalized_hhi(weights: Sequence[float] | np.ndarray) -> float:
    """
    HHI normalizado para concentración de recursos/demanda.

    0 = distribución uniforme.
    1 = concentración máxima.
    """
    arr = _as_float_array(weights, name="weights")

    if arr.size < 2:
        raise MetricInputError("Se requieren al menos dos componentes")
    if np.any(arr < 0):
        raise MetricInputError("Los pesos no pueden ser negativos")

    total = float(np.sum(arr))
    if total <= 0.0:
        raise MetricInputError("La suma de pesos debe ser positiva")

    shares = arr / total
    hhi = float(np.sum(shares**2))
    minimum = 1.0 / arr.size

    if minimum == 1.0:
        return 0.0

    return float((hhi - minimum) / (1.0 - minimum))


def bottleneck_ratio(
    demand: float,
    capacity: float,
) -> float:
    """Demanda/capacidad; >1 indica exceso de demanda sobre capacidad."""
    if demand < 0 or capacity <= 0:
        raise MetricInputError("demand >= 0 y capacity > 0 son obligatorios")
    return float(demand / capacity)


def regime_distance(
    current_state: Sequence[float] | np.ndarray,
    reference_state: Sequence[float] | np.ndarray,
) -> float:
    """Distancia euclídea entre estados normalizados en el mismo espacio."""
    current = _as_float_array(current_state, name="current_state")
    reference = _as_float_array(reference_state, name="reference_state")
    _validate_same_length(current, reference)
    return float(np.linalg.norm(current - reference))


def state_velocity(
    times: Sequence[float] | np.ndarray,
    states: Sequence[Sequence[float] | np.ndarray],
) -> np.ndarray:
    """
    Velocidad aproximada del estado multidimensional mediante diferencias
    finitas.
    """
    t = _as_float_array(times, name="times")
    x = np.asarray(states, dtype=float)

    if x.ndim != 2:
        raise MetricInputError("states debe ser una matriz 2D")
    if x.shape[0] != t.size:
        raise MetricInputError("times y states deben tener la misma longitud")
    if t.size < 2:
        raise MetricInputError("Se requieren al menos dos estados")

    dt = np.diff(t)
    if np.any(dt <= 0):
        raise MetricInputError("times debe ser estrictamente creciente")

    return np.diff(x, axis=0) / dt[:, None]


@dataclass(frozen=True, slots=True)
class EarlyWarningSignal:
    """Resultado descriptivo de una señal temprana."""

    metric_id: str
    value: float
    baseline: float
    deviation: float
    threshold: float
    direction: str
    triggered: bool
    uncertainty: float | None = None

    def validate(self) -> None:
        if not self.metric_id.strip():
            raise MetricInputError("metric_id no puede estar vacío")
        if self.threshold < 0:
            raise MetricInputError("threshold debe ser >= 0")
        if self.direction not in {"above", "below", "absolute"}:
            raise MetricInputError(
                "direction debe ser 'above', 'below' o 'absolute'"
            )
        if self.uncertainty is not None and self.uncertainty < 0:
            raise MetricInputError("uncertainty debe ser >= 0")


@dataclass(frozen=True, slots=True)
class DynamicStateSummary:
    """Resumen matemático de una trayectoria sin interpretación causal."""

    level: float
    slope: float
    acceleration: float
    variability: float
    reserve: float | None = None
    recovery_time: float | None = None
    coupling: float | None = None
    regime_distance: float | None = None

    def validate(self) -> None:
        values = (
            self.level,
            self.slope,
            self.acceleration,
            self.variability,
        )
        if not all(isfinite(value) for value in values):
            raise MetricInputError("DynamicStateSummary contiene valores no finitos")

        optional = (
            self.reserve,
            self.recovery_time,
            self.coupling,
            self.regime_distance,
        )
        if any(value is not None and not isfinite(value) for value in optional):
            raise MetricInputError(
                "DynamicStateSummary contiene valores opcionales no finitos"
            )


ADVANCED_METRIC_REGISTRY: Final[Mapping[str, str]] = {
    "skewness": "Asimetría de distribución.",
    "kurtosis_excess": "Curtosis en exceso.",
    "coefficient_of_variation": "Variabilidad relativa.",
    "rolling_coefficient_of_variation": "Variabilidad relativa móvil.",
    "recovery_time": "Tiempo de recuperación tras perturbación.",
    "recovery_ratio_dynamic": "Proporción de recuperación tras perturbación.",
    "dynamic_slope": "Velocidad media de cambio.",
    "dynamic_acceleration": "Aceleración de la trayectoria.",
    "hysteresis_gap": "Separación entre trayectorias dependientes de la historia.",
    "covariance": "Covariación entre variables.",
    "correlation": "Asociación lineal contemporánea.",
    "lagged_correlation": "Asociación temporal con retardo.",
    "interaction_effect": "Desviación respecto a una expectativa aditiva.",
    "coupling_strength": "Magnitud de acoplamiento temporal.",
    "synchronization_index": "Sincronización entre múltiples series.",
    "effective_capacity": "Capacidad operativa efectiva.",
    "capacity_reserve": "Reserva de capacidad.",
    "time_to_exhaustion": "Tiempo estimado hasta agotamiento bajo tasa constante.",
    "amplification_gain": "Ganancia de una perturbación.",
    "cascade_amplification": "Amplificación entre impacto inicial y final.",
    "propagation_depth": "Profundidad de propagación en red.",
    "normalized_hhi": "Concentración normalizada.",
    "bottleneck_ratio": "Relación demanda/capacidad.",
    "regime_distance": "Distancia entre estados.",
    "state_velocity": "Velocidad multidimensional del estado.",
}


def get_advanced_metric_definition(metric_id: str) -> str:
    """Obtiene la definición descriptiva de una métrica avanzada."""
    try:
        return ADVANCED_METRIC_REGISTRY[metric_id]
    except KeyError as exc:
        raise MetricError(f"Métrica avanzada no registrada: {metric_id}") from exc


def validate_advanced_metric_registry() -> None:
    """Comprueba la integridad mínima del registro avanzado."""
    for metric_id, description in ADVANCED_METRIC_REGISTRY.items():
        if not metric_id.strip():
            raise MetricError("Existe un metric_id vacío")
        if not description.strip():
            raise MetricError(f"Métrica sin descripción: {metric_id}")


validate_advanced_metric_registry()

__all__.extend(
    [
        "skewness",
        "kurtosis_excess",
        "coefficient_of_variation",
        "rolling_coefficient_of_variation",
        "recovery_time",
        "recovery_ratio_dynamic",
        "dynamic_slope",
        "dynamic_acceleration",
        "hysteresis_gap",
        "covariance",
        "correlation",
        "lagged_correlation",
        "interaction_effect",
        "coupling_strength",
        "synchronization_index",
        "effective_capacity",
        "capacity_reserve",
        "time_to_exhaustion",
        "amplification_gain",
        "cascade_amplification",
        "propagation_depth",
        "normalized_hhi",
        "bottleneck_ratio",
        "regime_distance",
        "state_velocity",
        "EarlyWarningSignal",
        "DynamicStateSummary",
        "ADVANCED_METRIC_REGISTRY",
        "get_advanced_metric_definition",
        "validate_advanced_metric_registry",
    ]
)

# ---------------------------------------------------------------------------
# Métricas avanzadas II — incertidumbre, estabilidad, persistencia,
# extremos, dependencia espacial y validación de modelos
# ---------------------------------------------------------------------------

def median_absolute_deviation(
    values: Sequence[float] | np.ndarray,
) -> float:
    """Desviación absoluta mediana respecto a la mediana."""
    arr = _as_float_array(values, name="values")
    _require_at_least_two(arr, "values")
    median = float(np.median(arr))
    return float(np.median(np.abs(arr - median)))


def interquartile_range(
    values: Sequence[float] | np.ndarray,
) -> float:
    """Rango intercuartílico."""
    arr = _as_float_array(values, name="values")
    _require_at_least_two(arr, "values")
    q75, q25 = np.percentile(arr, [75.0, 25.0])
    return float(q75 - q25)


def quantile(
    values: Sequence[float] | np.ndarray,
    q: float,
) -> float:
    """Cuantil q de una distribución."""
    arr = _as_float_array(values, name="values")
    _require_at_least_two(arr, "values")

    if not 0.0 <= q <= 1.0:
        raise MetricInputError("q debe estar entre 0 y 1")

    return float(np.quantile(arr, q))


def entropy_from_probabilities(
    probabilities: Sequence[float] | np.ndarray,
    *,
    base: float = 2.0,
) -> float:
    """Entropía de Shannon de una distribución de probabilidades."""
    prob = _as_float_array(probabilities, name="probabilities")

    if prob.size == 0:
        raise MetricInputError("La distribución no puede estar vacía")
    if np.any(prob < 0.0):
        raise MetricInputError("Las probabilidades no pueden ser negativas")
    if not np.isfinite(prob).all():
        raise MetricInputError("Las probabilidades deben ser finitas")
    if base <= 0.0 or base == 1.0:
        raise MetricInputError("base debe ser positiva y distinta de 1")

    total = float(np.sum(prob))
    if total <= 0.0:
        raise MetricInputError("La suma de probabilidades debe ser positiva")

    normalized = prob / total
    positive = normalized[normalized > 0.0]

    return float(-np.sum(positive * np.log(positive)) / np.log(base))


def normalized_entropy(
    probabilities: Sequence[float] | np.ndarray,
) -> float:
    """Entropía normalizada entre 0 y 1."""
    prob = _as_float_array(probabilities, name="probabilities")

    if prob.size < 2:
        raise MetricInputError("Se requieren al menos dos categorías")

    entropy = entropy_from_probabilities(prob)
    maximum = float(np.log2(prob.size))

    if maximum == 0.0:
        return 0.0

    return float(entropy / maximum)


def effective_sample_size(
    weights: Sequence[float] | np.ndarray,
) -> float:
    """
    Tamaño muestral efectivo para pesos no negativos.
    """
    w = _as_float_array(weights, name="weights")

    if w.size == 0:
        raise MetricInputError("weights no puede estar vacío")
    if np.any(w < 0.0):
        raise MetricInputError("Los pesos no pueden ser negativos")

    denominator = float(np.sum(w**2))
    total = float(np.sum(w))

    if total <= 0.0 or denominator <= 0.0:
        raise MetricInputError("Los pesos deben contener al menos un valor positivo")

    return float(total**2 / denominator)


def autocorrelation(
    values: Sequence[float] | np.ndarray,
    lag: int = 1,
) -> float:
    """Autocorrelación de Pearson a un retardo determinado."""
    arr = _as_float_array(values, name="values")
    _require_at_least_two(arr, "values")

    if lag <= 0 or lag >= arr.size:
        raise MetricInputError("lag debe estar entre 1 y n-1")

    return correlation(arr[:-lag], arr[lag:])


def partial_autocorrelation_proxy(
    values: Sequence[float] | np.ndarray,
    lag: int = 1,
) -> float:
    """
    Proxy simple de autocorrelación parcial mediante regresión lineal.

    No sustituye una estimación estadística especializada de PACF.
    """
    arr = _as_float_array(values, name="values")
    _require_at_least_two(arr, "values")

    if lag <= 0 or lag >= arr.size:
        raise MetricInputError("lag debe estar entre 1 y n-1")

    y = arr[lag:]
    predictors = np.column_stack(
        [arr[lag - j - 1 : arr.size - j - 1] for j in range(lag)]
    )

    design = np.column_stack([np.ones(predictors.shape[0]), predictors])
    coefficients, *_ = np.linalg.lstsq(design, y, rcond=None)

    fitted = design @ coefficients
    residual = y - fitted

    variance = float(np.var(residual))
    if variance == 0.0:
        return 1.0

    return float(
        np.corrcoef(
            predictors[:, -1],
            residual,
        )[0, 1]
    )


def persistence_length(
    values: Sequence[float] | np.ndarray,
    *,
    threshold: float = 0.0,
) -> int:
    """
    Longitud máxima de una secuencia consecutiva por encima o por debajo
    del umbral.
    """
    arr = _as_float_array(values, name="values")

    if arr.size == 0:
        raise MetricInputError("values no puede estar vacío")

    above = arr > threshold
    below = arr < threshold

    def longest_run(mask: np.ndarray) -> int:
        longest = current = 0
        for item in mask:
            if bool(item):
                current += 1
                longest = max(longest, current)
            else:
                current = 0
        return longest

    return max(longest_run(above), longest_run(below))


def threshold_exceedance_count(
    values: Sequence[float] | np.ndarray,
    threshold: float,
    *,
    direction: str = "above",
) -> int:
    """Número de observaciones que superan un umbral."""
    arr = _as_float_array(values, name="values")

    if direction == "above":
        return int(np.sum(arr > threshold))
    if direction == "below":
        return int(np.sum(arr < threshold))
    if direction == "absolute":
        return int(np.sum(np.abs(arr) > abs(threshold)))

    raise MetricInputError(
        "direction debe ser 'above', 'below' o 'absolute'"
    )


def threshold_exceedance_rate(
    values: Sequence[float] | np.ndarray,
    threshold: float,
    *,
    direction: str = "above",
) -> float:
    """Proporción de observaciones que superan un umbral."""
    arr = _as_float_array(values, name="values")

    if arr.size == 0:
        raise MetricInputError("values no puede estar vacío")

    return float(
        threshold_exceedance_count(
            arr,
            threshold,
            direction=direction,
        )
        / arr.size
    )


def mean_excess_over_threshold(
    values: Sequence[float] | np.ndarray,
    threshold: float,
) -> float:
    """Exceso medio sobre un umbral para observaciones superiores."""
    arr = _as_float_array(values, name="values")
    excess = arr[arr > threshold] - threshold

    if excess.size == 0:
        return 0.0

    return float(np.mean(excess))


def maximum_drawdown(
    values: Sequence[float] | np.ndarray,
) -> float:
    """
    Máxima caída relativa desde un máximo histórico de la trayectoria.
    """
    arr = _as_float_array(values, name="values")
    _require_at_least_two(arr, "values")

    running_max = np.maximum.accumulate(arr)

    if np.any(running_max == 0.0):
        raise MetricInputError(
            "maximum_drawdown relativo indefinido cuando el máximo es cero"
        )

    drawdowns = (running_max - arr) / np.abs(running_max)
    return float(np.max(drawdowns))


def state_stability(
    values: Sequence[float] | np.ndarray,
) -> float:
    """
    Índice descriptivo inverso de variabilidad relativa.

    Valores mayores indican menor variabilidad alrededor de la media.
    No representa estabilidad estructural por sí mismo.
    """
    cv = coefficient_of_variation(values)
    return float(1.0 / (1.0 + cv))


def perturbation_recovery_fraction(
    baseline: float,
    perturbed: float,
    recovered: float,
) -> float:
    """Fracción de la perturbación original que ha sido recuperada."""
    perturbation = perturbed - baseline

    if perturbation == 0.0:
        raise MetricInputError("No existe perturbación inicial")

    return float((recovered - perturbed) / (baseline - perturbed))


def resilience_loss(
    baseline: float,
    minimum: float,
) -> float:
    """Pérdida absoluta de estado respecto al baseline."""
    return float(abs(baseline - minimum))


def resilience_loss_relative(
    baseline: float,
    minimum: float,
) -> float:
    """Pérdida relativa respecto al baseline."""
    if baseline == 0.0:
        raise MetricInputError("baseline no puede ser cero")

    return float(abs(baseline - minimum) / abs(baseline))


def area_under_curve(
    times: Sequence[float] | np.ndarray,
    values: Sequence[float] | np.ndarray,
) -> float:
    """Integral trapezoidal de una trayectoria."""
    t = _as_float_array(times, name="times")
    x = _as_float_array(values, name="values")
    _validate_same_length(t, x)

    if t.size < 2:
        raise MetricInputError("Se requieren al menos dos observaciones")
    if np.any(np.diff(t) < 0.0):
        raise MetricInputError("times debe estar ordenado")

    return float(np.trapezoid(x, t))


def cumulative_exposure(
    times: Sequence[float] | np.ndarray,
    exposure: Sequence[float] | np.ndarray,
) -> float:
    """Carga acumulada de exposición en el tiempo."""
    return area_under_curve(times, exposure)


def lagged_effect_integral(
    times: Sequence[float] | np.ndarray,
    input_values: Sequence[float] | np.ndarray,
    output_values: Sequence[float] | np.ndarray,
    lag: int,
) -> float:
    """
    Integral del producto entre una entrada retardada y una respuesta.

    Es una medida descriptiva de acoplamiento temporal, no una prueba causal.
    """
    t = _as_float_array(times, name="times")
    x = _as_float_array(input_values, name="input_values")
    y = _as_float_array(output_values, name="output_values")

    _validate_same_length(t, x)
    _validate_same_length(t, y)

    if lag < 0 or lag >= x.size:
        raise MetricInputError("lag fuera del rango válido")

    if lag == 0:
        return area_under_curve(t, x * y)

    return area_under_curve(
        t[lag:],
        x[:-lag] * y[lag:],
    )


def spatial_weighted_mean(
    values: Sequence[float] | np.ndarray,
    weights: Sequence[float] | np.ndarray,
) -> float:
    """Media ponderada espacial."""
    x = _as_float_array(values, name="values")
    w = _as_float_array(weights, name="weights")
    _validate_same_length(x, w)

    if np.any(w < 0.0):
        raise MetricInputError("weights no puede contener valores negativos")

    total = float(np.sum(w))
    if total <= 0.0:
        raise MetricInputError("La suma de pesos debe ser positiva")

    return float(np.sum(x * w) / total)


def spatial_weighted_variance(
    values: Sequence[float] | np.ndarray,
    weights: Sequence[float] | np.ndarray,
) -> float:
    """Varianza ponderada espacial."""
    x = _as_float_array(values, name="values")
    w = _as_float_array(weights, name="weights")
    _validate_same_length(x, w)

    if np.any(w < 0.0):
        raise MetricInputError("weights no puede contener valores negativos")

    total = float(np.sum(w))
    if total <= 0.0:
        raise MetricInputError("La suma de pesos debe ser positiva")

    mean = float(np.sum(x * w) / total)
    return float(np.sum(w * (x - mean) ** 2) / total)


def morans_i(
    values: Sequence[float] | np.ndarray,
    weights_matrix: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    I de Moran global.

    Mide autocorrelación espacial bajo una matriz de pesos previamente
    especificada. No implica causalidad.
    """
    x = _as_float_array(values, name="values")
    w = np.asarray(weights_matrix, dtype=float)

    if x.ndim != 1:
        raise MetricInputError("values debe ser un vector")
    if w.ndim != 2 or w.shape[0] != w.shape[1]:
        raise MetricInputError("weights_matrix debe ser cuadrada")
    if w.shape[0] != x.size:
        raise MetricInputError(
            "weights_matrix y values deben tener dimensiones compatibles"
        )

    centered = x - np.mean(x)
    denominator = float(np.sum(centered**2))
    weight_sum = float(np.sum(w))

    if denominator == 0.0:
        raise MetricInputError("Moran's I indefinido para valores constantes")
    if weight_sum == 0.0:
        raise MetricInputError("La matriz de pesos no puede tener suma cero")

    numerator = float(centered @ w @ centered)

    return float((x.size / weight_sum) * (numerator / denominator))


def spatial_concentration_index(
    values: Sequence[float] | np.ndarray,
) -> float:
    """
    Concentración relativa de una distribución espacial no negativa.
    """
    arr = _as_float_array(values, name="values")

    if np.any(arr < 0.0):
        raise MetricInputError("values debe ser no negativo")

    total = float(np.sum(arr))
    if total <= 0.0:
        raise MetricInputError("La suma debe ser positiva")

    shares = arr / total
    return float(np.sum(shares**2))


def source_independence_adjusted_evidence(
    evidence_weights: Sequence[float] | np.ndarray,
    independence_weights: Sequence[float] | np.ndarray,
) -> float:
    """
    Evidencia ponderada por independencia de fuentes.

    No transforma fuentes dependientes en independientes; reduce su peso
    efectivo cuando la independencia estimada es baja.
    """
    evidence = _as_float_array(evidence_weights, name="evidence_weights")
    independence = _as_float_array(
        independence_weights,
        name="independence_weights",
    )
    _validate_same_length(evidence, independence)

    if np.any(evidence < 0.0):
        raise MetricInputError("evidence_weights no puede ser negativo")
    if np.any((independence < 0.0) | (independence > 1.0)):
        raise MetricInputError(
            "independence_weights debe estar entre 0 y 1"
        )

    effective = evidence * independence
    total = float(np.sum(evidence))

    if total == 0.0:
        return 0.0

    return float(np.sum(effective) / total)


def brier_skill_score(
    y_true: Sequence[int] | np.ndarray,
    probabilities: Sequence[float] | np.ndarray,
    reference_probabilities: Sequence[float] | np.ndarray,
) -> float:
    """Brier Skill Score respecto a un modelo de referencia."""
    model_brier = brier_score(y_true, probabilities)
    reference_brier = brier_score(y_true, reference_probabilities)

    if reference_brier == 0.0:
        raise MetricInputError(
            "El Brier del modelo de referencia no puede ser cero"
        )

    return float(1.0 - model_brier / reference_brier)


def calibration_slope(
    y_true: Sequence[int] | np.ndarray,
    probabilities: Sequence[float] | np.ndarray,
) -> float:
    """
    Pendiente de calibración aproximada mediante regresión logística
    sobre el logit de la probabilidad predicha.
    """
    truth = _validate_binary(y_true, name="y_true")
    prob = _validate_probabilities(probabilities)

    _validate_same_length(truth, prob)

    epsilon = np.finfo(float).eps
    clipped = np.clip(prob, epsilon, 1.0 - epsilon)
    logits = np.log(clipped / (1.0 - clipped))

    design = np.column_stack([np.ones(logits.size), logits])

    coefficients = np.linalg.lstsq(
        design,
        truth,
        rcond=None,
    )[0]

    return float(coefficients[1])


def calibration_intercept(
    y_true: Sequence[int] | np.ndarray,
    probabilities: Sequence[float] | np.ndarray,
) -> float:
    """Intercepto de calibración aproximado."""
    truth = _validate_binary(y_true, name="y_true")
    prob = _validate_probabilities(probabilities)

    _validate_same_length(truth, prob)

    epsilon = np.finfo(float).eps
    clipped = np.clip(prob, epsilon, 1.0 - epsilon)
    logits = np.log(clipped / (1.0 - clipped))

    design = np.column_stack([np.ones(logits.size), logits])

    coefficients = np.linalg.lstsq(
        design,
        truth,
        rcond=None,
    )[0]

    return float(coefficients[0])


def prevalence(
    outcomes: Sequence[int] | np.ndarray,
) -> float:
    """Prevalencia/proporción de positivos."""
    binary = _validate_binary(outcomes, name="outcomes")

    if binary.size == 0:
        raise MetricInputError("outcomes no puede estar vacío")

    return float(np.mean(binary))


def incidence_rate(
    events: float,
    population_time: float,
) -> float:
    """Tasa de incidencia por unidad de tiempo-persona."""
    if events < 0.0:
        raise MetricInputError("events debe ser >= 0")
    if population_time <= 0.0:
        raise MetricInputError("population_time debe ser > 0")

    return float(events / population_time)


def attack_rate(
    cases: float,
    population_at_risk: float,
) -> float:
    """Tasa de ataque acumulada."""
    if cases < 0.0:
        raise MetricInputError("cases debe ser >= 0")
    if population_at_risk <= 0.0:
        raise MetricInputError(
            "population_at_risk debe ser > 0"
        )
    if cases > population_at_risk:
        raise MetricInputError(
            "cases no puede superar population_at_risk"
        )

    return float(cases / population_at_risk)


def excess_rate(
    observed: float,
    expected: float,
) -> float:
    """Exceso relativo respecto al valor esperado."""
    if expected == 0.0:
        raise MetricInputError("expected no puede ser cero")

    return float((observed - expected) / abs(expected))


def standardized_mortality_ratio(
    observed: float,
    expected: float,
) -> float:
    """SMR = observado / esperado."""
    if observed < 0.0 or expected <= 0.0:
        raise MetricInputError(
            "observed >= 0 y expected > 0 son obligatorios"
        )

    return float(observed / expected)


def relative_risk(
    exposed_cases: float,
    exposed_total: float,
    unexposed_cases: float,
    unexposed_total: float,
) -> float:
    """Riesgo relativo entre expuestos y no expuestos."""
    if exposed_total <= 0.0 or unexposed_total <= 0.0:
        raise MetricInputError("Los denominadores deben ser > 0")
    if exposed_cases < 0.0 or unexposed_cases < 0.0:
        raise MetricInputError("Los casos no pueden ser negativos")
    if exposed_cases > exposed_total or unexposed_cases > unexposed_total:
        raise MetricInputError("Los casos no pueden superar los totales")

    exposed_risk = exposed_cases / exposed_total
    unexposed_risk = unexposed_cases / unexposed_total

    if unexposed_risk == 0.0:
        raise MetricInputError(
            "Riesgo relativo indefinido cuando el riesgo no expuesto es cero"
        )

    return float(exposed_risk / unexposed_risk)


def odds_ratio(
    exposed_cases: float,
    exposed_non_cases: float,
    unexposed_cases: float,
    unexposed_non_cases: float,
) -> float:
    """Odds ratio de una tabla 2×2."""
    values = (
        exposed_cases,
        exposed_non_cases,
        unexposed_cases,
        unexposed_non_cases,
    )

    if any(value < 0.0 for value in values):
        raise MetricInputError("Los recuentos no pueden ser negativos")

    denominator = exposed_non_cases * unexposed_cases

    if denominator == 0.0:
        raise MetricInputError("Odds ratio indefinido")

    return float(
        (exposed_cases * unexposed_non_cases) / denominator
    )


def attributable_fraction(
    relative_risk_value: float,
) -> float:
    """Fracción atribuible entre expuestos a partir del riesgo relativo."""
    if relative_risk_value < 0.0:
        raise MetricInputError("relative_risk debe ser >= 0")

    return float(
        (relative_risk_value - 1.0) / relative_risk_value
    )


def gini_coefficient(
    values: Sequence[float] | np.ndarray,
) -> float:
    """Coeficiente de Gini para valores no negativos."""
    arr = _as_float_array(values, name="values")

    if arr.size < 2:
        raise MetricInputError("Se requieren al menos dos observaciones")
    if np.any(arr < 0.0):
        raise MetricInputError("values debe ser no negativo")

    total = float(np.sum(arr))
    if total == 0.0:
        return 0.0

    sorted_values = np.sort(arr)
    n = sorted_values.size
    index = np.arange(1, n + 1)

    return float(
        (2.0 * np.sum(index * sorted_values))
        / (n * total)
        - (n + 1.0) / n
    )


def lorenz_area(
    values: Sequence[float] | np.ndarray,
) -> float:
    """Área bajo la curva de Lorenz."""
    arr = _as_float_array(values, name="values")

    if arr.size < 2:
        raise MetricInputError("Se requieren al menos dos observaciones")
    if np.any(arr < 0.0):
        raise MetricInputError("values debe ser no negativo")

    total = float(np.sum(arr))
    if total == 0.0:
        return 0.5

    sorted_values = np.sort(arr)
    cumulative = np.cumsum(sorted_values) / total
    cumulative = np.concatenate([[0.0], cumulative])

    x = np.linspace(0.0, 1.0, arr.size + 1)

    return float(np.trapezoid(cumulative, x))


def hazard_ratio_from_hazards(
    hazard_exposed: float,
    hazard_reference: float,
) -> float:
    """Razón instantánea de riesgos entre dos grupos."""
    if hazard_exposed < 0.0 or hazard_reference <= 0.0:
        raise MetricInputError(
            "hazard_exposed >= 0 y hazard_reference > 0"
        )

    return float(hazard_exposed / hazard_reference)


def cumulative_hazard(
    times: Sequence[float] | np.ndarray,
    hazards: Sequence[float] | np.ndarray,
) -> float:
    """Hazard acumulado mediante integración trapezoidal."""
    t = _as_float_array(times, name="times")
    h = _as_float_array(hazards, name="hazards")

    _validate_same_length(t, h)

    if t.size < 2:
        raise MetricInputError("Se requieren al menos dos observaciones")
    if np.any(h < 0.0):
        raise MetricInputError("hazards no puede contener valores negativos")

    return area_under_curve(t, h)


def survival_from_cumulative_hazard(
    cumulative_hazard_value: float,
) -> float:
    """Supervivencia S(t)=exp(-H(t))."""
    if cumulative_hazard_value < 0.0:
        raise MetricInputError(
            "cumulative_hazard debe ser >= 0"
        )

    return float(np.exp(-cumulative_hazard_value))


def probability_of_failure(
    survival_probability: float,
) -> float:
    """Probabilidad complementaria de fallo."""
    if not 0.0 <= survival_probability <= 1.0:
        raise MetricInputError(
            "survival_probability debe estar entre 0 y 1"
        )

    return float(1.0 - survival_probability)


def prediction_interval_width(
    lower: Sequence[float] | np.ndarray,
    upper: Sequence[float] | np.ndarray,
) -> float:
    """Anchura media de intervalos predictivos."""
    low = _as_float_array(lower, name="lower")
    high = _as_float_array(upper, name="upper")
    _validate_same_length(low, high)

    if np.any(high < low):
        raise MetricInputError(
            "upper no puede ser menor que lower"
        )

    return float(np.mean(high - low))


def empirical_coverage(
    y_true: Sequence[float] | np.ndarray,
    lower: Sequence[float] | np.ndarray,
    upper: Sequence[float] | np.ndarray,
) -> float:
    """Cobertura empírica de un intervalo predictivo."""
    truth = _as_float_array(y_true, name="y_true")
    low = _as_float_array(lower, name="lower")
    high = _as_float_array(upper, name="upper")

    _validate_same_length(truth, low)
    _validate_same_length(truth, high)

    if np.any(high < low):
        raise MetricInputError(
            "upper no puede ser menor que lower"
        )

    return float(np.mean((truth >= low) & (truth <= high)))


def mean_absolute_scaled_error(
    y_true: Sequence[float] | np.ndarray,
    y_pred: Sequence[float] | np.ndarray,
    training_series: Sequence[float] | np.ndarray,
) -> float:
    """MASE para series temporales."""
    truth = _as_float_array(y_true, name="y_true")
    pred = _as_float_array(y_pred, name="y_pred")
    training = _as_float_array(training_series, name="training_series")

    _validate_same_length(truth, pred)

    if training.size < 2:
        raise MetricInputError(
            "training_series requiere al menos dos observaciones"
        )

    scale = float(np.mean(np.abs(np.diff(training))))

    if scale == 0.0:
        raise MetricInputError(
            "Escala de referencia cero en MASE"
        )

    return float(np.mean(np.abs(truth - pred)) / scale)


def directional_accuracy(
    y_true: Sequence[float] | np.ndarray,
    y_pred: Sequence[float] | np.ndarray,
) -> float:
    """Exactitud de la dirección del cambio."""
    truth = _as_float_array(y_true, name="y_true")
    pred = _as_float_array(y_pred, name="y_pred")

    _validate_same_length(truth, pred)

    if truth.size < 2:
        raise MetricInputError("Se requieren al menos dos observaciones")

    actual_direction = np.sign(np.diff(truth))
    predicted_direction = np.sign(np.diff(pred))

    return float(np.mean(actual_direction == predicted_direction))


def lead_time(
    event_time: float,
    detection_time: float,
) -> float:
    """Tiempo de anticipación entre detección y evento."""
    if detection_time > event_time:
        raise MetricInputError(
            "La detección no puede ocurrir después del evento"
        )

    return float(event_time - detection_time)


def false_alarm_rate(
    false_alarms: int,
    non_events: int,
) -> float:
    """Tasa de falsas alarmas."""
    if false_alarms < 0 or non_events < 0:
        raise MetricInputError("Los recuentos no pueden ser negativos")
    if non_events == 0:
        raise MetricInputError("non_events debe ser > 0")

    return float(false_alarms / non_events)


def threat_score(
    hits: int,
    false_alarms: int,
    misses: int,
) -> float:
    """Critical Success Index / Threat Score."""
    values = (hits, false_alarms, misses)

    if any(value < 0 for value in values):
        raise MetricInputError("Los recuentos no pueden ser negativos")

    denominator = hits + false_alarms + misses

    if denominator == 0:
        raise MetricInputError("Threat Score indefinido")

    return float(hits / denominator)


def fowlkes_mallows_index(
    cm: ConfusionMatrix,
) -> float:
    """Índice de Fowlkes-Mallows."""
    precision = positive_predictive_value(cm)
    recall = sensitivity(cm)

    return float(np.sqrt(precision * recall))


def prevalence_threshold_adjusted_ppv(
    sensitivity_value: float,
    specificity_value: float,
    prevalence_value: float,
) -> float:
    """
    PPV teórico bajo sensibilidad, especificidad y prevalencia especificadas.
    """
    for name, value in (
        ("sensitivity", sensitivity_value),
        ("specificity", specificity_value),
        ("prevalence", prevalence_value),
    ):
        if not 0.0 <= value <= 1.0:
            raise MetricInputError(
                f"{name} debe estar entre 0 y 1"
            )

    numerator = sensitivity_value * prevalence_value
    denominator = numerator + (
        (1.0 - specificity_value)
        * (1.0 - prevalence_value)
    )

    if denominator == 0.0:
        raise MetricInputError(
            "PPV indefinido para estos parámetros"
        )

    return float(numerator / denominator)


def net_benefit(
    true_positives: int,
    false_positives: int,
    population: int,
    threshold_probability: float,
) -> float:
    """
    Net Benefit simplificado para evaluación de decisiones.
    """
    if population <= 0:
        raise MetricInputError("population debe ser > 0")
    if true_positives < 0 or false_positives < 0:
        raise MetricInputError("Los recuentos no pueden ser negativos")
    if not 0.0 < threshold_probability < 1.0:
        raise MetricInputError(
            "threshold_probability debe estar entre 0 y 1"
        )

    return float(
        true_positives / population
        - (
            false_positives / population
        )
        * (
            threshold_probability
            / (1.0 - threshold_probability)
        )
    )


def integrated_brier_score(
    observed: Sequence[float] | np.ndarray,
    predicted: Sequence[float] | np.ndarray,
) -> float:
    """
    Brier score medio para probabilidades/valores binarios a lo largo
    de múltiples horizontes.
    """
    truth = np.asarray(observed, dtype=float)
    pred = np.asarray(predicted, dtype=float)

    if truth.shape != pred.shape:
        raise MetricInputError(
            "observed y predicted deben tener la misma forma"
        )

    if truth.ndim != 2:
        raise MetricInputError(
            "Las entradas deben ser matrices [observaciones, horizontes]"
        )

    if np.any((truth < 0.0) | (truth > 1.0)):
        raise MetricInputError(
            "observed debe estar entre 0 y 1"
        )
    if np.any((pred < 0.0) | (pred > 1.0)):
        raise MetricInputError(
            "predicted debe estar entre 0 y 1"
        )

    return float(np.mean((pred - truth) ** 2))


def monte_carlo_standard_error(
    samples: Sequence[float] | np.ndarray,
) -> float:
    """Error estándar de Monte Carlo."""
    arr = _as_float_array(samples, name="samples")
    _require_at_least_two(arr, "samples")

    return float(np.std(arr, ddof=1) / np.sqrt(arr.size))


def monte_carlo_confidence_interval(
    samples: Sequence[float] | np.ndarray,
    confidence: float = 0.95,
) -> tuple[float, float]:
    """Intervalo empírico por cuantiles de Monte Carlo."""
    arr = _as_float_array(samples, name="samples")
    _require_at_least_two(arr, "samples")

    if not 0.0 < confidence < 1.0:
        raise MetricInputError(
            "confidence debe estar entre 0 y 1"
        )

    alpha = 1.0 - confidence

    return (
        float(np.quantile(arr, alpha / 2.0)),
        float(np.quantile(arr, 1.0 - alpha / 2.0)),
    )


def value_at_risk(
    losses: Sequence[float] | np.ndarray,
    confidence: float = 0.95,
) -> float:
    """Cuantil de pérdida para un nivel de confianza dado."""
    return quantile(losses, confidence)


def expected_shortfall(
    losses: Sequence[float] | np.ndarray,
    confidence: float = 0.95,
) -> float:
    """Pérdida media condicionada a superar VaR."""
    arr = _as_float_array(losses, name="losses")
    _require_at_least_two(arr, "losses")

    if not 0.0 < confidence < 1.0:
        raise MetricInputError(
            "confidence debe estar entre 0 y 1"
        )

    var = value_at_risk(arr, confidence)
    tail = arr[arr >= var]

    if tail.size == 0:
        return float(var)

    return float(np.mean(tail))


__all__.extend(
    [
        "median_absolute_deviation",
        "interquartile_range",
        "quantile",
        "entropy_from_probabilities",
        "normalized_entropy",
        "effective_sample_size",
        "autocorrelation",
        "partial_autocorrelation_proxy",
        "persistence_length",
        "threshold_exceedance_count",
        "threshold_exceedance_rate",
        "mean_excess_over_threshold",
        "maximum_drawdown",
        "state_stability",
        "perturbation_recovery_fraction",
        "resilience_loss",
        "resilience_loss_relative",
        "area_under_curve",
        "cumulative_exposure",
        "lagged_effect_integral",
        "spatial_weighted_mean",
        "spatial_weighted_variance",
        "morans_i",
        "spatial_concentration_index",
        "source_independence_adjusted_evidence",
        "brier_skill_score",
        "calibration_slope",
        "calibration_intercept",
        "prevalence",
        "incidence_rate",
        "attack_rate",
        "excess_rate",
        "standardized_mortality_ratio",
        "relative_risk",
        "odds_ratio",
        "attributable_fraction",
        "gini_coefficient",
        "lorenz_area",
        "hazard_ratio_from_hazards",
        "cumulative_hazard",
        "survival_from_cumulative_hazard",
        "probability_of_failure",
        "prediction_interval_width",
        "empirical_coverage",
        "mean_absolute_scaled_error",
        "directional_accuracy",
        "lead_time",
        "false_alarm_rate",
        "threat_score",
        "fowlkes_mallows_index",
        "prevalence_threshold_adjusted_ppv",
        "net_benefit",
        "integrated_brier_score",
        "monte_carlo_standard_error",
        "monte_carlo_confidence_interval",
        "value_at_risk",
        "expected_shortfall",
    ]
)


"""# ===========================================================================
# CEUTIA — MÉTRICAS AVANZADAS DE DINÁMICA, RESILIENCIA E INTERACCIÓN
# ===========================================================================
#
# Estas funciones son primitivas matemáticas generales.
#
# IMPORTANTE:
# - No constituyen por sí mismas un modelo causal.
# - No constituyen por sí mismas un índice de riesgo.
# - No se combinan mediante pesos arbitrarios para fabricar una puntuación.
# - Los composites propios de CeutIA se definirán posteriormente, cuando exista
#   una especificación formal del modelo de interacciones.
#
# Las métricas se mantienen separadas de:
#   observación → señal → inferencia → hipótesis → predicción → escenario → decisión.
#
# ===========================================================================


def skewness(values: Sequence[float] | np.ndarray) -> float:
    """Asimetría muestral estandarizada mediante momentos centrales."""
    arr = _as_float_array(values, name="values")
    _require_at_least_two(arr, "values")

    sd = float(np.std(arr, ddof=1))
    if sd == 0.0:
        raise MetricInputError("La asimetría no está definida con desviación 0")

    centered = arr - np.mean(arr)
    return float(np.mean(centered**3) / sd**3)


def kurtosis_excess(values: Sequence[float] | np.ndarray) -> float:
    """Curtosis excesiva basada en el cuarto momento central."""
    arr = _as_float_array(values, name="values")
    _require_at_least_two(arr, "values")

    sd = float(np.std(arr, ddof=1))
    if sd == 0.0:
        raise MetricInputError("La curtosis no está definida con desviación 0")

    centered = arr - np.mean(arr)
    return float(np.mean(centered**4) / sd**4 - 3.0)


def coefficient_of_variation_change(
    baseline: Sequence[float] | np.ndarray,
    current: Sequence[float] | np.ndarray,
) -> float:
    """Cambio relativo del coeficiente de variación."""
    baseline_cv = coefficient_of_variation(baseline)
    current_cv = coefficient_of_variation(current)

    if baseline_cv == 0.0:
        raise MetricInputError(
            "No puede calcularse cambio relativo desde CV basal igual a 0"
        )

    return float((current_cv - baseline_cv) / abs(baseline_cv))


def rolling_skewness(
    values: Sequence[float] | np.ndarray,
    window: int,
) -> np.ndarray:
    """Serie de asimetría móvil."""
    arr = _as_float_array(values, name="values")

    if window < 3 or window > arr.size:
        raise MetricInputError("window incompatible con la serie")

    return np.asarray(
        [
            skewness(arr[i - window + 1 : i + 1])
            for i in range(window - 1, arr.size)
        ],
        dtype=float,
    )


def rolling_kurtosis_excess(
    values: Sequence[float] | np.ndarray,
    window: int,
) -> np.ndarray:
    """Serie de curtosis excesiva móvil."""
    arr = _as_float_array(values, name="values")

    if window < 3 or window > arr.size:
        raise MetricInputError("window incompatible con la serie")

    return np.asarray(
        [
            kurtosis_excess(arr[i - window + 1 : i + 1])
            for i in range(window - 1, arr.size)
        ],
        dtype=float,
    )


# ---------------------------------------------------------------------------
# Recuperación, estabilidad y resiliencia
# ---------------------------------------------------------------------------


def recovery_time(
    values: Sequence[float] | np.ndarray,
    baseline: float,
    tolerance: float,
    *,
    shock_index: int = 0,
) -> int | None:
    """
    Primer número de pasos necesario para volver al intervalo:

        |x_t - baseline| <= tolerance

    después de un shock.

    Devuelve None si la recuperación no se observa.
    """
    arr = _as_float_array(values, name="values")

    if tolerance < 0.0:
        raise MetricInputError("tolerance debe ser >= 0")

    if not 0 <= shock_index < arr.size:
        raise MetricInputError("shock_index fuera de rango")

    for i in range(shock_index, arr.size):
        if abs(float(arr[i]) - baseline) <= tolerance:
            return i - shock_index

    return None


def recovery_fraction(
    baseline: float,
    nadir: float,
    current: float,
) -> float:
    """
    Fracción de recuperación desde el nadir hacia el estado basal.

    0 = no recuperación desde el nadir.
    1 = recuperación completa.
    Valores >1 representan sobrepaso del estado basal.
    """
    denominator = baseline - nadir

    if denominator == 0.0:
        raise MetricInputError(
            "La recuperación no está definida cuando baseline == nadir"
        )

    return float((current - nadir) / denominator)


def resilience_loss(
    baseline_capacity: float,
    minimum_capacity: float,
) -> float:
    """Pérdida relativa de capacidad durante un shock."""
    if baseline_capacity <= 0.0 or minimum_capacity < 0.0:
        raise MetricInputError("Capacidades inválidas")

    return float(
        (baseline_capacity - minimum_capacity) / baseline_capacity
    )


def resilience_recovery_ratio(
    baseline_capacity: float,
    minimum_capacity: float,
    recovered_capacity: float,
) -> float:
    """
    Recuperación relativa respecto a la pérdida sufrida.

    0 = ninguna recuperación.
    1 = recuperación completa.
    >1 = recuperación por encima del nivel basal.
    """
    loss = baseline_capacity - minimum_capacity

    if baseline_capacity <= 0.0:
        raise MetricInputError("baseline_capacity debe ser > 0")

    if minimum_capacity < 0.0 or recovered_capacity < 0.0:
        raise MetricInputError("Las capacidades no pueden ser negativas")

    if loss == 0.0:
        raise MetricInputError(
            "No existe pérdida de capacidad respecto al basal"
        )

    return float((recovered_capacity - minimum_capacity) / loss)


def overshoot(
    values: Sequence[float] | np.ndarray,
    baseline: float,
) -> float:
    """
    Máxima desviación positiva respecto al baseline.
    """
    arr = _as_float_array(values, name="values")
    return float(np.max(arr - baseline))


def undershoot(
    values: Sequence[float] | np.ndarray,
    baseline: float,
) -> float:
    """
    Máxima desviación negativa respecto al baseline.
    Devuelve una magnitud positiva.
    """
    arr = _as_float_array(values, name="values")
    return float(np.max(baseline - arr))


def area_between_curves(
    observed: Sequence[float] | np.ndarray,
    reference: Sequence[float] | np.ndarray,
    *,
    dt: float = 1.0,
) -> float:
    """
    Área absoluta entre una trayectoria observada y una referencia.
    """
    obs = _as_float_array(observed, name="observed")
    ref = _as_float_array(reference, name="reference")
    _validate_same_length(obs, ref)

    if dt <= 0.0:
        raise MetricInputError("dt debe ser positivo")

    return float(np.sum(np.abs(obs - ref)) * dt)


def trajectory_distance(
    first: Sequence[float] | np.ndarray,
    second: Sequence[float] | np.ndarray,
    *,
    dt: float = 1.0,
) -> float:
    """Distancia L2 integrada entre dos trayectorias."""
    x = _as_float_array(first, name="first")
    y = _as_float_array(second, name="second")
    _validate_same_length(x, y)

    if dt <= 0.0:
        raise MetricInputError("dt debe ser positivo")

    return float(np.sqrt(np.sum((x - y) ** 2) * dt))


# ---------------------------------------------------------------------------
# Dinámica no lineal y cambio de régimen
# ---------------------------------------------------------------------------


def local_slope(
    values: Sequence[float] | np.ndarray,
    *,
    dt: float = 1.0,
) -> float:
    """
    Pendiente lineal global de una trayectoria.
    """
    arr = _as_float_array(values, name="values")

    if dt <= 0.0:
        raise MetricInputError("dt debe ser positivo")

    if arr.size < 2:
        raise MetricInputError("Se requieren al menos dos observaciones")

    x = np.arange(arr.size, dtype=float) * dt
    slope, _ = np.polyfit(x, arr, 1)
    return float(slope)


def rolling_slope(
    values: Sequence[float] | np.ndarray,
    window: int,
    *,
    dt: float = 1.0,
) -> np.ndarray:
    """Pendiente local móvil."""
    arr = _as_float_array(values, name="values")

    if window < 2 or window > arr.size:
        raise MetricInputError("window incompatible con la serie")

    if dt <= 0.0:
        raise MetricInputError("dt debe ser positivo")

    out: list[float] = []

    for i in range(window - 1, arr.size):
        segment = arr[i - window + 1 : i + 1]
        x = np.arange(window, dtype=float) * dt
        slope, _ = np.polyfit(x, segment, 1)
        out.append(float(slope))

    return np.asarray(out)


def rolling_acceleration(
    values: Sequence[float] | np.ndarray,
    window: int,
    *,
    dt: float = 1.0,
) -> np.ndarray:
    """Segunda derivada aproximada mediante regresión polinómica local."""
    arr = _as_float_array(values, name="values")

    if window < 3 or window > arr.size:
        raise MetricInputError("window incompatible con la serie")

    if dt <= 0.0:
        raise MetricInputError("dt debe ser positivo")

    out: list[float] = []

    for i in range(window - 1, arr.size):
        segment = arr[i - window + 1 : i + 1]
        x = np.arange(window, dtype=float) * dt

        coefficients = np.polyfit(x, segment, 2)
        out.append(float(2.0 * coefficients[0]))

    return np.asarray(out)


def hysteresis_gap(
    upward_threshold: float,
    downward_threshold: float,
) -> float:
    """
    Distancia entre umbral de transición ascendente y descendente.

    Permite representar histéresis cuando ambos umbrales difieren.
    """
    if upward_threshold < downward_threshold:
        raise MetricInputError(
            "upward_threshold debe ser >= downward_threshold"
        )

    return float(upward_threshold - downward_threshold)


def threshold_crossing_index(
    values: Sequence[float] | np.ndarray,
    threshold: float,
    *,
    direction: str = "above",
) -> int | None:
    """Primer índice en que una trayectoria cruza un umbral."""
    arr = _as_float_array(values, name="values")

    if direction not in {"above", "below"}:
        raise MetricInputError("direction debe ser 'above' o 'below'")

    for index, value in enumerate(arr):
        if direction == "above" and value >= threshold:
            return index

        if direction == "below" and value <= threshold:
            return index

    return None


# ---------------------------------------------------------------------------
# Interacciones entre variables
# ---------------------------------------------------------------------------


def covariance(
    first: Sequence[float] | np.ndarray,
    second: Sequence[float] | np.ndarray,
) -> float:
    """Covarianza muestral entre dos trayectorias."""
    x = _as_float_array(first, name="first")
    y = _as_float_array(second, name="second")
    _validate_same_length(x, y)

    if x.size < 2:
        raise MetricInputError("Se requieren al menos dos observaciones")

    return float(np.cov(x, y, ddof=1)[0, 1])


def correlation(
    first: Sequence[float] | np.ndarray,
    second: Sequence[float] | np.ndarray,
) -> float:
    """Correlación de Pearson entre dos trayectorias."""
    x = _as_float_array(first, name="first")
    y = _as_float_array(second, name="second")
    _validate_same_length(x, y)

    if x.size < 2:
        raise MetricInputError("Se requieren al menos dos observaciones")

    sx = float(np.std(x, ddof=1))
    sy = float(np.std(y, ddof=1))

    if sx == 0.0 or sy == 0.0:
        raise MetricInputError(
            "La correlación no está definida con varianza 0"
        )

    return float(np.corrcoef(x, y)[0, 1])


def lagged_correlation(
    first: Sequence[float] | np.ndarray,
    second: Sequence[float] | np.ndarray,
    lag: int,
) -> float:
    """
    Correlación entre X_t y Y_(t+lag).

    lag > 0:
        first precede temporalmente a second.
    """
    x = _as_float_array(first, name="first")
    y = _as_float_array(second, name="second")
    _validate_same_length(x, y)

    if lag == 0:
        return correlation(x, y)

    if abs(lag) >= x.size:
        raise MetricInputError("lag fuera del tamaño de las series")

    if lag > 0:
        return correlation(x[:-lag], y[lag:])

    return correlation(x[-lag:], y[:lag])


def interaction_effect_proxy(
    baseline: float,
    joint: float,
    first_only: float,
    second_only: float,
) -> float:
    """
    Diferencia-en-diferencias para una interacción observacional.

    Esta función NO demuestra causalidad.

    Valor:
        joint - first_only - second_only + baseline
    """
    return float(joint - first_only - second_only + baseline)


def normalized_interaction_effect(
    baseline: float,
    joint: float,
    first_only: float,
    second_only: float,
) -> float:
    """
    Versión normalizada del efecto de interacción observacional.
    """
    effect = interaction_effect_proxy(
        baseline,
        joint,
        first_only,
        second_only,
    )

    scale = max(
        abs(baseline),
        abs(first_only),
        abs(second_only),
        abs(joint),
    )

    if scale == 0.0:
        raise MetricInputError(
            "No puede normalizarse una interacción con escala 0"
        )

    return float(effect / scale)


# ---------------------------------------------------------------------------
# Acoplamiento y sincronización
# ---------------------------------------------------------------------------


def synchronization_index(
    first: Sequence[float] | np.ndarray,
    second: Sequence[float] | np.ndarray,
) -> float:
    """
    Magnitud de correlación absoluta entre dos trayectorias.

    No implica causalidad.
    """
    return abs(correlation(first, second))


def coupling_change(
    baseline_coupling: float,
    current_coupling: float,
) -> float:
    """Cambio absoluto en la fuerza de acoplamiento."""
    return float(current_coupling - baseline_coupling)


def relative_coupling_change(
    baseline_coupling: float,
    current_coupling: float,
) -> float:
    if baseline_coupling == 0.0:
        raise MetricInputError(
            "No puede calcularse cambio relativo desde coupling 0"
        )

    return float(
        (current_coupling - baseline_coupling)
        / abs(baseline_coupling)
    )


# ---------------------------------------------------------------------------
# Capacidad dinámica
# ---------------------------------------------------------------------------


def effective_capacity(
    nominal_capacity: float,
    availability_fraction: float,
    accessibility_fraction: float = 1.0,
) -> float:
    """
    Capacidad efectiva:

        C_effective = C_nominal · availability · accessibility
    """
    if nominal_capacity < 0.0:
        raise MetricInputError("nominal_capacity debe ser >= 0")

    if not 0.0 <= availability_fraction <= 1.0:
        raise MetricInputError(
            "availability_fraction debe estar entre 0 y 1"
        )

    if not 0.0 <= accessibility_fraction <= 1.0:
        raise MetricInputError(
            "accessibility_fraction debe estar entre 0 y 1"
        )

    return float(
        nominal_capacity
        * availability_fraction
        * accessibility_fraction
    )


def capacity_reserve(
    effective_capacity_value: float,
    demand: float,
) -> float:
    """Reserva absoluta de capacidad."""
    if effective_capacity_value < 0.0 or demand < 0.0:
        raise MetricInputError("capacity y demand deben ser >= 0")

    return float(effective_capacity_value - demand)


def capacity_reserve_ratio(
    effective_capacity_value: float,
    demand: float,
) -> float:
    """Reserva relativa respecto a la capacidad efectiva."""
    if effective_capacity_value <= 0.0 or demand < 0.0:
        raise MetricInputError(
            "effective_capacity debe ser > 0 y demand >= 0"
        )

    return float(
        (effective_capacity_value - demand)
        / effective_capacity_value
    )


def time_to_capacity_exhaustion(
    current_load: float,
    capacity: float,
    net_load_rate: float,
) -> float | None:
    """
    Tiempo estimado hasta alcanzar capacidad bajo una tasa neta constante.

    Es una extrapolación determinista y no una predicción probabilística.
    """
    if current_load < 0.0 or capacity <= 0.0:
        raise MetricInputError("Carga/capacidad inválidas")

    if net_load_rate <= 0.0:
        return None

    if current_load >= capacity:
        return 0.0

    return float((capacity - current_load) / net_load_rate)


# ---------------------------------------------------------------------------
# Cascadas y propagación
# ---------------------------------------------------------------------------


def cascade_amplification(
    initial_shock: float,
    final_impact: float,
) -> float:
    """Amplificación total de un shock."""
    if initial_shock == 0.0:
        raise MetricInputError("initial_shock no puede ser 0")

    return float(final_impact / initial_shock)


def cascade_gain(
    impacts: Sequence[float] | np.ndarray,
) -> float:
    """
    Ganancia multiplicativa aproximada de una secuencia de impactos.

    Requiere impactos positivos.
    """
    arr = _as_float_array(impacts, name="impacts")

    if np.any(arr <= 0.0):
        raise MetricInputError(
            "Todos los impactos deben ser positivos"
        )

    return float(np.prod(arr))


def propagation_depth(
    adjacency_matrix: Sequence[Sequence[float]] | np.ndarray,
) -> int:
    """
    Número máximo de pasos alcanzables desde cualquier nodo.

    Esta función utiliza una matriz de adyacencia binaria.
    """
    matrix = np.asarray(adjacency_matrix, dtype=float)

    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise MetricInputError(
            "adjacency_matrix debe ser cuadrada"
        )

    if np.any(~np.isfinite(matrix)):
        raise MetricInputError(
            "adjacency_matrix contiene valores no finitos"
        )

    n = matrix.shape[0]

    if n == 0:
        return 0

    reachable = matrix > 0
    power = reachable.copy()
    maximum_depth = 0

    for depth in range(1, n):
        if np.any(power):
            maximum_depth = depth

        power = power @ reachable

    return maximum_depth


# ---------------------------------------------------------------------------
# Concentración, fragilidad y dependencia estructural
# ---------------------------------------------------------------------------


def normalized_hhi(
    shares: Sequence[float] | np.ndarray,
) -> float:
    """
    HHI normalizado a [0,1] cuando existe más de un componente.

    0 = distribución completamente uniforme.
    1 = concentración máxima.
    """
    arr = _as_float_array(shares, name="shares")

    if np.any(arr < 0.0):
        raise MetricInputError("shares no pueden ser negativas")

    total = float(np.sum(arr))

    if total <= 0.0:
        raise MetricInputError("shares deben tener suma positiva")

    shares_normalized = arr / total
    hhi = float(np.sum(shares_normalized**2))

    n = arr.size

    if n <= 1:
        return 1.0

    return float((hhi - 1.0 / n) / (1.0 - 1.0 / n))


def bottleneck_ratio(
    bottleneck_capacity: float,
    total_nominal_capacity: float,
) -> float:
    """
    Proporción de la capacidad nominal representada por el cuello de botella.
    """
    if bottleneck_capacity < 0.0 or total_nominal_capacity <= 0.0:
        raise MetricInputError("Capacidades inválidas")

    if bottleneck_capacity > total_nominal_capacity:
        raise MetricInputError(
            "El cuello de botella no puede superar la capacidad nominal total"
        )

    return float(bottleneck_capacity / total_nominal_capacity)


# ---------------------------------------------------------------------------
# Métricas de transición y régimen
# ---------------------------------------------------------------------------


def regime_distance(
    current_state: Sequence[float] | np.ndarray,
    reference_state: Sequence[float] | np.ndarray,
) -> float:
    """Distancia euclídea entre dos estados multidimensionales."""
    current = _as_float_array(current_state, name="current_state")
    reference = _as_float_array(reference_state, name="reference_state")

    _validate_same_length(current, reference)

    return float(np.linalg.norm(current - reference))


def normalized_regime_distance(
    current_state: Sequence[float] | np.ndarray,
    reference_state: Sequence[float] | np.ndarray,
    scale: Sequence[float] | np.ndarray,
) -> float:
    """Distancia entre estados normalizada componente a componente."""
    current = _as_float_array(current_state, name="current_state")
    reference = _as_float_array(reference_state, name="reference_state")
    scale_arr = _as_float_array(scale, name="scale")

    _validate_same_length(current, reference, scale_arr)

    if np.any(scale_arr <= 0.0):
        raise MetricInputError("scale debe ser estrictamente positivo")

    return float(
        np.linalg.norm((current - reference) / scale_arr)
    )


def state_velocity_norm(
    state_trajectory: Sequence[Sequence[float]] | np.ndarray,
    *,
    dt: float = 1.0,
) -> np.ndarray:
    """Norma de la velocidad del estado multidimensional."""
    states = np.asarray(state_trajectory, dtype=float)

    if states.ndim != 2 or states.shape[0] < 2:
        raise MetricInputError(
            "state_trajectory debe ser una matriz con al menos dos estados"
        )

    if not np.all(np.isfinite(states)):
        raise MetricInputError(
            "state_trajectory contiene valores no finitos"
        )

    if dt <= 0.0:
        raise MetricInputError("dt debe ser positivo")

    velocity = np.diff(states, axis=0) / dt
    return np.linalg.norm(velocity, axis=1)


# ---------------------------------------------------------------------------
# Evidencia de transición: combinación de señales sin convertirlas
# automáticamente en probabilidad
# ---------------------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class EarlyWarningSignal:
    """Resultado descriptivo de una señal temprana."""

    metric_id: str
    value: float
    direction: str
    window: int
    exploratory: bool = True


@dataclass(frozen=True, slots=True)
class DynamicStateSummary:
    """
    Resumen descriptivo de una trayectoria.

    No es un índice de riesgo y no debe convertirse automáticamente en una
    probabilidad.
    """

    level: float
    velocity: float
    acceleration: float
    variance: float
    autocorrelation: float
    cumulative_load: float


def summarize_dynamic_state(
    values: Sequence[float] | np.ndarray,
    *,
    dt: float = 1.0,
    autocorrelation_lag: int = 1,
) -> DynamicStateSummary:
    """
    Resume nivel, velocidad, aceleración, variabilidad, autocorrelación y carga.
    """
    arr = _as_float_array(values, name="values")

    if arr.size < 3:
        raise MetricInputError(
            "Se requieren al menos tres observaciones"
        )

    if dt <= 0.0:
        raise MetricInputError("dt debe ser positivo")

    return DynamicStateSummary(
        level=float(arr[-1]),
        velocity=float(finite_difference_velocity(arr, dt)[-1]),
        acceleration=float(finite_difference_acceleration(arr, dt)[-1]),
        variance=variance(arr),
        autocorrelation=autocorrelation(
            arr,
            lag=autocorrelation_lag,
        ),
        cumulative_load=cumulative_load(arr, dt=dt),
    )


# ---------------------------------------------------------------------------
# Registro de métricas avanzadas
# ---------------------------------------------------------------------------

ADVANCED_METRIC_REGISTRY: Final[dict[str, MetricDefinition]] = {
    "skewness": MetricDefinition(
        "skewness",
        "Asimetría",
        MetricDomain.DISTRIBUTION,
        MetricKind.FORMULA,
        ValidationStatus.VALIDATED,
        "Asimetría de una distribución",
        "dimensionless",
        "float",
        "E[(X-μ)^3]/σ^3",
        EvidenceLevel.METHODOLOGICAL_STANDARD,
    ),
    "kurtosis_excess": MetricDefinition(
        "kurtosis_excess",
        "Curtosis excesiva",
        MetricDomain.DISTRIBUTION,
        MetricKind.FORMULA,
        ValidationStatus.VALIDATED,
        "Curtosis respecto a la distribución normal",
        "dimensionless",
        "float",
        "E[(X-μ)^4]/σ^4 - 3",
        EvidenceLevel.METHODOLOGICAL_STANDARD,
    ),
    "recovery_time": MetricDefinition(
        "recovery_time",
        "Tiempo de recuperación",
        MetricDomain.RESILIENCE,
        MetricKind.FORMULA,
        ValidationStatus.VALIDATED_ELSEWHERE,
        "Tiempo hasta retornar a una banda definida alrededor del estado basal",
        "time_steps",
        "integer_or_none",
        "min{t: |X_t-X_baseline| <= tolerance}",
        EvidenceLevel.PEER_REVIEWED,
        limitations=(
            "Requiere definición explícita de baseline, tolerancia y shock.",
        ),
    ),
    "resilience_loss": MetricDefinition(
        "resilience_loss",
        "Pérdida de resiliencia/capacidad",
        MetricDomain.RESILIENCE,
        MetricKind.FORMULA,
        ValidationStatus.VALIDATED_ELSEWHERE,
        "Pérdida relativa de capacidad durante un shock",
        "fraction",
        "float",
        "(C_baseline-C_min)/C_baseline",
        EvidenceLevel.PEER_REVIEWED,
    ),
    "capacity_reserve_ratio": MetricDefinition(
        "capacity_reserve_ratio",
        "Reserva relativa de capacidad",
        MetricDomain.CAPACITY,
        MetricKind.RATE,
        ValidationStatus.VALIDATED,
        "Margen de capacidad disponible respecto a la capacidad efectiva",
        "fraction",
        "float",
        "(C-D)/C",
        EvidenceLevel.METHODOLOGICAL_STANDARD,
    ),
    "time_to_capacity_exhaustion": MetricDefinition(
        "time_to_capacity_exhaustion",
        "Tiempo hasta agotamiento de capacidad",
        MetricDomain.CAPACITY,
        MetricKind.FORMULA,
        ValidationStatus.EXPERIMENTAL,
        "Extrapolación determinista del tiempo hasta alcanzar capacidad",
        "time",
        "float_or_none",
        "(C-L)/dLdt",
        EvidenceLevel.METHODOLOGICAL_STANDARD,
        limitations=(
            "Sólo es válido bajo la hipótesis de tasa neta aproximadamente constante.",
        ),
    ),
    "lagged_correlation": MetricDefinition(
        "lagged_correlation",
        "Correlación retardada",
        MetricDomain.TIME_SERIES,
        MetricKind.FORMULA,
        ValidationStatus.VALIDATED,
        "Asociación entre dos series con desfase temporal",
        "correlation",
        "float",
        "corr(X_t,Y_t+lag)",
        EvidenceLevel.METHODOLOGICAL_STANDARD,
        limitations=(
            "La asociación temporal retardada no demuestra causalidad.",
        ),
    ),
    "interaction_effect_proxy": MetricDefinition(
        "interaction_effect_proxy",
        "Efecto de interacción observacional",
        MetricDomain.SYSTEM_DYNAMICS,
        MetricKind.FORMULA,
        ValidationStatus.VALIDATED,
        "Diferencia-en-diferencias para describir desviación de aditividad",
        "output_units",
        "float",
        "joint-first_only-second_only+baseline",
        EvidenceLevel.METHODOLOGICAL_STANDARD,
        limitations=(
            "No constituye identificación causal sin diseño causal apropiado.",
        ),
    ),
    "synchronization_index": MetricDefinition(
        "synchronization_index",
        "Índice de sincronización",
        MetricDomain.NETWORK,
        MetricKind.FORMULA,
        ValidationStatus.VALIDATED,
        "Magnitud de correlación entre trayectorias",
        "0-1",
        "float",
        "|corr(X,Y)|",
        EvidenceLevel.METHODOLOGICAL_STANDARD,
        limitations=(
            "No implica causalidad ni dirección de influencia.",
        ),
    ),
    "cascade_amplification": MetricDefinition(
        "cascade_amplification",
        "Amplificación de cascada",
        MetricDomain.SYSTEM_DYNAMICS,
        MetricKind.FORMULA,
        ValidationStatus.EXPERIMENTAL,
        "Relación entre impacto final y shock inicial",
        "ratio",
        "float",
        "final_impact/initial_shock",
        EvidenceLevel.METHODOLOGICAL_STANDARD,
        limitations=(
            "Requiere definición operacional del shock y del impacto.",
        ),
    ),
    "regime_distance": MetricDefinition(
        "regime_distance",
        "Distancia entre estados",
        MetricDomain.SYSTEM_DYNAMICS,
        MetricKind.FORMULA,
        ValidationStatus.VALIDATED,
        "Distancia euclídea entre dos estados multidimensionales",
        "state_units",
        "float",
        "||X-X_reference||₂",
        EvidenceLevel.METHODOLOGICAL_STANDARD,
    ),
}


def get_advanced_metric_definition(metric_id: str) -> MetricDefinition:
    """Obtiene una métrica avanzada sin modificar todavía el registro principal."""
    try:
        return ADVANCED_METRIC_REGISTRY[metric_id]
    except KeyError as exc:
        raise MetricError(
            f"Métrica avanzada no registrada: {metric_id}"
        ) from exc


def validate_advanced_metric_registry() -> None:
    """Comprueba la integridad del catálogo avanzado."""
    for metric_id, definition in ADVANCED_METRIC_REGISTRY.items():
        if metric_id != definition.id:
            raise MetricError(
                f"ID inconsistente en métrica avanzada: {metric_id}"
            )

        if not definition.description.strip():
            raise MetricError(
                f"Descripción vacía en métrica avanzada: {metric_id}"
            )

        if definition.status == ValidationStatus.OFFICIAL:
            if definition.formula is not None:
                raise MetricError(
                    "Una métrica oficial no debe recibir una fórmula local "
                    f"en el registro: {metric_id}"
                )


validate_advanced_metric_registry()


# Extensión explícita del catálogo público del módulo.
__all__.extend(
    (
        "EarlyWarningSignal",
        "DynamicStateSummary",
        "ADVANCED_METRIC_REGISTRY",
        "get_advanced_metric_definition",
        "validate_advanced_metric_registry",
        "skewness",
        "kurtosis_excess",
        "coefficient_of_variation_change",
        "rolling_skewness",
        "rolling_kurtosis_excess",
        "recovery_time",
        "recovery_fraction",
        "resilience_loss",
        "resilience_recovery_ratio",
        "overshoot",
        "undershoot",
        "area_between_curves",
        "trajectory_distance",
        "local_slope",
        "rolling_slope",
        "rolling_acceleration",
        "hysteresis_gap",
        "threshold_crossing_index",
        "covariance",
        "correlation",
        "lagged_correlation",
        "interaction_effect_proxy",
        "normalized_interaction_effect",
        "synchronization_index",
        "coupling_change",
        "relative_coupling_change",
        "effective_capacity",
        "capacity_reserve",
        "capacity_reserve_ratio",
        "time_to_capacity_exhaustion",
        "cascade_amplification",
        "cascade_gain",
        "propagation_depth",
        "normalized_hhi",
        "bottleneck_ratio",
        "regime_distance",
        "normalized_regime_distance",
        "state_velocity_norm",
        "summarize_dynamic_state",
    )
)

Catálogo matemático y motor de métricas de CeutIA.

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