"""Aggregate descriptive prediction evaluation with dependence-aware uncertainty."""
from __future__ import annotations

import json
import sqlite3
from typing import Any

from .limitation_controls import cluster_bootstrap_mean


PROTOCOL_ID = "CEUTIA-SERPIENTE-PREDICTIVE-EVAL-1"


def aggregate_prediction_evaluation(
    connection: sqlite3.Connection,
    *,
    target: str | None = None,
    model_id: str | None = None,
    horizon: str | None = None,
    dependence_unit: str = "decision_id",
    bootstrap_resamples: int = 1000,
) -> dict[str, Any]:
    if dependence_unit not in {"decision_id", "prediction_id"}:
        raise ValueError("unsupported dependence unit")
    clauses: list[str] = []
    params: list[str] = []
    if target:
        clauses.append("o.target=?")
        params.append(target)
    rows = connection.execute(
        "SELECT o.prediction_id, o.decision_id, o.target, o.observed, o.predicted_probability, "
        "o.brier_error, o.log_loss_error, p.payload_json "
        "FROM scientific_prediction_outcomes o "
        "JOIN scientific_predictions p ON p.prediction_id=o.prediction_id"
        + (" WHERE " + " AND ".join(clauses) if clauses else ""),
        params,
    ).fetchall()
    selected = []
    for row in rows:
        payload = json.loads(row[7])
        if model_id and str(payload.get("model_id")) != model_id:
            continue
        if horizon and str(payload.get("horizon")) != horizon:
            continue
        selected.append(row)
    if not selected:
        return {
            "protocol_id": PROTOCOL_ID,
            "n": 0,
            "target": target,
            "model_id": model_id,
            "horizon": horizon,
            "dependence_unit": dependence_unit,
            "mean_brier_error": None,
            "mean_log_loss": None,
            "observed_rate": None,
            "mean_predicted_probability": None,
            "calibration_gap": None,
            "brier_cluster_ci": None,
            "status": "insufficient_observed_outcomes",
            "prospective_validity_status": "NOT_ESTABLISHED",
            "scientific_interpretation": "No point-in-time eligible observed outcomes match the requested target/model/horizon slice.",
        }
    n = len(selected)
    mean_brier = sum(float(row[5]) for row in selected) / n
    mean_log_loss = sum(float(row[6]) for row in selected) / n
    observed_rate = sum(int(row[3]) for row in selected) / n
    mean_probability = sum(float(row[4]) for row in selected) / n
    calibration_gap = mean_probability - observed_rate
    groups = [str(row[1] if dependence_unit == "decision_id" else row[0]) for row in selected]
    try:
        brier_ci = cluster_bootstrap_mean(
            [float(row[5]) for row in selected],
            groups,
            resamples=bootstrap_resamples,
        )
        ci_payload = {"lower": brier_ci.lower, "upper": brier_ci.upper, "n_units": brier_ci.n_units}
    except ValueError as exc:
        ci_payload = {"lower": None, "upper": None, "n_units": len(set(groups)), "status": str(exc)}
    return {
        "protocol_id": PROTOCOL_ID,
        "n": n,
        "target": target,
        "model_id": model_id,
        "horizon": horizon,
        "dependence_unit": dependence_unit,
        "mean_brier_error": mean_brier,
        "mean_log_loss": mean_log_loss,
        "observed_rate": observed_rate,
        "mean_predicted_probability": mean_probability,
        "calibration_gap": calibration_gap,
        "brier_cluster_ci": ci_payload,
        "status": "descriptive_prospective_evaluation",
        "prospective_validity_status": "NOT_ESTABLISHED",
        "scientific_interpretation": "Observed-outcome performance is summarized descriptively under a predeclared eligibility protocol; dependence-aware uncertainty is reported at the declared unit. This does not establish prospective deployment validity or causal effectiveness.",
    }


__all__ = ["PROTOCOL_ID", "aggregate_prediction_evaluation"]
