from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib
import importlib.util
import os
from pathlib import Path
import sqlite3
import sys
import types

from fastapi.testclient import TestClient

from app.core.decision.persistence import SQLiteDecisionStore
from app.core.evidence.source_registry import SourceRecord, SourceRole, SourceVerification
from tests.core.test_cross_repo_scientific_adversarial import _payload


def _load_serpiente_transport():
    root = os.environ["SERPIENTE_ROOT"]
    path = Path(root) / "backend" / "app" / "scientific_transport.py"
    spec = importlib.util.spec_from_file_location("serpiente_scientific_transport_endpoint", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load SERPIENTE scientific transport module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_serpiente_runtime_modules():
    root = Path(os.environ["SERPIENTE_ROOT"]) / "backend"
    package_name = "serpiente_endpoint_runtime"
    package = types.ModuleType(package_name)
    package.__path__ = [str(root / "app")]
    package.__package__ = package_name
    sys.modules[package_name] = package
    return importlib.import_module(f"{package_name}.contracts"), importlib.import_module(f"{package_name}.scientific_boundary")


def _decision_payload(now: datetime, authenticated_prediction: dict, decision_id: str) -> dict:
    return {"decision_id": decision_id, "decision_maker": "test-owner", "horizon": "24h", "purpose": "cross-repository endpoint validation", "risk_class": "low", "mode": "robust", "state_refs": ["state:test"], "transformation_refs": ["serpiente-prediction-integration"], "evidence": [{"evidence_id": "evidence:test-1", "source_id": "source:test-official", "claim_id": "claim:test-1", "content_hash": "a" * 64, "valid_from": (now - timedelta(hours=1)).isoformat(), "recorded_from": (now - timedelta(hours=1)).isoformat(), "base_weight": 1.0, "provenance_refs": ["test:provenance"]}], "options": [{"option_id": "option-1", "scenarios": [{"scenario_id": "scenario-1", "probability": 1.0, "utility": 1.0, "harm": 0.0}]}], "serpiente_prediction": authenticated_prediction}


def _configure_endpoint(tmp_path, monkeypatch, now):
    database = tmp_path / "decision.sqlite"
    monkeypatch.setenv("CEUTIA_CODE_REVISION", "r" * 40)
    monkeypatch.setenv("CEUTIA_DECISION_DB", str(database))
    monkeypatch.setenv("CEUTIA_SERPIENTE_TRANSPORT_SECRET", "shared-secret")
    monkeypatch.setenv("CEUTIA_DECISION_API_KEY", "decision-key")
    store = SQLiteDecisionStore(str(database))
    try:
        store.record_source(SourceRecord(source_id="source:test-official", title="Test official source", source_class="official", url="https://example.org/source", publisher="Test authority", published_at=now.isoformat(), accessed_at=now.isoformat(), verification=SourceVerification.PRIMARY_SOURCE_VERIFIED, role=SourceRole.EVIDENCE, independence="independent", validation_level="test"))
    finally:
        store.close()
    from app import main
    main.RUNTIME_CONFIG = main.load_runtime_config()
    return database, main


def test_authenticated_prediction_reaches_actual_decision_endpoint(tmp_path, monkeypatch):
    now = datetime.now(timezone.utc).replace(microsecond=0)
    database, main = _configure_endpoint(tmp_path, monkeypatch, now)
    transport = _load_serpiente_transport()
    authenticated_prediction = transport.build_authenticated_prediction(_payload(), secret="shared-secret", timestamp=now.isoformat(), nonce="decision-endpoint-nonce-123456")
    decision_payload = _decision_payload(now, authenticated_prediction, "decision-crossrepo-1")
    with TestClient(main.app) as client:
        response = client.post("/decision/evaluate", headers={"X-CeutIA-Decision-Key": "decision-key"}, json=decision_payload)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["serpiente_prediction_id"] == "prediction-1"
    assert body["decision_id"] == "decision-crossrepo-1"
    assert body["lineage_fingerprint"]
    connection = sqlite3.connect(database)
    try:
        row = connection.execute("SELECT decision_id FROM scientific_predictions WHERE prediction_id='prediction-1'").fetchone()
    finally:
        connection.close()
    assert row == ("decision-crossrepo-1",)


def test_actual_serpiente_forecast_reaches_decision_endpoint(tmp_path, monkeypatch):
    contracts, boundary = _load_serpiente_runtime_modules()
    now = datetime.now(timezone.utc).replace(microsecond=0)
    origin = now - timedelta(minutes=10)
    forecast = contracts.Forecast(forecast_id="forecast-endpoint-real-1", origin_time=origin, horizon="24h", target="risk", probability=0.7, lower=0.5, upper=0.9, aleatoric=0.1, epistemic=0.1, measurement=0.0, parameter=0.05, structural=0.05, model_disagreement=0.1, regime="stable", provenance=("test:real-serpiente-forecast",), point_in_time_fingerprint="p" * 64)
    metadata = boundary.ScientificPredictionMetadata(model_id="model-test", method_id="method-test", method_version="1", training_window="2026-01-01/2026-09-01", reference_class="ceuta", ood_state="IN_DOMAIN", causal_status="ABSTAIN", calibration_status="CALIBRATED", evidence_level="TEST", source_independence="INDEPENDENT", configuration_hash="config-test", code_revision="revision-test")
    payload = boundary.forecast_to_scientific_prediction(forecast, available_at=now, metadata=metadata)
    database, main = _configure_endpoint(tmp_path, monkeypatch, now)
    transport = _load_serpiente_transport()
    authenticated_prediction = transport.build_authenticated_prediction(payload, secret="shared-secret", timestamp=now.isoformat(), nonce="actual-forecast-endpoint-123456")
    decision_payload = _decision_payload(now, authenticated_prediction, "decision-real-forecast-1")
    with TestClient(main.app) as client:
        response = client.post("/decision/evaluate", headers={"X-CeutIA-Decision-Key": "decision-key"}, json=decision_payload)
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["serpiente_prediction_id"] == "forecast-endpoint-real-1"
    assert body["decision_id"] == "decision-real-forecast-1"
    connection = sqlite3.connect(database)
    try:
        row = connection.execute("SELECT prediction_id, decision_id FROM scientific_predictions WHERE prediction_id=?", ("forecast-endpoint-real-1",)).fetchone()
    finally:
        connection.close()
    assert row == ("forecast-endpoint-real-1", "decision-real-forecast-1")


def test_invalid_prediction_is_abstained_before_persistence(tmp_path, monkeypatch):
    now = datetime.now(timezone.utc).replace(microsecond=0)
    database, main = _configure_endpoint(tmp_path, monkeypatch, now)
    transport = _load_serpiente_transport()
    invalid = _payload()
    invalid["probability"] = 2.0
    authenticated_prediction = transport.build_authenticated_prediction(invalid, secret="shared-secret", timestamp=now.isoformat(), nonce="invalid-prediction-nonce-123456")
    decision_payload = _decision_payload(now, authenticated_prediction, "decision-invalid-prediction")
    with TestClient(main.app) as client:
        response = client.post("/decision/evaluate", headers={"X-CeutIA-Decision-Key": "decision-key"}, json=decision_payload)
    assert response.status_code == 422
    connection = sqlite3.connect(database)
    try:
        row = connection.execute("SELECT prediction_id FROM scientific_predictions WHERE prediction_id='prediction-1'").fetchone()
    finally:
        connection.close()
    assert row is None


def test_prediction_without_epistemic_transformation_is_abstained(tmp_path, monkeypatch):
    database = tmp_path / "decision.sqlite"
    monkeypatch.setenv("CEUTIA_CODE_REVISION", "r" * 40)
    monkeypatch.setenv("CEUTIA_DECISION_DB", str(database))
    monkeypatch.setenv("CEUTIA_SERPIENTE_TRANSPORT_SECRET", "shared-secret")
    monkeypatch.setenv("CEUTIA_DECISION_API_KEY", "decision-key")
    from app import main
    main.RUNTIME_CONFIG = main.load_runtime_config()
    with TestClient(main.app) as client:
        response = client.post("/decision/evaluate", headers={"X-CeutIA-Decision-Key": "decision-key"}, json={"decision_id": "decision-missing-transformation", "decision_maker": "test-owner", "horizon": "24h", "purpose": "governance gate test", "state_refs": ["state:test"], "evidence": [], "options": [{"option_id": "option-1", "scenarios": [{"scenario_id": "scenario-1", "probability": 1.0, "utility": 1.0, "harm": 0.0}]}]})
    assert response.status_code == 422
