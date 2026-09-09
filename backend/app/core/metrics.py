# =============================================================================
# DISTRIBUCIÓN TERRITORIAL, CO-LOCALIZACIÓN, SENSIBILIDAD Y AMPLIFICACIÓN
# SISTÉMICA EN TERRITORIOS DE PEQUEÑA ESCALA
#
# Esta sección opera sobre unidades territoriales genéricas:
# barrios, distritos, zonas censales, áreas operativas, cuadrículas, etc.
#
# Principios:
# - una unidad territorial no es una característica de las personas que viven en ella;
# - concentración espacial != peligrosidad;
# - co-localización != causalidad;
# - sensibilidad != probabilidad de violencia;
# - amplificación observada != predicción individual;
# - las métricas deben conservar escala, denominador y ventana temporal.
# =============================================================================

def _as_territorial_matrix(
    values: Sequence[Sequence[float]] | np.ndarray,
    *,
    name: str = "values",
) -> np.ndarray:
    """Convierte datos territoriales en matriz [unidad territorial, variable]."""
    arr = np.asarray(values, dtype=float)

    if arr.ndim != 2:
        raise MetricInputError(f"{name} debe ser una matriz 2D")
    if arr.shape[0] < 1 or arr.shape[1] < 1:
        raise MetricInputError(f"{name} no puede estar vacía")
    if not np.all(np.isfinite(arr)):
        raise MetricInputError(f"{name} contiene valores no finitos")

    return arr


def _as_spatial_weights(
    weights: Sequence[Sequence[float]] | np.ndarray,
    n_units: int,
) -> np.ndarray:
    """Valida una matriz de pesos espaciales W."""
    w = np.asarray(weights, dtype=float)

    if w.ndim != 2 or w.shape != (n_units, n_units):
        raise MetricInputError("weights debe tener dimensión (n_units, n_units)")
    if not np.all(np.isfinite(w)):
        raise MetricInputError("weights contiene valores no finitos")
    if np.any(w < 0):
        raise MetricInputError("weights no puede contener valores negativos")

    w = w.copy()
    np.fill_diagonal(w, 0.0)

    if float(np.sum(w)) <= 0.0:
        raise MetricInputError("La matriz espacial debe contener al menos un vínculo")

    return w


def territorial_total(
    values: Sequence[float] | np.ndarray,
) -> float:
    """Carga, demanda o exposición territorial total."""
    arr = _as_float_array(values, name="values")
    if np.any(arr < 0):
        raise MetricInputError("values debe ser no negativo")
    return float(np.sum(arr))


