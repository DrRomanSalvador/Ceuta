from __future__ import annotations

from datetime import datetime, timedelta, timezone
import importlib
import importlib.util
import os
from pathlib import Path
import sys
import types

from app.core.scientific.cross_repo_consumer import consume_serpiente_prediction
from tests.core.test_cross_repo_scientific_adversarial import _payload


def _load_serpiente_transport():
    root = os.environ.get("SERPIENTE_ROOT")
    if not root:
        raise RuntimeError("SERPIENTE_ROOT is required for the cross-repository transport test")
    path = Path(root) / "backend" / "app" / "scientific_transport.py"
    spec = importlib.util.spec_from_file_location("serpiente_scientific_transport", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load SERPIENTE scientific transport module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_serpiente_runtime_modules():
    root = Path(os.environ["SERPIENTE_ROOT"]) / "backend"
    package_name = "serpiente_runtime"
    package = types.ModuleType(package_name)
    package.__path__ = [str(root / "app")]
    package.__package__ = package_name
    sys.modules[package_name] = package
    contracts = importlib.import_module(f"{package_name}.contracts")
    boundary = importlib.import_module(f"{package_name}.scientific_boundary")
    return contracts, boundary


def test_serpiente_authenticated_prediction_enters_ceutia_consumer(tmp_path, monkeypatch):
    transport = _load_serpiente_transport()
    payload = _payload()
    now = datetime(2026, 9, 15, 5, 0, tzinfo=timezone.utc)
    wrapped = transport.build_authenticated_prediction(payload, secret="shared-secret", timestamp=now.isoformat(), nonce="cross-repo-nonce-123456")
    monkeypatch.setenv("CEUTIA_SERPIENTE_TRANSPORT_SECRET", "shared-secret")
    monkeypatch.setenv("CEUTIA_DECISION_DB", str(tmp_path / "decision.sqlite"))
    result = consume_serpiente_prediction(wrapped, decision_time=now)
    assert result.accepted is True
    assert result.prediction is not None
    assert result.prediction.prediction_id == "prediction-1"


def test_real_serpiente_forecast_is_transformed_and_consumed_cross_repository(tmp_path, monkeypatch):
    contracts, boundary = _load_serpiente_runtime_modules()
    origin = datetime(2026, 9, 15, 4, 0, tzinfo=timezone.utc)
    available = origin + timedelta(minutes=5)
    forecast = contracts.Forecast(
        forecast_id="real-serpiente-forecast-1",
        origin_time=origin,
        horizon="1h",
        target="risk",
        probability=0.7,
        lower=0.5,
        upper=0.9,
        aleatoric=0.1,
        epistemic=0.1,
        measurement=0.0,
        parameter=0.05,
        structural=0.05,
        model_disagreement=0.1,
        regime="stable",
        provenance=("test:serpiente-forecast",),
        point_in_time_fingerprint="p" * 64,
    )
    metadata = boundary.ScientificPredictionMetadata(
        model_id="model-test",
        method_id="method-test",
        method_version="1",
        training_window="2026-01-01/2026-09-01",
        reference_class="ceuta",
        ood_state="IN_DOMAIN",
        causal_status="ABSTAIN",
        calibration_status="CALIBRATED",
        evidence_level="TEST",
        source_independence="INDEPENDENT",
        configuration_hash="config-test",
        code_revision="revision-test",
    )
    payload = boundary.forecast_to_scientific_prediction(forecast, available_at=available, metadata=metadata)
    transport = _load_serpiente_transport()
    wrapped = transport.build_authenticated_prediction(payload, secret="shared-secret", timestamp=available.isoformat(), nonce="real-forecast-crossrepo-123")
    monkeypatch.setenv("CEUTIA_SERPIENTE_TRANSPORT_SECRET", "shared-secret")
    monkeypatch.setenv("CEUTIA_DECISION_DB", str(tmp_path / "decision.sqlite"))
    result = consume_serpiente_prediction(wrapped, decision_time=available)
    assert result.accepted is True
    assert result.prediction is not None
    assert result.prediction.prediction_id == "real-serpiente-forecast-1"
    assert result.prediction.probability == 0.7
