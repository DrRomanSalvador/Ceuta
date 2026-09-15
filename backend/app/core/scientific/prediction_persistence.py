"""Persistence adapter for canonical cross-repository prediction records.

This module extends the existing SQLiteDecisionStore connection; it does not
create a second persistence system. Prediction records remain distinct from
model-release governance records.
"""
from __future__ import annotations

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
    connection.execute(
        """CREATE TABLE IF NOT EXISTS scientific_predictions (
            prediction_id TEXT PRIMARY KEY,
            decision_id TEXT,
            available_at TEXT NOT NULL,
            origin_time TEXT NOT NULL,
            contract_id TEXT NOT NULL,
            contract_version TEXT NOT NULL,
            payload_json TEXT NOT NULL,
            payload_fingerprint TEXT NOT NULL UNIQUE
        )"""
    )
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_scientific_predictions_decision ON scientific_predictions(decision_id, available_at)"
    )
    connection.commit()


def record_prediction(connection: sqlite3.Connection, payload: dict[str, Any], *, decision_id: str | None = None) -> str:
    ensure_prediction_schema(connection)
    prediction_id = str(payload["prediction_id"])
    fingerprint = _fingerprint(payload)
    canonical = _canonical(payload)
    row = connection.execute(
        "SELECT payload_fingerprint, payload_json, decision_id FROM scientific_predictions WHERE prediction_id=?",
        (prediction_id,),
    ).fetchone()
    if row is not None:
        if row[0] != fingerprint or row[1] != canonical or row[2] != decision_id:
            raise RuntimeError("scientific prediction identity collision: existing prediction differs")
        return fingerprint
    connection.execute(
        "INSERT INTO scientific_predictions(prediction_id,decision_id,available_at,origin_time,contract_id,contract_version,payload_json,payload_fingerprint) VALUES(?,?,?,?,?,?,?,?)",
        (
            prediction_id,
            decision_id,
            str(payload["available_at"]),
            str(payload["origin_time"]),
            str(payload["contract_id"]),
            str(payload["schema_version"]),
            canonical,
            fingerprint,
        ),
    )
    connection.commit()
    return fingerprint


def get_prediction(connection: sqlite3.Connection, prediction_id: str) -> dict[str, Any] | None:
    ensure_prediction_schema(connection)
    row = connection.execute(
        "SELECT payload_json FROM scientific_predictions WHERE prediction_id=?",
        (prediction_id,),
    ).fetchone()
    return None if row is None else json.loads(row[0])
