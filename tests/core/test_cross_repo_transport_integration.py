from datetime import datetime, timezone

from app.core.scientific.cross_repo_consumer import consume_serpiente_prediction
from app.core.scientific.transport_security import sign_transport
from tests.core.test_cross_repo_scientific_adversarial import _payload


def test_configured_consumer_requires_authenticated_transport(tmp_path, monkeypatch):
    monkeypatch.setenv("CEUTIA_SERPIENTE_TRANSPORT_SECRET", "shared-secret")
    monkeypatch.setenv("CEUTIA_DECISION_DB", str(tmp_path / "decision.sqlite"))
    result = consume_serpiente_prediction(_payload(), decision_time=datetime(2026, 9, 15, 5, 0, tzinfo=timezone.utc))
    assert result.accepted is False
    assert "transport_missing" in result.reason


def test_configured_consumer_rejects_replay(tmp_path, monkeypatch):
    monkeypatch.setenv("CEUTIA_SERPIENTE_TRANSPORT_SECRET", "shared-secret")
    monkeypatch.setenv("CEUTIA_DECISION_DB", str(tmp_path / "decision.sqlite"))
    payload = _payload()
    now = datetime(2026, 9, 15, 5, 0, tzinfo=timezone.utc)
    timestamp = now.isoformat()
    nonce = "producer-nonce-654321"
    signature = sign_transport(payload, secret="shared-secret", timestamp=timestamp, nonce=nonce)
    authenticated = {**payload, "_transport": {"timestamp": timestamp, "nonce": nonce, "signature": signature}}
    first = consume_serpiente_prediction(authenticated, decision_time=now)
    assert first.accepted is True
    replay = consume_serpiente_prediction(authenticated, decision_time=now)
    assert replay.accepted is False
    assert "already been consumed" in replay.reason
