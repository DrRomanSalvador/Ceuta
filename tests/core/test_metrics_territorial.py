import numpy as np
import pytest

from app.core.metrics import (
    MetricInputError,
    MetricNotPermittedError,
    MetricNotValidatedError,
    OutputChannel,
    TERRITORIAL_SYSTEMIC_METRICS,
    assert_output_permitted,
    assert_metric_executable,
    autocorrelation,
    calibration_in_the_large,
    calibration_slope,
    get_metric_definition,
    territorial_bottleneck_index,
    territorial_bottleneck_migration,
    territorial_bottleneck_ratio,
    territorial_capacity_reserve,
    territorial_demand_per_capacity,
    territorial_dependency_matrix,
    territorial_gearys_c,
    territorial_morans_i,
    territorial_multi_pressure_score,
    territorial_normalized_entropy,
    territorial_observation_coverage,
    territorial_pressure_breadth_fraction,
    territorial_pressure_dependence,
    territorial_reserve_depletion,
    territorial_signal_to_noise,
    territorial_share,
    territorial_spatial_lag,
    territorial_spatial_propagation,
    territorial_cascade_depth,
    territorial_spatiotemporal_variability,
    territorial_systemic_sensitivity_matrix,
    territorial_theil,
    territorial_variance,
    validate_registry_integrity,
    validate_probability_output,
    variance,
    z_score,
)


REQUIRED_TERRITORIAL_METRICS = {
    "territorial_share",
    "territorial_morans_i",
    "territorial_gearys_c",
    "territorial_demand_per_capacity",
    "territorial_capacity_reserve",
    "territorial_bottleneck_migration",
    "territorial_load_transfer",
    "territorial_spatial_propagation",
    "territorial_cascade_depth",
    "territorial_observation_coverage",
    "territorial_signal_to_noise",
}


def test_territorial_metric_inventory_contains_required_implementations():
    assert REQUIRED_TERRITORIAL_METRICS <= set(TERRITORIAL_SYSTEMIC_METRICS)
    for metric_id in REQUIRED_TERRITORIAL_METRICS:
        assert callable(TERRITORIAL_SYSTEMIC_METRICS[metric_id])


def test_territorial_metric_inventory_is_epistemically_registered():
    for metric_id in REQUIRED_TERRITORIAL_METRICS:
        definition = get_metric_definition(metric_id)
        assert definition.id == metric_id
        assert definition.permitted_channels == frozenset({OutputChannel.INTERNAL, OutputChannel.PRIVATE})
    assert get_metric_definition("territorial_bottleneck_migration").executable is False
    assert get_metric_definition("territorial_spatial_propagation").executable is False
    assert get_metric_definition("territorial_cascade_depth").executable is False


def test_territorial_share_is_normalized():
    shares = territorial_share([1.0, 1.0, 2.0])
    assert np.allclose(shares, [0.25, 0.25, 0.5])
    assert np.isclose(np.sum(shares), 1.0)


def test_territorial_demand_capacity_rejects_zero_capacity():
    with pytest.raises(MetricInputError):
        territorial_demand_per_capacity([10.0, 5.0], [0.0, 5.0])


def test_territorial_capacity_reserve_preserves_negative_debt():
    reserve = territorial_capacity_reserve([12.0, 5.0], [10.0, 8.0])
    assert np.allclose(reserve, [-2.0, 3.0])
    depletion = territorial_reserve_depletion([-2.0, 3.0], [-4.0, 2.0])
    assert np.allclose(depletion, [2.0, 1.0])


def test_territorial_bottleneck_ties_are_not_arbitrarily_ranked():
    assert territorial_bottleneck_index([8.0, 8.0], [10.0, 10.0]) is None
    assert territorial_bottleneck_migration(
        [8.0, 2.0], [10.0, 10.0], [8.0, 8.0], [10.0, 10.0]
    ) is None
    assert territorial_bottleneck_migration(
        [8.0, 2.0], [10.0, 10.0], [2.0, 9.0], [10.0, 10.0]
    ) == 1
    assert territorial_bottleneck_migration(
        [8.0, 2.0], [10.0, 10.0], [7.0, 2.0], [10.0, 10.0]
    ) is None
    assert territorial_bottleneck_ratio([8.0, 2.0], [10.0, 10.0]) == pytest.approx(0.8)


def test_spatial_lag_uses_row_normalization():
    values = [1.0, 3.0, 5.0]
    weights = [
        [0.0, 1.0, 0.0],
        [1.0, 0.0, 1.0],
        [0.0, 1.0, 0.0],
    ]
    assert np.allclose(territorial_spatial_lag(values, weights), [3.0, 3.0, 3.0])


def test_spatial_lag_rejects_isolated_territory():
    weights = [
        [0.0, 1.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0],
    ]
    with pytest.raises(MetricInputError, match="vecinos|conexión|fila"):
        territorial_spatial_lag([1.0, 2.0, 3.0], weights)


def test_spatial_matrix_rejects_single_territory():
    with pytest.raises(MetricInputError):
        territorial_spatial_lag([1.0], [[0.0]])


def test_spatial_metrics_reject_constant_values():
    weights = [[0.0, 1.0], [1.0, 0.0]]
    with pytest.raises(MetricInputError):
        territorial_morans_i([2.0, 2.0], weights)
    with pytest.raises(MetricInputError):
        territorial_gearys_c([2.0, 2.0], weights)


def test_spatial_propagation_is_descriptive_and_finite():
    previous = [1.0, 2.0, 3.0]
    current = [2.0, 2.0, 5.0]
    weights = [
        [0.0, 1.0, 0.0],
        [1.0, 0.0, 1.0],
        [0.0, 1.0, 0.0],
    ]
    result = territorial_spatial_propagation(previous, current, weights)
    assert np.isfinite(result)
    assert result >= 0.0


