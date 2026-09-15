from __future__ import annotations

from datetime import datetime, timezone
import importlib.util
import os
from pathlib import Path

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


def test_serpiente_authenticated_prediction_enters_ceutia_consumer(tmp_path, monkeypatch):
    transport = _load_serpiente_transport()
    payload = _payload()
    now = datetime(2026, 9, 15, 5, 0, tzinfo=timezone.utc)
    wrapped = transport.build_authenticated_prediction(
        payload,
        secret="shared-secret",
        timestamp=now.isoformat(),
        nonce="cross-repo-nonce-123456",
    )
    monkeypatch.setenv("CEUTIA_SERPIENTE_TRANSPORT_SECRET", "shared-secret")
    monkeypatch.setenv("CEUTIA_DECISION_DB", str(tmp_path / "decision.sqlite"))

    result = consume_serpiente_prediction(wrapped, decision_time=now)

    assert result.accepted is True
    assert result.prediction is not None
    assert result.prediction.prediction_id == "prediction-1"
