from datetime import datetime, timezone

from app.main import DecisionRequest, _final_epistemic_assessment
from app.core.decision.control_plane import EvidenceDisposition
from app.core.final_epistemic_control import EpistemicIntegrityStatus, SystemValidity
from app.core.runtime.decision_lifecycle import BitemporalRef, DecisionEvidence
from app.core.decision.control_plane import EvidenceAssessment
from app.core.decision.information_boundary import InformationVisibility


def payload(*, independent: bool = True, transformations: list[str] | None = None) -> DecisionRequest:
    return DecisionRequest(
        decision_id="d1",
        decision_maker="owner",
        horizon="24h",
        purpose="territorial decision support",
        state_refs=["state-1"],
        evidence=[
            {
                "evidence_id": "e1",
                "source_id": "s1",
                "claim_id": "c1",
                "content_hash": "a" * 64,
                "valid_from": datetime(2026, 9, 14, tzinfo=timezone.utc),
                "recorded_from": datetime(2026, 9, 14, tzinfo=timezone.utc),
                "base_weight": 1.0,
                "adversarial_risk": 0.0,
                "contradiction_weight": 0.0,
                "independent_origin": independent,
                "disposition": EvidenceDisposition.ACCEPT,
                "provenance_refs": ["source:s1"],
                "visibility": InformationVisibility.PUBLIC,
            }
        ],
        options=[
            {
                "option_id": "o1",
                "scenarios": [{"scenario_id": "sc1", "probability": 1.0, "utility": 1.0, "harm": 0.0}],
            }
        ],
        transformation_refs=transformations or ["t1"],
    )


def evidence_from_request(request: DecisionRequest) -> list[DecisionEvidence]:
    item = request.evidence[0]
    temporal = BitemporalRef(item.valid_from, item.valid_until, item.recorded_from, item.recorded_until, item.evidence_id)
    assessment = EvidenceAssessment(
        evidence_id=item.evidence_id,
        source_id=item.source_id,
        base_weight=item.base_weight,
        adversarial_risk=item.adversarial_risk,
        contradiction_weight=item.contradiction_weight,
        independent_origin=item.independent_origin,
        disposition=item.disposition,
    )
    return [DecisionEvidence(item.evidence_id, item.source_id, item.claim_id, item.content_hash, tuple(item.provenance_refs), temporal, assessment, item.visibility)]


def test_final_controller_is_on_the_decision_input_path():
    request = payload()
    assessment = _final_epistemic_assessment(request, evidence_from_request(request))
    assert assessment.validity is SystemValidity.SUPPORTED
    assert assessment.composition is EpistemicIntegrityStatus.PRESERVED


def test_missing_independent_evidence_suspends_decision_eligibility():
    request = payload(independent=False)
    assessment = _final_epistemic_assessment(request, evidence_from_request(request))
    assert assessment.validity is SystemValidity.DOUBT


def test_missing_transformation_contract_cannot_pass_final_composition():
    request = payload(transformations=[])
    request = request.model_copy(update={"transformation_refs": []})
    assessment = _final_epistemic_assessment(request, evidence_from_request(request))
    assert assessment.composition is EpistemicIntegrityStatus.UNKNOWN
