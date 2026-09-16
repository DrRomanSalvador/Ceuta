from datetime import datetime, timezone
import hashlib
import json

from fastapi.testclient import TestClient

import app.main as main_module
from app.main import RuntimeConfig, app
from app.core.decision.information_boundary import InformationVisibility
from app.core.decision.persistence import SQLiteDecisionStore
from app.core.evidence.source_registry import SourceRecord, SourceRole, SourceVerification
from app.core.scientific.cross_repo_contract import ScientificPredictionMessage


def _prediction_payload() -> dict[str, object]:
    message = ScientificPredictionMessage(
        producer_repository="DrRomanSalvador/SERPIENTE",
        producer_component="scientific_boundary.forecast_to_scientific_prediction",
        schema_version="1.1",
        prediction_id="pred-vertical-001",
        origin_time=datetime(2026, 9, 14, 8, tzinfo=timezone.utc),
        available_at=datetime(2026, 9, 14, 8, 1, tzinfo=timezone.utc),
        horizon="24h",
        target="territorial_risk",
        probability=0.62,
        lower=0.48,
        upper=0.74,
        uncertainty={"interval_width": 0.26},
        model_disagreement=0.08,
        model_id="serpiente:test-model",
        method_id="longitudinal_forecaster",
        method_version="1",
        training_window="2025-01-01/2026-09-13",
        reference_class="synthetic-test-reference-class",
        ood_state="IN_DOMAIN",
        causal_status="ABSTAIN",
        calibration_status="CALIBRATED",
        evidence_level="E1",
        source_independence="INDEPENDENT",
        provenance=("serpiente:synthetic:test",),
        configuration_hash="config-test-001",
        code_revision="serpiente-test-revision",
        point_in_time_fingerprint="pit-test-001",
        integrity_hash="pending",
    )
    canonical = message.payload_without_integrity()
    integrity = hashlib.sha256(json.dumps(canonical, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
    canonical["integrity_hash"] = integrity
    return canonical


def _configure_runtime(monkeypatch, tmp_path):
    db_path = tmp_path / "decision.sqlite3"
    monkeypatch.setattr(main_module, "RUNTIME_CONFIG", RuntimeConfig(host="127.0.0.1", port=8000, code_revision="ceutia-test-revision", decision_db=str(db_path)))
    monkeypatch.setenv("CEUTIA_DECISION_API_KEY", "test-key")
    store = SQLiteDecisionStore(str(db_path))
    store.record_source(SourceRecord(source_id="s1", title="Verified test source", source_class="test", url="https://example.org/source", publisher="Test Publisher", published_at=None, accessed_at="2026-09-14T00:00:00+00:00", verification=SourceVerification.INSTITUTIONALLY_VERIFIED, role=SourceRole.EVIDENCE))
    store.close()
    return db_path


def _request_payload() -> dict[str, object]:
    return {
        "decision_id": "decision-vertical-001",
        "decision_maker": "owner",
        "horizon": "24h",
        "purpose": "territorial decision support",
        "state_refs": ["state-1"],
        "evidence": [{
            "evidence_id": "e1", "source_id": "s1", "claim_id": "c1", "content_hash": "a" * 64,
            "valid_from": "2026-09-14T00:00:00+00:00", "recorded_from": "2026-09-14T00:00:00+00:00",
            "base_weight": 1.0, "adversarial_risk": 0.0, "contradiction_weight": 0.0,
            "independent_origin": True, "disposition": "accept", "provenance_refs": ["source:s1"],
            "visibility": InformationVisibility.PUBLIC.value,
        }],
        "options": [{"option_id": "o1", "scenarios": [{"scenario_id": "sc1", "probability": 1.0, "utility": 1.0, "harm": 0.0}]}],
        "transformation_refs": ["t1"],
        "serpiente_prediction": _prediction_payload(),
    }


def test_real_endpoint_consumes_canonical_prediction_and_persists_lineage(tmp_path, monkeypatch):
    db_path = _configure_runtime(monkeypatch, tmp_path)
    response = TestClient(app).post("/decision/evaluate", headers={"X-CeutIA-Decision-Key": "test-key"}, json=_request_payload())
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["serpiente_prediction_id"] == "pred-vertical-001"
    store = SQLiteDecisionStore(str(db_path))
    try:
        row = store.connection.execute("SELECT prediction_id, decision_id, payload_fingerprint FROM scientific_predictions WHERE prediction_id=?", ("pred-vertical-001",)).fetchone()
        assert row is not None
        assert row[1] == "decision-vertical-001"
        lineage = store.lineage("decision-vertical-001")
        assert lineage is not None
        assert any(node.stage == "prediction" and "serpiente-prediction:pred-vertical-001" in node.input_refs for node in lineage.nodes)
    finally:
        store.close()


def test_legacy_serpiente_envelope_cannot_bypass_canonical_contract(tmp_path, monkeypatch):
    _configure_runtime(monkeypatch, tmp_path)
    request = _request_payload()
    request["serpiente_prediction"] = {"prediction_id": "legacy", "origin_time": "2026-09-14T00:00:00+00:00"}
    response = TestClient(app).post("/decision/evaluate", headers={"X-CeutIA-Decision-Key": "test-key"}, json=request)
    assert response.status_code == 422
    assert response.json()["disposition"] == "abstain"
    assert "scientific contract identity mismatch" in response.json()["control_reason"]
