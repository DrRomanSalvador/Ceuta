from datetime import datetime, timezone

import pytest

from app.core.decision.control_plane import EvidenceAssessment, EvidenceDisposition
from app.core.decision.information_boundary import InformationVisibility
from app.core.runtime.decision_lifecycle import BitemporalRef, DecisionEvidence
from app.core.runtime.integrity import validate_evidence_set, validate_scenario_probabilities


def _evidence(evidence_id: str, disposition: EvidenceDisposition = EvidenceDisposition.ACCEPT) -> DecisionEvidence:
    now = datetime.now(timezone.utc)
    assessment = EvidenceAssessment(
        evidence_id=evidence_id,
        source_id="official:test",
        base_weight=1.0,
        disposition=disposition,
    )
    return DecisionEvidence(
        evidence_id=evidence_id,
        source_id="official:test",
        claim_id="claim:test",
        content_hash="0" * 64,
        provenance_refs=("source:test",),
        temporal=BitemporalRef(now, None, now, None, evidence_id),
        assessment=assessment,
        visibility=InformationVisibility.PUBLIC,
    )


def test_evidence_identity_is_unique() -> None:
    validate_evidence_set([_evidence("e1")])
    with pytest.raises(ValueError, match="duplicate evidence identity"):
        validate_evidence_set([_evidence("e1"), _evidence("e1")])


def test_blocked_evidence_fails_closed() -> None:
    with pytest.raises(ValueError, match="blocked/quarantined"):
        validate_evidence_set([_evidence("e1", EvidenceDisposition.BLOCK)])


def test_scenario_probabilities_must_form_distribution() -> None:
    validate_scenario_probabilities([0.25, 0.75])
    with pytest.raises(ValueError, match="sum to 1"):
        validate_scenario_probabilities([0.25, 0.25])
