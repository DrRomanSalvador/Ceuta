"""Aggregate descriptive prospective evaluation of persisted prediction outcomes."""
from __future__ import annotations

import json
import math
import sqlite3
from typing import Any


def aggregate_prediction_evaluation(
    connection: sqlite3.Connection,
    *,
    target: str | None = None,
    model_id: str | None = None,
) -> dict[str, Any]:
    clauses: list[str] = []
    params: list[str] = []
    if target:
        clauses.append("o.target=?")
        params.append(target)
    rows = connection.execute(
        "SELECT o.target, o.observed, o.predicted_probability, o.brier_error, o.log_loss_error, p.payload_json "
        "FROM scientific_prediction_outcomes o JOIN scientific_predictions p ON p.prediction_id=o.prediction_id"
        + (" WHERE " + " AND ".join(clauses) if clauses else ""),
        params,
    ).fetchall()
    selected = []
    for row in rows:
        payload = json.loads(row[5])
        if model_id and str(payload.get("model_id")) != model_id:
            continue
        selected.append(row)
    if not selected:
        return {
            "n": 0,
            "target": target,
            "model_id": model_id,
            "mean_brier_error": None,
            "mean_log_loss": None,
            "observed_rate": None,
            "mean_predicted_probability": None,
            "calibration_gap": None,
            "status": "insufficient_observed_outcomes",
            "scientific_interpretation": "No point-in-time eligible observed outcomes match the requested evaluation slice.",
        }
    n = len(selected)
    mean_brier = sum(float(row[3]) for row in selected) / n
    mean_log_loss = sum(float(row[4]) for row in selected) / n
    observed_rate = sum(int(row[1]) for row in selected) / n
    mean_probability = sum(float(row[2]) for row in selected) / n
    calibration_gap = mean_probability - observed_rate
    return {
        "n": n,
        "target": target,
        "model_id": model_id,
        "mean_brier_error": mean_brier,
        "mean_log_loss": mean_log_loss,
        "observed_rate": observed_rate,
        "mean_predicted_probability": mean_probability,
        "calibration_gap": calibration_gap,
        "status": "descriptive_prospective_evaluation",
        "scientific_interpretation": "Observed-outcome performance is summarized descriptively; this does not establish prospective deployment validity or causal effectiveness.",
    }


__all__ = ["aggregate_prediction_evaluation"]
