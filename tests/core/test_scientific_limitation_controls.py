from datetime import datetime, timedelta, timezone

import pytest

from app.core.scientific.limitation_controls import (
    BaselineSpec,
    FeatureDependency,
    FrozenBaselineRegistry,
    PITFeature,
    PITManifest,
    binary_calibration,
    cluster_bootstrap_mean,
)


def _time(minutes: int) -> datetime:
    return datetime(2026, 9, 16, 6, 0, tzinfo=timezone.utc) + timedelta(minutes=minutes)


def _dependency(**overrides: object) -> FeatureDependency:
    values: dict[str, object] = {
        "dependency_id": "d1",
        "source_id": "source-a",
        "source_version": "v1",
        "publication_time": _time(-20),
        "acquisition_time": _time(-10),
        "revision": 1,
        "transformation_id": "identity-v1",
    }
    values.update(overrides)
    return FeatureDependency(**values)


def test_pit_manifest_binds_feature_values_and_rejects_future_dependency() -> None:
    manifest = PITManifest.build(
        forecast_origin=_time(0),
        information_cutoff=_time(-5),
        dependencies=(_dependency(),),
        features=(PITFeature("x", 1.5, ("d1",)),),
    )
    assert manifest.manifest_fingerprint
    assert manifest.feature_fingerprint

    with pytest.raises(ValueError, match="ineligible"):
        PITManifest.build(
            forecast_origin=_time(0),
            information_cutoff=_time(-5),
            dependencies=(_dependency(publication_time=_time(1)),),
            features=(PITFeature("x", 1.5, ("d1",)),),
        )


def test_future_revision_cannot_masquerade_as_same_pit_state() -> None:
    first = PITManifest.build(
        forecast_origin=_time(0),
        information_cutoff=_time(-5),
        dependencies=(_dependency(revision=1),),
        features=(PITFeature("x", 1.5, ("d1",)),),
    )
    revised = PITManifest.build(
        forecast_origin=_time(0),
        information_cutoff=_time(-5),
        dependencies=(_dependency(revision=2),),
        features=(PITFeature("x", 1.5, ("d1",)),),
    )
    assert first.manifest_fingerprint != revised.manifest_fingerprint


def test_baseline_identity_is_immutable() -> None:
    registry = FrozenBaselineRegistry()
    original = BaselineSpec("prevalence", "1", "training prevalence", "ceuta", _time(-60), _time(-1))
    assert registry.register(original) == original.identity
    assert registry.register(original) == original.identity
    changed = BaselineSpec("prevalence", "1", "retrospectively tuned prevalence", "ceuta", _time(-60), _time(-1))
    with pytest.raises(ValueError, match="immutable"):
        registry.register(changed)


def test_cluster_bootstrap_does_not_treat_repeated_rows_as_independent() -> None:
    result = cluster_bootstrap_mean([0.0, 1.0, 0.0, 1.0], ["a", "a", "b", "b"], resamples=200)
    assert result.unit == "cluster"
    assert result.n_observations == 4
    assert result.n_units == 2


def test_calibration_uses_proper_scores_and_does_not_upgrade_scientific_status() -> None:
    result = binary_calibration([0, 1, 1, 0], [0.1, 0.8, 0.7, 0.2])
    assert result["brier"] is not None
    assert result["log_loss"] is not None
    assert result["expected_calibration_error"] is not None
    assert result["prospective_validity_status"] == "NOT_ESTABLISHED"
