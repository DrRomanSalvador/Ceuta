from datetime import datetime, timedelta, timezone

from app.core.scientific.response_closure import ObservedOutcome, ResponseClosureRegistry, ResponsePath


BASE = datetime(2030, 1, 1, tzinfo=timezone.utc)


def test_response_is_incomplete_until_feasible_action_and_observed_outcome():
    registry = ResponseClosureRegistry()
    path = ResponsePath(
        path_id="path-1",
        prediction_id="pred-1",
        decision_id="decision-1",
        action_id="action-1",
        policy_id="policy-1",
        feasible=True,
        created_at=BASE,
        expected_outcome_due_at=BASE + timedelta(days=2),
        evidence_ids=("evidence-1",),
    )
    registry.register(path)
    assert not registry.assess("path-1").complete
    registry.record_outcome(ObservedOutcome("path-1", "outcome-1", BASE + timedelta(days=3), 1.0, "official-1"))
    assert registry.assess("path-1").complete


def test_infeasible_path_remains_open_even_with_outcome():
    registry = ResponseClosureRegistry()
    path = ResponsePath(
        path_id="path-2",
        prediction_id="pred-2",
        decision_id="decision-2",
        action_id="action-2",
        policy_id="policy-2",
        feasible=False,
        created_at=BASE,
        expected_outcome_due_at=BASE + timedelta(days=2),
        evidence_ids=("evidence-2",),
    )
    registry.register(path)
    registry.record_outcome(ObservedOutcome("path-2", "outcome-2", BASE + timedelta(days=3), 0.0, "official-2"))
    assessment = registry.assess("path-2")
    assert not assessment.complete
    assert assessment.missing == ("feasible_response",)


def test_response_closure_persists():
    import tempfile

    with tempfile.NamedTemporaryFile(suffix=".sqlite") as handle:
        first = ResponseClosureRegistry(handle.name)
        first.register(ResponsePath("p", "pred", "dec", "act", "policy", True, BASE, BASE + timedelta(days=1), ("e",)))
        first.record_outcome(ObservedOutcome("p", "o", BASE + timedelta(days=2), 1.0, "src"))
        second = ResponseClosureRegistry(handle.name)
        assert second.assess("p").complete
        assert second.outcome("p").source_id == "src"
