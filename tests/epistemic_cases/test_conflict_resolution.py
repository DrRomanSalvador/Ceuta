from backend.app.core.evidence.conflict_resolution import ConflictResolver, ResolutionDisposition
from backend.app.core.evidence.conflicts import ConflictType, EvidenceConflict


def test_authority_does_not_resolve_methodological_conflict():
    conflict = EvidenceConflict("c1", ConflictType.METHODOLOGICAL, ("e1", "e2"), "different methods")
    result = ConflictResolver().resolve(conflict, policy_version="1")
    assert result.disposition is ResolutionDisposition.HUMAN_REVIEW
    assert result.selected_refs == ()
