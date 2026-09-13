from backend.app.core.decision.semantic_identity import execution_fingerprint, semantic_fingerprint


def test_semantic_identity_ignores_execution_metadata():
    payload = {"decision_id": "d1", "policy": "p1", "configuration": "c1"}
    assert semantic_fingerprint(payload) == semantic_fingerprint(payload)
    first = execution_fingerprint(payload, execution_id="x1", created_at="2026-09-13T10:00:00+00:00")
    second = execution_fingerprint(payload, execution_id="x2", created_at="2026-09-13T10:01:00+00:00")
    assert first != second
