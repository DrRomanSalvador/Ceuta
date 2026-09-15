from datetime import datetime, timedelta, timezone
import sqlite3

import pytest

from app.core.scientific.prediction_persistence import record_prediction, replay_prediction


NOW = datetime(2026, 9, 15, 5, 0, tzinfo=timezone.utc)


def _payload():
    return {
        "prediction_id": "p-replay",
        "available_at": NOW.isoformat(),
        "origin_time": NOW.isoformat(),
        "contract_id": "ceutia-serpiente-scientific-prediction",
        "schema_version": "1.1",
        "probability": 0.7,
        "point_in_time_fingerprint": "f" * 64,
    }


def test_prediction_replays_only_after_availability():
    connection = sqlite3.connect(":memory:")
    record_prediction(connection, _payload(), decision_id="d1")
    replayed = replay_prediction(connection, "p-replay", as_of=NOW + timedelta(minutes=1))
    assert replayed["prediction_id"] == "p-replay"
    with pytest.raises(ValueError, match="point-in-time eligible"):
        replay_prediction(connection, "p-replay", as_of=NOW - timedelta(seconds=1))


def test_replay_rejects_naive_time():
    connection = sqlite3.connect(":memory:")
    record_prediction(connection, _payload(), decision_id="d1")
    with pytest.raises(ValueError, match="timezone-aware"):
        replay_prediction(connection, "p-replay", as_of=datetime(2026, 9, 15, 5, 0))
