import hashlib
import json

import pytest

from app.core.decision.control_plane import DecisionAuditEvent
from app.core.decision.persistence import SQLiteDecisionStore


def event(decision_id: str, event_id: str, previous_hash: str, payload: dict[str, object]) -> DecisionAuditEvent:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    event_hash = hashlib.sha256(f"{previous_hash}|{event_id}|{canonical}".encode()).hexdigest()
    return DecisionAuditEvent(event_id, decision_id, "test", payload, previous_hash, event_hash, f"2026-09-14T12:00:00+00:00")


def test_stale_predecessor_is_rejected_and_chain_remains_linear(tmp_path):
    path = tmp_path / "audit.sqlite3"
    first = SQLiteDecisionStore(str(path))
    second = SQLiteDecisionStore(str(path))
    try:
        first.append(event("d1", "e1", "GENESIS", {"n": 1}))
        stale = event("d1", "e2", "GENESIS", {"n": 2})
        with pytest.raises(RuntimeError, match="stale predecessor hash"):
            second.append(stale)
        assert first.verify_chain("d1")
        assert [item.event_id for item in first.events("d1")] == ["e1"]
    finally:
        first.close()
        second.close()
