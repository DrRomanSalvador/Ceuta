from __future__ import annotations

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


def test_territorial_metric_inventory_is_registered():
    required = {
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
    assert required.issubset(TERRITORIAL_SYSTEMIC_METRICS)
    for metric_id in required:
        definition = get_metric_definition(metric_id)
        assert definition.metric_id == metric_id
        assert definition.permitted_channels


def test_experimental_territorial_metrics_are_not_executable():
    for metric_id in (
        "territorial_bottleneck_migration",
        "territorial_load_transfer",
        "territorial_spatial_propagation",
        "territorial_cascade_depth",
    ):
        with pytest.raises(MetricNotValidatedError):
            assert_metric_executable(metric_id)


def test_territorial_share_normalizes():
    assert np.allclose(territorial_share([2.0, 3.0]), [0.4, 0.6])


def test_territorial_demand_per_capacity_rejects_zero_capacity():
    with pytest.raises(MetricInputError):
        territorial_demand_per_capacity([10.0], [0.0])


def test_capacity_reserve_and_depletion_preserve_negative_reserve():
    assert territorial_capacity_reserve(80.0, 100.0) == 20.0
    assert territorial_capacity_reserve(120.0, 100.0) == -20.0
    assert territorial_reserve_depletion(120.0, 100.0) == -0.2


def test_bottleneck_index_returns_none_on_tie():
    assert territorial_bottleneck_index({"a": 2.0, "b": 2.0}) is None


def test_bottleneck_migration_requires_identifiable_bottlenecks():
    assert territorial_bottleneck_migration({"a": 2.0, "b": 2.0}, {"a": 1.0, "b": 3.0}) is None


def test_bottleneck_ratio_is_finite():
    assert territorial_bottleneck_ratio(4.0, 2.0) == 2.0


def test_spatial_lag_row_normalizes():
    values = [1.0, 2.0, 3.0]
    weights = [
        [0.0, 1.0, 0.0],
        [1.0, 0.0, 1.0],
        [0.0, 1.0, 0.0],
    ]
    assert np.allclose(territorial_spatial_lag(values, weights), [2.0, 2.0, 2.0])


def test_spatial_lag_rejects_isolated_territory():
    weights = [
        [0.0, 1.0, 0.0],
        [1.0, 0.0, 0.0],
        [0.0, 0.0, 0.0],
    ]
    with pytest.raises(MetricInputError, match="vecino|conexión|fila"):
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


def test_spatial_propagation_is_finite():
    assert np.isfinite(
        territorial_spatial_propagation(
            [0.0, 1.0, 0.0],
            [1.0, 1.0, 0.0],
        )
    )


def test_dependency_matrix_rejects_insufficient_observations_and_constants():
    with pytest.raises(MetricInputError):
        territorial_dependency_matrix([[1.0], [2.0]], min_observations=2)
    with pytest.raises(MetricInputError):
        territorial_dependency_matrix([[1.0, 1.0], [2.0, 2.0], [3.0, 3.0]])


def test_systemic_sensitivity_matrix_rejects_nonfinite_inputs():
    with pytest.raises(MetricInputError):
        territorial_systemic_sensitivity_matrix([[1.0, np.nan], [2.0, 3.0]])


def test_pressure_breadth_fraction_uses_one_standardization():
    assert territorial_pressure_breadth_fraction([0.0, 1.0, 2.0], threshold=0.0) == pytest.approx(2 / 3)


def test_pressure_dependence_rejects_constant_dimension():
    with pytest.raises(MetricInputError):
        territorial_pressure_dependence([[1.0, 1.0], [2.0, 2.0], [3.0, 3.0]])


def test_cascade_depth_accepts_monotonic_observed_layers():
    assert territorial_cascade_depth([1.0, 0.0], [0.0, 1.0], propagation_layers=[[1.0, 0.0], [1.0, 1.0]]) == 2


def test_cascade_depth_does_not_claim_causality():
    definition = get_metric_definition("territorial_cascade_depth")
    assert "causal" in " ".join(definition.limitations).lower()


def test_normalized_entropy_rejects_single_unit():
    with pytest.raises(MetricInputError):
        territorial_normalized_entropy([1.0])


def test_spatiotemporal_variability_rejects_single_period():
    with pytest.raises(MetricInputError):
        territorial_spatiotemporal_variability([[1.0, 2.0]])


def test_observation_coverage_is_bounded():
    assert 0.0 <= territorial_observation_coverage([True, False, True]) <= 1.0


def test_signal_to_noise_rejects_zero_noise():
    with pytest.raises(MetricInputError):
        territorial_signal_to_noise([1.0, 1.0], [0.0, 0.0])


def test_theil_includes_zero_observations_in_population_weighting():
    assert territorial_theil([0.0, 1.0, 3.0]) == pytest.approx((1 / 4) * np.log(1 / 4) + (3 / 4) * np.log(3 / 4))


def test_calibration_in_the_large_rejects_endpoint_prevalence():
    with pytest.raises(MetricInputError):
        calibration_in_the_large([0.0, 0.0], [0.2, 0.3])
    with pytest.raises(MetricInputError):
        calibration_in_the_large([1.0, 1.0], [0.7, 0.8])


def test_calibration_slope_rejects_endpoint_prevalence():
    with pytest.raises(MetricInputError):
        calibration_slope([0.0, 0.0, 1.0], [0.2, 0.3, 0.4])


def test_calibration_rejects_endpoint_predictions():
    with pytest.raises(MetricInputError):
        calibration_in_the_large([0.0, 1.0], [0.0, 1.0])
    with pytest.raises(MetricInputError):
        calibration_slope([0.0, 1.0, 1.0], [0.2, 1.0, 0.8])


def test_ddof_one_metrics_require_two_observations():
    with pytest.raises(MetricInputError):
        variance([1.0])
    with pytest.raises(MetricInputError):
        z_score([1.0], 1.0)
    with pytest.raises(MetricInputError):
        autocorrelation([1.0, 2.0], lag=2)
    with pytest.raises(MetricInputError):
        territorial_variance([1.0])


def test_strategic_probability_output_is_gated():
    with pytest.raises(MetricNotValidatedError):
        validate_probability_output(0.5, metric_id="territorial_bottleneck_migration", channel=OutputChannel.PUBLIC_USER)


def test_migration_event_is_not_reinterpreted_as_danger():
    definition = get_metric_definition("border_entry_event")
    assert not definition.executable
    assert "criminalidad" in " ".join(definition.limitations).lower()
    with pytest.raises(MetricNotPermittedError):
        assert_output_permitted("border_entry_event", OutputChannel.PUBLIC_USER)


def test_registry_integrity():
    validate_registry_integrity()
