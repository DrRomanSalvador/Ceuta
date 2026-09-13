from backend.app.core.decision.policy import PolicyProvenance


def test_policy_is_versioned_and_provenance_bearing():
    policy = PolicyProvenance("decision-policy", "2", "2026-09-13T00:00:00+00:00", None, ("source-1",), "explicit governance rationale", {"mode": "review"})
    assert policy.configuration_hash()
    assert policy.semantic_fingerprint()
    assert policy.semantic_payload()["version"] == "2"
