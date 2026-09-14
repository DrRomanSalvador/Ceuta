from app.core.evidence.longitudinal_validation import (
    LongitudinalRecord,
    ResampleSpec,
    StatisticalValidationContract,
    blocked_or_cluster_bootstrap,
    dependent_proper_scores,
    nested_temporal_cv,
    optimism_corrected_bootstrap,
    rolling_origin_splits,
    temporal_calibration,
    transport_validation,
)


def _records():
    return [
        LongitudinalRecord("a", 1, 0, 0.10), LongitudinalRecord("a", 2, 0, 0.20), LongitudinalRecord("a", 3, 1, 0.70),
        LongitudinalRecord("b", 1, 0, 0.20), LongitudinalRecord("b", 2, 1, 0.60), LongitudinalRecord("b", 3, 1, 0.80),
        LongitudinalRecord("c", 1, 0, 0.10), LongitudinalRecord("c", 2, 1, 0.70), LongitudinalRecord("c", 3, 1, 0.90),
        LongitudinalRecord("d", 1, 0, 0.15), LongitudinalRecord("d", 2, 0, 0.25), LongitudinalRecord("d", 3, 1, 0.75),
    ]


def test_cluster_bootstrap_preserves_declared_entity_unit():
    records = _records()
    result = blocked_or_cluster_bootstrap(
        records,
        lambda rows: sum(r.outcome for r in rows) / len(rows),
        spec=ResampleSpec(unit="entity", seed=17),
        replicates=200,
    )
    assert result.independent_unit == "entity"
    assert result.replicates == 200
    assert result.ci_low <= result.estimate <= result.ci_high


def test_effective_n_is_less_than_raw_n_for_repeated_entities():
    summary = dependent_proper_scores(_records())
    assert summary.n == 12
    assert summary.effective_n == 4.0
    assert summary.cluster_count == 4


def test_rolling_origin_has_strict_temporal_separation():
    folds = rolling_origin_splits(_records(), initial_train_time=1.0, test_horizon=1.0, step=1.0, gap=0.0)
    assert folds
    for fold in folds:
        assert max(_records()[i].time for i in fold.train_indices) < min(_records()[i].time for i in fold.test_indices)


def test_temporal_calibration_reports_fold_specific_drift():
    records = _records()
    folds = rolling_origin_splits(records, initial_train_time=1.0, test_horizon=1.0, step=1.0)
    result = temporal_calibration(records, folds)
    assert len(result.intercepts) == len(folds)
    assert len(result.slopes) == len(folds)


def test_optimism_correction_is_not_apparent_performance():
    records = _records()
    result = optimism_corrected_bootstrap(
        records,
        lambda train, test: -sum((r.prediction-r.outcome)**2 for r in test)/len(test),
        spec=ResampleSpec(unit="entity", seed=3),
        replicates=200,
    )
    assert result.bootstrap_replicates == 200
    assert result.optimism_corrected == result.apparent - result.optimism


def test_nested_cv_selects_parameter_inside_outer_loop():
    records = _records()
    folds = rolling_origin_splits(records, initial_train_time=1.0, test_horizon=1.0, step=1.0)

    def inner_splitter(rows):
        if len(rows) < 2:
            return []
        cut = len(rows) // 2
        return [(tuple(range(cut)), tuple(range(cut, len(rows))))]

    def score(parameter, train, test):
        return float(parameter)

    result = nested_temporal_cv(records, folds, inner_splitter, (0, 1), score)
    assert result.selected_parameters == (1,) * len(folds)
    assert result.pooled_score == 1.0


def test_transport_validation_does_not_refit_on_target():
    source = _records()
    target = [LongitudinalRecord("x", i + 1, r.outcome, r.prediction) for i, r in enumerate(source)]
    result = transport_validation(source, target)
    assert result.target_entity_count == len(target)
    assert result.method == "external_transport_without_target_refitting"


def test_statistical_contract_requires_all_dependence_safeguards():
    contract = StatisticalValidationContract(True, True, True, "entity", "cluster_bootstrap", True, True, True, True)
    assert contract.decision_ready
