import os

import pytest

from app.core.scientific.cross_repo_consumer import consume_serpiente_prediction
from app.core.scientific.transport_security import sign_transport

from test_cross_repo_scientific_adversarial import _payload


def test_configured_consumer_requires_and_consumes_authenticated_transport(tmp_path, monkeypatch):
    monkeypatch.setenv("CEUTIA_SERPIENTE_TRANSPORT_SECRET", "shared-secret")
    monkeypatch.setenv("CEUTIA_DECISION_DB", str(tmp_path / "decision.sqlite"))
    payload = _payload()
    timestamp = "2026-09-15T05:00:00+00:00"
    nonce = "producer-nonce-123456"
    transport = sign_transport(payload, secret="shared-secret", timestamp=timestamp, nonce=nonce)
    authenticated = {**payload, "_transport": transport}
    result = consume_serpiente_prediction(authenticated, decision_time="")
    assert result.accepted is False
    assert "decision_time_not_timezone_aware" in result.reason


def test_configured_consumer_rejects_replay(tmp_path, monkeypatch):
    from datetime import datetime, timezone

    monkeypatch.setenv("CEUTIA_SERPIENTE_TRANSPORT_SECRET", "shared-secret")
    monkeypatch.setenv("CEUTIA_DECISION_DB", str(tmp_path / "decision.sqlite"))
    payload = _payload()
    now = datetime(2026, 9, 15, 5, 0, tzinfo=timezone.utc)
    transport = sign_transport(payload, secret="shared-secret", timestamp=now.isoformat(), nonce="producer-nonce-654321")
    authenticated = {**payload, "_transport": transport}
    first = consume_serpiente_prediction(authenticated, decision_time=now)
    assert first.accepted is True
    replay = consume_serpiente_prediction(authenticated, decision_time=now)
    assert replay.accepted is False
    assert "already been consumed" in replay.reason
