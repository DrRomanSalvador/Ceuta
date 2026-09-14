from app.core.evidence.frontier_longitudinal import (
    BlockBootstrapSpec,
    block_bootstrap_indices,
    cluster_bootstrap,
    cluster_robust_mean,
    dependence_diagnostic,
    dependent_proper_score_interval,
    horizon_scores,
    temporal_calibration_robust,
    validate_frontier_contract,
)
from app.core.evidence.frontier_selection_transport import (
    nested_temporal_cv,
    optimism_corrected_bootstrap,
    transport_validate,
)
from app.core.evidence.frontier_temporal import strict_rolling_origin
from app.core.evidence.longitudinal_validation import LongitudinalRecord


def _records() -> list[LongitudinalRecord]:
    return [
        LongitudinalRecord("a", 1, 0, 0.2, cluster_id="x", horizon=1),
        LongitudinalRecord("a", 2, 1, 0.7, cluster_id="x", horizon=2),
        LongitudinalRecord("b", 1, 0, 0.1, cluster_id="y", horizon=1),
        LongitudinalRecord("b", 2, 0, 0.2, cluster_id="y", horizon=2),
        LongitudinalRecord("c", 1, 1, 0.8, cluster_id="z", horizon=1),
        LongitudinalRecord("c", 2, 1, 0.9, cluster_id="z", horizon=2),
        LongitudinalRecord("d", 1, 0, 0.3, cluster_id="w", horizon=1),
        LongitudinalRecord("d", 2, 1, 0.6, cluster_id="w", horizon=2),
        LongitudinalRecord("e", 3, 1, 0.7, cluster_id="v", horizon=1),
        LongitudinalRecord("f", 3, 0, 0.3, cluster_id="u", horizon=1),
        LongitudinalRecord("g", 4, 1, 0.8, cluster_id="t", horizon=1),
    ]


def test_dependence_diagnostic_counts_independent_units():
    result = dependence_diagnostic(_records())
    assert result.n_observations == 11
    assert result.independent_units == 7
    assert result.max_repeated_per_unit == 2


def test_cluster_bootstrap_preserves_repeated_units():
    result = cluster_bootstrap(
        _records(), lambda rows: sum(r.prediction for r in rows) / len(rows), replicates=500, seed=3
    )
    assert result.independent_unit == "entity"
    assert result.replicates == 500
    assert result.ci_low <= result.ci_high


def test_true_block_bootstrap_generates_full_samples():
    indices = block_bootstrap_indices(_records(), BlockBootstrapSpec("circular", 2, 500, 7))
    assert len(indices) == 500
    assert all(len(sample) == 11 for sample in indices)


def test_cluster_robust_mean_uses_units_not_rows():
    records = _records()
    result = cluster_robust_mean(records, [r.prediction for r in records])
    assert result.independent_unit == "entity"
    assert result.replicates == 0
    assert result.standard_error >= 0


def test_proper_score_interval_is_dependence_aware():
    result = dependent_proper_score_interval(_records(), replicates=500, seed=11)
    assert result.method == "cluster_bootstrap_percentile"
    assert result.replicates == 500


def test_horizon_scoring_is_explicit():
    result = horizon_scores(_records())
    assert [item.horizon for item in result.horizons] == [1, 2]
    assert result.integrated_brier >= 0


def test_frontier_contract_blocks_incomplete_validation():
    result = validate_frontier_contract(
        independent_unit="entity",
        temporal_validation=True,
        dependence_aware_uncertainty=True,
        proper_scoring=True,
        optimism_correction=False,
        nested_selection=True,
        transport_validation=True,
        missingness_assessed=True,
        leakage_checked=True,
    )
    assert not result.decision_ready
    assert "optimism correction is absent" in result.blockers


def test_optimism_correction_is_nested_inside_bootstrap():
    records = _records()
    result = optimism_corrected_bootstrap(
        records,
        fit=lambda rows: sum(r.outcome for r in rows) / len(rows),
        score=lambda model, rows: -sum(abs(model - r.outcome) for r in rows) / len(rows),
        replicates=500,
        seed=5,
    )
    assert result.corrected == result.apparent - result.optimism
    assert result.unit == "entity"


def test_nested_temporal_cv_keeps_selection_inside_outer_training():
    records = _records()
    outer_design = strict_rolling_origin(
        records, initial_train_duration=1, test_duration=1, step=1, purge_gap=0, expanding=True
    )
    inner_design = strict_rolling_origin(
        records, initial_train_duration=1, test_duration=1, step=1, purge_gap=0, expanding=True
    )
    result = nested_temporal_cv(
        records,
        outer_design,
        inner_design,
        parameters=(0, 1),
        fit=lambda rows, parameter: parameter,
        score=lambda model, rows: -sum(abs(model - r.outcome) for r in rows) / len(rows),
    )
    assert len(result.outer_scores) == len(outer_design)
    assert len(result.selected_parameters) == len(outer_design)


def test_strict_temporal_design_has_no_overlap():
    records = _records()
    folds = strict_rolling_origin(
        records, initial_train_duration=1, test_duration=1, step=1, purge_gap=0
    )
    for fold in folds:
        assert max(records[i].time for i in fold.train_indices) < min(
            records[i].time for i in fold.test_indices
        )


def test_temporal_calibration_reports_robust_intervals():
    records = _records()
    folds = strict_rolling_origin(
        records, initial_train_duration=1, test_duration=1, step=1, purge_gap=0
    )
    result = temporal_calibration_robust(records, folds, replicates=500, seed=13)
    assert len(result) == len(folds)
    assert all(item.replicates >= 250 for item in result)
    assert all(item.intercept_ci[0] <= item.intercept_ci[1] for item in result)


def test_transport_validation_does_not_refit_target():
    source = _records()
    target = [
        LongitudinalRecord("t1", 1, 0, 0.2),
        LongitudinalRecord("t2", 1, 1, 0.8),
        LongitudinalRecord("t3", 1, 0, 0.3),
    ]
    result = transport_validate(
        source, target, lambda rows: [r.prediction for r in rows], replicates=500
    )
    assert not result.target_refit
    assert result.target_independent_units == 3