def territorial_share(
    values: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Participación relativa de cada unidad territorial en el total."""
    arr = _as_float_array(values, name="values")
    if np.any(arr < 0):
        raise MetricInputError("values debe ser no negativo")

    total = float(np.sum(arr))
    if total <= 0.0:
        raise MetricInputError("El total territorial debe ser positivo")

    return arr / total


def territorial_concentration_hhi(
    values: Sequence[float] | np.ndarray,
) -> float:
    """HHI territorial: concentración de una carga entre unidades."""
    shares = territorial_share(values)
    return float(np.sum(shares**2))


def territorial_entropy(
    values: Sequence[float] | np.ndarray,
) -> float:
    """Entropía de distribución territorial."""
    shares = territorial_share(values)
    positive = shares[shares > 0.0]
    return float(-np.sum(positive * np.log(positive)))


def territorial_effective_unit_count(
    values: Sequence[float] | np.ndarray,
) -> float:
    """
    Número efectivo de unidades territoriales:
    1 / HHI.

    No representa población ni vulnerabilidad; mide concentración
    de la magnitud introducida.
    """
    hhi = territorial_concentration_hhi(values)
    if hhi <= 0.0:
        raise MetricInputError("HHI inválido")
    return float(1.0 / hhi)


def territorial_inequality_ratio(
    values: Sequence[float] | np.ndarray,
) -> float:
    """
    Cociente entre la mayor participación territorial y la participación
    uniforme esperada.
    """
    arr = _as_float_array(values, name="values")
    if np.any(arr < 0):
        raise MetricInputError("values debe ser no negativo")

    n = arr.size
    if n == 0:
        raise MetricInputError("values no puede estar vacío")

    shares = territorial_share(arr)
    return float(np.max(shares) * n)


def territorial_burden_per_population(
    burden: Sequence[float] | np.ndarray,
    population: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Carga territorial normalizada por población."""
    b = _as_float_array(burden, name="burden")
    p = _as_float_array(population, name="population")
    _validate_same_length(b, p)

    if np.any(b < 0):
        raise MetricInputError("burden debe ser no negativo")
    if np.any(p <= 0):
        raise MetricInputError("population debe ser positiva")

    return b / p


def territorial_capacity_utilization(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Utilización local por unidad territorial."""
    d = _as_float_array(demand, name="demand")
    c = _as_float_array(capacity, name="capacity")
    _validate_same_length(d, c)

    if np.any(d < 0):
        raise MetricInputError("demand debe ser no negativa")
    if np.any(c <= 0):
        raise MetricInputError("capacity debe ser positiva")

    return d / c


def territorial_capacity_headroom(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Reserva relativa de capacidad por unidad territorial."""
    utilization_values = territorial_capacity_utilization(demand, capacity)
    return 1.0 - utilization_values


def territorial_excess_demand(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Déficit absoluto local cuando la demanda supera la capacidad."""
    d = _as_float_array(demand, name="demand")
    c = _as_float_array(capacity, name="capacity")
    _validate_same_length(d, c)

    if np.any(d < 0):
        raise MetricInputError("demand debe ser no negativa")
    if np.any(c <= 0):
        raise MetricInputError("capacity debe ser positiva")

    return np.maximum(d - c, 0.0)


def territorial_bottleneck_share(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
) -> float:
    """
    Fracción del déficit territorial total atribuible a la unidad
    con mayor déficit.
    """
    excess = territorial_excess_demand(demand, capacity)
    total = float(np.sum(excess))

    if total <= 0.0:
        return 0.0

    return float(np.max(excess) / total)


def territorial_saturation_fraction(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
    *,
    threshold: float = 1.0,
) -> float:
    """Fracción de unidades cuya utilización alcanza el umbral."""
    if threshold <= 0.0:
        raise MetricInputError("threshold debe ser positivo")

    utilization_values = territorial_capacity_utilization(demand, capacity)
    return float(np.mean(utilization_values >= threshold))


def territorial_hotspot_share(
    values: Sequence[float] | np.ndarray,
    *,
    quantile: float = 0.90,
) -> float:
    """
    Proporción del total territorial localizada en unidades por encima
    del cuantil especificado.
    """
    arr = _as_float_array(values, name="values")
    if np.any(arr < 0):
        raise MetricInputError("values debe ser no negativo")
    if not 0.0 < quantile < 1.0:
        raise MetricInputError("quantile debe estar entre 0 y 1")

    threshold = float(np.quantile(arr, quantile))
    hotspot_values = arr[arr >= threshold]
    total = float(np.sum(arr))

    if total <= 0.0:
        return 0.0

    return float(np.sum(hotspot_values) / total)


def territorial_burden_coefficient(
    values: Sequence[float] | np.ndarray,
) -> float:
    """
    Coeficiente de concentración relativa:
    desviación estándar de las participaciones / participación uniforme.
    """
    shares = territorial_share(values)
    uniform_share = 1.0 / shares.size

    return float(np.std(shares, ddof=0) / uniform_share)


def spatial_lag(
    values: Sequence[float] | np.ndarray,
    weights: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """Rezago espacial W·x con normalización por suma de pesos de fila."""
    x = _as_float_array(values, name="values")
    w = _as_spatial_weights(weights, x.size)

    row_sums = np.sum(w, axis=1)
    normalized_w = w / row_sums[:, None]

    return normalized_w @ x


def spatial_gradient(
    values: Sequence[float] | np.ndarray,
    weights: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """
    Gradiente espacial aproximado:
    diferencia entre el valor local y el promedio ponderado de sus vecinos.
    """
    x = _as_float_array(values, name="values")
    lag = spatial_lag(x, weights)

    return x - lag


def spatial_gradient_magnitude(
    values: Sequence[float] | np.ndarray,
    weights: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """Magnitud media del gradiente espacial."""
    gradient = spatial_gradient(values, weights)
    return float(np.mean(np.abs(gradient)))


def spatial_dispersion_index(
    values: Sequence[float] | np.ndarray,
    weights: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    Heterogeneidad espacial relativa respecto a los vecinos.
    """
    x = _as_float_array(values, name="values")
    lag = spatial_lag(x, weights)

    scale = float(np.std(x, ddof=0))
    if scale == 0.0:
        return 0.0

    return float(np.mean(np.abs(x - lag)) / scale)


def spatial_morans_i(
    values: Sequence[float] | np.ndarray,
    weights: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    I de Moran global.

    La interpretación depende de la definición de W y de la geometría
    territorial. No implica causalidad.
    """
    x = _as_float_array(values, name="values")
    w = _as_spatial_weights(weights, x.size)

    centered = x - float(np.mean(x))
    denominator = float(np.sum(centered**2))

    if denominator <= 0.0:
        raise MetricInputError("La variable territorial tiene varianza nula")

    weight_sum = float(np.sum(w))
    if weight_sum <= 0.0:
        raise MetricInputError("La suma de pesos espaciales debe ser positiva")

    numerator = float(centered @ w @ centered)

    return float((x.size / weight_sum) * (numerator / denominator))


def spatial_local_association(
    values: Sequence[float] | np.ndarray,
    weights: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """
    Asociación espacial local simplificada:
    z_i × promedio espacial ponderado de z_j.

    Es una señal exploratoria de agrupación local, no un test inferencial.
    """
    x = _as_float_array(values, name="values")
    w = _as_spatial_weights(weights, x.size)

    sd = float(np.std(x, ddof=0))
    if sd == 0.0:
        raise MetricInputError("La variable territorial tiene varianza nula")

    z = (x - float(np.mean(x))) / sd
    lag_z = spatial_lag(z, w)

    return z * lag_z


def territorial_cospatial_burden(
    first: Sequence[float] | np.ndarray,
    second: Sequence[float] | np.ndarray,
) -> float:
    """
    Co-localización ponderada de dos presiones territoriales.

    No demuestra interacción causal.
    """
    a = _as_float_array(first, name="first")
    b = _as_float_array(second, name="second")
    _validate_same_length(a, b)

    if np.any(a < 0) or np.any(b < 0):
        raise MetricInputError("Las presiones deben ser no negativas")

    sa = territorial_share(a)
    sb = territorial_share(b)

    return float(np.sum(sa * sb))


def territorial_cospatial_overlap(
    first: Sequence[float] | np.ndarray,
    second: Sequence[float] | np.ndarray,
    *,
    quantile: float = 0.90,
) -> float:
    """
    Superposición de hotspots de dos fenómenos territoriales.
    """
    a = _as_float_array(first, name="first")
    b = _as_float_array(second, name="second")
    _validate_same_length(a, b)

    if not 0.0 < quantile < 1.0:
        raise MetricInputError("quantile debe estar entre 0 y 1")

    threshold_a = float(np.quantile(a, quantile))
    threshold_b = float(np.quantile(b, quantile))

    hotspot_a = a >= threshold_a
    hotspot_b = b >= threshold_b

    union = hotspot_a | hotspot_b
    if not np.any(union):
        return 0.0

    return float(np.sum(hotspot_a & hotspot_b) / np.sum(union))


def territorial_multi_pressure_score(
    pressures: Sequence[Sequence[float]] | np.ndarray,
    weights: Sequence[float] | np.ndarray | None = None,
) -> np.ndarray:
    """
    Perfil multidimensional de presión territorial.

    Cada columna representa una dimensión distinta.
    Cada dimensión se estandariza por su distribución territorial antes
    de agregarse. La salida NO es un riesgo individual.
    """
    matrix = _as_territorial_matrix(pressures, name="pressures")

    means = np.mean(matrix, axis=0)
    stds = np.std(matrix, axis=0, ddof=0)

    if np.any(stds == 0.0):
        raise MetricInputError(
            "No se puede integrar una dimensión territorial constante"
        )

    z = (matrix - means) / stds

    if weights is None:
        normalized_weights = np.ones(matrix.shape[1]) / matrix.shape[1]
    else:
        normalized_weights = _as_float_array(weights, name="weights")
        if normalized_weights.size != matrix.shape[1]:
            raise MetricInputError("weights debe coincidir con el número de dimensiones")
        if np.any(normalized_weights < 0):
            raise MetricInputError("weights no puede contener valores negativos")
        total_weight = float(np.sum(normalized_weights))
        if total_weight <= 0.0:
            raise MetricInputError("La suma de weights debe ser positiva")
        normalized_weights = normalized_weights / total_weight

    return z @ normalized_weights


def territorial_pressure_breadth(
    pressures: Sequence[Sequence[float]] | np.ndarray,
    *,
    threshold: float = 1.0,
) -> np.ndarray:
    """
    Número de dimensiones que superan un umbral estandarizado en cada zona.
    """
    matrix = _as_territorial_matrix(pressures, name="pressures")

    if threshold < 0.0:
        raise MetricInputError("threshold debe ser no negativo")

    means = np.mean(matrix, axis=0)
    stds = np.std(matrix, axis=0, ddof=0)

    if np.any(stds == 0.0):
        raise MetricInputError("No se puede calcular breadth con dimensiones constantes")

    z = (matrix - means) / stds

    return np.sum(z >= threshold, axis=1).astype(float)


def territorial_pressure_breadth_fraction(
    pressures: Sequence[Sequence[float]] | np.ndarray,
    *,
    threshold: float = 1.0,
) -> np.ndarray:
    """Fracción de dimensiones simultáneamente elevadas por zona."""
    matrix = _as_territorial_matrix(pressures, name="pressures")
    breadth = territorial_pressure_breadth(matrix, threshold=threshold)

    return breadth / matrix.shape[1]


def territorial_pressure_correlation(
    pressures: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """
    Matriz de correlación transversal entre presiones territoriales.

    No implica causalidad.
    """
    matrix = _as_territorial_matrix(pressures, name="pressures")

    if matrix.shape[0] < 2:
        raise MetricInputError("Se requieren al menos dos unidades territoriales")

    stds = np.std(matrix, axis=0, ddof=1)
    if np.any(stds == 0.0):
        raise MetricInputError("Una dimensión territorial tiene varianza nula")

    return np.corrcoef(matrix, rowvar=False)


def territorial_pressure_dependence(
    pressures: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    Fuerza media absoluta de asociación entre dimensiones territoriales.
    """
    correlation_matrix = territorial_pressure_correlation(pressures)

    n = correlation_matrix.shape[0]
    if n < 2:
        return 0.0

    upper = correlation_matrix[np.triu_indices(n, k=1)]

    return float(np.mean(np.abs(upper)))


def territorial_capacity_pressure(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Presión local relativa sobre capacidad.

    >1 indica demanda superior a capacidad.
    """
    return territorial_capacity_utilization(demand, capacity)


def territorial_local_reserve(
    capacity: Sequence[float] | np.ndarray,
    load: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Reserva absoluta local."""
    c = _as_float_array(capacity, name="capacity")
    l = _as_float_array(load, name="load")
    _validate_same_length(c, l)

    if np.any(c < 0) or np.any(l < 0):
        raise MetricInputError("capacity y load deben ser no negativas")

    return c - l


def territorial_reserve_depletion(
    reserve_before: Sequence[float] | np.ndarray,
    reserve_after: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Pérdida absoluta de reserva por unidad territorial."""
    before = _as_float_array(reserve_before, name="reserve_before")
    after = _as_float_array(reserve_after, name="reserve_after")
    _validate_same_length(before, after)

    if np.any(before < 0) or np.any(after < 0):
        raise MetricInputError("Las reservas deben ser no negativas")

    return before - after


def territorial_response_sensitivity(
    perturbation: Sequence[float] | np.ndarray,
    response: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Sensibilidad territorial observada:

        Δrespuesta / Δperturbación

    Debe utilizarse con variables temporalmente alineadas.
    No constituye causalidad por sí misma.
    """
    p = _as_float_array(perturbation, name="perturbation")
    r = _as_float_array(response, name="response")
    _validate_same_length(p, r)

    if np.any(p < 0):
        raise MetricInputError("perturbation debe ser no negativa")

    nonzero = p > 0.0
    if not np.any(nonzero):
        raise MetricInputError("No existe perturbación positiva")

    return np.divide(
        r,
        p,
        out=np.zeros_like(r, dtype=float),
        where=nonzero,
    )


def territorial_amplification_factor(
    baseline: Sequence[float] | np.ndarray,
    response: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Amplificación relativa entre estímulo y respuesta.

    No debe interpretarse como probabilidad de un resultado concreto.
    """
    b = _as_float_array(baseline, name="baseline")
    r = _as_float_array(response, name="response")
    _validate_same_length(b, r)

    if np.any(b < 0) or np.any(r < 0):
        raise MetricInputError("baseline y response deben ser no negativas")

    return np.divide(
        r,
        b,
        out=np.full_like(r, np.nan, dtype=float),
        where=b > 0.0,
    )


def territorial_response_elasticity(
    baseline_perturbation: Sequence[float] | np.ndarray,
    perturbed_perturbation: Sequence[float] | np.ndarray,
    baseline_response: Sequence[float] | np.ndarray,
    perturbed_response: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Elasticidad territorial:

        (% cambio de respuesta) / (% cambio de perturbación)

    Requiere valores basales positivos.
    """
    p0 = _as_float_array(baseline_perturbation, name="baseline_perturbation")
    p1 = _as_float_array(perturbed_perturbation, name="perturbed_perturbation")
    r0 = _as_float_array(baseline_response, name="baseline_response")
    r1 = _as_float_array(perturbed_response, name="perturbed_response")

    _validate_same_length(p0, p1, r0, r1)

    if np.any(p0 <= 0) or np.any(r0 <= 0):
        raise MetricInputError("Los valores basales deben ser positivos")

    delta_p = (p1 - p0) / p0
    delta_r = (r1 - r0) / r0

    if np.any(delta_p == 0.0):
        raise MetricInputError(
            "La elasticidad es indefinida cuando no cambia la perturbación"
        )

    return delta_r / delta_p


def territorial_cross_pressure(
    first: Sequence[float] | np.ndarray,
    second: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Interacción multiplicativa normalizada de dos presiones territoriales.

    Es una métrica descriptiva de co-presencia, no una inferencia causal.
    """
    a = _as_float_array(first, name="first")
    b = _as_float_array(second, name="second")
    _validate_same_length(a, b)

    if np.any(a < 0) or np.any(b < 0):
        raise MetricInputError("Las presiones deben ser no negativas")

    a_mean = float(np.mean(a))
    b_mean = float(np.mean(b))

    if a_mean == 0.0 or b_mean == 0.0:
        raise MetricInputError("Las medias de las presiones deben ser positivas")

    return (a / a_mean) * (b / b_mean)


def territorial_cross_pressure_breadth(
    first: Sequence[float] | np.ndarray,
    second: Sequence[float] | np.ndarray,
    *,
    threshold: float = 1.0,
) -> float:
    """Fracción territorial con dos presiones simultáneamente elevadas."""
    cross = territorial_cross_pressure(first, second)
    return float(np.mean(cross >= threshold))


def territorial_multi_pressure_concentration(
    pressures: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    Concentración territorial de la carga multidimensional integrada.
    """
    profile = territorial_multi_pressure_score(pressures)

    shifted = profile - float(np.min(profile))
    shifted += 1e-12

    return territorial_concentration_hhi(shifted)


def territorial_multi_pressure_hotspot(
    pressures: Sequence[Sequence[float]] | np.ndarray,
    *,
    threshold: float = 1.0,
) -> np.ndarray:
    """
    Identifica unidades con múltiples dimensiones simultáneamente elevadas.

    Devuelve una señal cuantitativa; no clasifica personas ni grupos.
    """
    breadth_fraction = territorial_pressure_breadth_fraction(
        pressures,
        threshold=threshold,
    )

    return breadth_fraction


def territorial_bottleneck_migration(
    previous_utilization: Sequence[float] | np.ndarray,
    current_utilization: Sequence[float] | np.ndarray,
) -> int | None:
    """
    Detecta el desplazamiento de la unidad más saturada.

    Devuelve:
    - índice de la unidad actualmente más saturada si ha cambiado;
    - None si el cuello de botella permanece en la misma unidad.
    """
    previous = _as_float_array(previous_utilization, name="previous_utilization")
    current = _as_float_array(current_utilization, name="current_utilization")
    _validate_same_length(previous, current)

    if previous.size == 0:
        raise MetricInputError("No hay unidades territoriales")

    previous_index = int(np.argmax(previous))
    current_index = int(np.argmax(current))

    if previous_index == current_index:
        return None

    return current_index


def territorial_load_transfer(
    previous_load: Sequence[float] | np.ndarray,
    current_load: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Variación territorial de carga entre dos momentos."""
    previous = _as_float_array(previous_load, name="previous_load")
    current = _as_float_array(current_load, name="current_load")
    _validate_same_length(previous, current)

    if np.any(previous < 0) or np.any(current < 0):
        raise MetricInputError("Las cargas deben ser no negativas")

    return current - previous


def territorial_load_transfer_concentration(
    previous_load: Sequence[float] | np.ndarray,
    current_load: Sequence[float] | np.ndarray,
) -> float:
    """Concentración absoluta del incremento positivo de carga."""
    transfer = territorial_load_transfer(previous_load, current_load)
    positive_transfer = np.maximum(transfer, 0.0)

    total = float(np.sum(positive_transfer))
    if total <= 0.0:
        return 0.0

    return territorial_concentration_hhi(positive_transfer)


def territorial_spatial_propagation(
    previous_values: Sequence[float] | np.ndarray,
    current_values: Sequence[float] | np.ndarray,
    weights: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    Fracción del incremento observado que aparece en unidades vecinas
    de acuerdo con W.

    Es una métrica descriptiva de propagación espacial, no una prueba causal.
    """
    previous = _as_float_array(previous_values, name="previous_values")
    current = _as_float_array(current_values, name="current_values")
    _validate_same_length(previous, current)

    if np.any(previous < 0) or np.any(current < 0):
        raise MetricInputError("Los valores deben ser no negativos")

    w = _as_spatial_weights(weights, previous.size)
    increase = np.maximum(current - previous, 0.0)

    total_increase = float(np.sum(increase))
    if total_increase <= 0.0:
        return 0.0

    previous_signal = previous / max(float(np.max(previous)), 1e-12)
    neighbor_exposure = spatial_lag(previous_signal, w)

    propagated = float(np.sum(increase * neighbor_exposure))

    return float(propagated / total_increase)


def territorial_spatial_synchronization(
    first: Sequence[float] | np.ndarray,
    second: Sequence[float] | np.ndarray,
) -> float:
    """
    Sincronización temporal/territorial entre dos fenómenos agregados
    sobre las mismas unidades.
    """
    a = _as_float_array(first, name="first")
    b = _as_float_array(second, name="second")
    _validate_same_length(a, b)

    if np.std(a, ddof=0) == 0.0 or np.std(b, ddof=0) == 0.0:
        raise MetricInputError("No se puede calcular sincronización con varianza nula")

    return float(np.corrcoef(a, b)[0, 1])


def territorial_coincidence_breadth(
    variables: Sequence[Sequence[float]] | np.ndarray,
    *,
    thresholds: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Número de fenómenos que superan simultáneamente sus umbrales
    en cada unidad territorial.
    """
    matrix = _as_territorial_matrix(variables, name="variables")
    threshold_array = _as_float_array(thresholds, name="thresholds")

    if threshold_array.size != matrix.shape[1]:
        raise MetricInputError("thresholds debe coincidir con las dimensiones")

    return np.sum(matrix >= threshold_array[None, :], axis=1).astype(float)


def territorial_coincidence_fraction(
    variables: Sequence[Sequence[float]] | np.ndarray,
    *,
    thresholds: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Fracción de fenómenos simultáneamente elevados por unidad."""
    matrix = _as_territorial_matrix(variables, name="variables")
    coincidence = territorial_coincidence_breadth(
        matrix,
        thresholds=thresholds,
    )

    return coincidence / matrix.shape[1]


def territorial_systemic_sensitivity(
    perturbation: Sequence[float] | np.ndarray,
    response_matrix: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """
    Sensibilidad multidimensional:

        respuesta de cada dimensión / perturbación

    Devuelve matriz [unidad, dimensión].
    """
    p = _as_float_array(perturbation, name="perturbation")
    responses = _as_territorial_matrix(response_matrix, name="response_matrix")

    if p.size != responses.shape[0]:
        raise MetricInputError(
            "perturbation debe tener una observación por unidad territorial"
        )
    if np.any(p < 0):
        raise MetricInputError("perturbation debe ser no negativa")

    return np.divide(
        responses,
        p[:, None],
        out=np.zeros_like(responses, dtype=float),
        where=p[:, None] > 0.0,
    )


def territorial_systemic_amplification(
    perturbation: Sequence[float] | np.ndarray,
    response_matrix: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """
    Amplificación multidimensional de una perturbación sobre el territorio.

    Devuelve una matriz [unidad, dimensión].
    """
    sensitivity = territorial_systemic_sensitivity(
        perturbation,
        response_matrix,
    )

    return sensitivity


def territorial_small_stimulus_response(
    perturbation: Sequence[float] | np.ndarray,
    response: Sequence[float] | np.ndarray,
    *,
    small_stimulus_quantile: float = 0.25,
) -> float:
    """
    Respuesta media normalizada ante perturbaciones situadas en el extremo
    bajo de su distribución.

    Es una métrica exploratoria de sensibilidad no lineal.
    """
    p = _as_float_array(perturbation, name="perturbation")
    r = _as_float_array(response, name="response")
    _validate_same_length(p, r)

    if np.any(p < 0) or np.any(r < 0):
        raise MetricInputError("perturbation y response deben ser no negativas")
    if not 0.0 < small_stimulus_quantile < 1.0:
        raise MetricInputError("small_stimulus_quantile debe estar entre 0 y 1")

    threshold = float(np.quantile(p, small_stimulus_quantile))
    mask = p <= threshold

    if not np.any(mask):
        raise MetricInputError("No existen observaciones de estímulo pequeño")

    mean_response = float(np.mean(r[mask]))
    global_response = float(np.mean(r))

    if global_response == 0.0:
        return 0.0

    return float(mean_response / global_response)


def territorial_non_linear_response_index(
    perturbation: Sequence[float] | np.ndarray,
    response: Sequence[float] | np.ndarray,
) -> float:
    """
    Índice exploratorio de no linealidad basado en la correlación entre
    cambios de perturbación y cambios de respuesta.

    Un valor elevado no demuestra un mecanismo causal concreto.
    """
    p = _as_float_array(perturbation, name="perturbation")
    r = _as_float_array(response, name="response")
    _validate_same_length(p, r)

    if p.size < 3:
        raise MetricInputError("Se requieren al menos tres observaciones")

    dp = np.diff(p)
    dr = np.diff(r)

    if np.std(dp, ddof=0) == 0.0 or np.std(dr, ddof=0) == 0.0:
        raise MetricInputError("Los cambios no presentan variabilidad suficiente")

    linear_fit = np.polyfit(dp, dr, 1)
    predicted = linear_fit[0] * dp + linear_fit[1]

    residual = dr - predicted
    residual_scale = float(np.std(residual, ddof=0))
    response_scale = float(np.std(dr, ddof=0))

    if response_scale == 0.0:
        return 0.0

    return float(residual_scale / response_scale)


def territorial_threshold_proximity(
    values: Sequence[float] | np.ndarray,
    thresholds: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Distancia relativa al umbral para cada unidad territorial.

    Valores:
    >0  -> por debajo del umbral si values < threshold
    =0  -> en el umbral
    <0  -> superación del umbral
    """
    x = _as_float_array(values, name="values")
    t = _as_float_array(thresholds, name="thresholds")
    _validate_same_length(x, t)

    if np.any(t <= 0.0):
        raise MetricInputError("thresholds debe ser positivo")

    return (t - x) / t


def territorial_time_series_concentration(
    values_by_time: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """
    HHI territorial para cada instante.

    Entrada: [tiempo, unidades].
    Salida: HHI por instante.
    """
    matrix = _as_territorial_matrix(values_by_time, name="values_by_time")

    result = np.empty(matrix.shape[0], dtype=float)

    for i, row in enumerate(matrix):
        result[i] = territorial_concentration_hhi(row)

    return result


def territorial_hotspot_persistence(
    values_by_time: Sequence[Sequence[float]] | np.ndarray,
    *,
    quantile: float = 0.90,
) -> np.ndarray:
    """
    Persistencia de hotspot por unidad territorial a lo largo del tiempo.
    """
    matrix = _as_territorial_matrix(values_by_time, name="values_by_time")

    if not 0.0 < quantile < 1.0:
        raise MetricInputError("quantile debe estar entre 0 y 1")

    thresholds = np.quantile(matrix, quantile, axis=0)
    hotspot = matrix >= thresholds[None, :]

    return np.mean(hotspot, axis=0)


def territorial_hotspot_turnover(
    values_by_time: Sequence[Sequence[float]] | np.ndarray,
    *,
    quantile: float = 0.90,
) -> float:
    """
    Cambio medio de composición de hotspots entre periodos consecutivos.
    """
    matrix = _as_territorial_matrix(values_by_time, name="values_by_time")

    if matrix.shape[0] < 2:
        raise MetricInputError("Se requieren al menos dos periodos")
    if not 0.0 < quantile < 1.0:
        raise MetricInputError("quantile debe estar entre 0 y 1")

    thresholds = np.quantile(matrix, quantile, axis=0)
    hotspots = matrix >= thresholds[None, :]

    changes = np.sum(hotspots[1:] != hotspots[:-1], axis=1)

    return float(np.mean(changes) / matrix.shape[1])


def territorial_multi_pressure_persistence(
    pressures_by_time: Sequence[Sequence[Sequence[float]]] | np.ndarray,
    *,
    threshold: float = 1.0,
) -> np.ndarray:
    """
    Persistencia de presión multidimensional elevada.

    Entrada:
        [tiempo, unidad territorial, dimensión]
    """
    tensor = np.asarray(pressures_by_time, dtype=float)

    if tensor.ndim != 3:
        raise MetricInputError(
            "pressures_by_time debe ser un tensor 3D [tiempo, unidad, dimensión]"
        )
    if not np.all(np.isfinite(tensor)):
        raise MetricInputError("pressures_by_time contiene valores no finitos")
    if tensor.shape[0] < 1:
        raise MetricInputError("Se requiere al menos un periodo")

    persistence = np.zeros(tensor.shape[1], dtype=float)

    for t in range(tensor.shape[0]):
        breadth = territorial_pressure_breadth_fraction(
            tensor[t],
            threshold=threshold,
        )
        persistence += breadth

    return persistence / tensor.shape[0]


def territorial_compound_pressure(
    pressures: Sequence[Sequence[float]] | np.ndarray,
    *,
    weights: Sequence[float] | np.ndarray | None = None,
) -> np.ndarray:
    """
    Presión compuesta territorial preservando la dimensionalidad original
    hasta la fase explícita de agregación.

    Se utiliza únicamente cuando la combinación de dimensiones está
    justificada por el modelo y sus pesos.
    """
    return territorial_multi_pressure_score(
        pressures,
        weights=weights,
    )


def territorial_reserve_adjusted_pressure(
    load: Sequence[float] | np.ndarray,
    reserve: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Presión ajustada por reserva disponible.

        load / reserve

    No se define cuando la reserva es cero.
    """
    l = _as_float_array(load, name="load")
    r = _as_float_array(reserve, name="reserve")
    _validate_same_length(l, r)

    if np.any(l < 0) or np.any(r < 0):
        raise MetricInputError("load y reserve deben ser no negativos")

    if np.any(r == 0.0):
        raise MetricInputError(
            "La presión ajustada por reserva es indefinida con reserva cero"
        )

    return l / r


def territorial_compound_shock_index(
    shocks: Sequence[Sequence[float]] | np.ndarray,
    *,
    weights: Sequence[float] | np.ndarray | None = None,
) -> np.ndarray:
    """
    Intensidad territorial de perturbaciones simultáneas.

    Entrada:
        [unidad territorial, tipo de perturbación]
    """
    return territorial_multi_pressure_score(
        shocks,
        weights=weights,
    )


def territorial_compound_shock_breadth(
    shocks: Sequence[Sequence[float]] | np.ndarray,
    *,
    threshold: float = 1.0,
) -> np.ndarray:
    """Número de perturbaciones simultáneamente elevadas por unidad."""
    return territorial_pressure_breadth(
        shocks,
        threshold=threshold,
    )


def territorial_systemic_exposure(
    exposure: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Exposición relativa a capacidad local.

    Permite comparar fenómenos diferentes siempre que las unidades
    estén correctamente normalizadas.
    """
    return territorial_capacity_utilization(
        exposure,
        capacity,
    )


def territorial_response_capacity_gap(
    demand: Sequence[float] | np.ndarray,
    response_capacity: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Brecha local entre demanda y capacidad de respuesta."""
    return territorial_excess_demand(
        demand,
        response_capacity,
    )


def territorial_recovery_fraction(
    baseline: Sequence[float] | np.ndarray,
    nadir: Sequence[float] | np.ndarray,
    current: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Fracción de recuperación desde el peor estado observado hacia baseline.

        (current - nadir) / (baseline - nadir)
    """
    b = _as_float_array(baseline, name="baseline")
    n = _as_float_array(nadir, name="nadir")
    c = _as_float_array(current, name="current")
    _validate_same_length(b, n, c)

    denominator = b - n

    if np.any(denominator <= 0.0):
        raise MetricInputError(
            "baseline debe ser estrictamente mayor que nadir"
        )

    return np.clip((c - n) / denominator, 0.0, 1.0)


def territorial_recovery_heterogeneity(
    baseline: Sequence[float] | np.ndarray,
    nadir: Sequence[float] | np.ndarray,
    current: Sequence[float] | np.ndarray,
) -> float:
    """Heterogeneidad territorial de recuperación."""
    recovery = territorial_recovery_fraction(
        baseline,
        nadir,
        current,
    )

    return float(np.std(recovery, ddof=0))


def territorial_systemic_profile(
    load: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
    population: Sequence[float] | np.ndarray,
) -> dict[str, np.ndarray | float]:
    """
    Perfil territorial integrado.

    Mantiene separadas las dimensiones fundamentales para evitar que
    una única puntuación oculte heterogeneidad territorial.
    """
    l = _as_float_array(load, name="load")
    c = _as_float_array(capacity, name="capacity")
    p = _as_float_array(population, name="population")
    _validate_same_length(l, c, p)

    utilization_values = territorial_capacity_utilization(l, c)
    reserve = territorial_local_reserve(c, l)
    load_per_population = territorial_burden_per_population(l, p)

    return {
        "load": l,
        "capacity": c,
        "population": p,
        "utilization": utilization_values,
        "reserve": reserve,
        "load_per_population": load_per_population,
        "load_concentration_hhi": territorial_concentration_hhi(l),
        "saturation_fraction": float(np.mean(utilization_values >= 1.0)),
        "maximum_utilization": float(np.max(utilization_values)),
        "minimum_reserve": float(np.min(reserve)),
    }


TERRITORIAL_SYSTEMIC_METRICS = {
    "territorial_total": territorial_total,
    "territorial_share": territorial_share,
    "territorial_concentration_hhi": territorial_concentration_hhi,
    "territorial_entropy": territorial_entropy,
    "territorial_effective_unit_count": territorial_effective_unit_count,
    "territorial_inequality_ratio": territorial_inequality_ratio,
    "territorial_burden_per_population": territorial_burden_per_population,
    "territorial_capacity_utilization": territorial_capacity_utilization,
    "territorial_capacity_headroom": territorial_capacity_headroom,
    "territorial_excess_demand": territorial_excess_demand,
    "territorial_bottleneck_share": territorial_bottleneck_share,
    "territorial_saturation_fraction": territorial_saturation_fraction,
    "territorial_hotspot_share": territorial_hotspot_share,
    "territorial_burden_coefficient": territorial_burden_coefficient,
    "spatial_lag": spatial_lag,
    "spatial_gradient": spatial_gradient,
    "spatial_gradient_magnitude": spatial_gradient_magnitude,
    "spatial_dispersion_index": spatial_dispersion_index,
    "spatial_morans_i": spatial_morans_i,
    "spatial_local_association": spatial_local_association,
    "territorial_cospatial_burden": territorial_cospatial_burden,
    "territorial_cospatial_overlap": territorial_cospatial_overlap,
    "territorial_multi_pressure_score": territorial_multi_pressure_score,
    "territorial_pressure_breadth": territorial_pressure_breadth,
    "territorial_pressure_breadth_fraction": territorial_pressure_breadth_fraction,
    "territorial_pressure_correlation": territorial_pressure_correlation,
    "territorial_pressure_dependence": territorial_pressure_dependence,
    "territorial_capacity_pressure": territorial_capacity_pressure,
    "territorial_local_reserve": territorial_local_reserve,
    "territorial_reserve_depletion": territorial_reserve_depletion,
    "territorial_response_sensitivity": territorial_response_sensitivity,
    "territorial_amplification_factor": territorial_amplification_factor,
    "territorial_response_elasticity": territorial_response_elasticity,
    "territorial_cross_pressure": territorial_cross_pressure,
    "territorial_cross_pressure_breadth": territorial_cross_pressure_breadth,
    "territorial_bottleneck_migration": territorial_bottleneck_migration,
    "territorial_load_transfer": territorial_load_transfer,
    "territorial_load_transfer_concentration": territorial_load_transfer_concentration,
    "territorial_spatial_propagation": territorial_spatial_propagation,
    "territorial_spatial_synchronization": territorial_spatial_synchronization,
    "territorial_coincidence_breadth": territorial_coincidence_breadth,
    "territorial_coincidence_fraction": territorial_coincidence_fraction,
    "territorial_systemic_sensitivity": territorial_systemic_sensitivity,
    "territorial_systemic_amplification": territorial_systemic_amplification,
    "territorial_small_stimulus_response": territorial_small_stimulus_response,
    "territorial_non_linear_response_index": territorial_non_linear_response_index,
    "territorial_threshold_proximity": territorial_threshold_proximity,
    "territorial_time_series_concentration": territorial_time_series_concentration,
    "territorial_hotspot_persistence": territorial_hotspot_persistence,
    "territorial_hotspot_turnover": territorial_hotspot_turnover,
    "territorial_multi_pressure_persistence": territorial_multi_pressure_persistence,
    "territorial_compound_pressure": territorial_compound_pressure,
    "territorial_reserve_adjusted_pressure": territorial_reserve_adjusted_pressure,
    "territorial_compound_shock_index": territorial_compound_shock_index,
    "territorial_compound_shock_breadth": territorial_compound_shock_breadth,
    "territorial_systemic_exposure": territorial_systemic_exposure,
    "territorial_response_capacity_gap": territorial_response_capacity_gap,
    "territorial_recovery_fraction": territorial_recovery_fraction,
    "territorial_recovery_heterogeneity": territorial_recovery_heterogeneity,
    "territorial_systemic_profile": territorial_systemic_profile,
}


TERRITORIAL_SYSTEMIC_INVARIANTS = (
    "Una concentración territorial no implica peligrosidad de la población residente.",
    "Co-localización no implica causalidad.",
    "Una señal territorial no debe transformarse automáticamente en riesgo individual.",
    "Las unidades territoriales deben conservar su definición, escala y denominador.",
    "Las métricas espaciales dependen de la matriz de pesos W y de su justificación.",
    "Un hotspot es una propiedad de la variable observada en una ventana temporal concreta.",
    "La amplificación observada no equivale a probabilidad de violencia ni de mortalidad.",
    "La sensibilidad a pequeños estímulos debe analizarse respecto al estado previo del sistema.",
    "Las perturbaciones deben conservar intensidad, duración, momento y localización.",
    "La combinación de presiones no demuestra un mecanismo causal por sí misma.",
    "Las métricas agregadas no deben utilizarse para inferir peligrosidad individual o grupal.",
    "La interpretación operacional requiere contexto temporal, espacial, epistemológico y de capacidad.",
    "CeutIA debe conservar la incertidumbre y la procedencia de cada variable territorial.",
)


__all__.extend(TERRITORIAL_SYSTEMIC_METRICS.keys())

# =============================================================================
# CeutIA — MÉTRICAS DE TRANSICIÓN, EARLY WARNING, EXTREMOS, ESPACIO-TIEMPO
#         E INCERTIDUMBRE
# =============================================================================
#
# Capa exclusivamente métrica.
#
# Estas funciones cuantifican propiedades observables o derivadas de datos.
# No constituyen por sí mismas modelos causales, predicciones calibradas,
# diagnósticos ni decisiones operativas.
#
# Principio:
# fenómeno → variable → dinámica observable → métrica
#
# =============================================================================


def lag_autocorrelation(
    values: Sequence[float] | np.ndarray,
    *,
    lag: int = 1,
) -> float:
    """
    Autocorrelación de una trayectoria para un desfase determinado.
    """
    x = _as_float_array(values, name="values")

    if lag < 1 or lag >= x.size:
        raise MetricInputError(
            "lag debe ser >= 1 y menor que el número de observaciones"
        )

    left = x[:-lag]
    right = x[lag:]

    if np.std(left) == 0 or np.std(right) == 0:
        raise MetricInputError(
            "No puede calcularse autocorrelación con varianza cero"
        )

    return float(np.corrcoef(left, right)[0, 1])


def lag1_autocorrelation(
    values: Sequence[float] | np.ndarray,
) -> float:
    """Autocorrelación de primer orden."""
    return lag_autocorrelation(values, lag=1)


def rolling_variance(
    values: Sequence[float] | np.ndarray,
    *,
    window: int,
) -> np.ndarray:
    """Varianza móvil de una trayectoria."""
    x = _as_float_array(values, name="values")

    if window < 2 or window > x.size:
        raise MetricInputError(
            "window debe estar entre 2 y el número de observaciones"
        )

    return np.asarray(
        [
            np.var(
                x[i - window + 1:i + 1],
                ddof=1,
            )
            for i in range(window - 1, x.size)
        ],
        dtype=float,
    )


def rolling_autocorrelation(
    values: Sequence[float] | np.ndarray,
    *,
    window: int,
    lag: int = 1,
) -> np.ndarray:
    """Autocorrelación móvil."""
    x = _as_float_array(values, name="values")

    if window < lag + 2:
        raise MetricInputError(
            "window debe ser suficientemente grande para el lag solicitado"
        )

    if window > x.size:
        raise MetricInputError(
            "window no puede superar el número de observaciones"
        )

    result: list[float] = []

    for end in range(window, x.size + 1):
        segment = x[end - window:end]
        result.append(
            lag_autocorrelation(
                segment,
                lag=lag,
            )
        )

    return np.asarray(result, dtype=float)


def variance_trend(
    values: Sequence[float] | np.ndarray,
    *,
    window: int,
) -> float:
    """
    Tendencia de la varianza móvil.

    Valor positivo:
        incremento de variabilidad.

    Valor negativo:
        reducción de variabilidad.
    """
    variance = rolling_variance(
        values,
        window=window,
    )

    if variance.size < 2:
        return 0.0

    return dynamic_slope(variance)


def autocorrelation_trend(
    values: Sequence[float] | np.ndarray,
    *,
    window: int,
    lag: int = 1,
) -> float:
    """Tendencia temporal de la autocorrelación móvil."""
    autocorrelation = rolling_autocorrelation(
        values,
        window=window,
        lag=lag,
    )

    if autocorrelation.size < 2:
        return 0.0

    return dynamic_slope(autocorrelation)


def critical_slowing_down_index(
    values: Sequence[float] | np.ndarray,
    *,
    window: int,
) -> float:
    """
    Indicador compuesto descriptivo de aproximación a pérdida de recuperación.

    Combina tendencia de autocorrelación y tendencia de varianza.

    No demuestra una transición crítica.
    """
    ac_trend = autocorrelation_trend(
        values,
        window=window,
    )

    variance = variance_trend(
        values,
        window=window,
    )

    scale = max(
        abs(ac_trend),
        abs(variance),
        1e-15,
    )

    return float(
        (max(ac_trend, 0.0) + max(variance, 0.0))
        / scale
    )


def recovery_time_from_threshold(
    values: Sequence[float] | np.ndarray,
    *,
    baseline: float,
    threshold: float,
) -> int | None:
    """
    Tiempo de recuperación hasta volver a una banda alrededor del baseline.

    threshold representa una tolerancia absoluta.
    """
    x = _as_float_array(values, name="values")

    baseline = float(baseline)
    threshold = _validate_nonnegative_scalar(
        threshold,
        name="threshold",
    )

    if not np.isfinite(baseline):
        raise MetricInputError(
            "baseline debe ser finito"
        )

    distance = np.abs(x - baseline)

    if np.all(distance <= threshold):
        return 0

    disturbed = np.flatnonzero(distance > threshold)

    if disturbed.size == 0:
        return 0

    start = int(disturbed[0])

    for index in range(start + 1, x.size):
        if np.all(
            distance[index:] <= threshold
        ):
            return index - start

    return None


def recovery_rate_from_trajectory(
    values: Sequence[float] | np.ndarray,
    *,
    baseline: float,
) -> float:
    """
    Velocidad media de recuperación desde el mínimo observado hacia baseline.
    """
    x = _as_float_array(values, name="values")

    baseline = float(baseline)

    if not np.isfinite(baseline):
        raise MetricInputError(
            "baseline debe ser finito"
        )

    minimum_index = int(np.argmin(x))
    minimum_value = float(x[minimum_index])

    if minimum_index >= x.size - 1:
        return 0.0

    remaining_steps = x.size - 1 - minimum_index
    recovered = float(x[-1] - minimum_value)

    if remaining_steps <= 0:
        return 0.0

    return float(recovered / remaining_steps)


def recovery_fraction_from_trajectory(
    values: Sequence[float] | np.ndarray,
    *,
    baseline: float,
) -> float:
    """
    Fracción de recuperación desde el mínimo hasta el valor final.

    0 = ninguna recuperación.
    1 = recuperación completa hasta baseline.
    >1 = sobrepaso del baseline.
    """
    x = _as_float_array(values, name="values")

    baseline = float(baseline)

    if not np.isfinite(baseline):
        raise MetricInputError(
            "baseline debe ser finito"
        )

    minimum = float(np.min(x))
    denominator = baseline - minimum

    if denominator == 0:
        return 0.0

    return float(
        (x[-1] - minimum) / denominator
    )


def flickering_index(
    values: Sequence[float] | np.ndarray,
    *,
    threshold: float,
) -> float:
    """
    Frecuencia normalizada de cruces de un umbral.
    """
    x = _as_float_array(values, name="values")

    threshold = float(threshold)

    if not np.isfinite(threshold):
        raise MetricInputError(
            "threshold debe ser finito"
        )

    if x.size < 2:
        return 0.0

    states = x >= threshold
    crossings = np.sum(states[1:] != states[:-1])

    return float(
        crossings / (x.size - 1)
    )


def threshold_crossing_rate(
    values: Sequence[float] | np.ndarray,
    *,
    threshold: float,
) -> float:
    """Tasa de cruces de un umbral."""
    return flickering_index(
        values,
        threshold=threshold,
    )


def time_near_threshold(
    values: Sequence[float] | np.ndarray,
    *,
    threshold: float,
    tolerance: float,
) -> float:
    """
    Fracción de observaciones próximas a un umbral.
    """
    x = _as_float_array(values, name="values")

    threshold = float(threshold)
    tolerance = _validate_nonnegative_scalar(
        tolerance,
        name="tolerance",
    )

    if not np.isfinite(threshold):
        raise MetricInputError(
            "threshold debe ser finito"
        )

    return float(
        np.mean(
            np.abs(x - threshold) <= tolerance
        )
    )


def threshold_distance(
    value: float,
    threshold: float,
    *,
    scale: float = 1.0,
) -> float:
    """
    Distancia normalizada entre un estado y un umbral.
    """
    value = float(value)
    threshold = float(threshold)
    scale = _validate_positive_scalar(
        scale,
        name="scale",
    )

    if not np.isfinite(value) or not np.isfinite(threshold):
        raise MetricInputError(
            "value y threshold deben ser finitos"
        )

    return float(
        abs(value - threshold) / scale
    )


def threshold_approach_rate(
    values: Sequence[float] | np.ndarray,
    *,
    threshold: float,
) -> float:
    """
    Velocidad media de aproximación al umbral.

    Valores positivos indican aproximación cuando la distancia al umbral
    disminuye.
    """
    x = _as_float_array(values, name="values")
    threshold = float(threshold)

    if not np.isfinite(threshold):
        raise MetricInputError(
            "threshold debe ser finito"
        )

    distance = np.abs(x - threshold)

    if distance.size < 2:
        return 0.0

    return float(
        -dynamic_slope(distance)
    )


def threshold_persistence(
    values: Sequence[float] | np.ndarray,
    *,
    threshold: float,
) -> int:
    """
    Número de observaciones consecutivas recientes por encima del umbral.
    """
    x = _as_float_array(values, name="values")
    threshold = float(threshold)

    if not np.isfinite(threshold):
        raise MetricInputError(
            "threshold debe ser finito"
        )

    count = 0

    for value in reversed(x):
        if value >= threshold:
            count += 1
        else:
            break

    return int(count)


def regime_persistence(
    states: Sequence[int | str],
) -> float:
    """
    Proporción de observaciones pertenecientes al estado modal.
    """
    if not states:
        raise MetricInputError(
            "states no puede estar vacío"
        )

    values = list(states)
    counts = Counter(values)

    return float(
        max(counts.values()) / len(values)
    )


def regime_transition_count(
    states: Sequence[int | str],
) -> int:
    """Número de cambios de régimen observados."""
    if len(states) < 2:
        return 0

    return int(
        sum(
            left != right
            for left, right in zip(
                states[:-1],
                states[1:],
            )
        )
    )


def regime_transition_rate(
    states: Sequence[int | str],
) -> float:
    """Tasa de transición entre estados."""
    if len(states) < 2:
        return 0.0

    return float(
        regime_transition_count(states)
        / (len(states) - 1)
    )


def state_flickering(
    states: Sequence[int | str],
) -> float:
    """
    Medida de alternancia rápida entre estados.
    """
    return regime_transition_rate(states)


def overshoot_ratio(
    peak: float,
    baseline: float,
) -> float:
    """
    Sobrepaso relativo respecto al baseline.
    """
    peak = float(peak)
    baseline = _validate_positive_scalar(
        baseline,
        name="baseline",
    )

    if not np.isfinite(peak):
        raise MetricInputError(
            "peak debe ser finito"
        )

    return float(
        max(peak - baseline, 0.0) / baseline
    )


def recovery_overshoot(
    values: Sequence[float] | np.ndarray,
    *,
    baseline: float,
) -> float:
    """Máximo sobrepaso posterior respecto al baseline."""
    x = _as_float_array(values, name="values")
    baseline = float(baseline)

    if not np.isfinite(baseline):
        raise MetricInputError(
            "baseline debe ser finito"
        )

    return float(
        max(
            np.max(x) - baseline,
            0.0,
        )
    )


def extreme_quantile(
    values: Sequence[float] | np.ndarray,
    *,
    quantile_level: float = 0.95,
) -> float:
    """Cuantil extremo descriptivo."""
    if not 0 < quantile_level < 1:
        raise MetricInputError(
            "quantile_level debe estar entre 0 y 1"
        )

    return float(
        np.quantile(
            _as_float_array(values, name="values"),
            quantile_level,
        )
    )


def exceedance_count(
    values: Sequence[float] | np.ndarray,
    *,
    threshold: float,
) -> int:
    """Número de observaciones que superan un umbral."""
    x = _as_float_array(values, name="values")
    threshold = float(threshold)

    if not np.isfinite(threshold):
        raise MetricInputError(
            "threshold debe ser finito"
        )

    return int(
        np.sum(x >= threshold)
    )


def exceedance_rate(
    values: Sequence[float] | np.ndarray,
    *,
    threshold: float,
) -> float:
    """Proporción de observaciones que superan un umbral."""
    x = _as_float_array(values, name="values")

    if x.size == 0:
        return 0.0

    return float(
        exceedance_count(
            x,
            threshold=threshold,
        ) / x.size
    )


def mean_exceedance(
    values: Sequence[float] | np.ndarray,
    *,
    threshold: float,
) -> float:
    """
    Exceso medio sobre un umbral, condicionado a superar dicho umbral.
    """
    x = _as_float_array(values, name="values")
    threshold = float(threshold)

    if not np.isfinite(threshold):
        raise MetricInputError(
            "threshold debe ser finito"
        )

    excess = x[x >= threshold] - threshold

    if excess.size == 0:
        return 0.0

    return float(np.mean(excess))


def cumulative_exceedance(
    values: Sequence[float] | np.ndarray,
    *,
    threshold: float,
) -> float:
    """Carga acumulada por encima de un umbral."""
    x = _as_float_array(values, name="values")
    threshold = float(threshold)

    if not np.isfinite(threshold):
        raise MetricInputError(
            "threshold debe ser finito"
        )

    return float(
        np.sum(
            np.maximum(
                x - threshold,
                0.0,
            )
        )
    )


def peak_over_threshold_duration(
    values: Sequence[float] | np.ndarray,
    *,
    threshold: float,
) -> int:
    """Duración total por encima de un umbral."""
    return exceedance_count(
        values,
        threshold=threshold,
    )


def compound_shock_burden(
    shock_series: Sequence[Sequence[float]] | np.ndarray,
    *,
    weights: Sequence[float] | np.ndarray | None = None,
) -> float:
    """
    Carga integrada de perturbaciones simultáneas.

    La ponderación debe especificarse explícitamente si las dimensiones
    tienen diferente significado o escala.
    """
    x = np.asarray(shock_series, dtype=float)

    if x.ndim != 2:
        raise MetricInputError(
            "shock_series debe ser una matriz 2D"
        )

    if not np.all(np.isfinite(x)):
        raise MetricInputError(
            "shock_series contiene valores no finitos"
        )

    if np.any(x < 0):
        raise MetricInputError(
            "shock_series debe ser no negativa"
        )

    if weights is None:
        w = np.ones(x.shape[1], dtype=float)
    else:
        w = _as_float_array(
            weights,
            name="weights",
        )

        if w.size != x.shape[1]:
            raise MetricInputError(
                "weights debe tener una entrada por dimensión"
            )

        if np.any(w < 0) or np.sum(w) <= 0:
            raise MetricInputError(
                "weights debe ser no negativo y tener suma positiva"
            )

    w = w / np.sum(w)

    return float(
        np.mean(
            np.sum(x * w, axis=1)
        )
    )


def shock_coincidence_rate(
    shock_matrix: Sequence[Sequence[float]] | np.ndarray,
    *,
    threshold: float,
) -> float:
    """
    Fracción temporal de observaciones en las que al menos dos perturbaciones
    superan simultáneamente el umbral.
    """
    x = np.asarray(shock_matrix, dtype=float)

    if x.ndim != 2:
        raise MetricInputError(
            "shock_matrix debe ser una matriz 2D"
        )

    if x.shape[1] < 2:
        return 0.0

    threshold = float(threshold)

    if not np.isfinite(threshold):
        raise MetricInputError(
            "threshold debe ser finito"
        )

    simultaneous = np.sum(
        x >= threshold,
        axis=1,
    )

    return float(
        np.mean(simultaneous >= 2)
    )


def shock_dimension_breadth(
    shock_matrix: Sequence[Sequence[float]] | np.ndarray,
    *,
    threshold: float,
) -> float:
    """
    Número medio normalizado de dimensiones perturbadas simultáneamente.
    """
    x = np.asarray(shock_matrix, dtype=float)

    if x.ndim != 2 or x.shape[1] == 0:
        raise MetricInputError(
            "shock_matrix debe ser una matriz 2D no vacía"
        )

    threshold = float(threshold)

    if not np.isfinite(threshold):
        raise MetricInputError(
            "threshold debe ser finito"
        )

    return float(
        np.mean(
            np.sum(x >= threshold, axis=1)
            / x.shape[1]
        )
    )


def intershock_interval(
    event_times: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Intervalos entre eventos consecutivos."""
    times = _as_float_array(
        event_times,
        name="event_times",
    )

    if times.size < 2:
        return np.asarray([], dtype=float)

    differences = np.diff(times)

    if np.any(differences <= 0):
        raise MetricInputError(
            "event_times debe estar estrictamente ordenado"
        )

    return differences


def mean_intershock_interval(
    event_times: Sequence[float] | np.ndarray,
) -> float:
    """Intervalo medio entre perturbaciones."""
    intervals = intershock_interval(event_times)

    if intervals.size == 0:
        return 0.0

    return float(np.mean(intervals))


def uncertainty_interval_width(
    lower: float,
    upper: float,
) -> float:
    """Anchura absoluta de un intervalo de incertidumbre."""
    lower = float(lower)
    upper = float(upper)

    if not np.isfinite(lower) or not np.isfinite(upper):
        raise MetricInputError(
            "Los límites deben ser finitos"
        )

    if upper < lower:
        raise MetricInputError(
            "upper debe ser >= lower"
        )

    return float(upper - lower)


def relative_uncertainty_width(
    estimate: float,
    lower: float,
    upper: float,
) -> float:
    """Anchura de incertidumbre relativa al valor estimado."""
    estimate = float(estimate)

    if not np.isfinite(estimate):
        raise MetricInputError(
            "estimate debe ser finito"
        )

    width = uncertainty_interval_width(
        lower,
        upper,
    )

    denominator = abs(estimate)

    if denominator == 0:
        return float("inf") if width > 0 else 0.0

    return float(width / denominator)


def interval_containment(
    values: Sequence[float] | np.ndarray,
    *,
    lower: float,
    upper: float,
) -> float:
    """Proporción de observaciones contenidas en un intervalo."""
    x = _as_float_array(values, name="values")

    if upper < lower:
        raise MetricInputError(
            "upper debe ser >= lower"
        )

    return float(
        np.mean(
            (x >= lower) & (x <= upper)
        )
    )


def bootstrap_mean_interval(
    values: Sequence[float] | np.ndarray,
    *,
    confidence: float = 0.95,
    iterations: int = 2000,
    random_seed: int = 42,
) -> tuple[float, float]:
    """
    Intervalo bootstrap percentil para la media.

    El intervalo cuantifica incertidumbre muestral bajo el procedimiento
    bootstrap; no constituye validación externa ni garantía frecuentista
    universal.
    """
    x = _as_float_array(values, name="values")

    if x.size < 2:
        raise MetricInputError(
            "Se requieren al menos dos observaciones"
        )

    if not 0 < confidence < 1:
        raise MetricInputError(
            "confidence debe estar entre 0 y 1"
        )

    if iterations < 100:
        raise MetricInputError(
            "iterations debe ser >= 100"
        )

    rng = np.random.default_rng(random_seed)

    indices = rng.integers(
        0,
        x.size,
        size=(iterations, x.size),
    )

    bootstrap_means = np.mean(
        x[indices],
        axis=1,
    )

    alpha = 1.0 - confidence

    return (
        float(np.quantile(bootstrap_means, alpha / 2)),
        float(np.quantile(bootstrap_means, 1.0 - alpha / 2)),
    )


def coefficient_of_uncertainty(
    standard_error: float,
    estimate: float,
) -> float:
    """Error estándar relativo al valor estimado."""
    standard_error = _validate_nonnegative_scalar(
        standard_error,
        name="standard_error",
    )
    estimate = float(estimate)

    if not np.isfinite(estimate):
        raise MetricInputError(
            "estimate debe ser finito"
        )

    if estimate == 0:
        return float("inf") if standard_error > 0 else 0.0

    return float(
        standard_error / abs(estimate)
    )


def probability_entropy(
    probabilities: Sequence[float] | np.ndarray,
) -> float:
    """Entropía de una distribución probabilística."""
    return information_entropy(probabilities)


def effective_sample_size(
    weights: Sequence[float] | np.ndarray,
) -> float:
    """
    Tamaño muestral efectivo de un conjunto ponderado.
    """
    w = _as_nonnegative_array(
        weights,
        name="weights",
    )

    total = float(np.sum(w))

    if total <= 0:
        raise MetricInputError(
            "weights debe tener suma positiva"
        )

    normalized = w / total

    denominator = float(
        np.sum(normalized**2)
    )

    if denominator == 0:
        return 0.0

    return float(
        1.0 / denominator
    )


def weighted_missingness_rate(
    observed_weights: Sequence[float] | np.ndarray,
    total_weights: Sequence[float] | np.ndarray,
) -> float:
    """
    Tasa de ausencia ponderada por importancia de observación.
    """
    observed = _as_nonnegative_array(
        observed_weights,
        name="observed_weights",
    )
    total = _as_nonnegative_array(
        total_weights,
        name="total_weights",
    )

    _validate_same_length(observed, total)

    denominator = float(np.sum(total))

    if denominator <= 0:
        raise MetricInputError(
            "total_weights debe tener suma positiva"
        )

    if np.any(observed > total):
        raise MetricInputError(
            "observed_weights no puede superar total_weights"
        )

    return float(
        1.0 - np.sum(observed) / denominator
    )


# =============================================================================
# MÉTRICAS ESPACIALES
# =============================================================================


def spatial_weighted_mean(
    values: Sequence[float] | np.ndarray,
    weights: Sequence[float] | np.ndarray,
) -> float:
    """Media espacial ponderada."""
    x = _as_float_array(values, name="values")
    w = _as_nonnegative_array(
        weights,
        name="weights",
    )

    _validate_same_length(x, w)

    total = float(np.sum(w))

    if total <= 0:
        raise MetricInputError(
            "weights debe tener suma positiva"
        )

    return float(
        np.sum(x * w) / total
    )


def spatial_dispersion(
    values: Sequence[float] | np.ndarray,
    weights: Sequence[float] | np.ndarray,
) -> float:
    """Dispersión espacial ponderada."""
    x = _as_float_array(values, name="values")
    w = _as_nonnegative_array(
        weights,
        name="weights",
    )

    _validate_same_length(x, w)

    total = float(np.sum(w))

    if total <= 0:
        raise MetricInputError(
            "weights debe tener suma positiva"
        )

    mean_value = np.sum(x * w) / total

    return float(
        np.sum(w * (x - mean_value) ** 2) / total
    )


def morans_i(
    values: Sequence[float] | np.ndarray,
    spatial_weights: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    I de Moran.

    La matriz de pesos espaciales debe estar definida previamente y representar
    explícitamente la estructura de vecindad utilizada.
    """
    x = _as_float_array(values, name="values")
    w = np.asarray(
        spatial_weights,
        dtype=float,
    )

    if w.ndim != 2 or w.shape[0] != w.shape[1]:
        raise MetricInputError(
            "spatial_weights debe ser una matriz cuadrada"
        )

    if w.shape[0] != x.size:
        raise MetricInputError(
            "spatial_weights debe corresponder a values"
        )

    if not np.all(np.isfinite(w)):
        raise MetricInputError(
            "spatial_weights contiene valores no finitos"
        )

    centered = x - np.mean(x)
    denominator = float(
        np.sum(centered**2)
    )

    if denominator == 0:
        raise MetricInputError(
            "values no puede tener varianza cero"
        )

    weight_sum = float(np.sum(w))

    if weight_sum == 0:
        raise MetricInputError(
            "La matriz espacial debe contener pesos"
        )

    numerator = float(
        np.sum(
            w * np.outer(centered, centered)
        )
    )

    n = x.size

    return float(
        (n / weight_sum)
        * (numerator / denominator)
    )


def gearys_c(
    values: Sequence[float] | np.ndarray,
    spatial_weights: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """C de Geary."""
    x = _as_float_array(values, name="values")
    w = np.asarray(
        spatial_weights,
        dtype=float,
    )

    if w.ndim != 2 or w.shape[0] != w.shape[1]:
        raise MetricInputError(
            "spatial_weights debe ser una matriz cuadrada"
        )

    if w.shape[0] != x.size:
        raise MetricInputError(
            "spatial_weights debe corresponder a values"
        )

    weight_sum = float(np.sum(w))

    if weight_sum == 0:
        raise MetricInputError(
            "La matriz espacial debe contener pesos"
        )

    centered = x - np.mean(x)
    denominator = float(
        np.sum(centered**2)
    )

    if denominator == 0:
        raise MetricInputError(
            "values no puede tener varianza cero"
        )

    numerator = float(
        np.sum(
            w
            * (
                x[:, None] - x[None, :]
            ) ** 2
        )
    )

    n = x.size

    return float(
        ((n - 1) / (2.0 * weight_sum))
        * (numerator / denominator)
    )


def spatial_autocorrelation_strength(
    values: Sequence[float] | np.ndarray,
    spatial_weights: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """Magnitud absoluta de la autocorrelación espacial."""
    return float(
        abs(
            morans_i(
                values,
                spatial_weights,
            )
        )
    )


def spatial_concentration(
    values: Sequence[float] | np.ndarray,
) -> float:
    """
    Concentración espacial de una cantidad no negativa.
    """
    return distribution_concentration(values)


def spatial_inequality(
    values: Sequence[float] | np.ndarray,
) -> float:
    """Desigualdad espacial mediante Gini."""
    return gini_coefficient(values)


def space_time_concentration(
    values: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    Concentración conjunta espacio-temporal.

    La matriz representa tiempo × unidades espaciales.
    """
    x = _as_nonnegative_array(
        values,
        name="values",
    )

    if x.ndim != 2:
        raise MetricInputError(
            "values debe ser una matriz 2D"
        )

    flattened = x.reshape(-1)

    return distribution_concentration(flattened)


def space_time_burstiness(
    values: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    Burstiness de una señal espacio-temporal agregada.
    """
    x = _as_nonnegative_array(
        values,
        name="values",
    )

    if x.ndim != 2:
        raise MetricInputError(
            "values debe ser una matriz 2D"
        )

    return burstiness_index(
        np.sum(x, axis=1)
    )


# =============================================================================
# MÉTRICAS INTEGRATIVAS BIOPSICOSOCIALES Y DE SALUD
# =============================================================================


def multidimensional_health_burden(
    dimensions: Sequence[float] | np.ndarray,
    weights: Sequence[float] | np.ndarray,
) -> float:
    """
    Carga multidimensional de salud.

    Los pesos deben proceder de un protocolo explícito; no se asume que todas
    las dimensiones tengan igual importancia.
    """
    x = _as_nonnegative_array(
        dimensions,
        name="dimensions",
    )
    w = _as_nonnegative_array(
        weights,
        name="weights",
    )

    _validate_same_length(x, w)

    return weighted_systemic_load(
        x,
        w,
    )


def biopsychosocial_load(
    biological_load: float,
    psychological_load: float,
    social_load: float,
    *,
    weights: Sequence[float] | np.ndarray | None = None,
) -> float:
    """
    Carga biopsicosocial integrada.

    No representa un diagnóstico ni un score clínico universal.
    """
    values = np.asarray(
        [
            biological_load,
            psychological_load,
            social_load,
        ],
        dtype=float,
    )

    if np.any(values < 0) or not np.all(np.isfinite(values)):
        raise MetricInputError(
            "Las cargas biopsicosociales deben ser finitas y no negativas"
        )

    if weights is None:
        weights_array = np.ones(3, dtype=float)
    else:
        weights_array = _as_nonnegative_array(
            weights,
            name="weights",
        )

    _validate_same_length(
        values,
        weights_array,
    )

    return weighted_systemic_load(
        values,
        weights_array,
    )


def biopsychosocial_reserve(
    biological_reserve: float,
    psychological_reserve: float,
    social_reserve: float,
    *,
    weights: Sequence[float] | np.ndarray | None = None,
) -> float:
    """Reserva adaptativa biopsicosocial integrada."""
    values = np.asarray(
        [
            biological_reserve,
            psychological_reserve,
            social_reserve,
        ],
        dtype=float,
    )

    if np.any(values < 0) or not np.all(np.isfinite(values)):
        raise MetricInputError(
            "Las reservas deben ser finitas y no negativas"
        )

    if weights is None:
        weights_array = np.ones(3, dtype=float)
    else:
        weights_array = _as_nonnegative_array(
            weights,
            name="weights",
        )

    return weighted_systemic_load(
        values,
        weights_array,
    )


def sleep_stress_interaction(
    sleep_impairment: float,
    stress_load: float,
) -> float:
    """Producto normalizado de deterioro del sueño y carga de estrés."""
    sleep = _validate_nonnegative_scalar(
        sleep_impairment,
        name="sleep_impairment",
    )
    stress = _validate_nonnegative_scalar(
        stress_load,
        name="stress_load",
    )

    return float(
        sleep * stress
    )


def trauma_sleep_interaction(
    trauma_load: float,
    sleep_impairment: float,
) -> float:
    """Interacción descriptiva entre carga traumática y deterioro del sueño."""
    return sleep_stress_interaction(
        trauma_load,
        sleep_impairment,
    )


def cumulative_health_burden(
    values: Sequence[float] | np.ndarray,
    *,
    dt: float = 1.0,
) -> float:
    """Carga sanitaria acumulada mediante integración trapezoidal."""
    x = _as_nonnegative_array(
        values,
        name="values",
    )

    if dt <= 0:
        raise MetricInputError(
            "dt debe ser positivo"
        )

    if x.size < 2:
        return 0.0

    return float(
        np.trapezoid(x, dx=dt)
    )


def functional_deterioration(
    baseline: float,
    current: float,
) -> float:
    """Deterioro funcional relativo respecto al baseline."""
    baseline = _validate_positive_scalar(
        baseline,
        name="baseline",
    )
    current = _validate_nonnegative_scalar(
        current,
        name="current",
    )

    return float(
        (baseline - current) / baseline
    )


def functional_recovery(
    baseline: float,
    nadir: float,
    current: float,
) -> float:
    """
    Recuperación funcional desde el nadir hacia baseline.
    """
    baseline = float(baseline)
    nadir = float(nadir)
    current = float(current)

    if not all(
        np.isfinite(value)
        for value in (baseline, nadir, current)
    ):
        raise MetricInputError(
            "Los valores deben ser finitos"
        )

    denominator = baseline - nadir

    if denominator == 0:
        return 0.0

    return float(
        (current - nadir) / denominator
    )


def allostatic_load_trajectory(
    values: Sequence[float] | np.ndarray,
) -> dict[str, float]:
    """
    Resumen longitudinal de una trayectoria de carga alostática.

    No modifica la definición clínica de allostatic load.
    """
    x = _as_float_array(
        values,
        name="values",
    )

    if np.any(x < 0):
        raise MetricInputError(
            "allostatic load no puede ser negativa"
        )

    return {
        "mean": float(np.mean(x)),
        "maximum": float(np.max(x)),
        "minimum": float(np.min(x)),
        "slope": (
            float(dynamic_slope(x))
            if x.size > 1
            else 0.0
        ),
        "acceleration": (
            float(dynamic_acceleration(x))
            if x.size > 2
            else 0.0
        ),
        "cumulative_burden": float(
            np.sum(x)
        ),
    }


def wellbeing_trajectory_slope(
    values: Sequence[float] | np.ndarray,
) -> float:
    """Pendiente longitudinal de bienestar."""
    return dynamic_slope(values)


def stress_trajectory_slope(
    values: Sequence[float] | np.ndarray,
) -> float:
    """Pendiente longitudinal de estrés."""
    return dynamic_slope(values)


def recovery_reserve_ratio(
    current_reserve: float,
    required_reserve: float,
) -> float:
    """Reserva disponible respecto a la reserva requerida."""
    current = _validate_nonnegative_scalar(
        current_reserve,
        name="current_reserve",
    )
    required = _validate_positive_scalar(
        required_reserve,
        name="required_reserve",
    )

    return float(
        current / required
    )


# =============================================================================
# MÉTRICAS INTEGRATIVAS DE GESTIÓN
# =============================================================================


def detection_decision_action_latency(
    detection_time: float,
    decision_time: float,
    action_time: float,
) -> tuple[float, float, float]:
    """
    Descompone el ciclo operativo en:
        detección → decisión
        decisión → acción
        detección → acción
    """
    detection_to_decision = decision_latency(
        detection_time,
        decision_time,
    )

    decision_to_action = intervention_latency(
        decision_time,
        action_time,
    )

    detection_to_action = response_time(
        detection_time,
        action_time,
    )

    return (
        detection_to_decision,
        decision_to_action,
        detection_to_action,
    )


def response_capacity_ratio(
    completed_actions: float,
    required_actions: float,
) -> float:
    """Capacidad efectiva de respuesta respecto a necesidad."""
    completed = _validate_nonnegative_scalar(
        completed_actions,
        name="completed_actions",
    )
    required = _validate_positive_scalar(
        required_actions,
        name="required_actions",
    )

    return float(
        completed / required
    )


def coordination_coverage(
    coordinated_units: float,
    active_units: float,
) -> float:
    """Proporción de unidades activas coordinadas."""
    coordinated = _validate_nonnegative_scalar(
        coordinated_units,
        name="coordinated_units",
    )
    active = _validate_positive_scalar(
        active_units,
        name="active_units",
    )

    if coordinated > active:
        raise MetricInputError(
            "coordinated_units no puede superar active_units"
        )

    return float(
        coordinated / active
    )


def coordination_redundancy(
    active_channels: float,
    critical_channels: float,
) -> float:
    """
    Canales activos por canal considerado crítico.
    """
    active = _validate_nonnegative_scalar(
        active_channels,
        name="active_channels",
    )
    critical = _validate_positive_scalar(
        critical_channels,
        name="critical_channels",
    )

    return float(
        active / critical
    )


def response_debt(
    required_response: float,
    delivered_response: float,
) -> float:
    """Déficit acumulado de respuesta."""
    required = _validate_nonnegative_scalar(
        required_response,
        name="required_response",
    )
    delivered = _validate_nonnegative_scalar(
        delivered_response,
        name="delivered_response",
    )

    return float(
        max(required - delivered, 0.0)
    )


def sustainable_throughput(
    completed: float,
    duration: float,
) -> float:
    """Rendimiento sostenible durante una ventana temporal."""
    return throughput_rate(
        completed,
        duration,
    )


def saturation_time(
    utilization_series: Sequence[float] | np.ndarray,
    *,
    threshold: float = 1.0,
) -> int | None:
    """Primera observación en la que la utilización alcanza saturación."""
    x = _as_float_array(
        utilization_series,
        name="utilization_series",
    )

    threshold = float(threshold)

    if not np.isfinite(threshold):
        raise MetricInputError(
            "threshold debe ser finito"
        )

    indices = np.flatnonzero(x >= threshold)

    if indices.size == 0:
        return None

    return int(indices[0])


def desaturation_time(
    utilization_series: Sequence[float] | np.ndarray,
    *,
    threshold: float = 1.0,
) -> int | None:
    """Primera observación posterior a saturación por debajo del umbral."""
    x = _as_float_array(
        utilization_series,
        name="utilization_series",
    )

    threshold = float(threshold)

    if not np.isfinite(threshold):
        raise MetricInputError(
            "threshold debe ser finito"
        )

    saturated = np.flatnonzero(x >= threshold)

    if saturated.size == 0:
        return None

    start = int(saturated[0])

    for index in range(start + 1, x.size):
        if x[index] < threshold:
            return index - start

    return None


def capacity_utilization_series(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Utilización temporal demanda/capacidad."""
    d = _as_nonnegative_array(
        demand,
        name="demand",
    )
    c = _as_nonnegative_array(
        capacity,
        name="capacity",
    )

    _validate_same_length(d, c)

    if np.any(c <= 0):
        raise MetricInputError(
            "capacity debe ser estrictamente positiva"
        )

    return d / c


def peak_utilization(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
) -> float:
    """Máxima utilización observada."""
    return float(
        np.max(
            capacity_utilization_series(
                demand,
                capacity,
            )
        )
    )


def utilization_variability(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
) -> float:
    """Variabilidad de la utilización temporal."""
    utilization = capacity_utilization_series(
        demand,
        capacity,
    )

    return float(
        np.std(
            utilization,
            ddof=1,
        )
    ) if utilization.size > 1 else 0.0


# =============================================================================
# REGISTRO DE LA ITERACIÓN
# =============================================================================


TRANSITION_EXTREME_SPATIOTEMPORAL_METRICS: Final[tuple[str, ...]] = (
    "lag_autocorrelation",
    "lag1_autocorrelation",
    "rolling_variance",
    "rolling_autocorrelation",
    "variance_trend",
    "autocorrelation_trend",
    "critical_slowing_down_index",
    "recovery_time_from_threshold",
    "recovery_rate_from_trajectory",
    "recovery_fraction_from_trajectory",
    "flickering_index",
    "threshold_crossing_rate",
    "time_near_threshold",
    "threshold_distance",
    "threshold_approach_rate",
    "threshold_persistence",
    "regime_persistence",
    "regime_transition_count",
    "regime_transition_rate",
    "state_flickering",
    "overshoot_ratio",
    "recovery_overshoot",
    "extreme_quantile",
    "exceedance_count",
    "exceedance_rate",
    "mean_exceedance",
    "cumulative_exceedance",
    "peak_over_threshold_duration",
    "compound_shock_burden",
    "shock_coincidence_rate",
    "shock_dimension_breadth",
    "intershock_interval",
    "mean_intershock_interval",
    "uncertainty_interval_width",
    "relative_uncertainty_width",
    "interval_containment",
    "bootstrap_mean_interval",
    "coefficient_of_uncertainty",
    "probability_entropy",
    "effective_sample_size",
    "weighted_missingness_rate",
    "spatial_weighted_mean",
    "spatial_dispersion",
    "morans_i",
    "gearys_c",
    "spatial_autocorrelation_strength",
    "spatial_concentration",
    "spatial_inequality",
    "space_time_concentration",
    "space_time_burstiness",
    "multidimensional_health_burden",
    "biopsychosocial_load",
    "biopsychosocial_reserve",
    "sleep_stress_interaction",
    "trauma_sleep_interaction",
    "cumulative_health_burden",
    "functional_deterioration",
    "functional_recovery",
    "allostatic_load_trajectory",
    "wellbeing_trajectory_slope",
    "stress_trajectory_slope",
    "recovery_reserve_ratio",
    "detection_decision_action_latency",
    "response_capacity_ratio",
    "coordination_coverage",
    "coordination_redundancy",
    "response_debt",
    "sustainable_throughput",
    "saturation_time",
    "desaturation_time",
    "capacity_utilization_series",
    "peak_utilization",
    "utilization_variability",
)


TRANSITION_EXTREME_SPATIOTEMPORAL_INVARIANTS: Final[tuple[str, ...]] = (
    "El aumento de autocorrelación o varianza es una señal compatible con determinados procesos de desaceleración crítica, no una prueba de transición crítica.",
    "Un early warning debe conservar horizonte temporal, ventana, umbral y método de cálculo.",
    "La proximidad a un umbral sólo es interpretable si el umbral tiene significado independiente del propio indicador.",
    "Un cruce de umbral no demuestra que exista un cambio de régimen.",
    "Flickering y persistencia describen la trayectoria observada y no demuestran mecanismos subyacentes.",
    "Las métricas de extremos dependen del periodo de observación y del régimen estadístico.",
    "Un exceso sobre un umbral no equivale a un evento clínico, social o estratégico.",
    "Los shocks coincidentes no demuestran que exista una causa común.",
    "La incertidumbre debe conservarse junto con la estimación y no ocultarse mediante un único valor.",
    "Un intervalo bootstrap cuantifica incertidumbre muestral bajo sus supuestos; no sustituye validación externa.",
    "La autocorrelación espacial depende de la matriz de pesos espaciales elegida.",
    "Moran's I y Geary's C describen estructura espacial y no identifican causalidad espacial.",
    "La concentración espacial puede reflejar estructura poblacional, denominadores, exposición o medición.",
    "Una métrica espacio-temporal requiere conservar simultáneamente escala temporal y unidad espacial.",
    "Una carga biopsicosocial integrada no constituye un diagnóstico ni un estándar clínico universal.",
    "La integración de dimensiones clínicas requiere especificar pesos, escalas, población y finalidad.",
    "Una trayectoria de allostatic load no debe interpretarse sin conocer sus componentes y umbrales.",
    "Una intervención posterior a un cambio temporal no demuestra por sí sola efecto causal.",
    "La saturación observada depende de cómo se haya definido y medido la capacidad.",
    "La capacidad nominal, efectiva, accesible y sostenible son magnitudes distintas.",
    "La deuda de respuesta describe déficit operativo y no atribuye responsabilidad causal.",
    "La utilización agregada puede ocultar cuellos de botella internos.",
)


__all__.extend(
    TRANSITION_EXTREME_SPATIOTEMPORAL_METRICS
)
# =============================================================================
# CeutIA — MÉTRICAS DE INTERACCIÓN, PROPAGACIÓN, INFORMACIÓN Y ESTRUCTURA
# =============================================================================
#
# Estas métricas describen relaciones entre dimensiones, subsistemas,
# observaciones, fuentes y distribuciones.
#
# No establecen causalidad por sí mismas.
# No convierten correlación en mecanismo causal.
# No generan peligrosidad individual ni clasificación de personas o grupos.
# =============================================================================


def covariance_matrix(
    values: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """
    Matriz de covarianzas entre dimensiones.

    Entrada:
        matriz con forma (observaciones, dimensiones).
    """
    x = np.asarray(values, dtype=float)

    if x.ndim != 2:
        raise MetricInputError("values debe ser una matriz 2D")

    if x.shape[0] < 2:
        raise MetricInputError(
            "Se requieren al menos dos observaciones"
        )

    if not np.all(np.isfinite(x)):
        raise MetricInputError("values contiene valores no finitos")

    return np.asarray(np.cov(x, rowvar=False, ddof=1), dtype=float)


def correlation_matrix(
    values: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """Matriz de correlación entre dimensiones."""
    covariance = covariance_matrix(values)

    standard_deviations = np.sqrt(np.diag(covariance))

    if np.any(standard_deviations <= 0):
        raise MetricInputError(
            "Todas las dimensiones deben presentar variabilidad positiva"
        )

    return covariance / np.outer(
        standard_deviations,
        standard_deviations,
    )


def cross_correlation(
    x: Sequence[float] | np.ndarray,
    y: Sequence[float] | np.ndarray,
    *,
    lag: int = 0,
) -> float:
    """
    Correlación entre dos trayectorias con desfase temporal.

    lag > 0:
        x_t frente a y_(t-lag)

    lag < 0:
        x_(t-lag) frente a y_t
    """
    a = _as_float_array(x, name="x")
    b = _as_float_array(y, name="y")
    _validate_same_length(a, b)

    if abs(lag) >= a.size:
        raise MetricInputError(
            "El lag debe ser menor que el número de observaciones"
        )

    if lag > 0:
        a = a[lag:]
        b = b[:-lag]
    elif lag < 0:
        a = a[:lag]
        b = b[-lag:]

    if np.std(a) == 0 or np.std(b) == 0:
        raise MetricInputError(
            "No puede calcularse correlación con varianza cero"
        )

    return float(np.corrcoef(a, b)[0, 1])


def maximum_lagged_correlation(
    x: Sequence[float] | np.ndarray,
    y: Sequence[float] | np.ndarray,
    *,
    max_lag: int,
) -> tuple[int, float]:
    """
    Encuentra el lag con mayor correlación absoluta.

    Devuelve:
        (lag, correlación)
    """
    if max_lag < 0:
        raise MetricInputError("max_lag debe ser >= 0")

    a = _as_float_array(x, name="x")
    b = _as_float_array(y, name="y")
    _validate_same_length(a, b)

    if max_lag >= a.size:
        max_lag = a.size - 1

    candidates: list[tuple[int, float]] = []

    for lag in range(-max_lag, max_lag + 1):
        try:
            value = cross_correlation(a, b, lag=lag)
        except MetricInputError:
            continue

        candidates.append((lag, value))

    if not candidates:
        raise MetricInputError(
            "No existe ningún desfase con variabilidad suficiente"
        )

    return max(
        candidates,
        key=lambda item: abs(item[1]),
    )


def coupling_strength(
    x: Sequence[float] | np.ndarray,
    y: Sequence[float] | np.ndarray,
) -> float:
    """
    Magnitud absoluta del acoplamiento lineal entre dos trayectorias.
    """
    return float(abs(cross_correlation(x, y)))


def coupling_change(
    x: Sequence[float] | np.ndarray,
    y: Sequence[float] | np.ndarray,
    *,
    split: int,
) -> float:
    """
    Cambio del acoplamiento entre dos periodos.

    Permite detectar aumento o disminución de dependencia estadística.
    """
    a = _as_float_array(x, name="x")
    b = _as_float_array(y, name="y")
    _validate_same_length(a, b)

    if split <= 1 or split >= a.size - 1:
        raise MetricInputError(
            "split debe dejar al menos dos observaciones en cada periodo"
        )

    first = coupling_strength(a[:split], b[:split])
    second = coupling_strength(a[split:], b[split:])

    return float(second - first)


def decoupling_index(
    x: Sequence[float] | np.ndarray,
    y: Sequence[float] | np.ndarray,
    *,
    baseline_split: int,
) -> float:
    """
    Disminución absoluta del acoplamiento respecto al periodo basal.
    """
    change = coupling_change(
        x,
        y,
        split=baseline_split,
    )

    return float(max(-change, 0.0))


def synchronization_index(
    values: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    Sincronización media entre dimensiones.

    Se calcula sobre correlaciones absolutas entre trayectorias.
    """
    x = np.asarray(values, dtype=float)

    if x.ndim != 2:
        raise MetricInputError("values debe ser una matriz 2D")

    if x.shape[1] < 2:
        raise MetricInputError(
            "Se requieren al menos dos dimensiones"
        )

    correlations = correlation_matrix(x)

    upper = correlations[
        np.triu_indices_from(correlations, k=1)
    ]

    return float(np.mean(np.abs(upper)))


def asynchrony_index(
    values: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """Complemento de la sincronización media."""
    return float(1.0 - synchronization_index(values))


def interaction_matrix(
    values: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """
    Matriz de interacción estadística de primer orden.

    Es una representación descriptiva, no una matriz causal.
    """
    return correlation_matrix(values)


def interaction_density(
    interactions: Sequence[Sequence[float]] | np.ndarray,
    *,
    threshold: float,
) -> float:
    """
    Densidad de relaciones cuya magnitud supera un umbral.
    """
    matrix = np.asarray(interactions, dtype=float)

    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise MetricInputError(
            "interactions debe ser una matriz cuadrada"
        )

    if threshold < 0:
        raise MetricInputError("threshold debe ser >= 0")

    mask = ~np.eye(matrix.shape[0], dtype=bool)

    if not np.any(mask):
        return 0.0

    return float(
        np.mean(np.abs(matrix[mask]) >= threshold)
    )


def interaction_entropy(
    interactions: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    Entropía normalizada de la distribución de magnitudes de interacción.
    """
    matrix = np.asarray(interactions, dtype=float)

    if matrix.ndim != 2 or matrix.shape[0] != matrix.shape[1]:
        raise MetricInputError(
            "interactions debe ser una matriz cuadrada"
        )

    mask = ~np.eye(matrix.shape[0], dtype=bool)
    values = np.abs(matrix[mask])

    total = float(np.sum(values))

    if total <= 0:
        return 0.0

    probabilities = values / total
    probabilities = probabilities[probabilities > 0]

    entropy = -float(
        np.sum(probabilities * np.log(probabilities))
    )

    maximum = float(np.log(len(values)))

    if maximum <= 0:
        return 0.0

    return float(entropy / maximum)


def redundancy_index(
    capacities: Sequence[float] | np.ndarray,
) -> float:
    """
    Redundancia normalizada de capacidad.

    Mide cuánto se distribuye la capacidad entre dimensiones,
    evitando confundir concentración con capacidad total.
    """
    x = _as_nonnegative_array(
        capacities,
        name="capacities",
    )

    if x.size < 2:
        return 0.0

    total = float(np.sum(x))

    if total <= 0:
        return 0.0

    probabilities = x / total

    concentration = float(np.sum(probabilities**2))

    return float(
        np.clip(
            1.0 - concentration,
            0.0,
            1.0,
        )
    )


def substitutability_index(
    capacities: Sequence[float] | np.ndarray,
) -> float:
    """
    Índice descriptivo de distribución de capacidad.

    No demuestra sustituibilidad funcional real; esa propiedad requiere
    especificar qué recursos pueden reemplazarse entre sí.
    """
    x = _as_nonnegative_array(
        capacities,
        name="capacities",
    )

    if x.size < 2:
        return 0.0

    positive = x[x > 0]

    if positive.size == 0:
        return 0.0

    minimum = float(np.min(positive))
    maximum = float(np.max(positive))

    if maximum == 0:
        return 0.0

    return float(minimum / maximum)


def propagation_ratio(
    source_change: float,
    target_change: float,
) -> float:
    """
    Relación de magnitud entre cambio observado en origen y destino.
    """
    source = abs(float(source_change))
    target = abs(float(target_change))

    if not np.isfinite(source) or not np.isfinite(target):
        raise MetricInputError(
            "Los cambios deben ser finitos"
        )

    if source == 0:
        if target == 0:
            return 0.0
        return float("inf")

    return float(target / source)


def amplification_gain(
    baseline: float,
    output: float,
) -> float:
    """Ganancia relativa entre una perturbación de entrada y su salida."""
    baseline = _validate_positive_scalar(
        baseline,
        name="baseline",
    )
    output = _validate_nonnegative_scalar(
        output,
        name="output",
    )

    return float(output / baseline)


def damping_ratio(
    input_magnitude: float,
    output_magnitude: float,
) -> float:
    """
    Atenuación de una señal entre origen y destino.

    1 = misma magnitud.
    <1 = atenuación.
    >1 = amplificación.
    """
    input_value = _validate_positive_scalar(
        input_magnitude,
        name="input_magnitude",
    )
    output_value = _validate_nonnegative_scalar(
        output_magnitude,
        name="output_magnitude",
    )

    return float(output_value / input_value)


def cascade_depth(
    graph: object,
    source: object,
) -> int:
    """
    Profundidad máxima alcanzable desde un nodo origen en una red dirigida.

    Requiere un objeto NetworkX compatible con descendants/path_length.
    """
    try:
        import networkx as nx
    except ImportError as exc:
        raise MetricError(
            "NetworkX es necesario para cascade_depth"
        ) from exc

    if not isinstance(graph, nx.DiGraph):
        raise MetricInputError(
            "graph debe ser un networkx.DiGraph"
        )

    if source not in graph:
        raise MetricInputError(
            "source no existe en graph"
        )

    lengths = nx.single_source_shortest_path_length(
        graph,
        source,
    )

    return int(max(lengths.values(), default=0))


def network_vulnerability(
    graph: object,
) -> float:
    """
    Vulnerabilidad estructural aproximada de una red.

    Utiliza la concentración de centralidad de grado.
    """
    try:
        import networkx as nx
    except ImportError as exc:
        raise MetricError(
            "NetworkX es necesario para network_vulnerability"
        ) from exc

    if len(graph) == 0:
        return 0.0

    centralities = np.asarray(
        list(nx.degree_centrality(graph).values()),
        dtype=float,
    )

    if centralities.size == 0:
        return 0.0

    return float(
        np.max(centralities)
    )


def critical_node_dependence(
    graph: object,
    *,
    node: object,
) -> float:
    """
    Dependencia estructural relativa respecto a un nodo concreto.

    La eliminación hipotética del nodo no implica por sí misma que el sistema
    real vaya a fallar.
    """
    try:
        import networkx as nx
    except ImportError as exc:
        raise MetricError(
            "NetworkX es necesario para critical_node_dependence"
        ) from exc

    if node not in graph:
        raise MetricInputError(
            "node no existe en graph"
        )

    original = nx.node_connectivity(graph) if len(graph) > 1 else 0

    reduced = graph.copy()
    reduced.remove_node(node)

    if len(reduced) <= 1:
        remaining = 0
    else:
        try:
            remaining = nx.node_connectivity(reduced)
        except nx.NetworkXError:
            remaining = 0

    if original <= 0:
        return 0.0

    return float(
        np.clip(
            (original - remaining) / original,
            0.0,
            1.0,
        )
    )


def source_concentration_index(
    source_counts: Sequence[float] | np.ndarray,
) -> float:
    """
    Concentración de procedencia de información mediante HHI normalizado.
    """
    x = _as_nonnegative_array(
        source_counts,
        name="source_counts",
    )

    total = float(np.sum(x))

    if total <= 0:
        return 0.0

    shares = x / total
    hhi = float(np.sum(shares**2))

    if x.size <= 1:
        return 1.0

    minimum = 1.0 / x.size

    return float(
        np.clip(
            (hhi - minimum) / (1.0 - minimum),
            0.0,
            1.0,
        )
    )


def source_diversity_entropy(
    source_counts: Sequence[float] | np.ndarray,
) -> float:
    """Diversidad normalizada de fuentes."""
    x = _as_nonnegative_array(
        source_counts,
        name="source_counts",
    )

    total = float(np.sum(x))

    if total <= 0:
        return 0.0

    probabilities = x / total
    probabilities = probabilities[probabilities > 0]

    if probabilities.size <= 1:
        return 0.0

    entropy = -float(
        np.sum(probabilities * np.log(probabilities))
    )

    return float(
        entropy / np.log(x.size)
    )


def information_entropy(
    probabilities: Sequence[float] | np.ndarray,
) -> float:
    """Entropía de Shannon normalizada."""
    p = _as_nonnegative_array(
        probabilities,
        name="probabilities",
    )

    total = float(np.sum(p))

    if total <= 0:
        raise MetricInputError(
            "La suma de probabilities debe ser > 0"
        )

    p = p / total
    p = p[p > 0]

    if p.size <= 1:
        return 0.0

    entropy = -float(
        np.sum(p * np.log(p))
    )

    return float(
        entropy / np.log(len(p))
    )


def information_surprise(
    probability: float,
) -> float:
    """
    Contenido informativo de una observación:

        I(x) = -log(P(x))

    Valores mayores corresponden a observaciones menos probables bajo el
    modelo probabilístico suministrado.
    """
    probability = float(probability)

    if not np.isfinite(probability):
        raise MetricInputError(
            "probability debe ser finita"
        )

    if probability <= 0 or probability > 1:
        raise MetricInputError(
            "probability debe estar en (0, 1]"
        )

    return float(-np.log(probability))


def information_gain(
    prior_entropy: float,
    posterior_entropy: float,
) -> float:
    """
    Ganancia de información aproximada como reducción de entropía.
    """
    prior = _validate_nonnegative_scalar(
        prior_entropy,
        name="prior_entropy",
    )
    posterior = _validate_nonnegative_scalar(
        posterior_entropy,
        name="posterior_entropy",
    )

    return float(prior - posterior)


def observation_coverage(
    observed: float,
    expected: float,
) -> float:
    """Cobertura observacional respecto al universo esperado."""
    observed = _validate_nonnegative_scalar(
        observed,
        name="observed",
    )
    expected = _validate_positive_scalar(
        expected,
        name="expected",
    )

    return float(observed / expected)


def observation_latency(
    observation_time: float,
    availability_time: float,
) -> float:
    """Latencia entre ocurrencia/observación y disponibilidad."""
    observation_time = float(observation_time)
    availability_time = float(availability_time)

    if not np.isfinite(observation_time) or not np.isfinite(
        availability_time
    ):
        raise MetricInputError(
            "Los tiempos deben ser finitos"
        )

    latency = availability_time - observation_time

    if latency < 0:
        raise MetricInputError(
            "availability_time no puede preceder a observation_time"
        )

    return float(latency)


def information_loss_fraction(
    expected_information: float,
    observed_information: float,
) -> float:
    """Fracción de información no observada respecto al total esperado."""
    expected = _validate_positive_scalar(
        expected_information,
        name="expected_information",
    )
    observed = _validate_nonnegative_scalar(
        observed_information,
        name="observed_information",
    )

    return float(
        np.clip(
            1.0 - observed / expected,
            0.0,
            1.0,
        )
    )


def contradictory_observation_rate(
    contradictions: float,
    total_observations: float,
) -> float:
    """Proporción de observaciones clasificadas como contradictorias."""
    contradictions = _validate_nonnegative_scalar(
        contradictions,
        name="contradictions",
    )
    total = _validate_positive_scalar(
        total_observations,
        name="total_observations",
    )

    if contradictions > total:
        raise MetricInputError(
            "contradictions no puede superar total_observations"
        )

    return float(contradictions / total)


def gini_coefficient(
    values: Sequence[float] | np.ndarray,
) -> float:
    """Coeficiente de Gini para distribuciones no negativas."""
    x = np.sort(
        _as_nonnegative_array(values, name="values")
    )

    total = float(np.sum(x))

    if total <= 0:
        return 0.0

    n = x.size
    index = np.arange(1, n + 1)

    return float(
        (
            2.0 * np.sum(index * x)
            - (n + 1) * total
        )
        / (n * total)
    )


def theil_index(
    values: Sequence[float] | np.ndarray,
) -> float:
    """Índice de Theil para distribución desigual."""
    x = _as_nonnegative_array(values, name="values")

    mean_value = float(np.mean(x))

    if mean_value <= 0:
        return 0.0

    positive = x[x > 0]

    if positive.size == 0:
        return 0.0

    ratios = positive / mean_value

    return float(
        np.mean(
            ratios * np.log(ratios)
        )
    )


def distribution_concentration(
    values: Sequence[float] | np.ndarray,
) -> float:
    """
    HHI de una distribución.

    Mayor valor = mayor concentración.
    """
    x = _as_nonnegative_array(values, name="values")
    total = float(np.sum(x))

    if total <= 0:
        return 0.0

    shares = x / total

    return float(np.sum(shares**2))


def temporal_concentration(
    values: Sequence[float] | np.ndarray,
) -> float:
    """
    Concentración temporal de una carga, demanda o evento.
    """
    return distribution_concentration(values)


def burstiness_index(
    values: Sequence[float] | np.ndarray,
) -> float:
    """
    Índice de burstiness:

        B = (σ - μ) / (σ + μ)

    Útil para diferenciar procesos relativamente regulares de procesos
    concentrados en pulsos.
    """
    x = _as_nonnegative_array(values, name="values")

    mean_value = float(np.mean(x))
    std_value = float(np.std(x, ddof=1)) if x.size > 1 else 0.0

    denominator = std_value + mean_value

    if denominator == 0:
        return 0.0

    return float(
        (std_value - mean_value) / denominator
    )


def event_rate(
    events: float,
    exposure_time: float,
) -> float:
    """Tasa de eventos por unidad temporal."""
    events = _validate_nonnegative_scalar(
        events,
        name="events",
    )
    exposure_time = _validate_positive_scalar(
        exposure_time,
        name="exposure_time",
    )

    return float(events / exposure_time)


def incidence_density(
    events: float,
    population_time: float,
) -> float:
    """Densidad de incidencia por unidad de persona-tiempo."""
    return event_rate(
        events,
        population_time,
    )


def prevalence(
    cases: float,
    population: float,
) -> float:
    """Prevalencia descriptiva."""
    cases = _validate_nonnegative_scalar(
        cases,
        name="cases",
    )
    population = _validate_positive_scalar(
        population,
        name="population",
    )

    if cases > population:
        raise MetricInputError(
            "cases no puede superar population"
        )

    return float(cases / population)


def access_rate(
    accessible_population: float,
    target_population: float,
) -> float:
    """Proporción de población con acceso observado."""
    accessible = _validate_nonnegative_scalar(
        accessible_population,
        name="accessible_population",
    )
    target = _validate_positive_scalar(
        target_population,
        name="target_population",
    )

    return float(
        np.clip(accessible / target, 0.0, 1.0)
    )


def unmet_demand_rate(
    unmet_demand: float,
    total_demand: float,
) -> float:
    """Proporción de demanda no satisfecha."""
    unmet = _validate_nonnegative_scalar(
        unmet_demand,
        name="unmet_demand",
    )
    total = _validate_positive_scalar(
        total_demand,
        name="total_demand",
    )

    if unmet > total:
        raise MetricInputError(
            "unmet_demand no puede superar total_demand"
        )

    return float(unmet / total)


def service_coverage(
    served: float,
    demand: float,
) -> float:
    """Proporción de demanda atendida."""
    served = _validate_nonnegative_scalar(
        served,
        name="served",
    )
    demand = _validate_positive_scalar(
        demand,
        name="demand",
    )

    return float(
        np.clip(served / demand, 0.0, 1.0)
    )


def throughput_rate(
    completed: float,
    time_window: float,
) -> float:
    """Producción/atención completada por unidad temporal."""
    return event_rate(
        completed,
        time_window,
    )


def backlog(
    demand: Sequence[float] | np.ndarray,
    served: Sequence[float] | np.ndarray,
) -> float:
    """
    Acumulación neta de demanda pendiente.

    backlog_t = backlog_(t-1) + demand_t - served_t
    """
    d = _as_nonnegative_array(
        demand,
        name="demand",
    )
    s = _as_nonnegative_array(
        served,
        name="served",
    )
    _validate_same_length(d, s)

    current = 0.0

    for demand_value, served_value in zip(d, s):
        current = max(
            0.0,
            current + float(demand_value) - float(served_value),
        )

    return float(current)


def backlog_series(
    demand: Sequence[float] | np.ndarray,
    served: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Trayectoria temporal del backlog."""
    d = _as_nonnegative_array(
        demand,
        name="demand",
    )
    s = _as_nonnegative_array(
        served,
        name="served",
    )
    _validate_same_length(d, s)

    result = np.empty_like(d)
    current = 0.0

    for i, (demand_value, served_value) in enumerate(
        zip(d, s)
    ):
        current = max(
            0.0,
            current + float(demand_value) - float(served_value),
        )
        result[i] = current

    return result


def backlog_age(
    backlog_values: Sequence[float] | np.ndarray,
    *,
    threshold: float = 0.0,
) -> int:
    """
    Antigüedad de backlog continuo por número de observaciones.
    """
    x = _as_nonnegative_array(
        backlog_values,
        name="backlog_values",
    )

    threshold = _validate_nonnegative_scalar(
        threshold,
        name="threshold",
    )

    age = 0

    for value in reversed(x):
        if value > threshold:
            age += 1
        else:
            break

    return int(age)


def response_time(
    detection_time: float,
    action_time: float,
) -> float:
    """Tiempo entre detección y acción."""
    detection = float(detection_time)
    action = float(action_time)

    if not np.isfinite(detection) or not np.isfinite(action):
        raise MetricInputError(
            "Los tiempos deben ser finitos"
        )

    if action < detection:
        raise MetricInputError(
            "action_time no puede preceder a detection_time"
        )

    return float(action - detection)


def decision_latency(
    detection_time: float,
    decision_time: float,
) -> float:
    """Tiempo entre detección y decisión."""
    return response_time(
        detection_time,
        decision_time,
    )


def intervention_latency(
    decision_time: float,
    intervention_time: float,
) -> float:
    """Tiempo entre decisión e intervención."""
    return response_time(
        decision_time,
        intervention_time,
    )


def intervention_effect(
    baseline: float,
    post_intervention: float,
) -> float:
    """
    Cambio relativo observado tras una intervención.

    No implica causalidad sin diseño causal apropiado.
    """
    baseline = _validate_positive_scalar(
        baseline,
        name="baseline",
    )
    post = float(post_intervention)

    if not np.isfinite(post):
        raise MetricInputError(
            "post_intervention debe ser finito"
        )

    return float(
        (post - baseline) / baseline
    )


def intervention_persistence(
    baseline: float,
    post_intervention: Sequence[float] | np.ndarray,
) -> float:
    """
    Fracción de observaciones posteriores que conservan el efecto observado
    respecto al baseline.
    """
    baseline = _validate_positive_scalar(
        baseline,
        name="baseline",
    )
    x = _as_float_array(
        post_intervention,
        name="post_intervention",
    )

    if x.size == 0:
        return 0.0

    effect = np.abs(x - baseline)
    initial_effect = float(effect[0])

    if initial_effect == 0:
        return 0.0

    return float(
        np.mean(effect >= initial_effect * 0.5)
    )


def rebound_magnitude(
    minimum_value: float,
    subsequent_peak: float,
) -> float:
    """Magnitud absoluta del rebote desde un mínimo."""
    minimum = _validate_nonnegative_scalar(
        minimum_value,
        name="minimum_value",
    )
    peak = _validate_nonnegative_scalar(
        subsequent_peak,
        name="subsequent_peak",
    )

    return float(max(peak - minimum, 0.0))


def unintended_load_shift(
    source_before: float,
    source_after: float,
    target_before: float,
    target_after: float,
) -> float:
    """
    Detecta aumento relativo de carga en un subsistema receptor mientras
    disminuye la carga del subsistema de origen.

    Es descriptivo y no demuestra que una intervención haya causado el cambio.
    """
    source_before = _validate_nonnegative_scalar(
        source_before,
        name="source_before",
    )
    source_after = _validate_nonnegative_scalar(
        source_after,
        name="source_after",
    )
    target_before = _validate_nonnegative_scalar(
        target_before,
        name="target_before",
    )
    target_after = _validate_nonnegative_scalar(
        target_after,
        name="target_after",
    )

    source_reduction = source_before - source_after
    target_increase = target_after - target_before

    if source_reduction <= 0 or target_increase <= 0:
        return 0.0

    return float(
        target_increase / max(source_reduction, 1e-15)
    )


# =============================================================================
# Registro de esta iteración
# =============================================================================

INTERACTION_INFORMATION_MANAGEMENT_METRICS: Final[tuple[str, ...]] = (
    "covariance_matrix",
    "correlation_matrix",
    "cross_correlation",
    "maximum_lagged_correlation",
    "coupling_strength",
    "coupling_change",
    "decoupling_index",
    "synchronization_index",
    "asynchrony_index",
    "interaction_matrix",
    "interaction_density",
    "interaction_entropy",
    "redundancy_index",
    "substitutability_index",
    "propagation_ratio",
    "amplification_gain",
    "damping_ratio",
    "cascade_depth",
    "network_vulnerability",
    "critical_node_dependence",
    "source_concentration_index",
    "source_diversity_entropy",
    "information_entropy",
    "information_surprise",
    "information_gain",
    "observation_coverage",
    "observation_latency",
    "information_loss_fraction",
    "contradictory_observation_rate",
    "gini_coefficient",
    "theil_index",
    "distribution_concentration",
    "temporal_concentration",
    "burstiness_index",
    "event_rate",
    "incidence_density",
    "prevalence",
    "access_rate",
    "unmet_demand_rate",
    "service_coverage",
    "throughput_rate",
    "backlog",
    "backlog_series",
    "backlog_age",
    "response_time",
    "decision_latency",
    "intervention_latency",
    "intervention_effect",
    "intervention_persistence",
    "rebound_magnitude",
    "unintended_load_shift",
)


INTERACTION_INFORMATION_INVARIANTS: Final[tuple[str, ...]] = (
    "Correlación no equivale a causalidad.",
    "Acoplamiento estadístico no identifica por sí mismo un mecanismo causal.",
    "La dependencia temporal debe conservar explícitamente el desfase utilizado.",
    "Una cascada observada debe distinguir propagación temporal de simple simultaneidad.",
    "La centralidad de una red no demuestra importancia causal.",
    "La concentración de fuentes reduce independencia epistemológica potencial.",
    "Diversidad de fuentes no equivale automáticamente a independencia.",
    "La entropía cuantifica distribución de información, no veracidad.",
    "La sorpresa depende del modelo probabilístico de referencia.",
    "La cobertura observacional no equivale a cobertura real del fenómeno.",
    "La ausencia de observación no equivale a ausencia del fenómeno.",
    "Backlog y demanda no son equivalentes.",
    "Capacidad atendida no equivale a capacidad nominal.",
    "Una reducción posterior a una intervención no demuestra causalidad sin identificación causal.",
    "El desplazamiento de carga entre subsistemas debe analizarse longitudinalmente.",
    "Una métrica agregada no debe ocultar heterogeneidad entre dimensiones.",
)


__all__.extend(
    INTERACTION_INFORMATION_MANAGEMENT_METRICS
)

# =============================================================================
# CEUTIA — MÉTRICAS HOLÍSTICAS, INTEGRATIVAS Y DE GESTIÓN SISTÉMICA
# =============================================================================
#
# Esta sección añade magnitudes de nivel sistémico sin convertirlas en modelos
# causales, predictores de riesgo ni decisiones operativas.
#
# Principio:
#   carga → capacidad → reserva → degradación → recuperación
#
# Estas funciones describen relaciones cuantificables. No establecen por sí
# mismas causalidad, peligrosidad individual, ni probabilidad de eventos.
# =============================================================================

from dataclasses import dataclass
from typing import NamedTuple


def _as_nonnegative_array(
    values: Sequence[float] | np.ndarray,
    *,
    name: str,
) -> np.ndarray:
    """Convierte una secuencia en vector numérico no negativo."""
    arr = _as_float_array(values, name=name)
    if np.any(arr < 0):
        raise MetricInputError(f"{name} no puede contener valores negativos")
    return arr


def _validate_positive_scalar(value: float, *, name: str) -> float:
    """Valida un escalar estrictamente positivo."""
    value = float(value)
    if not np.isfinite(value) or value <= 0:
        raise MetricInputError(f"{name} debe ser un número finito > 0")
    return value


def _validate_nonnegative_scalar(value: float, *, name: str) -> float:
    """Valida un escalar no negativo."""
    value = float(value)
    if not np.isfinite(value) or value < 0:
        raise MetricInputError(f"{name} debe ser un número finito >= 0")
    return value


def weighted_systemic_load(
    loads: Sequence[float] | np.ndarray,
    weights: Sequence[float] | np.ndarray,
) -> float:
    """
    Carga sistémica integrada mediante media ponderada.

    No presupone independencia entre dimensiones ni implica causalidad.
    """
    x = _as_nonnegative_array(loads, name="loads")
    w = _as_nonnegative_array(weights, name="weights")
    _validate_same_length(x, w)

    total_weight = float(np.sum(w))
    if total_weight <= 0:
        raise MetricInputError("La suma de weights debe ser > 0")

    return float(np.sum(x * w) / total_weight)


def geometric_systemic_load(
    loads: Sequence[float] | np.ndarray,
    weights: Sequence[float] | np.ndarray,
) -> float:
    """
    Carga integrada geométrica.

    Penaliza configuraciones donde una dimensión presenta valores muy bajos
    cuando todas las dimensiones representan componentes normalizados de carga.
    """
    x = _as_nonnegative_array(loads, name="loads")
    w = _as_nonnegative_array(weights, name="weights")
    _validate_same_length(x, w)

    total_weight = float(np.sum(w))
    if total_weight <= 0:
        raise MetricInputError("La suma de weights debe ser > 0")

    return float(
        np.exp(
            np.sum(w * np.log(np.clip(x, 1e-15, None)))
            / total_weight
        )
    )


def accumulated_load(
    load: Sequence[float] | np.ndarray,
    *,
    decay: float = 1.0,
) -> float:
    """
    Carga acumulada con memoria temporal exponencial.

    decay=1 conserva toda la carga histórica.
    decay<1 introduce pérdida progresiva de memoria.
    """
    x = _as_nonnegative_array(load, name="load")

    if not 0 < decay <= 1:
        raise MetricInputError("decay debe estar en el intervalo (0, 1]")

    state = 0.0
    for value in x:
        state = decay * state + float(value)

    return float(state)


def accumulated_load_series(
    load: Sequence[float] | np.ndarray,
    *,
    decay: float = 1.0,
) -> np.ndarray:
    """Trayectoria de carga acumulada con memoria temporal."""
    x = _as_nonnegative_array(load, name="load")

    if not 0 < decay <= 1:
        raise MetricInputError("decay debe estar en el intervalo (0, 1]")

    result = np.empty_like(x)
    state = 0.0

    for i, value in enumerate(x):
        state = decay * state + float(value)
        result[i] = state

    return result


def acute_chronic_load_ratio(
    load: Sequence[float] | np.ndarray,
    *,
    chronic_window: int,
) -> float:
    """
    Relación entre carga aguda y carga crónica.

    La carga aguda se representa por el último valor y la crónica por la
    media de la ventana previa disponible.
    """
    x = _as_nonnegative_array(load, name="load")

    if chronic_window < 1:
        raise MetricInputError("chronic_window debe ser >= 1")

    if x.size < 2:
        raise MetricInputError("Se requieren al menos dos observaciones")

    start = max(0, x.size - chronic_window - 1)
    chronic = x[start:-1]

    if chronic.size == 0:
        raise MetricInputError("No hay observaciones suficientes para la carga crónica")

    denominator = float(np.mean(chronic))

    if denominator == 0:
        if x[-1] == 0:
            return 0.0
        return float("inf")

    return float(x[-1] / denominator)


def load_capacity_gap(
    load: float,
    capacity: float,
) -> float:
    """Capacidad disponible menos carga."""
    load = _validate_nonnegative_scalar(load, name="load")
    capacity = _validate_nonnegative_scalar(capacity, name="capacity")
    return float(capacity - load)


def load_capacity_pressure(
    load: float,
    capacity: float,
) -> float:
    """
    Presión relativa carga/capacidad.

    1.0 = carga igual a capacidad.
    >1.0 = carga superior a capacidad.
    """
    load = _validate_nonnegative_scalar(load, name="load")
    capacity = _validate_positive_scalar(capacity, name="capacity")
    return float(load / capacity)


def capacity_headroom_fraction(
    load: float,
    capacity: float,
) -> float:
    """Fracción de capacidad aún disponible."""
    load = _validate_nonnegative_scalar(load, name="load")
    capacity = _validate_positive_scalar(capacity, name="capacity")

    return float((capacity - load) / capacity)


def effective_capacity(
    nominal_capacity: float,
    availability: float = 1.0,
    efficiency: float = 1.0,
) -> float:
    """
    Capacidad efectiva.

    nominal_capacity × availability × efficiency.
    """
    capacity = _validate_nonnegative_scalar(
        nominal_capacity,
        name="nominal_capacity",
    )
    availability = _validate_nonnegative_scalar(
        availability,
        name="availability",
    )
    efficiency = _validate_nonnegative_scalar(
        efficiency,
        name="efficiency",
    )

    if availability > 1 or efficiency > 1:
        raise MetricInputError(
            "availability y efficiency deben estar entre 0 y 1"
        )

    return float(capacity * availability * efficiency)


def accessible_capacity(
    effective_capacity_value: float,
    accessibility: float,
) -> float:
    """Capacidad efectivamente accesible por la población o proceso."""
    capacity = _validate_nonnegative_scalar(
        effective_capacity_value,
        name="effective_capacity_value",
    )
    accessibility = _validate_nonnegative_scalar(
        accessibility,
        name="accessibility",
    )

    if accessibility > 1:
        raise MetricInputError("accessibility debe estar entre 0 y 1")

    return float(capacity * accessibility)


def sustainable_capacity(
    effective_capacity_value: float,
    sustainability: float,
) -> float:
    """
    Capacidad sostenible bajo funcionamiento prolongado.
    """
    capacity = _validate_nonnegative_scalar(
        effective_capacity_value,
        name="effective_capacity_value",
    )
    sustainability = _validate_nonnegative_scalar(
        sustainability,
        name="sustainability",
    )

    if sustainability > 1:
        raise MetricInputError("sustainability debe estar entre 0 y 1")

    return float(capacity * sustainability)


def adaptive_reserve(
    capacity: float,
    current_load: float,
) -> float:
    """
    Reserva adaptativa absoluta.

    Representa el margen entre capacidad disponible y carga actual.
    """
    capacity = _validate_nonnegative_scalar(capacity, name="capacity")
    load = _validate_nonnegative_scalar(current_load, name="current_load")

    return float(capacity - load)


def adaptive_reserve_fraction(
    capacity: float,
    current_load: float,
) -> float:
    """Reserva adaptativa normalizada respecto a la capacidad."""
    capacity = _validate_positive_scalar(capacity, name="capacity")
    load = _validate_nonnegative_scalar(current_load, name="current_load")

    return float((capacity - load) / capacity)


def reserve_depletion_rate(
    reserve: Sequence[float] | np.ndarray,
    time: Sequence[float] | np.ndarray | None = None,
) -> float:
    """
    Velocidad media de consumo de reserva.

    Valor negativo: la reserva disminuye.
    Valor positivo: la reserva aumenta.
    """
    r = _as_float_array(reserve, name="reserve")

    if r.size < 2:
        raise MetricInputError("Se requieren al menos dos observaciones")

    if time is None:
        return float((r[-1] - r[0]) / (r.size - 1))

    t = _as_float_array(time, name="time")
    _validate_same_length(r, t)

    duration = float(t[-1] - t[0])
    if duration <= 0:
        raise MetricInputError("time debe ser estrictamente creciente")

    return float((r[-1] - r[0]) / duration)


def time_to_reserve_exhaustion(
    reserve: float,
    depletion_rate: float,
) -> float:
    """
    Tiempo lineal estimado hasta reserva cero.

    Sólo representa una extrapolación matemática local; no constituye una
    predicción validada del comportamiento futuro.
    """
    reserve = _validate_nonnegative_scalar(reserve, name="reserve")

    depletion_rate = float(depletion_rate)
    if not np.isfinite(depletion_rate):
        raise MetricInputError("depletion_rate debe ser finito")

    if depletion_rate >= 0:
        return float("inf")

    return float(reserve / abs(depletion_rate))


def capacity_debt(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
) -> float:
    """
    Área acumulada de exceso de demanda sobre capacidad.

    Sólo contabiliza periodos donde demand > capacity.
    """
    d = _as_nonnegative_array(demand, name="demand")
    c = _as_nonnegative_array(capacity, name="capacity")
    _validate_same_length(d, c)

    return float(np.sum(np.maximum(d - c, 0.0)))


def recovery_debt(
    baseline: Sequence[float] | np.ndarray,
    observed: Sequence[float] | np.ndarray,
) -> float:
    """
    Déficit acumulado respecto a una trayectoria de referencia.

    Sólo contabiliza desviaciones negativas.
    """
    b = _as_float_array(baseline, name="baseline")
    x = _as_float_array(observed, name="observed")
    _validate_same_length(b, x)

    return float(np.sum(np.maximum(b - x, 0.0)))


def degradation_magnitude(
    baseline: float,
    minimum_observed: float,
) -> float:
    """Magnitud absoluta de degradación respecto a una referencia."""
    baseline = _validate_nonnegative_scalar(baseline, name="baseline")
    minimum = _validate_nonnegative_scalar(
        minimum_observed,
        name="minimum_observed",
    )

    return float(max(baseline - minimum, 0.0))


def degradation_fraction(
    baseline: float,
    minimum_observed: float,
) -> float:
    """Degradación normalizada respecto a la referencia."""
    baseline = _validate_positive_scalar(baseline, name="baseline")
    minimum = _validate_nonnegative_scalar(
        minimum_observed,
        name="minimum_observed",
    )

    return float(max(baseline - minimum, 0.0) / baseline)


def recovery_fraction(
    baseline: float,
    minimum_observed: float,
    recovered_value: float,
) -> float:
    """
    Fracción de recuperación desde el mínimo hacia la referencia.

    0 = no recuperación.
    1 = recuperación completa.
    """
    baseline = _validate_positive_scalar(baseline, name="baseline")
    minimum = _validate_nonnegative_scalar(
        minimum_observed,
        name="minimum_observed",
    )
    recovered = _validate_nonnegative_scalar(
        recovered_value,
        name="recovered_value",
    )

    loss = baseline - minimum

    if loss <= 0:
        return 1.0 if recovered >= baseline else 0.0

    return float(np.clip((recovered - minimum) / loss, 0.0, 1.0))


def resilience_resistance(
    baseline: float,
    minimum_observed: float,
) -> float:
    """
    Resistencia al shock: proporción del estado basal conservada en el mínimo.
    """
    baseline = _validate_positive_scalar(baseline, name="baseline")
    minimum = _validate_nonnegative_scalar(
        minimum_observed,
        name="minimum_observed",
    )

    return float(np.clip(minimum / baseline, 0.0, 1.0))


def resilience_area(
    baseline: Sequence[float] | np.ndarray,
    observed: Sequence[float] | np.ndarray,
) -> float:
    """
    Área normalizada de funcionamiento conservado.

    Una trayectoria igual al baseline produce 1.
    """
    b = _as_nonnegative_array(baseline, name="baseline")
    x = _as_nonnegative_array(observed, name="observed")
    _validate_same_length(b, x)

    if b.size < 2:
        raise MetricInputError("Se requieren al menos dos observaciones")

    denominator = float(np.sum(b))
    if denominator <= 0:
        raise MetricInputError("baseline debe contener carga funcional positiva")

    preserved = np.minimum(x, b)

    return float(np.sum(preserved) / denominator)


def recovery_area(
    baseline: Sequence[float] | np.ndarray,
    observed: Sequence[float] | np.ndarray,
) -> float:
    """
    Área normalizada de déficit acumulado respecto al baseline.

    0 = sin déficit.
    Valores mayores = mayor déficit acumulado.
    """
    b = _as_nonnegative_array(baseline, name="baseline")
    x = _as_nonnegative_array(observed, name="observed")
    _validate_same_length(b, x)

    denominator = float(np.sum(b))
    if denominator <= 0:
        raise MetricInputError("baseline debe contener valores positivos")

    deficit = np.maximum(b - x, 0.0)

    return float(np.sum(deficit) / denominator)


def shock_intensity(
    baseline: float,
    shocked_value: float,
) -> float:
    """Magnitud relativa de una perturbación respecto al baseline."""
    baseline = _validate_positive_scalar(baseline, name="baseline")
    shocked = _validate_nonnegative_scalar(
        shocked_value,
        name="shocked_value",
    )

    return float(abs(shocked - baseline) / baseline)


def shock_duration(
    values: Sequence[float] | np.ndarray,
    baseline: float,
    *,
    threshold_fraction: float = 0.05,
) -> int:
    """
    Duración de una desviación sostenida respecto al baseline.

    Cuenta observaciones cuya desviación absoluta supera el umbral relativo.
    """
    x = _as_nonnegative_array(values, name="values")
    baseline = _validate_positive_scalar(baseline, name="baseline")

    if threshold_fraction < 0:
        raise MetricInputError("threshold_fraction debe ser >= 0")

    threshold = baseline * threshold_fraction

    return int(np.sum(np.abs(x - baseline) > threshold))


def shock_burden(
    values: Sequence[float] | np.ndarray,
    baseline: float,
) -> float:
    """
    Carga acumulada de perturbación absoluta respecto a un baseline.
    """
    x = _as_float_array(values, name="values")
    baseline = _validate_nonnegative_scalar(baseline, name="baseline")

    return float(np.sum(np.abs(x - baseline)))


def repeated_shock_recovery(
    values: Sequence[float] | np.ndarray,
    baseline: float,
    *,
    recovery_threshold: float = 0.95,
) -> float:
    """
    Proporción de episodios en los que el sistema vuelve a alcanzar una
    fracción determinada del baseline.

    Esta métrica describe recuperación observada; no demuestra resiliencia
    futura.
    """
    x = _as_nonnegative_array(values, name="values")
    baseline = _validate_positive_scalar(baseline, name="baseline")

    if not 0 < recovery_threshold <= 1:
        raise MetricInputError(
            "recovery_threshold debe estar en (0, 1]"
        )

    if x.size == 0:
        return 0.0

    return float(np.mean(x >= baseline * recovery_threshold))


def bottleneck_share(
    loads: Sequence[float] | np.ndarray,
) -> float:
    """
    Proporción de la carga total concentrada en la dimensión más cargada.
    """
    x = _as_nonnegative_array(loads, name="loads")
    total = float(np.sum(x))

    if total <= 0:
        return 0.0

    return float(np.max(x) / total)


def bottleneck_index(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
) -> int:
    """
    Índice de la dimensión con mayor presión demanda/capacidad.
    """
    d = _as_nonnegative_array(demand, name="demand")
    c = _as_nonnegative_array(capacity, name="capacity")
    _validate_same_length(d, c)

    if np.any(c <= 0):
        raise MetricInputError("capacity debe ser > 0 en todas las dimensiones")

    return int(np.argmax(d / c))


def systemic_capacity_pressure(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
    weights: Sequence[float] | np.ndarray | None = None,
) -> float:
    """
    Presión sistémica integrada demanda/capacidad.

    Con weights=None utiliza media simple.
    """
    d = _as_nonnegative_array(demand, name="demand")
    c = _as_nonnegative_array(capacity, name="capacity")
    _validate_same_length(d, c)

    if np.any(c <= 0):
        raise MetricInputError("capacity debe ser > 0 en todas las dimensiones")

    pressure = d / c

    if weights is None:
        return float(np.mean(pressure))

    w = _as_nonnegative_array(weights, name="weights")
    _validate_same_length(pressure, w)

    total_weight = float(np.sum(w))
    if total_weight <= 0:
        raise MetricInputError("La suma de weights debe ser > 0")

    return float(np.sum(pressure * w) / total_weight)


def systemic_headroom(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
) -> float:
    """
    Headroom sistémico conservador.

    Utiliza el menor margen relativo entre dimensiones.
    """
    d = _as_nonnegative_array(demand, name="demand")
    c = _as_nonnegative_array(capacity, name="capacity")
    _validate_same_length(d, c)

    if np.any(c <= 0):
        raise MetricInputError("capacity debe ser > 0 en todas las dimensiones")

    headroom = (c - d) / c

    return float(np.min(headroom))


def reserve_distribution_entropy(
    reserves: Sequence[float] | np.ndarray,
) -> float:
    """
    Entropía normalizada de la distribución de reserva entre dimensiones.

    Mayor valor = reserva más distribuida.
    """
    x = _as_nonnegative_array(reserves, name="reserves")
    total = float(np.sum(x))

    if total <= 0:
        return 0.0

    p = x / total
    positive = p[p > 0]

    if positive.size <= 1:
        return 0.0

    entropy = -float(np.sum(positive * np.log(positive)))
    maximum = float(np.log(x.size))

    if maximum == 0:
        return 0.0

    return float(entropy / maximum)


def integrated_resilience_profile(
    resistance: float,
    recovery: float,
    reserve: float,
    redundancy: float,
    *,
    weights: Sequence[float] | np.ndarray | None = None,
) -> float:
    """
    Perfil integrado de resiliencia.

    Integra dimensiones normalizadas proporcionadas por el llamador.
    No constituye una escala clínica ni un índice universal de resiliencia.
    """
    values = _as_nonnegative_array(
        [resistance, recovery, reserve, redundancy],
        name="resilience_components",
    )

    if np.any(values > 1):
        raise MetricInputError(
            "Las dimensiones de resiliencia deben estar normalizadas en [0, 1]"
        )

    if weights is None:
        return float(np.mean(values))

    w = _as_nonnegative_array(weights, name="weights")
    _validate_same_length(values, w)

    total_weight = float(np.sum(w))
    if total_weight <= 0:
        raise MetricInputError("La suma de weights debe ser > 0")

    return float(np.sum(values * w) / total_weight)


class SystemicCapacitySnapshot(NamedTuple):
    """Instantánea integrada de presión, reserva y capacidad."""
    demand: float
    capacity: float
    pressure: float
    headroom: float
    reserve: float


@dataclass(frozen=True, slots=True)
class HolisticSystemProfile:
    """
    Perfil descriptivo de un sistema multifactorial.

    Los componentes permanecen separados para evitar que un único score
    oculte qué dimensión está determinando el estado.
    """

    integrated_load: float
    capacity_pressure: float
    headroom: float
    adaptive_reserve: float
    bottleneck_share: float
    resistance: float
    recovery: float
    resilience: float


def build_holistic_system_profile(
    loads: Sequence[float] | np.ndarray,
    capacities: Sequence[float] | np.ndarray,
    *,
    load_weights: Sequence[float] | np.ndarray | None = None,
    resistance: float = 0.0,
    recovery: float = 0.0,
    redundancy: float = 0.0,
) -> HolisticSystemProfile:
    """
    Construye un perfil sistémico manteniendo las dimensiones explícitas.
    """
    x = _as_nonnegative_array(loads, name="loads")
    c = _as_nonnegative_array(capacities, name="capacities")
    _validate_same_length(x, c)

    if load_weights is None:
        weights = np.ones_like(x)
    else:
        weights = _as_nonnegative_array(load_weights, name="load_weights")
        _validate_same_length(x, weights)

    integrated_load = weighted_systemic_load(x, weights)
    pressure = systemic_capacity_pressure(x, c, weights)
    headroom = systemic_headroom(x, c)
    reserve = float(np.min(c - x))
    bottleneck = bottleneck_share(x)

    resistance_value = float(np.clip(resistance, 0.0, 1.0))
    recovery_value = float(np.clip(recovery, 0.0, 1.0))
    redundancy_value = float(np.clip(redundancy, 0.0, 1.0))
    reserve_normalized = float(
        np.clip(
            np.mean((c - x) / np.maximum(c, 1e-15)),
            0.0,
            1.0,
        )
    )

    resilience = integrated_resilience_profile(
        resistance_value,
        recovery_value,
        reserve_normalized,
        redundancy_value,
    )

    return HolisticSystemProfile(
        integrated_load=integrated_load,
        capacity_pressure=pressure,
        headroom=headroom,
        adaptive_reserve=reserve,
        bottleneck_share=bottleneck,
        resistance=resistance_value,
        recovery=recovery_value,
        resilience=resilience,
    )


HOLISTIC_INTEGRATIVE_METRICS: Final[tuple[str, ...]] = (
    "weighted_systemic_load",
    "geometric_systemic_load",
    "accumulated_load",
    "accumulated_load_series",
    "acute_chronic_load_ratio",
    "load_capacity_gap",
    "load_capacity_pressure",
    "capacity_headroom_fraction",
    "effective_capacity",
    "accessible_capacity",
    "sustainable_capacity",
    "adaptive_reserve",
    "adaptive_reserve_fraction",
    "reserve_depletion_rate",
    "time_to_reserve_exhaustion",
    "capacity_debt",
    "recovery_debt",
    "degradation_magnitude",
    "degradation_fraction",
    "recovery_fraction",
    "resilience_resistance",
    "resilience_area",
    "recovery_area",
    "shock_intensity",
    "shock_duration",
    "shock_burden",
    "repeated_shock_recovery",
    "bottleneck_share",
    "bottleneck_index",
    "systemic_capacity_pressure",
    "systemic_headroom",
    "reserve_distribution_entropy",
    "integrated_resilience_profile",
    "build_holistic_system_profile",
)


HOLISTIC_METRIC_INVARIANTS: Final[tuple[str, ...]] = (
    "Una métrica integrada no demuestra causalidad entre sus componentes.",
    "Una media integrada no debe ocultar el componente que determina el cuello de botella.",
    "Carga, capacidad y reserva deben conservar sus unidades y contexto temporal.",
    "Capacidad nominal no equivale a capacidad efectiva, accesible o sostenible.",
    "Una extrapolación de agotamiento no constituye una predicción validada.",
    "Resiliencia debe poder descomponerse en sus dimensiones observables.",
    "La recuperación observada no garantiza recuperación futura.",
    "Un shock aislado y una secuencia de shocks no son fenómenos equivalentes.",
    "La agregación de dimensiones no elimina la incertidumbre de cada dimensión.",
)


__all__.extend(HOLISTIC_INTEGRATIVE_METRICS)



# ============================================================================
# CEUTIA — ADVANCED DYNAMIC SYSTEM METRICS
# ============================================================================
# Additive extension for backend/app/core/metrics.py
#
# Purpose:
#   Provide mathematical primitives for the dynamic, multifactorial,
#   multiscale and epistemically-aware analysis of CeutIA.
#
# Architectural rule:
#   observation → evidence → state → trajectory → interaction → dynamics
#   → perturbation → response → capacity/reserve → propagation
#   → transition → signal
#
# This layer computes quantitative properties.
# It does NOT:
#   - establish causality by correlation alone;
#   - diagnose individuals;
#   - infer dangerousness from identity/group membership;
#   - autonomously decide security actions;
#   - convert a metric into an alert without validation;
#   - treat statistical significance as operational significance;
#   - treat model survival under testing as proof of truth.
#
# ============================================================================

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from math import exp, isfinite, log, sqrt
from typing import Any, Iterable, Mapping, Sequence

import numpy as np


# ============================================================================
# ENUMERATIONS
# ============================================================================


class DynamicMetricType(str, Enum):
    """Epistemic/dynamic role of a computed quantity."""

    DESCRIPTIVE = "descriptive"
    TRAJECTORY = "trajectory"
    INTERACTION = "interaction"
    CAPACITY = "capacity"
    PROPAGATION = "propagation"
    RESILIENCE = "resilience"
    TRANSITION = "transition"
    EARLY_WARNING = "early_warning"
    UNCERTAINTY = "uncertainty"


class DynamicEvidenceStatus(str, Enum):
    """Status of the evidence underlying a dynamic metric."""

    OBSERVED = "observed"
    DERIVED = "derived"
    MODEL_DEPENDENT = "model_dependent"
    EXPLORATORY = "exploratory"
    VALIDATED = "validated"
    UNCALIBRATED = "uncalibrated"


class InteractionKind(str, Enum):
    """Relationship type represented by a mathematical interaction."""

    ASSOCIATION = "association"
    TEMPORAL_ASSOCIATION = "temporal_association"
    LAGGED_ASSOCIATION = "lagged_association"
    NONLINEAR_ASSOCIATION = "nonlinear_association"
    INTERACTION = "interaction"
    COUPLING = "coupling"
    SYNCHRONIZATION = "synchronization"
    PROPAGATION = "propagation"
    FEEDBACK = "feedback"


# ============================================================================
# VALIDATION / NUMERICAL UTILITIES
# ============================================================================


def _ceutia_array(
    values: Sequence[float] | np.ndarray,
    *,
    ndim: int | None = None,
    name: str = "values",
) -> np.ndarray:
    """Convert input to a finite float array."""

    array = np.asarray(values, dtype=float)

    if array.size == 0:
        raise ValueError(f"{name} must not be empty.")

    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} contains non-finite values.")

    if ndim is not None and array.ndim != ndim:
        raise ValueError(
            f"{name} must have ndim={ndim}; received ndim={array.ndim}."
        )

    return array


def _ceutia_1d(
    values: Sequence[float] | np.ndarray,
    *,
    name: str = "values",
) -> np.ndarray:
    return _ceutia_array(values, ndim=1, name=name)


def _ceutia_2d(
    values: Sequence[Sequence[float]] | np.ndarray,
    *,
    name: str = "values",
) -> np.ndarray:
    return _ceutia_array(values, ndim=2, name=name)


def _ceutia_same_length(
    *arrays: Sequence[float] | np.ndarray,
) -> None:
    lengths = {len(array) for array in arrays}

    if len(lengths) != 1:
        raise ValueError("All supplied series must have the same length.")


def _ceutia_validate_window(window: int, n: int) -> None:
    if window < 2:
        raise ValueError("window must be >= 2.")

    if window > n:
        raise ValueError("window must not exceed the number of observations.")


def _ceutia_safe_std(values: np.ndarray, ddof: int = 0) -> float:
    if values.size <= ddof:
        return 0.0

    result = float(np.std(values, ddof=ddof))

    if not isfinite(result):
        return 0.0

    return result


def _ceutia_safe_mean(values: np.ndarray) -> float:
    return float(np.mean(values))


def _ceutia_safe_divide(
    numerator: float,
    denominator: float,
    *,
    default: float = 0.0,
) -> float:
    if denominator == 0:
        return default

    result = numerator / denominator

    if not isfinite(result):
        return default

    return float(result)


# ============================================================================
# DYNAMIC STATE
# ============================================================================


def ceutia_state_vector(
    observations: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """
    Construct the state trajectory X(t).

    Expected shape:
        observations[t, variable]

    Returns:
        State matrix with the same shape.
    """

    return _ceutia_2d(observations, name="observations")


def ceutia_state_mean(
    observations: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """Mean state across the observed temporal trajectory."""

    matrix = _ceutia_2d(observations, name="observations")
    return np.mean(matrix, axis=0)


def ceutia_state_std(
    observations: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """Temporal standard deviation of each state dimension."""

    matrix = _ceutia_2d(observations, name="observations")
    return np.std(matrix, axis=0)


def ceutia_state_velocity(
    observations: Sequence[Sequence[float]] | np.ndarray,
    *,
    dt: float = 1.0,
) -> np.ndarray:
    """
    First temporal derivative:

        dX/dt

    Returns one velocity vector per temporal interval.
    """

    if dt <= 0:
        raise ValueError("dt must be > 0.")

    matrix = _ceutia_2d(observations, name="observations")

    if matrix.shape[0] < 2:
        raise ValueError("At least two observations are required.")

    return np.diff(matrix, axis=0) / dt


def ceutia_state_acceleration(
    observations: Sequence[Sequence[float]] | np.ndarray,
    *,
    dt: float = 1.0,
) -> np.ndarray:
    """
    Second temporal derivative:

        d²X/dt²
    """

    if dt <= 0:
        raise ValueError("dt must be > 0.")

    velocity = ceutia_state_velocity(observations, dt=dt)

    if velocity.shape[0] < 2:
        raise ValueError("At least three observations are required.")

    return np.diff(velocity, axis=0) / dt


def ceutia_state_speed(
    observations: Sequence[Sequence[float]] | np.ndarray,
    *,
    dt: float = 1.0,
) -> np.ndarray:
    """Euclidean norm of the state velocity."""

    velocity = ceutia_state_velocity(observations, dt=dt)
    return np.linalg.norm(velocity, axis=1)


def ceutia_state_acceleration_magnitude(
    observations: Sequence[Sequence[float]] | np.ndarray,
    *,
    dt: float = 1.0,
) -> np.ndarray:
    """Euclidean norm of state acceleration."""

    acceleration = ceutia_state_acceleration(observations, dt=dt)
    return np.linalg.norm(acceleration, axis=1)


def ceutia_state_distance(
    state_a: Sequence[float] | np.ndarray,
    state_b: Sequence[float] | np.ndarray,
) -> float:
    """Euclidean distance between two system states."""

    a = _ceutia_1d(state_a, name="state_a")
    b = _ceutia_1d(state_b, name="state_b")

    if a.shape != b.shape:
        raise ValueError("States must have identical dimensions.")

    return float(np.linalg.norm(a - b))


def ceutia_standardized_state_distance(
    state_a: Sequence[float] | np.ndarray,
    state_b: Sequence[float] | np.ndarray,
    scale: Sequence[float] | np.ndarray,
) -> float:
    """
    Distance after normalization by variable-specific scale.

    This avoids allowing variables with large numerical units to dominate
    the state-space distance.
    """

    a = _ceutia_1d(state_a, name="state_a")
    b = _ceutia_1d(state_b, name="state_b")
    s = _ceutia_1d(scale, name="scale")

    if not (a.shape == b.shape == s.shape):
        raise ValueError("state_a, state_b and scale must have equal dimensions.")

    if np.any(s <= 0):
        raise ValueError("All scale values must be > 0.")

    return float(np.linalg.norm((a - b) / s))


# ============================================================================
# TRAJECTORY / PERSISTENCE / MEMORY
# ============================================================================


def ceutia_persistence(
    values: Sequence[float] | np.ndarray,
    *,
    threshold: float = 0.0,
) -> float:
    """
    Fraction of observations remaining above a threshold.

    This is descriptive persistence, not a probability of future persistence.
    """

    x = _ceutia_1d(values, name="values")

    return float(np.mean(x >= threshold))


def ceutia_duration_above_threshold(
    values: Sequence[float] | np.ndarray,
    *,
    threshold: float,
) -> int:
    """Number of consecutive observations at the end of the series above threshold."""

    x = _ceutia_1d(values, name="values")

    duration = 0

    for value in reversed(x):
        if value >= threshold:
            duration += 1
        else:
            break

    return duration


def ceutia_time_above_threshold(
    values: Sequence[float] | np.ndarray,
    *,
    threshold: float,
    dt: float = 1.0,
) -> float:
    """Total observed time spent above a threshold."""

    if dt <= 0:
        raise ValueError("dt must be > 0.")

    x = _ceutia_1d(values, name="values")
    return float(np.sum(x >= threshold) * dt)


def ceutia_autocorrelation(
    values: Sequence[float] | np.ndarray,
    *,
    lag: int = 1,
) -> float:
    """
    Lag-k autocorrelation.

    Useful as one component of critical-transition analysis.
    """

    x = _ceutia_1d(values, name="values")

    if lag < 1 or lag >= len(x):
        raise ValueError("lag must satisfy 1 <= lag < len(values).")

    a = x[:-lag]
    b = x[lag:]

    a_centered = a - np.mean(a)
    b_centered = b - np.mean(b)

    denominator = np.sqrt(
        np.sum(a_centered**2) * np.sum(b_centered**2)
    )

    return _ceutia_safe_divide(
        float(np.sum(a_centered * b_centered)),
        float(denominator),
    )


def ceutia_variance_trend(
    values: Sequence[float] | np.ndarray,
    *,
    window: int,
) -> float:
    """
    Slope of rolling variance.

    Positive values indicate increasing local variance.
    """

    x = _ceutia_1d(values, name="values")
    _ceutia_validate_window(window, len(x))

    rolling_variances = np.array(
        [
            np.var(x[index - window + 1 : index + 1])
            for index in range(window - 1, len(x))
        ]
    )

    if len(rolling_variances) < 2:
        return 0.0

    return ceutia_dynamic_slope(rolling_variances)


def ceutia_autocorrelation_trend(
    values: Sequence[float] | np.ndarray,
    *,
    window: int,
    lag: int = 1,
) -> float:
    """
    Trend in local lagged autocorrelation.

    This is a potential early-warning feature, not an autonomous
    critical-transition detector.
    """

    x = _ceutia_1d(values, name="values")
    _ceutia_validate_window(window, len(x))

    if lag >= window:
        raise ValueError("lag must be smaller than window.")

    local_values: list[float] = []

    for end in range(window, len(x) + 1):
        segment = x[end - window : end]
        local_values.append(ceutia_autocorrelation(segment, lag=lag))

    if len(local_values) < 2:
        return 0.0

    return ceutia_dynamic_slope(np.asarray(local_values))


# ============================================================================
# LOCAL DYNAMICS
# ============================================================================


def ceutia_dynamic_slope(
    values: Sequence[float] | np.ndarray,
    *,
    dt: float = 1.0,
) -> float:
    """Least-squares temporal slope."""

    if dt <= 0:
        raise ValueError("dt must be > 0.")

    x = _ceutia_1d(values, name="values")

    if len(x) < 2:
        raise ValueError("At least two observations are required.")

    time = np.arange(len(x), dtype=float) * dt
    slope = np.polyfit(time, x, 1)[0]

    return float(slope)


def ceutia_dynamic_acceleration(
    values: Sequence[float] | np.ndarray,
    *,
    dt: float = 1.0,
) -> float:
    """Least-squares slope of the first derivative."""

    if dt <= 0:
        raise ValueError("dt must be > 0.")

    x = _ceutia_1d(values, name="values")

    if len(x) < 3:
        raise ValueError("At least three observations are required.")

    velocity = np.diff(x) / dt
    return ceutia_dynamic_slope(velocity, dt=dt)


def ceutia_rolling_slope(
    values: Sequence[float] | np.ndarray,
    *,
    window: int,
    dt: float = 1.0,
) -> np.ndarray:
    """Local slope trajectory."""

    x = _ceutia_1d(values, name="values")
    _ceutia_validate_window(window, len(x))

    return np.asarray(
        [
            ceutia_dynamic_slope(
                x[index - window + 1 : index + 1],
                dt=dt,
            )
            for index in range(window - 1, len(x))
        ]
    )


def ceutia_rolling_coefficient_of_variation(
    values: Sequence[float] | np.ndarray,
    *,
    window: int,
) -> np.ndarray:
    """Rolling coefficient of variation."""

    x = _ceutia_1d(values, name="values")
    _ceutia_validate_window(window, len(x))

    result: list[float] = []

    for index in range(window - 1, len(x)):
        segment = x[index - window + 1 : index + 1]
        mean = float(np.mean(segment))
        std = float(np.std(segment))

        result.append(
            _ceutia_safe_divide(std, abs(mean))
        )

    return np.asarray(result)


# ============================================================================
# MULTIVARIATE STATE GEOMETRY
# ============================================================================


def ceutia_multivariate_zscore(
    observations: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """Column-wise standardized state trajectory."""

    matrix = _ceutia_2d(observations, name="observations")

    mean = np.mean(matrix, axis=0)
    std = np.std(matrix, axis=0)

    safe_std = np.where(std == 0, 1.0, std)

    return (matrix - mean) / safe_std


def ceutia_multivariate_anomaly_score(
    observations: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """
    Mahalanobis-like anomaly score.

    Covariance regularization is used to remain numerically stable in
    high-dimensional or partially collinear systems.
    """

    matrix = _ceutia_2d(observations, name="observations")

    if matrix.shape[0] < 2:
        raise ValueError("At least two observations are required.")

    centered = matrix - np.mean(matrix, axis=0)

    covariance = np.cov(centered, rowvar=False)

    if covariance.ndim == 0:
        covariance = np.asarray([[float(covariance)]])

    regularization = max(
        float(np.trace(covariance)),
        1.0,
    ) * 1e-8

    covariance = covariance + (
        np.eye(covariance.shape[0]) * regularization
    )

    inverse = np.linalg.pinv(covariance)

    distances = np.einsum(
        "ij,jk,ik->i",
        centered,
        inverse,
        centered,
    )

    return np.sqrt(np.maximum(distances, 0.0))


def ceutia_effective_dimension(
    observations: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    Effective dimensionality derived from covariance eigenvalues.

    Higher values indicate that variability is distributed across more
    independent directions of the observed state space.
    """

    matrix = _ceutia_2d(observations, name="observations")

    centered = matrix - np.mean(matrix, axis=0)

    covariance = np.cov(centered, rowvar=False)

    if covariance.ndim == 0:
        return 1.0

    eigenvalues = np.linalg.eigvalsh(covariance)
    eigenvalues = np.clip(eigenvalues, 0.0, None)

    total = float(np.sum(eigenvalues))

    if total == 0:
        return 0.0

    proportions = eigenvalues / total

    return float(
        1.0 / np.sum(proportions**2)
    )


def ceutia_principal_component_concentration(
    observations: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    Fraction of total covariance explained by the first principal component.
    """

    matrix = _ceutia_2d(observations, name="observations")

    centered = matrix - np.mean(matrix, axis=0)
    covariance = np.cov(centered, rowvar=False)

    if covariance.ndim == 0:
        return 1.0

    eigenvalues = np.linalg.eigvalsh(covariance)
    eigenvalues = np.clip(eigenvalues, 0.0, None)

    total = float(np.sum(eigenvalues))

    if total == 0:
        return 0.0

    return float(np.max(eigenvalues) / total)


# ============================================================================
# INTERACTION STRUCTURE
# ============================================================================


def ceutia_covariance_matrix(
    observations: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """Temporal covariance matrix between state variables."""

    matrix = _ceutia_2d(observations, name="observations")

    if matrix.shape[0] < 2:
        raise ValueError("At least two observations are required.")

    return np.asarray(
        np.cov(matrix, rowvar=False),
        dtype=float,
    )


def ceutia_correlation_matrix(
    observations: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """Pearson correlation matrix."""

    matrix = _ceutia_2d(observations, name="observations")

    if matrix.shape[0] < 2:
        raise ValueError("At least two observations are required.")

    return np.asarray(
        np.corrcoef(matrix, rowvar=False),
        dtype=float,
    )


def ceutia_lagged_cross_correlation(
    series_a: Sequence[float] | np.ndarray,
    series_b: Sequence[float] | np.ndarray,
    *,
    lag: int,
) -> float:
    """
    Cross-correlation with explicit temporal lag.

    Positive lag means A(t) is compared with B(t + lag).
    """

    a = _ceutia_1d(series_a, name="series_a")
    b = _ceutia_1d(series_b, name="series_b")

    _ceutia_same_length(a, b)

    if lag >= len(a) or lag <= -len(a):
        raise ValueError("Absolute lag must be smaller than series length.")

    if lag > 0:
        return ceutia_autocorrelation_like(
            a[:-lag],
            b[lag:],
        )

    if lag < 0:
        return ceutia_autocorrelation_like(
            a[-lag:],
            b[:lag],
        )

    return ceutia_autocorrelation_like(a, b)


def ceutia_autocorrelation_like(
    series_a: Sequence[float] | np.ndarray,
    series_b: Sequence[float] | np.ndarray,
) -> float:
    """Correlation between two equally-sized series."""

    a = _ceutia_1d(series_a, name="series_a")
    b = _ceutia_1d(series_b, name="series_b")

    _ceutia_same_length(a, b)

    a_centered = a - np.mean(a)
    b_centered = b - np.mean(b)

    denominator = np.sqrt(
        np.sum(a_centered**2) *
        np.sum(b_centered**2)
    )

    return _ceutia_safe_divide(
        float(np.sum(a_centered * b_centered)),
        float(denominator),
    )


def ceutia_interaction_effect(
    x1: Sequence[float] | np.ndarray,
    x2: Sequence[float] | np.ndarray,
    y: Sequence[float] | np.ndarray,
) -> float:
    """
    Incremental interaction coefficient from:

        y ~ x1 + x2 + x1*x2

    The returned value is the fitted coefficient of x1*x2.

    IMPORTANT:
        This is an interaction association unless the surrounding
        identification assumptions justify causal interpretation.
    """

    a = _ceutia_1d(x1, name="x1")
    b = _ceutia_1d(x2, name="x2")
    target = _ceutia_1d(y, name="y")

    _ceutia_same_length(a, b, target)

    design = np.column_stack(
        [
            np.ones(len(a)),
            a,
            b,
            a * b,
        ]
    )

    coefficients, *_ = np.linalg.lstsq(
        design,
        target,
        rcond=None,
    )

    return float(coefficients[3])


def ceutia_interaction_matrix(
    observations: Sequence[Sequence[float]] | np.ndarray,
) -> np.ndarray:
    """
    Pairwise interaction matrix.

    Each element represents the absolute correlation between two variables.
    It is a dependency map, not a causal graph.
    """

    return np.abs(
        ceutia_correlation_matrix(observations)
    )


def ceutia_dynamic_interaction_matrix(
    observations: Sequence[Sequence[float]] | np.ndarray,
    *,
    window: int,
) -> np.ndarray:
    """
    Interaction matrix over time.

    Returns:
        [time_window, variable, variable]
    """

    matrix = _ceutia_2d(observations, name="observations")
    _ceutia_validate_window(window, matrix.shape[0])

    result = []

    for end in range(window, matrix.shape[0] + 1):
        result.append(
            ceutia_interaction_matrix(
                matrix[end - window : end]
            )
        )

    return np.asarray(result)


def ceutia_coupling_change(
    observations: Sequence[Sequence[float]] | np.ndarray,
    *,
    window: int,
) -> np.ndarray:
    """
    Change in total pairwise dependency structure between consecutive
    temporal windows.
    """

    dynamic = ceutia_dynamic_interaction_matrix(
        observations,
        window=window,
    )

    if dynamic.shape[0] < 2:
        return np.empty(0, dtype=float)

    changes = []

    for previous, current in zip(
        dynamic[:-1],
        dynamic[1:],
    ):
        changes.append(
            float(np.linalg.norm(current - previous))
        )

    return np.asarray(changes)


def ceutia_synchronization_index(
    observations: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    Mean absolute off-diagonal correlation.

    High synchronization means variables are moving together.
    This is not inherently good or bad.
    """

    correlation = np.abs(
        ceutia_correlation_matrix(observations)
    )

    n = correlation.shape[0]

    if n < 2:
        return 0.0

    upper = correlation[
        np.triu_indices(n, k=1)
    ]

    return float(np.mean(upper))


def ceutia_redundancy_index(
    observations: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    Mean absolute inter-variable correlation.

    It is a descriptive redundancy/dependence measure and should not
    be interpreted as resilience by itself.
    """

    return ceutia_synchronization_index(observations)


# ============================================================================
# HIGHER-ORDER INTERACTION
# ============================================================================


def ceutia_higher_order_interaction(
    variables: Sequence[Sequence[float] | np.ndarray],
    outcome: Sequence[float] | np.ndarray,
) -> float:
    """
    Estimate the coefficient of the full multiplicative interaction:

        x1 * x2 * ... * xn

    This is deliberately restricted to a supplied set of variables.
    """

    if len(variables) < 2:
        raise ValueError(
            "At least two variables are required."
        )

    arrays = [
        _ceutia_1d(variable, name=f"variable_{index}")
        for index, variable in enumerate(variables)
    ]

    target = _ceutia_1d(outcome, name="outcome")

    _ceutia_same_length(*arrays, target)

    interaction = np.ones(len(target))

    for variable in arrays:
        interaction *= variable

    design = np.column_stack(
        [np.ones(len(target)), *arrays, interaction]
    )

    coefficients, *_ = np.linalg.lstsq(
        design,
        target,
        rcond=None,
    )

    return float(coefficients[-1])


# ============================================================================
# CAPACITY / LOAD / RESERVE
# ============================================================================


def ceutia_utilization_ratio(
    demand: Sequence[float] | np.ndarray,
    capacity: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Demand/capacity ratio."""

    d = _ceutia_1d(demand, name="demand")
    c = _ceutia_1d(capacity, name="capacity")

    _ceutia_same_length(d, c)

    return np.divide(
        d,
        c,
        out=np.full_like(d, np.inf, dtype=float),
        where=c != 0,
    )


def ceutia_capacity_reserve(
    capacity: Sequence[float] | np.ndarray,
    demand: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Absolute remaining capacity."""

    c = _ceutia_1d(capacity, name="capacity")
    d = _ceutia_1d(demand, name="demand")

    _ceutia_same_length(c, d)

    return c - d


def ceutia_capacity_headroom(
    capacity: Sequence[float] | np.ndarray,
    demand: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Relative remaining capacity."""

    c = _ceutia_1d(capacity, name="capacity")
    d = _ceutia_1d(demand, name="demand")

    _ceutia_same_length(c, d)

    return np.divide(
        c - d,
        c,
        out=np.zeros_like(c),
        where=c != 0,
    )


def ceutia_effective_capacity(
    nominal_capacity: Sequence[float] | np.ndarray,
    availability: Sequence[float] | np.ndarray,
    efficiency: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Effective capacity:

        C_effective = C_nominal × availability × efficiency

    This distinguishes nominal capacity from deployable capacity.
    """

    nominal = _ceutia_1d(
        nominal_capacity,
        name="nominal_capacity",
    )
    available = _ceutia_1d(
        availability,
        name="availability",
    )
    efficient = _ceutia_1d(
        efficiency,
        name="efficiency",
    )

    _ceutia_same_length(
        nominal,
        available,
        efficient,
    )

    return nominal * available * efficient


def ceutia_bottleneck_index(
    subsystem_capacities: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """
    Identifies the most constrained subsystem relative to the median
    subsystem capacity.

    Lower capacity means greater potential bottleneck.
    """

    matrix = _ceutia_2d(
        subsystem_capacities,
        name="subsystem_capacities",
    )

    latest = matrix[-1]

    if np.any(latest < 0):
        raise ValueError("Capacities cannot be negative.")

    median = float(np.median(latest))

    if median == 0:
        return 1.0

    minimum = float(np.min(latest))

    return float(
        1.0 - minimum / median
    )


def ceutia_time_to_exhaustion(
    reserve: Sequence[float] | np.ndarray,
    depletion_rate: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Estimated time to reserve exhaustion under the current depletion rate.

    This is a local deterministic projection, not a forecast unless
    stationarity/model assumptions are validated.
    """

    r = _ceutia_1d(reserve, name="reserve")
    d = _ceutia_1d(
        depletion_rate,
        name="depletion_rate",
    )

    _ceutia_same_length(r, d)

    result = np.full_like(r, np.inf, dtype=float)

    valid = d > 0

    result[valid] = r[valid] / d[valid]

    return result


# ============================================================================
# LOAD ACCUMULATION / ADAPTIVE RESERVE
# ============================================================================


def ceutia_accumulated_load(
    load: Sequence[float] | np.ndarray,
    *,
    dt: float = 1.0,
    decay: float = 0.0,
) -> np.ndarray:
    """
    Exponentially weighted accumulated load.

        L_t = load_t + (1-decay) L_(t-1)

    decay=0:
        complete memory.

    decay approaching 1:
        very short memory.

    This is a mathematical state variable, not a biological diagnosis.
    """

    if not 0 <= decay <= 1:
        raise ValueError("decay must be between 0 and 1.")

    if dt <= 0:
        raise ValueError("dt must be > 0.")

    x = _ceutia_1d(load, name="load")

    accumulated = np.zeros_like(x)

    accumulated[0] = x[0] * dt

    for index in range(1, len(x)):
        accumulated[index] = (
            accumulated[index - 1] * (1.0 - decay)
            + x[index] * dt
        )

    return accumulated


def ceutia_reserve_depletion(
    reserve: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """
    Negative change in reserve.

    Positive values indicate depletion.
    """

    r = _ceutia_1d(reserve, name="reserve")

    if len(r) < 2:
        return np.empty(0, dtype=float)

    return -np.diff(r)


# ============================================================================
# PROPAGATION / CASCADE
# ============================================================================


def ceutia_amplification_gain(
    input_signal: Sequence[float] | np.ndarray,
    output_signal: Sequence[float] | np.ndarray,
) -> float:
    """
    RMS output/input gain.

    Descriptive only; causal interpretation requires an identified mechanism.
    """

    x = _ceutia_1d(input_signal, name="input_signal")
    y = _ceutia_1d(output_signal, name="output_signal")

    _ceutia_same_length(x, y)

    rms_x = sqrt(float(np.mean(x**2)))
    rms_y = sqrt(float(np.mean(y**2)))

    return _ceutia_safe_divide(
        rms_y,
        rms_x,
    )


def ceutia_propagation_ratio(
    upstream: Sequence[float] | np.ndarray,
    downstream: Sequence[float] | np.ndarray,
) -> float:
    """
    Relative downstream change per unit upstream change.
    """

    upstream_array = _ceutia_1d(
        upstream,
        name="upstream",
    )
    downstream_array = _ceutia_1d(
        downstream,
        name="downstream",
    )

    _ceutia_same_length(
        upstream_array,
        downstream_array,
    )

    upstream_change = float(
        np.mean(np.abs(np.diff(upstream_array)))
    )

    downstream_change = float(
        np.mean(np.abs(np.diff(downstream_array)))
    )

    return _ceutia_safe_divide(
        downstream_change,
        upstream_change,
    )


def ceutia_cascade_amplification(
    stages: Sequence[Sequence[float] | np.ndarray],
) -> float:
    """
    Product of consecutive stage gains.

    stages:
        [stage_0, stage_1, ..., stage_n]

    A value >1 indicates net amplification in the observed chain.
    """

    if len(stages) < 2:
        raise ValueError(
            "At least two stages are required."
        )

    arrays = [
        _ceutia_1d(stage, name=f"stage_{index}")
        for index, stage in enumerate(stages)
    ]

    gains = [
        ceutia_amplification_gain(
            arrays[index],
            arrays[index + 1],
        )
        for index in range(len(arrays) - 1)
    ]

    return float(np.prod(gains))


def ceutia_feedback_strength(
    source: Sequence[float] | np.ndarray,
    response: Sequence[float] | np.ndarray,
    *,
    lag: int = 1,
) -> float:
    """
    Quantifies temporal association from source(t) to response(t+lag).

    This does NOT prove feedback. Feedback requires a reciprocal pathway,
    temporal ordering and a defensible mechanism.
    """

    return ceutia_lagged_cross_correlation(
        source,
        response,
        lag=lag,
    )


# ============================================================================
# REGIMES / TRANSITIONS / THRESHOLDS
# ============================================================================


def ceutia_threshold_distance(
    values: Sequence[float] | np.ndarray,
    threshold: float,
) -> np.ndarray:
    """Signed distance from a threshold."""

    x = _ceutia_1d(values, name="values")

    return threshold - x


def ceutia_threshold_proximity(
    values: Sequence[float] | np.ndarray,
    threshold: float,
    *,
    scale: float = 1.0,
) -> np.ndarray:
    """
    Bounded proximity to a threshold.

        1 = at threshold
        0 = infinitely far from threshold

    scale controls the spatial sensitivity.
    """

    if scale <= 0:
        raise ValueError("scale must be > 0.")

    x = _ceutia_1d(values, name="values")

    return np.exp(
        -np.abs(x - threshold) / scale
    )


def ceutia_threshold_approach_rate(
    values: Sequence[float] | np.ndarray,
    threshold: float,
    *,
    dt: float = 1.0,
) -> float:
    """
    Rate of change in distance to a threshold.

    Negative values indicate movement toward the threshold.
    """

    distance = np.abs(
        ceutia_threshold_distance(
            values,
            threshold,
        )
    )

    return ceutia_dynamic_slope(
        distance,
        dt=dt,
    )


def ceutia_regime_distance(
    current_state: Sequence[float] | np.ndarray,
    reference_state: Sequence[float] | np.ndarray,
    scale: Sequence[float] | np.ndarray | None = None,
) -> float:
    """Distance between current and reference regimes."""

    if scale is None:
        return ceutia_state_distance(
            current_state,
            reference_state,
        )

    return ceutia_standardized_state_distance(
        current_state,
        reference_state,
        scale,
    )


def ceutia_regime_transition_score(
    observations: Sequence[Sequence[float]] | np.ndarray,
    *,
    window: int,
) -> np.ndarray:
    """
    Change in local state-space distribution.

    This detects structural movement; it does not label the new state.
    """

    matrix = _ceutia_2d(
        observations,
        name="observations",
    )

    _ceutia_validate_window(
        window,
        matrix.shape[0],
    )

    scores = []

    for end in range(window * 2, matrix.shape[0] + 1):
        previous = matrix[
            end - 2 * window : end - window
        ]
        current = matrix[
            end - window : end
        ]

        previous_mean = np.mean(
            previous,
            axis=0,
        )
        current_mean = np.mean(
            current,
            axis=0,
        )

        pooled_scale = np.std(
            np.vstack([previous, current]),
            axis=0,
        )

        pooled_scale = np.where(
            pooled_scale == 0,
            1.0,
            pooled_scale,
        )

        scores.append(
            float(
                np.linalg.norm(
                    (current_mean - previous_mean)
                    / pooled_scale
                )
            )
        )

    return np.asarray(scores)


# ============================================================================
# HYSTERESIS / RECOVERY
# ============================================================================


def ceutia_hysteresis_gap(
    loading_path: Sequence[float] | np.ndarray,
    recovery_path: Sequence[float] | np.ndarray,
) -> float:
    """
    Difference between loading and recovery trajectories.

    A positive gap indicates asymmetric system response.

    This is descriptive and requires a meaningful matched perturbation/
    recovery design for interpretation as hysteresis.
    """

    loading = _ceutia_1d(
        loading_path,
        name="loading_path",
    )
    recovery = _ceutia_1d(
        recovery_path,
        name="recovery_path",
    )

    _ceutia_same_length(
        loading,
        recovery,
    )

    return float(
        np.mean(
            np.abs(loading - recovery)
        )
    )


def ceutia_recovery_time(
    values: Sequence[float] | np.ndarray,
    baseline: float,
    *,
    tolerance: float,
    dt: float = 1.0,
) -> float:
    """
    Time required to return within tolerance of baseline after the
    observed maximum deviation.

    Returns infinity if recovery is not observed.
    """

    if tolerance < 0:
        raise ValueError("tolerance must be >= 0.")

    if dt <= 0:
        raise ValueError("dt must be > 0.")

    x = _ceutia_1d(values, name="values")

    peak_index = int(
        np.argmax(
            np.abs(x - baseline)
        )
    )

    target = abs(tolerance)

    for index in range(
        peak_index,
        len(x),
    ):
        if abs(x[index] - baseline) <= target:
            return float(
                (index - peak_index) * dt
            )

    return float("inf")


def ceutia_recovery_ratio(
    baseline: float,
    perturbed: float,
    recovered: float,
) -> float:
    """
    Fraction of perturbation recovered.

        1 = full recovery
        0 = no recovery
        >1 = overshoot
    """

    perturbation = abs(
        perturbed - baseline
    )

    if perturbation == 0:
        return 1.0

    remaining = abs(
        recovered - baseline
    )

    return float(
        1.0 - remaining / perturbation
    )


def ceutia_resilience_area(
    capacity: Sequence[float] | np.ndarray,
    *,
    dt: float = 1.0,
) -> float:
    """
    Integral of normalized capacity over time.

    Requires capacity to already be normalized to a meaningful reference.
    """

    if dt <= 0:
        raise ValueError("dt must be > 0.")

    x = _ceutia_1d(
        capacity,
        name="capacity",
    )

    return float(
        np.trapezoid(x, dx=dt)
    )


# ============================================================================
# MULTISCALE / TEMPORAL CONCENTRATION
# ============================================================================


def ceutia_temporal_concentration(
    events: Sequence[float] | np.ndarray,
) -> float:
    """
    Concentration of event mass over time.

    Uses normalized squared event weights.

        1/n ≈ evenly distributed
        1   ≈ concentrated in one observation
    """

    x = np.abs(
        _ceutia_1d(events, name="events")
    )

    total = float(np.sum(x))

    if total == 0:
        return 0.0

    weights = x / total

    return float(
        np.sum(weights**2)
    )


def ceutia_burstiness_index(
    events: Sequence[float] | np.ndarray,
) -> float:
    """
    Burstiness based on coefficient of variation.

        B = (CV - 1) / (CV + 1)

    Descriptive only.
    """

    x = _ceutia_1d(events, name="events")

    if len(x) < 2:
        raise ValueError(
            "At least two observations are required."
        )

    mean = float(np.mean(x))
    std = float(np.std(x))

    if mean == 0:
        return 0.0

    cv = std / abs(mean)

    return float(
        (cv - 1.0) / (cv + 1.0)
    )


# ============================================================================
# UNCERTAINTY PROPAGATION
# ============================================================================


@dataclass(frozen=True)
class CeutiaUncertainValue:
    """
    Quantitative value with explicit uncertainty.

    mean:
        central estimate.

    standard_deviation:
        uncertainty around the estimate.

    lower/upper:
        optional externally supplied interval.

    confidence_level:
        semantic level of the supplied interval, if applicable.
    """

    mean: float
    standard_deviation: float = 0.0
    lower: float | None = None
    upper: float | None = None
    confidence_level: float | None = None
    evidence_status: DynamicEvidenceStatus = (
        DynamicEvidenceStatus.DERIVED
    )

    def __post_init__(self) -> None:
        if not all(
            isfinite(float(value))
            for value in (
                self.mean,
                self.standard_deviation,
            )
        ):
            raise ValueError(
                "mean and standard_deviation must be finite."
            )

        if self.standard_deviation < 0:
            raise ValueError(
                "standard_deviation must be >= 0."
            )

        if (
            self.lower is not None
            and self.upper is not None
            and self.lower > self.upper
        ):
            raise ValueError(
                "lower must not exceed upper."
            )

        if self.confidence_level is not None and not (
            0 < self.confidence_level < 1
        ):
            raise ValueError(
                "confidence_level must be between 0 and 1."
            )


def ceutia_propagate_linear_uncertainty(
    coefficients: Sequence[float] | np.ndarray,
    standard_deviations: Sequence[float] | np.ndarray,
) -> float:
    """
    First-order uncertainty propagation for:

        y = Σ a_i x_i
    """

    a = _ceutia_1d(
        coefficients,
        name="coefficients",
    )
    sigma = _ceutia_1d(
        standard_deviations,
        name="standard_deviations",
    )

    _ceutia_same_length(a, sigma)

    if np.any(sigma < 0):
        raise ValueError(
            "standard_deviations cannot be negative."
        )

    variance = np.sum(
        (a * sigma) ** 2
    )

    return float(
        sqrt(max(float(variance), 0.0))
    )


def ceutia_interval_overlap(
    lower_a: float,
    upper_a: float,
    lower_b: float,
    upper_b: float,
) -> float:
    """
    Jaccard-like overlap of two intervals.
    """

    if lower_a > upper_a or lower_b > upper_b:
        raise ValueError(
            "Interval lower bounds must not exceed upper bounds."
        )

    intersection = max(
        0.0,
        min(upper_a, upper_b)
        - max(lower_a, lower_b),
    )

    union = max(
        upper_a,
        upper_b,
    ) - min(
        lower_a,
        lower_b,
    )

    return _ceutia_safe_divide(
        intersection,
        union,
    )


# ============================================================================
# EARLY-WARNING COMPONENTS
# ============================================================================


@dataclass(frozen=True)
class CeutiaDynamicSignal:
    """
    Composite dynamic signal.

    It deliberately does not represent an alert or decision.
    """

    value: float
    components: Mapping[str, float]
    metric_type: DynamicMetricType
    evidence_status: DynamicEvidenceStatus
    interpretation_notes: tuple[str, ...] = field(
        default_factory=tuple
    )


def ceutia_early_warning_components(
    values: Sequence[float] | np.ndarray,
    *,
    threshold: float,
    window: int,
    lag: int = 1,
) -> Mapping[str, float]:
    """
    Compute independent dynamic-warning components:

        threshold proximity
        slope
        variance trend
        autocorrelation trend

    Components remain separate so downstream validation can determine
    which combinations are actually informative.
    """

    x = _ceutia_1d(values, name="values")
    _ceutia_validate_window(window, len(x))

    local = x[-window:]

    proximity = float(
        ceutia_threshold_proximity(
            local,
            threshold,
        )[-1]
    )

    slope = ceutia_dynamic_slope(local)

    variance_trend = ceutia_variance_trend(
        x,
        window=window,
    )

    autocorrelation_trend = ceutia_autocorrelation_trend(
        x,
        window=window,
        lag=lag,
    )

    return {
        "threshold_proximity": proximity,
        "dynamic_slope": slope,
        "variance_trend": variance_trend,
        "autocorrelation_trend": autocorrelation_trend,
    }


def ceutia_build_dynamic_signal(
    values: Sequence[float] | np.ndarray,
    *,
    threshold: float,
    window: int,
    lag: int = 1,
) -> CeutiaDynamicSignal:
    """
    Build a structured dynamic signal without converting it into an
    operational alert.
    """

    components = ceutia_early_warning_components(
        values,
        threshold=threshold,
        window=window,
        lag=lag,
    )

    normalized = np.asarray(
        list(components.values()),
        dtype=float,
    )

    scale = float(
        np.linalg.norm(normalized)
    )

    return CeutiaDynamicSignal(
        value=scale,
        components=components,
        metric_type=DynamicMetricType.EARLY_WARNING,
        evidence_status=DynamicEvidenceStatus.EXPLORATORY,
        interpretation_notes=(
            "Composite signal requires empirical validation.",
            "Components must not be interpreted as independent evidence "
            "when they derive from the same observations.",
            "A signal is not an alert or an autonomous decision.",
        ),
    )


# ============================================================================
# SYSTEM STATE SUMMARY
# ============================================================================


@dataclass(frozen=True)
class CeutiaSystemState:
    """
    Snapshot of a multidimensional dynamic system.

    The object preserves state, trajectory and capacity dimensions without
    collapsing them into a single universal score.
    """

    timestamp: Any
    state: tuple[float, ...]
    velocity: tuple[float, ...]
    acceleration: tuple[float, ...]
    speed: float
    acceleration_magnitude: float
    anomaly_score: float | None = None
    capacity_reserve: tuple[float, ...] | None = None
    uncertainty: tuple[float, ...] | None = None
    regime_distance: float | None = None
    evidence_status: DynamicEvidenceStatus = (
        DynamicEvidenceStatus.DERIVED
    )


def ceutia_build_system_state(
    observations: Sequence[Sequence[float]] | np.ndarray,
    *,
    timestamp: Any,
    capacity: Sequence[float] | np.ndarray | None = None,
    uncertainty: Sequence[float] | np.ndarray | None = None,
    reference_state: Sequence[float] | np.ndarray | None = None,
    reference_scale: Sequence[float] | np.ndarray | None = None,
    dt: float = 1.0,
) -> CeutiaSystemState:
    """
    Construct a state snapshot from the latest observed system trajectory.
    """

    matrix = _ceutia_2d(
        observations,
        name="observations",
    )

    if matrix.shape[0] < 3:
        raise ValueError(
            "At least three observations are required."
        )

    velocity = ceutia_state_velocity(
        matrix,
        dt=dt,
    )

    acceleration = ceutia_state_acceleration(
        matrix,
        dt=dt,
    )

    latest_state = matrix[-1]

    reserve: tuple[float, ...] | None = None

    if capacity is not None:
        c = _ceutia_1d(
            capacity,
            name="capacity",
        )

        if len(c) != matrix.shape[1]:
            raise ValueError(
                "capacity must have one value per state variable."
            )

        reserve = tuple(
            (c - latest_state).tolist()
        )

    uncertainty_tuple: tuple[float, ...] | None = None

    if uncertainty is not None:
        u = _ceutia_1d(
            uncertainty,
            name="uncertainty",
        )

        if len(u) != matrix.shape[1]:
            raise ValueError(
                "uncertainty must have one value per state variable."
            )

        uncertainty_tuple = tuple(
            u.tolist()
        )

    regime_distance = None

    if reference_state is not None:
        if reference_scale is None:
            regime_distance = ceutia_state_distance(
                latest_state,
                reference_state,
            )
        else:
            regime_distance = ceutia_standardized_state_distance(
                latest_state,
                reference_state,
                reference_scale,
            )

    anomaly_score = float(
        ceutia_multivariate_anomaly_score(matrix)[-1]
    )

    return CeutiaSystemState(
        timestamp=timestamp,
        state=tuple(latest_state.tolist()),
        velocity=tuple(velocity[-1].tolist()),
        acceleration=tuple(acceleration[-1].tolist()),
        speed=float(
            np.linalg.norm(velocity[-1])
        ),
        acceleration_magnitude=float(
            np.linalg.norm(acceleration[-1])
        ),
        anomaly_score=anomaly_score,
        capacity_reserve=reserve,
        uncertainty=uncertainty_tuple,
        regime_distance=regime_distance,
    )


# ============================================================================
# MULTIFACTORIAL SYSTEM PROFILE
# ============================================================================


@dataclass(frozen=True)
class CeutiaDynamicSystemProfile:
    """
    Non-collapsed description of the current system dynamics.

    No single scalar represents the whole system.
    """

    state: CeutiaSystemState
    interaction_matrix: tuple[tuple[float, ...], ...]
    synchronization: float
    effective_dimension: float
    principal_component_concentration: float
    coupling_change: float | None
    systemic_headroom: float | None
    bottleneck_index: float | None
    transition_score: float | None
    notes: tuple[str, ...] = field(
        default_factory=tuple
    )


def ceutia_build_dynamic_system_profile(
    observations: Sequence[Sequence[float]] | np.ndarray,
    *,
    timestamp: Any,
    window: int,
    capacity: Sequence[float] | np.ndarray | None = None,
    reference_state: Sequence[float] | np.ndarray | None = None,
    reference_scale: Sequence[float] | np.ndarray | None = None,
    dt: float = 1.0,
) -> CeutiaDynamicSystemProfile:
    """
    Construct a multidimensional dynamic profile.

    The profile preserves different dimensions of system behavior instead
    of collapsing them into one synthetic risk number.
    """

    matrix = _ceutia_2d(
        observations,
        name="observations",
    )

    if matrix.shape[0] < max(window, 3):
        raise ValueError(
            "Insufficient observations for requested window."
        )

    state = ceutia_build_system_state(
        matrix,
        timestamp=timestamp,
        capacity=capacity,
        reference_state=reference_state,
        reference_scale=reference_scale,
        dt=dt,
    )

    interaction = ceutia_interaction_matrix(
        matrix[-window:]
    )

    coupling = ceutia_coupling_change(
        matrix,
        window=window,
    )

    transition = ceutia_regime_transition_score(
        matrix,
        window=window,
    )

    headroom = None
    bottleneck = None

    if capacity is not None:
        latest = matrix[-1]

        c = _ceutia_1d(
            capacity,
            name="capacity",
        )

        if len(c) != matrix.shape[1]:
            raise ValueError(
                "capacity must have one value per state variable."
            )

        relative_headroom = np.divide(
            c - latest,
            c,
            out=np.zeros_like(c),
            where=c != 0,
        )

        headroom = float(
            np.mean(relative_headroom)
        )

        bottleneck = ceutia_bottleneck_index(
            np.vstack(
                [
                    c,
                    latest,
                ]
            )
        )

    notes = (
        "Association is not causation.",
        "Multivariate synchronization is not inherently positive or negative.",
        "A regime-transition score detects structural movement, not its cause.",
        "Capacity must be operationally defined before interpreting headroom.",
        "No component constitutes an autonomous security decision.",
    )

    return CeutiaDynamicSystemProfile(
        state=state,
        interaction_matrix=tuple(
            tuple(float(value) for value in row)
            for row in interaction
        ),
        synchronization=ceutia_synchronization_index(
            matrix[-window:]
        ),
        effective_dimension=ceutia_effective_dimension(
            matrix[-window:]
        ),
        principal_component_concentration=(
            ceutia_principal_component_concentration(
                matrix[-window:]
            )
        ),
        coupling_change=(
            float(coupling[-1])
            if len(coupling) > 0
            else None
        ),
        systemic_headroom=headroom,
        bottleneck_index=bottleneck,
        transition_score=(
            float(transition[-1])
            if len(transition) > 0
            else None
        ),
        notes=notes,
    )


# ============================================================================
# METRIC DEFINITIONS / REGISTRY
# ============================================================================


@dataclass(frozen=True)
class CeutiaAdvancedMetricDefinition:
    """Metadata for an advanced dynamic metric."""

    name: str
    metric_type: DynamicMetricType
    mathematical_role: str
    requires_time: bool
    supports_multivariate: bool
    supports_uncertainty: bool
    causal_interpretation_requires_validation: bool
    operational_use_requires_validation: bool


CEUTIA_ADVANCED_METRIC_REGISTRY: dict[
    str,
    CeutiaAdvancedMetricDefinition,
] = {
    "ceutia_state_velocity": CeutiaAdvancedMetricDefinition(
        name="ceutia_state_velocity",
        metric_type=DynamicMetricType.TRAJECTORY,
        mathematical_role="first temporal derivative",
        requires_time=True,
        supports_multivariate=True,
        supports_uncertainty=False,
        causal_interpretation_requires_validation=True,
        operational_use_requires_validation=True,
    ),
    "ceutia_state_acceleration": CeutiaAdvancedMetricDefinition(
        name="ceutia_state_acceleration",
        metric_type=DynamicMetricType.TRAJECTORY,
        mathematical_role="second temporal derivative",
        requires_time=True,
        supports_multivariate=True,
        supports_uncertainty=False,
        causal_interpretation_requires_validation=True,
        operational_use_requires_validation=True,
    ),
    "ceutia_multivariate_anomaly_score": CeutiaAdvancedMetricDefinition(
        name="ceutia_multivariate_anomaly_score",
        metric_type=DynamicMetricType.DESCRIPTIVE,
        mathematical_role="state-space anomaly",
        requires_time=True,
        supports_multivariate=True,
        supports_uncertainty=False,
        causal_interpretation_requires_validation=True,
        operational_use_requires_validation=True,
    ),
    "ceutia_interaction_effect": CeutiaAdvancedMetricDefinition(
        name="ceutia_interaction_effect",
        metric_type=DynamicMetricType.INTERACTION,
        mathematical_role="multiplicative interaction association",
        requires_time=False,
        supports_multivariate=False,
        supports_uncertainty=False,
        causal_interpretation_requires_validation=True,
        operational_use_requires_validation=True,
    ),
    "ceutia_dynamic_interaction_matrix": CeutiaAdvancedMetricDefinition(
        name="ceutia_dynamic_interaction_matrix",
        metric_type=DynamicMetricType.INTERACTION,
        mathematical_role="time-varying dependency structure",
        requires_time=True,
        supports_multivariate=True,
        supports_uncertainty=False,
        causal_interpretation_requires_validation=True,
        operational_use_requires_validation=True,
    ),
    "ceutia_effective_capacity": CeutiaAdvancedMetricDefinition(
        name="ceutia_effective_capacity",
        metric_type=DynamicMetricType.CAPACITY,
        mathematical_role="deployable system capacity",
        requires_time=True,
        supports_multivariate=True,
        supports_uncertainty=False,
        causal_interpretation_requires_validation=False,
        operational_use_requires_validation=True,
    ),
    "ceutia_cascade_amplification": CeutiaAdvancedMetricDefinition(
        name="ceutia_cascade_amplification",
        metric_type=DynamicMetricType.PROPAGATION,
        mathematical_role="multiplicative stage amplification",
        requires_time=True,
        supports_multivariate=True,
        supports_uncertainty=False,
        causal_interpretation_requires_validation=True,
        operational_use_requires_validation=True,
    ),
    "ceutia_regime_transition_score": CeutiaAdvancedMetricDefinition(
        name="ceutia_regime_transition_score",
        metric_type=DynamicMetricType.TRANSITION,
        mathematical_role="change in local state distribution",
        requires_time=True,
        supports_multivariate=True,
        supports_uncertainty=False,
        causal_interpretation_requires_validation=True,
        operational_use_requires_validation=True,
    ),
    "ceutia_resilience_area": CeutiaAdvancedMetricDefinition(
        name="ceutia_resilience_area",
        metric_type=DynamicMetricType.RESILIENCE,
        mathematical_role="integrated normalized capacity",
        requires_time=True,
        supports_multivariate=False,
        supports_uncertainty=False,
        causal_interpretation_requires_validation=False,
        operational_use_requires_validation=True,
    ),
    "ceutia_propagate_linear_uncertainty": CeutiaAdvancedMetricDefinition(
        name="ceutia_propagate_linear_uncertainty",
        metric_type=DynamicMetricType.UNCERTAINTY,
        mathematical_role="first-order uncertainty propagation",
        requires_time=False,
        supports_multivariate=True,
        supports_uncertainty=True,
        causal_interpretation_requires_validation=False,
        operational_use_requires_validation=True,
    ),
}


def validate_ceutia_advanced_metric_registry() -> None:
    """Validate registry integrity at runtime."""

    for name, definition in (
        CEUTIA_ADVANCED_METRIC_REGISTRY.items()
    ):
        if name != definition.name:
            raise ValueError(
                "Metric registry key does not match metric definition name."
            )

        if not definition.operational_use_requires_validation:
            raise ValueError(
                "Operational metrics must require validation."
            )

        if (
            definition.causal_interpretation_requires_validation
            and not definition.operational_use_requires_validation
        ):
            raise ValueError(
                "Causal metrics cannot bypass operational validation."
            )


# ============================================================================
# SCIENTIFIC / EPISTEMIC INVARIANTS
# ============================================================================


CEUTIA_ADVANCED_METRIC_INVARIANTS: tuple[str, ...] = (
    "metric != evidence",
    "metric != hypothesis",
    "metric != causality",
    "metric != prediction",
    "metric != alert",
    "metric != decision",
    "correlation != causation",
    "temporal precedence != causation",
    "survival_under_red_team != truth",
    "statistical_significance != operational_significance",
    "nominal_capacity != effective_capacity",
    "global_capacity != accessible_capacity",
    "synchronization != resilience",
    "anomaly != danger",
    "migration != criminality",
    "group_identity != individual_risk",
    "uncertainty_must_not_be_discarded",
    "contradictory_evidence_must_not_be_silently_removed",
    "source_count != source_independence",
    "forecast != observation",
    "scenario != prediction",
    "signal != alert",
    "alert != autonomous_action",
)


def validate_ceutia_advanced_metric_invariants() -> tuple[str, ...]:
    """
    Return the mathematical/epistemic invariants governing this layer.
    """

    validate_ceutia_advanced_metric_registry()

    if len(CEUTIA_ADVANCED_METRIC_INVARIANTS) < 10:
        raise RuntimeError(
            "Advanced metric invariant set is incomplete."
        )

    return CEUTIA_ADVANCED_METRIC_INVARIANTS


# ============================================================================
# EXPORTS
# ============================================================================


_CEUTIA_ADVANCED_EXPORTS = [
    "DynamicMetricType",
    "DynamicEvidenceStatus",
    "InteractionKind",
    "CeutiaUncertainValue",
    "CeutiaDynamicSignal",
    "CeutiaSystemState",
    "CeutiaDynamicSystemProfile",
    "CeutiaAdvancedMetricDefinition",
    "ceutia_state_vector",
    "ceutia_state_mean",
    "ceutia_state_std",
    "ceutia_state_velocity",
    "ceutia_state_acceleration",
    "ceutia_state_speed",
    "ceutia_state_acceleration_magnitude",
    "ceutia_state_distance",
    "ceutia_standardized_state_distance",
    "ceutia_persistence",
    "ceutia_duration_above_threshold",
    "ceutia_time_above_threshold",
    "ceutia_autocorrelation",
    "ceutia_variance_trend",
    "ceutia_autocorrelation_trend",
    "ceutia_dynamic_slope",
    "ceutia_dynamic_acceleration",
    "ceutia_rolling_slope",
    "ceutia_rolling_coefficient_of_variation",
    "ceutia_multivariate_zscore",
    "ceutia_multivariate_anomaly_score",
    "ceutia_effective_dimension",
    "ceutia_principal_component_concentration",
    "ceutia_covariance_matrix",
    "ceutia_correlation_matrix",
    "ceutia_lagged_cross_correlation",
    "ceutia_autocorrelation_like",
    "ceutia_interaction_effect",
    "ceutia_interaction_matrix",
    "ceutia_dynamic_interaction_matrix",
    "ceutia_coupling_change",
    "ceutia_synchronization_index",
    "ceutia_redundancy_index",
    "ceutia_higher_order_interaction",
    "ceutia_utilization_ratio",
    "ceutia_capacity_reserve",
    "ceutia_capacity_headroom",
    "ceutia_effective_capacity",
    "ceutia_bottleneck_index",
    "ceutia_time_to_exhaustion",
    "ceutia_accumulated_load",
    "ceutia_reserve_depletion",
    "ceutia_amplification_gain",
    "ceutia_propagation_ratio",
    "ceutia_cascade_amplification",
    "ceutia_feedback_strength",
    "ceutia_threshold_distance",
    "ceutia_threshold_proximity",
    "ceutia_threshold_approach_rate",
    "ceutia_regime_distance",
    "ceutia_regime_transition_score",
    "ceutia_hysteresis_gap",
    "ceutia_recovery_time",
    "ceutia_recovery_ratio",
    "ceutia_resilience_area",
    "ceutia_temporal_concentration",
    "ceutia_burstiness_index",
    "ceutia_propagate_linear_uncertainty",
    "ceutia_interval_overlap",
    "ceutia_early_warning_components",
    "ceutia_build_dynamic_signal",
    "ceutia_build_system_state",
    "ceutia_build_dynamic_system_profile",
    "CEUTIA_ADVANCED_METRIC_REGISTRY",
    "validate_ceutia_advanced_metric_registry",
    "CEUTIA_ADVANCED_METRIC_INVARIANTS",
    "validate_ceutia_advanced_metric_invariants",
]

if "__all__" in globals():
    __all__.extend(
        name
        for name in _CEUTIA_ADVANCED_EXPORTS
        if name not in __all__
    )
else:
    __all__ = list(_CEUTIA_ADVANCED_EXPORTS)


# Do not execute scientific validation automatically at import time.
# Registry validation remains explicitly callable so importing metrics.py
# never silently turns a mathematical definition into an operational claim.

# metrics.py
│
├── métricas básicas existentes
├── métricas estadísticas existentes
├── métricas clínicas/epidemiológicas
├── métricas de capacidad/colas/redes
├── métricas dinámicas que ya añadimos
│
└── MULTIVARIATE / SYSTEM-LEVEL METRICS
    ├── estado multidimensional
    ├── velocidad/aceleración vectorial
    ├── covarianza dinámica
    ├── correlaciones dinámicas
    ├── interacción multifactorial
    ├── acoplamiento entre subsistemas
    ├── anomalía multivariante
    ├── distancia respecto al régimen histórico
    ├── emergencia
    ├── estabilidad
    ├── resiliencia
    ├── cascadas
    ├── propagación
    └── transición de régimen
    
    
    Añadir al final de backend/app/core/metrics.py, antes de __all__ si existe.
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
    w = np.asarray(weights, dtype=float)

    if w.ndim != 2 or w.shape != (n, n):
        raise MetricInputError("weights debe tener dimensión (n, n)")
    if not np.all(np.isfinite(w)):
        raise MetricInputError("weights contiene valores no finitos")
    if np.any(w < 0.0):
        raise MetricInputError("weights no puede contener valores negativos")

    w = w.copy()
    np.fill_diagonal(w, 0.0)

    if float(np.sum(w)) <= 0.0:
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
    """
    arr = _validate_territorial_vector(values, name="values", nonnegative=True)

    if arr.size < 2:
        return 1.0

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

    return float(np.mean(ratio[positive] * np.log(ratio[positive])))


def territorial_mean(
    values: Sequence[float] | np.ndarray,
) -> float:
    """Media territorial."""
    return float(np.mean(_validate_territorial_vector(values, name="values")))


def territorial_variance(
    values: Sequence[float] | np.ndarray,
) -> float:
    """Varianza transversal entre unidades territoriales."""
    return float(np.var(_validate_territorial_vector(values, name="values"), ddof=1))


def territorial_coefficient_of_variation(
    values: Sequence[float] | np.ndarray,
) -> float:
    """CV territorial = σ / |μ|."""
    arr = _validate_territorial_vector(values, name="values")
    mean_value = float(np.mean(arr))

    if mean_value == 0.0:
        raise MetricInputError("CV indefinido con media 0")

    return float(np.std(arr, ddof=1) / abs(mean_value))


def territorial_z_scores(
    values: Sequence[float] | np.ndarray,
) -> np.ndarray:
    """Estandarización transversal territorial."""
    arr = _validate_territorial_vector(values, name="values")
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
) -> int:
    """Unidad territorial con mayor utilización."""
    utilization_values = territorial_demand_per_capacity(demand, capacity)

    return int(np.argmax(utilization_values))


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
        return 0.0

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
) -> int:
    """
    Profundidad descriptiva de propagación basada en capas de unidades
    que pasan a estar activadas respecto a un estado inicial.

    Esta función no infiere causalidad.
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

    initial_active = initial > threshold
    final_active = final > threshold

    newly_active = final_active & ~initial_active

    if not np.any(newly_active):
        return 0

    return 1


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

    if p.shape[0] < 1:
        raise MetricInputError("No hay unidades territoriales")

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
    """
    matrix = territorial_multi_pressure_matrix(variables)

    if matrix.shape[1] < 2:
        return np.ones((1, 1), dtype=float)

    return np.corrcoef(matrix, rowvar=False)


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