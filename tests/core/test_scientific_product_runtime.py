from __future__ import annotations

from datetime import datetime, timezone

from fastapi.testclient import TestClient

from app.core.scientific.prediction_persistence import record_prediction
from test_cross_repo_scientific_adversarial import _payload


def test_product_replay_and_outcome_endpoints(tmp_path, monkeypatch):
    database = tmp_path / "decision.sqlite"
    monkeypatch.setenv("CEUTIA_CODE_REVISION", "r" * 40)
    monkeypatch.setenv("CEUTIA_DECISION_DB", str(database))
    monkeypatch.setenv("CEUTIA_SERPIENTE_TRANSPORT_SECRET", "shared-secret")
    monkeypatch.setenv("CEUTIA_DECISION_API_KEY", "decision-key")

    from app import main

    main.RUNTIME_CONFIG = main.load_runtime_config()
    payload = _payload()
    import sqlite3

    connection = sqlite3.connect(database)
    try:
        record_prediction(connection, payload, decision_id="decision-1")
    finally:
        connection.close()

    with TestClient(main.app) as client:
        headers = {"X-CeutIA-Decision-Key": "decision-key"}
        replay = client.get(
            "/scientific/predictions/prediction-1/replay",
            params={"as_of": "2026-09-15T06:00:00+00:00"},
            headers=headers,
        )
        assert replay.status_code == 200
        assert replay.json()["point_in_time_eligible"] is True
        assert replay.json()["scientific_contract_valid"] is True

        early = client.get(
            "/scientific/predictions/prediction-1/replay",
            params={"as_of": "2026-09-15T04:59:00+00:00"},
            headers=headers,
        )
        assert early.status_code == 422

        outcome = client.post(
            "/scientific/predictions/outcomes",
            headers=headers,
            json={
                "prediction_id": "prediction-1",
                "decision_id": "decision-1",
                "action_id": "option-1",
                "outcome_id": "outcome-1",
                "target": "risk",
                "outcome_time": "2026-09-16T05:00:00+00:00",
                "observed": 1,
                "provenance": ["test:outcome"],
            },
        )
        assert outcome.status_code == 200
        assert outcome.json()["prediction_id"] == "prediction-1"
        assert outcome.json()["brier_error"] == 0.09


def test_readiness_requires_transport_secret(monkeypatch, tmp_path):
    monkeypatch.setenv("CEUTIA_CODE_REVISION", "r" * 40)
    monkeypatch.setenv("CEUTIA_DECISION_DB", str(tmp_path / "decision.sqlite"))
    monkeypatch.delenv("CEUTIA_SERPIENTE_TRANSPORT_SECRET", raising=False)
    monkeypatch.setenv("CEUTIA_DECISION_API_KEY", "decision-key")

    from app import main

    main.RUNTIME_CONFIG = main.load_runtime_config()
    with TestClient(main.app) as client:
        response = client.get("/ready")
    assert response.status_code == 503
    assert "CEUTIA_SERPIENTE_TRANSPORT_SECRET" in response.json()["reason"]
