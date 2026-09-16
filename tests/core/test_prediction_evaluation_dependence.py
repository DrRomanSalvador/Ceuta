import json
import sqlite3

from app.core.scientific.prediction_evaluation import aggregate_prediction_evaluation


def test_prediction_aggregate_reports_cluster_uncertainty() -> None:
    connection = sqlite3.connect(":memory:")
    connection.executescript(
        """
        CREATE TABLE scientific_predictions (
            prediction_id TEXT PRIMARY KEY,
            payload_json TEXT NOT NULL
        );
        CREATE TABLE scientific_prediction_outcomes (
            prediction_id TEXT PRIMARY KEY,
            decision_id TEXT NOT NULL,
            target TEXT NOT NULL,
            observed INTEGER NOT NULL,
            predicted_probability REAL NOT NULL,
            brier_error REAL NOT NULL,
            log_loss_error REAL NOT NULL
        );
        """
    )
    for prediction_id, decision_id, observed, probability in (
        ("p1", "d1", 0, 0.2),
        ("p2", "d1", 1, 0.8),
        ("p3", "d2", 1, 0.7),
        ("p4", "d2", 0, 0.3),
    ):
        connection.execute(
            "INSERT INTO scientific_predictions VALUES (?, ?)",
            (prediction_id, json.dumps({"model_id": "m1", "horizon": "PT1H"})),
        )
        brier = (probability - observed) ** 2
        connection.execute(
            "INSERT INTO scientific_prediction_outcomes VALUES (?, ?, ?, ?, ?, ?, ?)",
            (prediction_id, decision_id, "target", observed, probability, brier, brier),
        )
    connection.commit()

    result = aggregate_prediction_evaluation(connection, target="target", model_id="m1", horizon="PT1H", bootstrap_resamples=100)

    assert result["dependence_unit"] == "decision_id"
    assert result["brier_cluster_ci"]["n_units"] == 2
