from datetime import datetime, timedelta, timezone

import pytest

from app.core.decision.control_plane import EvidenceAssessment, EvidenceDisposition
from app.core.decision.information_boundary import InformationVisibility
from app.core.runtime.decision_lifecycle import BitemporalRef, DecisionEvidence
from app.core.runtime.integrity import validate_evidence_set


def make_evidence(valid_from: datetime, valid_until: datetime | None, recorded_from: datetime) -> DecisionEvidence:
    temporal = BitemporalRef(valid_from, valid_until, recorded_from, None, "e1")
    assessment = EvidenceAssessment(
        evidence_id="e1", source_id="s1", base_weight=1.0, adversarial_risk=0.0,
        contradiction_weight=0.0, independent_origin=True, disposition=EvidenceDisposition.ACCEPT,
    )
    return DecisionEvidence("e1", "s1", "c1", "a" * 64, ("source:s1",), temporal, assessment, InformationVisibility.PUBLIC)


def test_future_evidence_is_rejected():
    now = datetime.now(timezone.utc)
    evidence = make_evidence(now + timedelta(hours=1), None, now)
    with pytest.raises(ValueError, match="not valid at decision time"):
        validate_evidence_set([evidence], as_of=now)


def test_expired_evidence_is_rejected():
    now = datetime.now(timezone.utc)
    evidence = make_evidence(now - timedelta(hours=2), now - timedelta(hours=1), now - timedelta(hours=2))
    with pytest.raises(ValueError, match="not valid at decision time"):
        validate_evidence_set([evidence], as_of=now)
