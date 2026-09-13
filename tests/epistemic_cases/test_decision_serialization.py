from backend.app.core.decision.control_plane import DecisionManifest
from backend.app.core.decision.serialization import (
    manifest_execution_fingerprint,
    manifest_execution_payload,
    manifest_semantic_fingerprint,
    manifest_semantic_payload,
    serialize_manifest,
)


def _manifest(created_at: str) -> DecisionManifest:
    return DecisionManifest(
        decision_id="decision-1",
        state_refs=("state:1",),
        evidence_refs=("evidence:1",),
        model_refs=("model:1",),
        hypothesis_refs=(),
        transformation_refs=(),
        assumption_refs=(),
        scenario_refs=("scenario:1",),
        utility_definition_ref="utility:1",
        constraint_refs=(),
        policy_version="policy-1",
        configuration_hash="config-1",
        code_revision="revision-1",
        created_at=created_at,
    )


def test_semantic_manifest_serialization_excludes_execution_timestamp() -> None:
    first = _manifest("2026-09-13T10:00:00+00:00")
    second = _manifest("2026-09-13T10:00:01+00:00")

    assert manifest_semantic_payload(first) == manifest_semantic_payload(second)
    assert serialize_manifest(first, include_execution_metadata=False) == serialize_manifest(
        second, include_execution_metadata=False
    )
    assert manifest_semantic_fingerprint(first) == manifest_semantic_fingerprint(second)


def test_execution_serialization_retains_timestamp() -> None:
    first = _manifest("2026-09-13T10:00:00+00:00")
    second = _manifest("2026-09-13T10:00:01+00:00")

    assert manifest_execution_payload(first) != manifest_execution_payload(second)
    assert serialize_manifest(first) != serialize_manifest(second)
    assert manifest_execution_fingerprint(first) != manifest_execution_fingerprint(second)
