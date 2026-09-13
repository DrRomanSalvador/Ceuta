from backend.app.core.decision.epistemic_gate import EpistemicDecisionGate, EpistemicDisposition
from backend.app.core.evidence.epistemic import EpistemicStatus


def test_unknown_and_insufficient_evidence_are_not_authorized():
    gate = EpistemicDecisionGate()
    assert gate.evaluate(EpistemicStatus.UNKNOWN).disposition is EpistemicDisposition.HUMAN_REVIEW
    assert gate.evaluate(EpistemicStatus.INSUFFICIENT_EVIDENCE).disposition is EpistemicDisposition.ABSTAIN
    assert gate.evaluate(EpistemicStatus.HYPOTHESIS).disposition is EpistemicDisposition.HUMAN_REVIEW
