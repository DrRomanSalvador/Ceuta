from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import json
import sqlite3

import pytest

from app.core.decision.persistence import SQLiteDecisionStore
from app.core.scientific.prediction_outcome_evaluation import record_prediction_outcome
from app.core.scientific.prediction_persistence import record_prediction


def _prediction(prediction_id: str = "concurrent-prediction") -> dict[str, object]:
    return {
        "prediction_id": prediction_id,
        "available_at": "2026-09-16T07:00:00+00:00",
        "origin_time": "2026-09-16T06:59:00+00:00",
        "contract_id": "serpiente.scientific_prediction",
        "schema_version": "1.1",
        "probability": 0.7,
        "target": "risk",
        "horizon": "1h",
    }


def test_sqlite_migration_rolls_back_partial_ddl(tmp_path, monkeypatch):
    database = tmp_path / "migration.sqlite"
    original = SQLiteDecisionStore._execute_migration_script

    def fail_after_first_statement(self: SQLiteDecisionStore, script: str) -> None:
        statement = next(item.strip() for item in script.split(";") if item.strip())
        self.connection.execute(statement)
        raise RuntimeError("synthetic migration failure")

    monkeypatch.setattr(SQLiteDecisionStore, "_execute_migration_script", fail_after_first_statement)
    with pytest.raises(RuntimeError, match="synthetic migration failure"):
        SQLiteDecisionStore(str(database))

    monkeypatch.setattr(SQLiteDecisionStore, "_execute_migration_script", original)
    connection = sqlite3.connect(database)
    try:
        assert connection.execute("SELECT version FROM ceutia_schema_version").fetchone() is None
        assert connection.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='decision_audit'").fetchone() is None
    finally:
        connection.close()

    store = SQLiteDecisionStore(str(database))
    try:
        assert store.schema_version == SQLiteDecisionStore.SCHEMA_VERSION
    finally:
        store.close()


def test_concurrent_identical_prediction_delivery_is_idempotent(tmp_path):
    database = tmp_path / "prediction.sqlite"
    payload = _prediction()

    def deliver() -> str:
        connection = sqlite3.connect(database, timeout=10.0)
        try:
            return record_prediction(connection, payload, decision_id="decision-concurrent")
        finally:
            connection.close()

    with ThreadPoolExecutor(max_workers=8) as executor:
        results = list(executor.map(lambda _: deliver(), range(32)))

    assert len(set(results)) == 1
    connection = sqlite3.connect(database)
    try:
        assert connection.execute("SELECT COUNT(*) FROM scientific_predictions").fetchone() == (1,)
    finally:
        connection.close()


def test_concurrent_conflicting_prediction_identity_is_rejected(tmp_path):
    database = tmp_path / "prediction-conflict.sqlite"
    first = _prediction()
    second = _prediction()
    second["probability"] = 0.8

    connection = sqlite3.connect(database, timeout=10.0)
    try:
        record_prediction(connection, first, decision_id="decision-1")
    finally:
        connection.close()

    conflicting = sqlite3.connect(database, timeout=10.0)
    try:
        with pytest.raises(RuntimeError, match="identity collision"):
            record_prediction(conflicting, second, decision_id="decision-1")
    finally:
        conflicting.close()


def test_mutated_prediction_cannot_enter_outcome_evaluation(tmp_path):
    database = tmp_path / "prediction-integrity.sqlite"
    connection = sqlite3.connect(database, timeout=10.0)
    try:
        record_prediction(connection, _prediction("integrity-prediction"), decision_id="decision-integrity")
        payload = json.loads(connection.execute("SELECT payload_json FROM scientific_predictions WHERE prediction_id=?", ("integrity-prediction",)).fetchone()[0])
        payload["probability"] = 0.99
        connection.execute("UPDATE scientific_predictions SET payload_json=? WHERE prediction_id=?", (json.dumps(payload, sort_keys=True, separators=(",", ":")), "integrity-prediction"))
        connection.commit()
        with pytest.raises(RuntimeError, match="integrity mismatch"):
            record_prediction_outcome(connection, prediction_id="integrity-prediction", decision_id="decision-integrity", action_id="action-1", outcome_id="outcome-1", target="risk", outcome_time=datetime.now(timezone.utc) + timedelta(hours=2), observed=1, provenance=("test",))
    finally:
        connection.close()
