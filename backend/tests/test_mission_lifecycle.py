import pytest

from app.missions.lifecycle import LifecycleError, MissionLifecycleGovernance


def metrics(**overrides):
    value = {"value": "HIGH", "complexity": "LOW", "validation": "PASS", "redundancy": "LOW", "coherence": "COHERENT", "usage": "RECURRING"}
    value.update(overrides)
    return value


def test_active_review_retains_mission():
    review = MissionLifecycleGovernance.review(mission_id="M", metrics=metrics(), evidence_refs=("e:1",))
    assert review.status == "ACTIVE_RETAIN"
    assert not review.action_required


def test_low_value_redundant_mission_is_proposed_for_retirement():
    review = MissionLifecycleGovernance.review(mission_id="M", metrics=metrics(value="LOW", redundancy="MATERIAL"), evidence_refs=("e:1",))
    assert review.status == "PROPOSE_RETIREMENT"
    MissionLifecycleGovernance.authorize_retirement(review, {"CAN_AUTHORIZE": True})


def test_lifecycle_review_fails_without_evidence():
    with pytest.raises(LifecycleError):
        MissionLifecycleGovernance.review(mission_id="M", metrics=metrics(), evidence_refs=())
