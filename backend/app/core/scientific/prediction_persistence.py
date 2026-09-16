"""Persistence adapter for canonical cross-repository prediction records."""
from __future__ import annotations

from datetime import datetime, timezone
import json
import sqlite3
from hashlib import sha256
from typing import Any

SCHEMA_VERSION = 1


def _canonical(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _fingerprint(payload: dict[str, Any]) -> str:
    return sha256(_canonical(payload).encode("utf-8")).hexdigest()


def ensure_prediction_schema(connection: sqlite3.Connection) -> None:
    connection.execute("""CREATE TABLE IF NOT EXISTS scientific_predictions (
        prediction_id TEXT PRIMARY KEY,
        decision_id TEXT,
        available_at TEXT NOT NULL,
        origin_time TEXT NOT NULL,
        contract_id TEXT NOT NULL,
        contract_version TEXT NOT NULL,
        payload_json TEXT NOT NULL,
        payload_fingerprint TEXT NOT NULL UNIQUE
    )""")
    connection.execute("CREATE INDEX IF NOT EXISTS idx_scientific_predictions_decision ON scientific_predictions(decision_id, available_at)")
    connection.commit()


def record_prediction(connection: sqlite3.Connection, payload: dict[str, Any], *, decision_id: str | None = None) -> str:
    scientific_payload = {key: value for key, value in payload.items() if key != "_transport"}
    ensure_prediction_schema(connection)
    prediction_id = str(scientific_payload["prediction_id"])
    fingerprint = _fingerprint(scientific_payload)
    canonical = _canonical(scientific_payload)
    connection.execute("BEGIN IMMEDIATE")
    try:
        row = connection.execute("SELECT payload_fingerprint, payload_json, decision_id FROM scientific_predictions WHERE prediction_id=?", (prediction_id,)).fetchone()
        if row is not None:
            if row[0] != fingerprint or row[1] != canonical or row[2] != decision_id:
                raise RuntimeError("scientific prediction identity collision: existing prediction differs")
            connection.commit()
            return fingerprint
        try:
            connection.execute("INSERT INTO scientific_predictions(prediction_id,decision_id,available_at,origin_time,contract_id,contract_version,payload_json,payload_fingerprint) VALUES(?,?,?,?,?,?,?,?)", (prediction_id, decision_id, str(scientific_payload["available_at"]), str(scientific_payload["origin_time"]), str(scientific_payload["contract_id"]), str(scientific_payload["schema_version"]), canonical, fingerprint))
            connection.commit()
            return fingerprint
        except sqlite3.IntegrityError:
            row = connection.execute("SELECT payload_fingerprint, payload_json, decision_id FROM scientific_predictions WHERE prediction_id=?", (prediction_id,)).fetchone()
            if row is not None and row[0] == fingerprint and row[1] == canonical and row[2] == decision_id:
                connection.commit()
                return fingerprint
            raise RuntimeError("scientific prediction identity collision: concurrent delivery differs")
    except Exception:
        connection.rollback()
        raise


def get_prediction(connection: sqlite3.Connection, prediction_id: str) -> dict[str, Any] | None:
    ensure_prediction_schema(connection)
    row = connection.execute("SELECT payload_json FROM scientific_predictions WHERE prediction_id=?", (prediction_id,)).fetchone()
    return None if row is None else json.loads(row[0])


def replay_prediction(connection: sqlite3.Connection, prediction_id: str, *, as_of: datetime) -> dict[str, Any]:
    """Reconstruct the prediction only if it was legitimately available at as_of."""
    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise ValueError("replay as_of must be timezone-aware")
    ensure_prediction_schema(connection)
    row = connection.execute("SELECT available_at, origin_time, payload_json, payload_fingerprint FROM scientific_predictions WHERE prediction_id=?", (prediction_id,)).fetchone()
    if row is None:
        raise KeyError("prediction_id not found")
    available_at = datetime.fromisoformat(str(row[0])).astimezone(timezone.utc)
    origin_time = datetime.fromisoformat(str(row[1])).astimezone(timezone.utc)
    reference = as_of.astimezone(timezone.utc)
    if available_at > reference or origin_time > reference:
        raise ValueError("prediction was not point-in-time eligible at replay time")
    payload = json.loads(row[2])
    if _fingerprint(payload) != str(row[3]):
        raise RuntimeError("prediction persistence integrity mismatch")
    return payload
