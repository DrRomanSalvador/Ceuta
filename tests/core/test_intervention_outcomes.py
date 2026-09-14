from datetime import datetime, timezone

import pytest

from app.core.scientific.intervention_outcomes import (
    InterventionOutcome,
    InterventionOutcomeLedger,
    InterventionOutcomeStatus,
)


def test_prevented_event_is_not_ordinary_false_positive(tmp_path):
    ledger = InterventionOutcomeLedger(storage_path=str(tmp_path / "outcomes.sqlite"))
    with pytest.raises(ValueError):
        ledger.settle(InterventionOutcome("w1", "i1", InterventionOutcomeStatus.EVENT_AVERTED, "outcome:1", False, datetime.now(timezone.utc)))
    ledger.settle(InterventionOutcome("w1", "i1", InterventionOutcomeStatus.EVENT_AVERTED, "outcome:1", True, datetime.now(timezone.utc)))
    assert ledger.scoreable_counts()["not_scoreable_as_ordinary_accuracy"] == 1


def test_no_event_without_intervention_is_scoreable(tmp_path):
    ledger = InterventionOutcomeLedger(storage_path=str(tmp_path / "outcomes.sqlite"))
    ledger.settle(InterventionOutcome("w1", "none", InterventionOutcomeStatus.NO_EVENT_NO_INTERVENTION, "outcome:1", False, datetime.now(timezone.utc)))
    assert ledger.scoreable_counts()["true_negative"] == 1


def test_restart_preserves_reflexive_outcome(tmp_path):
    path = tmp_path / "outcomes.sqlite"
    ledger = InterventionOutcomeLedger(storage_path=str(path))
    ledger.settle(InterventionOutcome("w1", "i1", InterventionOutcomeStatus.EVENT_OCCURRED, "outcome:1", False, datetime.now(timezone.utc)))
    restored = InterventionOutcomeLedger(storage_path=str(path))
    assert restored.outcomes()[0].ordinary_accuracy_label == "true_positive"
