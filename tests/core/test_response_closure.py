from datetime import datetime, timedelta, timezone
import tempfile
import pytest

from app.core.scientific.response_closure import ObservedOutcome, ResponseClosureRegistry, ResponsePath

BASE = datetime(2030, 1, 1, tzinfo=timezone.utc)


def test_response_is_incomplete_until_feasible_action_and_observed_outcome():
    registry = ResponseClosureRegistry()
    path = ResponsePath("path-1", "pred-1", "decision-1", "action-1", "policy-1", True, BASE, BASE + timedelta(days=2), ("evidence-1",))
    registry.register(path)
    assert not registry.assess("path-1").complete
    registry.record_outcome(ObservedOutcome("path-1", "outcome-1", BASE + timedelta(days=3), 1.0, "official-1"))
    assert registry.assess("path-1").complete


def test_infeasible_path_remains_open_even_with_outcome():
    registry = ResponseClosureRegistry()
    path = ResponsePath("path-2", "pred-2", "decision-2", "action-2", "policy-2", False, BASE, BASE + timedelta(days=2), ("evidence-2",))
    registry.register(path)
    registry.record_outcome(ObservedOutcome("path-2", "outcome-2", BASE + timedelta(days=3), 0.0, "official-2"))
    assessment = registry.assess("path-2")
    assert not assessment.complete
    assert assessment.missing == ("feasible_response",)


def test_warning_without_response_is_representable_without_synthetic_action_id():
    registry = ResponseClosureRegistry()
    path = ResponsePath("path-no-action", "pred-3", "decision-3", "", "policy-3", True, BASE, BASE + timedelta(days=2), ("warning-evidence",), response_status="NO_ACTION", non_execution_reason="no action authorized")
    registry.register(path)
    registry.record_outcome(ObservedOutcome("path-no-action", "outcome-3", BASE + timedelta(days=2), 1.0, "official-3"))
    assessment = registry.assess("path-no-action")
    assert assessment.complete
    assert registry.path("path-no-action").response_status == "NO_ACTION"


def test_planned_response_cannot_be_closed_as_executed():
    registry = ResponseClosureRegistry()
    path = ResponsePath("path-planned", "pred-4", "decision-4", "action-4", "policy-4", True, BASE, BASE + timedelta(days=2), ("evidence-4",), response_status="PLANNED")
    registry.register(path)
    registry.record_outcome(ObservedOutcome("path-planned", "outcome-4", BASE + timedelta(days=2), 1.0, "official-4"))
    assessment = registry.assess("path-planned")
    assert not assessment.complete
    assert assessment.missing == ("response_execution",)


def test_non_execution_requires_reason_or_capacity_constraint():
    with pytest.raises(ValueError):
        ResponsePath("path-failed", "pred-5", "decision-5", "action-5", "policy-5", True, BASE, BASE + timedelta(days=2), ("evidence-5",), response_status="FAILED")


def test_response_closure_persists():
    with tempfile.NamedTemporaryFile(suffix=".sqlite") as handle:
        first = ResponseClosureRegistry(handle.name)
        first.register(ResponsePath("p", "pred", "dec", "act", "policy", True, BASE, BASE + timedelta(days=1), ("e",)))
        first.record_outcome(ObservedOutcome("p", "o", BASE + timedelta(days=2), 1.0, "src"))
        second = ResponseClosureRegistry(handle.name)
        assert second.assess("p").complete
        assert second.outcome("p").source_id == "src"
