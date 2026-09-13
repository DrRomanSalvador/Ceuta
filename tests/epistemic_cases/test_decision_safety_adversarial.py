from backend.app.core.decision.epistemic_gate import EpistemicDecisionGate, EpistemicDisposition
from backend.app.core.evidence.conflict_resolution import ConflictResolver, ResolutionDisposition
from backend.app.core.evidence.conflicts import ConflictType, EvidenceConflict
from backend.app.core.evidence.epistemic import EpistemicStatus


def test_contradictory_evidence_cannot_be_silently_resolved_by_authority():
    conflict = EvidenceConflict("c", ConflictType.VALUE, ("official", "independent"), "contradictory values")
    result = ConflictResolver().resolve(conflict, policy_version="1")
    assert result.disposition is ResolutionDisposition.HUMAN_REVIEW
    assert not result.selected_refs


def test_dependent_sources_require_review():
    conflict = EvidenceConflict("c", ConflictType.DEPENDENCE, ("s1", "s2"), "common origin")
    result = ConflictResolver().resolve(conflict, policy_version="1")
    assert result.disposition is ResolutionDisposition.HUMAN_REVIEW


def test_unknown_and_insufficient_evidence_cannot_auto_authorize():
    gate = EpistemicDecisionGate()
    assert gate.evaluate(EpistemicStatus.UNKNOWN).disposition is not EpistemicDisposition.ALLOW
    assert gate.evaluate(EpistemicStatus.INSUFFICIENT_EVIDENCE).disposition is EpistemicDisposition.ABSTAIN
