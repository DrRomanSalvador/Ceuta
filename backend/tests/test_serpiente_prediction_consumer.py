from datetime import datetime, timedelta, timezone

import pytest

from app.core.decision.control_plane import EvidenceAssessment, EvidenceDisposition
from app.core.decision.information_boundary import InformationVisibility
from app.core.final_epistemic_control import EpistemicIntegrityStatus, SystemValidity
from app.core.runtime.decision_lifecycle import BitemporalRef, DecisionEvidence
from app.main import DecisionRequest, _final_epistemic_assessment


def _request(origin_time: datetime) -> DecisionRequest:
    return DecisionRequest(
        decision_id="serpiente-consumer-test",
        decision_maker="owner",
        horizon="24h",
        purpose="cross-system prediction consumption",
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
                "independent_origin": True,
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
        transformation_refs=["t1"],
        serpiente_prediction={
            "schema_version": "1.0",
            "prediction_id": "prediction-1",
            "origin_time": origin_time,
            "horizon": "24h",
            "target": "risk",
            "probability": 0.7,
            "lower": 0.5,
            "upper": 0.9,
            "uncertainty": {"aleatoric": 0.1, "epistemic": 0.2},
            "model_disagreement": 0.1,
            "regime": "STABLE",
            "provenance": ["official:source-1"],
            "point_in_time_fingerprint": "b" * 64,
        },
    )


def _evidence(request: DecisionRequest) -> list[DecisionEvidence]:
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


def test_serpiente_prediction_is_consumed_by_epistemic_decision_gate():
    request = _request(datetime.now(timezone.utc) - timedelta(minutes=1))
    assessment = _final_epistemic_assessment(request, _evidence(request))
    assert assessment.validity is SystemValidity.SUPPORTED
    assert assessment.composition is EpistemicIntegrityStatus.PRESERVED
    assert f"serpiente:prediction:{request.serpiente_prediction.prediction_id}" in assessment.reality_anchor.external_evidence_refs


def test_future_serpiente_prediction_is_rejected_before_decision_eligibility():
    request = _request(datetime.now(timezone.utc) + timedelta(minutes=1))
    with pytest.raises(ValueError, match="future"):
        _final_epistemic_assessment(request, _evidence(request))
