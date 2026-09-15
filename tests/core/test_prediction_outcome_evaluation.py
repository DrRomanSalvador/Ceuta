from __future__ import annotations

from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
import math
import sqlite3

import pytest

from app.core.scientific.prediction_outcome_evaluation import (
    get_prediction_outcome,
    record_prediction_outcome,
)
from app.core.scientific.prediction_persistence import record_prediction


def _prediction() -> dict[str, object]:
    return {
        "contract_id": "ceutia-serpiente-scientific-prediction",
        "contract_hash": "672dfa6b60d2e8c0854a024e83acf6b23eed44f2cd3293708aee533d7a9dc1f0",
        "producer_repository": "DrRomanSalvador/SERPIENTE",
        "producer_component": "test",
        "schema_version": "1.1",
        "prediction_id": "prediction-outcome-1",
        "origin_time": "2026-09-15T06:00:00+00:00",
        "available_at": "2026-09-15T06:05:00+00:00",
        "horizon": "PT1H",
        "target": "target.binary",
        "probability": 0.75,
        "lower": 0.6,
        "upper": 0.9,
        "uncertainty": {"aleatoric": 0.1},
        "model_disagreement": 0.05,
        "model_id": "model-1",
        "method_id": "method-1",
        "method_version": "1",
        "training_window": "2026-01-01/2026-09-01",
        "reference_class": "ceuta",
        "ood_state": "IN_DOMAIN",
        "causal_status": "ABSTAIN",
        "calibration_status": "CALIBRATED",
        "evidence_level": "TEST",
        "source_independence": "INDEPENDENT",
        "provenance": ["test:source"],
        "configuration_hash": "config",
        "code_revision": "revision",
        "point_in_time_fingerprint": "fingerprint",
        "integrity_hash": "integrity",
    }


def test_prediction_outcome_is_linked_and_evaluated() -> None:
    connection = sqlite3.connect(":memory:")
    now = datetime.now(timezone.utc).replace(microsecond=0)
    prediction = _prediction()
    prediction["origin_time"] = (now - timedelta(hours=2)).isoformat()
    prediction["available_at"] = (now - timedelta(hours=1, minutes=55)).isoformat()
    unsigned = dict(prediction)
    unsigned.pop("integrity_hash", None)
    prediction["integrity_hash"] = sha256(json.dumps(unsigned, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
    record_prediction(connection, prediction, decision_id="decision-1")

    result = record_prediction_outcome(
        connection,
        prediction_id="prediction-outcome-1",
        decision_id="decision-1",
        action_id="option-1",
        outcome_id="outcome-1",
        target="target.binary",
        outcome_time=now,
        observed=1,
        provenance=("outcome:test",),
    )

    assert result["brier_error"] == pytest.approx(0.0625)
    assert result["log_loss_error"] == pytest.approx(-math.log(0.75))
    assert get_prediction_outcome(connection, "prediction-outcome-1")["action_id"] == "option-1"


def test_outcome_cannot_precede_prediction_availability() -> None:
    connection = sqlite3.connect(":memory:")
    record_prediction(connection, _prediction(), decision_id="decision-1")

    with pytest.raises(ValueError, match="availability"):
        record_prediction_outcome(
            connection,
            prediction_id="prediction-outcome-1",
            decision_id="decision-1",
            action_id="option-1",
            outcome_id="outcome-early",
            target="target.binary",
            outcome_time=datetime(2026, 9, 15, 6, 1, tzinfo=timezone.utc),
            observed=1,
            provenance=("outcome:test",),
        )


def test_outcome_cannot_precede_prediction_target_time() -> None:
    connection = sqlite3.connect(":memory:")
    record_prediction(connection, _prediction(), decision_id="decision-1")

    with pytest.raises(ValueError, match="target time"):
        record_prediction_outcome(
            connection,
            prediction_id="prediction-outcome-1",
            decision_id="decision-1",
            action_id="option-1",
            outcome_id="outcome-before-target",
            target="target.binary",
            outcome_time=datetime(2026, 9, 15, 6, 30, tzinfo=timezone.utc),
            observed=1,
            provenance=("outcome:test",),
        )


def test_outcome_requires_prediction_decision_alignment() -> None:
    connection = sqlite3.connect(":memory:")
    record_prediction(connection, _prediction(), decision_id="decision-1")

    with pytest.raises(ValueError, match="does not belong"):
        record_prediction_outcome(
            connection,
            prediction_id="prediction-outcome-1",
            decision_id="decision-2",
            action_id="option-1",
            outcome_id="outcome-2",
            target="target.binary",
            outcome_time=datetime(2026, 9, 15, 7, 5, tzinfo=timezone.utc),
            observed=0,
            provenance=("outcome:test",),
        )