def test_territorial_dependency_rejects_constant_or_single_observation():
    with pytest.raises(MetricInputError):
        territorial_dependency_matrix([[1.0, 2.0]])
    with pytest.raises(MetricInputError):
        territorial_dependency_matrix([[1.0, 2.0], [1.0, 3.0]])


def test_systemic_sensitivity_rejects_nonfinite_inputs():
    with pytest.raises(MetricInputError):
        territorial_systemic_sensitivity_matrix([[1.0], [np.nan]], [[1.0], [2.0]])


def test_pressure_breadth_fraction_uses_one_zscore_transform():
    pressures = [[0.0, 0.0], [1.0, 2.0], [2.0, 4.0]]
    score = territorial_multi_pressure_score(pressures)
    assert np.all(np.isfinite(score))
    breadth = territorial_pressure_breadth_fraction(pressures, threshold=0.0)
    assert np.allclose(breadth, [0.0, 1.0, 1.0])


def test_pressure_dependence_rejects_constant_dimension():
    with pytest.raises(MetricInputError):
        territorial_pressure_dependence([[1.0, 1.0], [2.0, 1.0]])


def test_cascade_depth_accepts_explicit_observed_layers():
    layers = [
        [0.0, 0.0, 0.0],
        [1.0, 0.0, 0.0],
        [1.0, 1.0, 0.0],
        [1.0, 1.0, 1.0],
    ]
    assert territorial_cascade_depth([0, 0, 0], [1, 1, 1], propagation_layers=layers) == 3
    with pytest.raises(MetricInputError):
        territorial_cascade_depth(
            [0, 0, 0], [1, 1, 1],
            propagation_layers=[[1, 0, 0], [0, 1, 0]],
        )


def test_cascade_depth_does_not_claim_causality():
    assert territorial_cascade_depth([0.0, 1.0], [1.0, 1.0]) == 1
    assert territorial_cascade_depth([1.0, 1.0], [1.0, 1.0]) == 0


def test_normalized_entropy_rejects_single_unit():
    with pytest.raises(MetricInputError):
        territorial_normalized_entropy([1.0])


def test_spatiotemporal_variability_rejects_single_period():
    with pytest.raises(MetricInputError):
        territorial_spatiotemporal_variability([[1.0, 2.0]])


def test_observation_coverage_is_bounded():
    coverage = territorial_observation_coverage([50.0, 100.0], [100.0, 100.0])
    assert np.all((coverage >= 0.0) & (coverage <= 1.0))
    with pytest.raises(MetricInputError):
        territorial_observation_coverage([101.0], [100.0])


def test_signal_to_noise_rejects_zero_noise():
    with pytest.raises(MetricInputError):
        territorial_signal_to_noise([1.0, 2.0], [0.0, 1.0])


def test_theil_zero_observation_keeps_population_weighting():
    values = np.array([0.0, 1.0, 3.0])
    mean_value = np.mean(values)
    ratios = values / mean_value
    expected = np.mean(np.where(values > 0.0, ratios * np.log(ratios), 0.0))
    assert territorial_theil(values) == pytest.approx(expected)


def test_calibration_in_the_large_rejects_boundary_prevalence_and_endpoint_logits():
    with pytest.raises(MetricInputError, match="prevalencia|prevalence|0 y 1|interior"):
        calibration_in_the_large([0, 0, 0], [0.1, 0.2, 0.3])
    with pytest.raises(MetricInputError, match="prevalencia|prevalence|0 y 1|interior"):
        calibration_in_the_large([1, 1, 1], [0.1, 0.2, 0.3])
    with pytest.raises(MetricInputError, match="probabilidades|probabilities|entre 0 y 1"):
        calibration_in_the_large([0, 1, 1], [0.0, 0.5, 1.0])
    with pytest.raises(MetricInputError, match="prevalencia|prevalence|0 y 1|interior"):
        calibration_slope([0, 0, 0], [0.1, 0.2, 0.3])
    with pytest.raises(MetricInputError, match="probabilidades|probabilities|entre 0 y 1"):
        calibration_slope([0, 1, 1], [0.0, 0.5, 1.0])


def test_ddof_one_requires_two_observations_across_metric_families():
    with pytest.raises(MetricInputError):
        variance([1.0])
    with pytest.raises(MetricInputError):
        z_score(1.0, [1.0])
    with pytest.raises(MetricInputError):
        autocorrelation([1.0, 2.0, 3.0], lag=2)
    with pytest.raises(MetricInputError):
        territorial_variance([1.0])


def test_registry_controls_unvalidated_strategic_probability():
    definition = get_metric_definition("intergroup_violence_early_warning")
    assert definition.executable is False
    with pytest.raises(MetricNotValidatedError):
        assert_metric_executable("intergroup_violence_early_warning")
    with pytest.raises(MetricNotPermittedError):
        assert_output_permitted("intergroup_violence_early_warning", OutputChannel.PUBLIC_USER)
    with pytest.raises(MetricNotValidatedError):
        validate_probability_output(
            "intergroup_violence_early_warning",
            [0.2, 0.8],
            calibrated=True,
            externally_validated=True,
        )


def test_migration_event_cannot_be_reinterpreted_as_danger():
    definition = get_metric_definition("border_entry_event")
    assert definition.executable is False
    assert any("criminalidad" in limitation.lower() for limitation in definition.limitations)
    with pytest.raises(MetricNotPermittedError):
        assert_output_permitted("border_entry_event", OutputChannel.PUBLIC_USER)


def test_registry_integrity_remains_executable():
    validate_registry_integrity()
