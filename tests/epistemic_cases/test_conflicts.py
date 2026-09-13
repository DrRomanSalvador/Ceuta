from backend.app.core.evidence.conflicts import (
    ConflictSet,
    ConflictStatus,
    ConflictType,
    EvidenceConflict,
)


def test_conflict_taxonomy_requires_multiple_evidence_refs():
    conflict = EvidenceConflict(
        conflict_id="c1",
        conflict_type=ConflictType.METHODOLOGICAL,
        evidence_refs=("e1", "e2"),
        description="Different methods produce incompatible estimates.",
    )
    assert conflict.status is ConflictStatus.UNRESOLVED
    assert ConflictSet.from_iterable([conflict]).unresolved == (conflict,)


def test_conflict_ids_are_unique():
    conflict = EvidenceConflict("c1", ConflictType.VALUE, ("e1", "e2"), "value disagreement")
    try:
        ConflictSet.from_iterable([conflict, conflict])
    except ValueError as exc:
        assert "unique" in str(exc)
    else:
        raise AssertionError("duplicate conflict IDs must be rejected")
