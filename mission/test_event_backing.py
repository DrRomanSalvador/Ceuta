import pytest

from .bootstrap import _validate_event_backing


def test_event_backing_accepts_existing_mutation_event():
    _validate_event_backing([{"handoff_id": "HF-1", "mutation_event_id": "EV-0003"}], {"EV-0003"}, "handoff")


def test_event_backing_rejects_silent_mutation():
    with pytest.raises(ValueError, match="lacks canonical mutation_event_id"):
        _validate_event_backing([{"handoff_id": "HF-1"}], {"EV-0003"}, "handoff")


def test_event_backing_rejects_missing_event_reference():
    with pytest.raises(ValueError, match="references missing mutation event"):
        _validate_event_backing([{"handoff_id": "HF-1", "mutation_event_id": "EV-9999"}], {"EV-0003"}, "handoff")
