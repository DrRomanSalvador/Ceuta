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
    """Z-score territorial independiente para cada dimensión.

    A constant dimension has no territorial contrast, so its standardized
    value is defined as zero rather than making the whole multidimensional
    profile undefined. This preserves the distinction between "no contrast"
    and invalid/non-finite input.
    """
    matrix = territorial_multi_pressure_matrix(pressures)
    if matrix.shape[0] < 2:
        raise MetricInputError("Se requieren al menos dos unidades territoriales")
    mean_values = np.mean(matrix, axis=0)
    std_values = np.std(matrix, axis=0, ddof=1)

    z = np.zeros_like(matrix, dtype=float)
    varying = std_values > 0.0
    if np.any(varying):
        z[:, varying] = (matrix[:, varying] - mean_values[varying]) / std_values[varying]
    return z


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
    """Fracción de dimensiones cuyo z-score territorial supera el umbral."""
    if threshold < 0.0:
        raise MetricInputError("threshold debe ser no negativo")
    z = territorial_multi_pressure_zscores(pressures)
    return np.mean(z >= threshold, axis=1)


def territorial_pressure_dependence(
    pressures: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """Dependencia media absoluta entre dimensiones no constantes."""
    matrix = territorial_multi_pressure_matrix(pressures)

    if matrix.shape[0] < 2:
        raise MetricInputError("Se requieren al menos dos observaciones territoriales")
    if matrix.shape[1] < 2:
        return 0.0
    if np.any(np.std(matrix, axis=0, ddof=1) == 0.0):
        raise MetricInputError("La dependencia por correlación no está definida para una dimensión constante")

    correlation = np.corrcoef(matrix, rowvar=False)
    upper = correlation[np.triu_indices(correlation.shape[0], k=1)]
    if not np.all(np.isfinite(upper)):
        raise MetricInputError("La dependencia territorial contiene valores no finitos")

    return float(np.mean(np.abs(upper)))


def territorial_pressure_concentration(
    pressures: Sequence[Sequence[float]] | np.ndarray,
) -> float:
    """Concentración territorial de la carga multidimensional."""
    score = territorial_multi_pressure_score(pressures)

    shifted = score - np.min(score)
    if np.allclose(shifted, 0.0):
        return float(1.0 / shifted.size)

    return territorial_concentration_hhi(shifted)
