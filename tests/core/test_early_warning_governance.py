from datetime import datetime, timedelta, timezone

import pytest

from app.core.scientific.early_warning_governance import (
    CriticalSlowingDown,
    CryWolfPolicy,
    CryWolfTracker,
    EarlyWarningGovernance,
    PredictionMarketObservation,
    VulnerabilityProfile,
    WarningOutcome,
)


def test_false_alarms_degrade_credibility_asymmetrically():
    policy = CryWolfPolicy(false_alarm_penalty=3.0, correct_warning_reward=1.0)
    tracker = CryWolfTracker(policy)
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for i in range(5):
        tracker.record(WarningOutcome(f"w{i}", True, True, now + timedelta(days=i)))
    trusted = tracker.state()

    noisy = CryWolfTracker(policy)
    for i in range(5):
        noisy.record(WarningOutcome(f"w{i}", True, False, now + timedelta(days=i)))
    degraded = noisy.state()

    assert degraded.trust < trusted.trust
    assert degraded.preparedness < trusted.preparedness
    assert tracker.disposition() == "release"
    assert noisy.disposition() == "abstain"


def test_cry_wolf_persistence_survives_restart(tmp_path):
    path = str(tmp_path / "warnings.sqlite")
    policy = CryWolfPolicy(false_alarm_penalty=2.0, correct_warning_reward=1.0)
    tracker = CryWolfTracker(policy, storage_path=path)
    tracker.record(WarningOutcome("false-1", True, False, datetime(2026, 1, 1, tzinfo=timezone.utc)))
    tracker.record(WarningOutcome("true-1", True, True, datetime(2026, 1, 2, tzinfo=timezone.utc)))

    restored = CryWolfTracker(policy, storage_path=path)
    assert restored.state().false_alarms == 1
    assert restored.state().correct_warnings == 1


def test_critical_slowing_down_is_bounded_by_data_contract():
    detector = CriticalSlowingDown(minimum_observations=30)
    short = detector.evaluate([float(i) for i in range(10)])
    assert not short.sufficient_data
    assert not short.usable_as_supporting_signal
    assert short.interpretation == "insufficient_data"

    values = [0.5 + 0.01 * (i % 3) for i in range(30)]
    usable = detector.evaluate(values)
    assert usable.sufficient_data
    assert usable.usable_as_supporting_signal
    assert -1.0 <= usable.lag1_autocorrelation <= 1.0

    confounded = detector.evaluate(values, confounders_present=True)
    assert not confounded.usable_as_supporting_signal
    assert confounded.interpretation == "confounded_do_not_release"


def test_prediction_market_is_benchmark_not_causal_authority():
    observation = PredictionMarketObservation(
        market_id="market-1",
        probability=0.7,
        liquidity_score=0.9,
        integrity_valid=True,
        observed_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    assert observation.usable_as_benchmark


def test_vulnerability_changes_response_design_not_hazard_probability():
    profile = VulnerabilityProfile(
        exposure=0.9,
        susceptibility=0.9,
        coping_capacity=0.1,
        structural_drivers=("institutional fragility", "resource dependence"),
    )
    assert profile.vulnerability_score > 0.5


def test_integrated_assessment_fails_closed_when_credibility_and_data_are_weak(tmp_path):
    path = str(tmp_path / "assessment.sqlite")
    tracker = CryWolfTracker(CryWolfPolicy(false_alarm_penalty=3.0), storage_path=path)
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for i in range(5):
        tracker.record(WarningOutcome(f"false-{i}", True, False, now + timedelta(days=i)))

    governance = EarlyWarningGovernance(tracker, storage_path=path)
    assessment = governance.assess(
        values=[float(i) for i in range(10)],
        vulnerability=VulnerabilityProfile(0.8, 0.8, 0.2, ("inequality",)),
        markets=(PredictionMarketObservation("m1", 0.6, 0.8, True, now),),
        now=now,
    )

    assert not assessment.alert_allowed
    assert "cry_wolf_credibility_below_abstain_threshold" in assessment.reasons
    assert "critical_slowing_down_insufficient_data" in assessment.reasons


def test_invalid_policy_rejects_symmetric_or_reverse_cry_wolf_weighting():
    with pytest.raises(ValueError):
        CryWolfPolicy(false_alarm_penalty=1.0, correct_warning_reward=1.0)
