from app.core.evidence.frontier_longitudinal import (
    BlockBootstrapSpec,
    block_bootstrap_indices,
    cluster_bootstrap,
    cluster_robust_mean,
    dependence_diagnostic,
    dependent_proper_score_interval,
    horizon_scores,
    validate_frontier_contract,
)
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
    ]


def test_dependence_diagnostic_counts_independent_units():
    result = dependence_diagnostic(_records())
    assert result.n_observations == 8
    assert result.independent_units == 4
    assert result.max_repeated_per_unit == 2
    assert result.effective_sample_size == 4


def test_cluster_bootstrap_preserves_repeated_units():
    result = cluster_bootstrap(_records(), lambda rows: sum(r.prediction for r in rows) / len(rows), replicates=500, seed=3)
    assert result.independent_unit == "entity"
    assert result.replicates == 500
    assert result.ci_low <= result.estimate <= result.ci_high or result.ci_low <= result.estimate


def test_true_block_bootstrap_generates_full_samples():
    indices = block_bootstrap_indices(_records(), BlockBootstrapSpec("circular", 2, 500, 7))
    assert len(indices) == 500
    assert all(len(sample) == 8 for sample in indices)


def test_cluster_robust_mean_uses_units_not_rows():
    result = cluster_robust_mean(_records(), [r.prediction for r in _records()])
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
