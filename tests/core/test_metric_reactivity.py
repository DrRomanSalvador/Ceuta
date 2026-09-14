from datetime import datetime, timedelta, timezone

import pytest

from app.core.scientific.metric_reactivity import (
    IndicatorObservation,
    IndicatorSpec,
    MetricReactivityMonitor,
)


def _monitor(tmp_path):
    monitor = MetricReactivityMonitor(storage_path=str(tmp_path / "reactivity.sqlite"), max_exposure_observations=4)
    monitor.register(IndicatorSpec("primary", "v1", "underlying outcome", True, "risk", "outcome:underlying"))
    monitor.register(IndicatorSpec("backup", "v1", "independent mechanism", False, "risk"))
    return monitor


def test_targetable_indicator_requires_causal_anchor(tmp_path):
    with pytest.raises(ValueError):
        MetricReactivityMonitor(storage_path=str(tmp_path / "x.sqlite")).register(
            IndicatorSpec("bad", "v1", "proxy", True, "risk")
        )


def test_prolonged_exposure_degrades_and_requires_review(tmp_path):
    monitor = _monitor(tmp_path)
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for i in range(4):
        monitor.observe(IndicatorObservation("primary", float(i + 1), now + timedelta(days=i), "source-a", True))
    usable, validity, flags, disposition = monitor.governance_state("primary")
    assert usable
    assert validity < 1.0
    assert flags == 1
    assert disposition == "review_required"


def test_cross_source_divergence_is_detected(tmp_path):
    monitor = _monitor(tmp_path)
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for i in range(3):
        monitor.observe(IndicatorObservation("primary", 1.0 + i * 0.01, now + timedelta(days=i), "trusted", False))
        monitor.observe(IndicatorObservation("primary", 10.0 + i, now + timedelta(days=i), "alternate", False))
    diagnostics = monitor.diagnose("primary")
    assert diagnostics.cross_source_divergence > 0.45
    assert "cross_source_divergence" in diagnostics.flags


def test_indicator_outcome_decoupling_and_persistence(tmp_path):
    path = tmp_path / "reactivity.sqlite"
    monitor = MetricReactivityMonitor(storage_path=str(path), max_exposure_observations=10)
    monitor.register(IndicatorSpec("primary", "v1", "underlying outcome", True, "risk", "outcome:underlying"))
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for i, value in enumerate((1.0, 3.0, 5.0, 9.0)):
        monitor.observe(IndicatorObservation("primary", value, now + timedelta(days=i), "source", False))
    diagnostics = monitor.diagnose("primary", outcomes=(1.0, 1.0, 1.0, 1.0))
    assert diagnostics.outcome_decoupling > 0.45
    restored = MetricReactivityMonitor(storage_path=str(path), max_exposure_observations=10)
    assert restored.diagnose("primary", outcomes=(1.0, 1.0, 1.0, 1.0)).observation_count == 4


def test_rotation_requires_same_rotation_group(tmp_path):
    monitor = _monitor(tmp_path)
    monitor.register(IndicatorSpec("other", "v1", "other", False, "different"))
    with pytest.raises(ValueError):
        monitor.rotate("primary", replacement_id="other")
