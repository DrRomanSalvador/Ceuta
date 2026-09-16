from datetime import datetime, timedelta, timezone

import pytest

from backend.app.core.scientific.governance_signals import GovernanceDisposition, ScientificGovernance
from backend.app.core.scientific.nonstationarity import NonStationarityMonitor, RegimeObservation
from backend.app.core.scientific.nonstationarity_adapter import NonStationarityGovernanceAdapter


def _obs(values, *, low=0.0, high=10.0):
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return tuple(
        RegimeObservation(start + timedelta(days=i), float(value), low, high, "source-a", f"prov-{i}")
        for i, value in enumerate(values)
    )


def test_structural_shift_is_persisted_and_downgraded(tmp_path):
    monitor = NonStationarityMonitor(str(tmp_path / "ns.sqlite"), window=4, mean_shift=0.5)
    assessment = monitor.assess(_obs([1, 1, 1, 1, 1, 1, 1, 1, 4, 4, 4, 4]))
    assert assessment.regime_change is True
    assert assessment.state == "review"
    assert monitor.verify_integrity() is True


def test_deployment_extrapolation_abstains(tmp_path):
    monitor = NonStationarityMonitor(str(tmp_path / "ns.sqlite"), window=4)
    assessment = monitor.assess(_obs([1, 1, 1, 1, 1, 1, 1, 1]), deployment_value=20.0)
    assert assessment.extrapolation is True
    assert assessment.state == "abstain"

    value = NonStationarityGovernanceAdapter(code_revision="rev-1", configuration_hash="cfg-1").to_input(
        assessment, evidence_ids=("e1",), provenance_refs=("p1",)
    )
    signal = ScientificGovernance().evaluate("decision-1", value)
    assert signal.disposition == GovernanceDisposition.ABSTAIN


def test_insufficient_history_is_not_silently_assumed_stationary(tmp_path):
    monitor = NonStationarityMonitor(str(tmp_path / "ns.sqlite"), window=4)
    with pytest.raises(ValueError):
        monitor.assess(_obs([1, 1, 1, 1, 1]))
