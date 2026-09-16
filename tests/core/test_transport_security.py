from datetime import datetime, timedelta, timezone
import sqlite3

import pytest

from app.core.scientific.transport_security import sign_transport, verify_and_consume_transport

NOW = datetime(2026, 9, 15, 7, 0, tzinfo=timezone.utc)


def _payload():
    return {"prediction_id": "p1", "probability": 0.7, "contract_hash": "abc"}


def test_valid_transport_is_authenticated_and_consumed_once():
    connection = sqlite3.connect(":memory:")
    timestamp = NOW.isoformat()
    nonce = "nonce-1234567890"
    signature = sign_transport(_payload(), secret="shared-secret", timestamp=timestamp, nonce=nonce)
    verify_and_consume_transport(connection, _payload(), secret="shared-secret", timestamp=timestamp, nonce=nonce, signature=signature, now=NOW)
    with pytest.raises(ValueError, match="already been consumed"):
        verify_and_consume_transport(connection, _payload(), secret="shared-secret", timestamp=timestamp, nonce=nonce, signature=signature, now=NOW)


def test_tampering_fails_signature_verification():
    connection = sqlite3.connect(":memory:")
    timestamp = NOW.isoformat()
    nonce = "nonce-1234567891"
    signature = sign_transport(_payload(), secret="shared-secret", timestamp=timestamp, nonce=nonce)
    with pytest.raises(ValueError, match="signature verification failed"):
        verify_and_consume_transport(connection, {**_payload(), "probability": 0.8}, secret="shared-secret", timestamp=timestamp, nonce=nonce, signature=signature, now=NOW)


def test_stale_transport_fails_before_consumption():
    connection = sqlite3.connect(":memory:")
    timestamp = (NOW - timedelta(minutes=6)).isoformat()
    nonce = "nonce-1234567892"
    signature = sign_transport(_payload(), secret="shared-secret", timestamp=timestamp, nonce=nonce)
    with pytest.raises(ValueError, match="replay window"):
        verify_and_consume_transport(connection, _payload(), secret="shared-secret", timestamp=timestamp, nonce=nonce, signature=signature, now=NOW)
