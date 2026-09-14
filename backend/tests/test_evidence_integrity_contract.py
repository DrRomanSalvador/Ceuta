from datetime import datetime, timezone

import pytest

from app.core.decision.control_plane import EvidenceAssessment
from app.core.decision.information_boundary import InformationVisibility
from app.core.runtime.decision_lifecycle import BitemporalRef, DecisionEvidence
from app.core.runtime.integrity import validate_evidence_set


def test_evidence_set_rejects_non_hex_content_hash() -> None:
    assessment = EvidenceAssessment("e1", "s1", 1.0)
    evidence = DecisionEvidence(
        "e1",
        "s1",
        "c1",
        "z" * 64,
        ("source:s1",),
        BitemporalRef(
            datetime(2026, 1, 1, tzinfo=timezone.utc),
            None,
            datetime(2026, 1, 1, tzinfo=timezone.utc),
            None,
            "v1",
        ),
        assessment,
        InformationVisibility.PUBLIC,
    )
    with pytest.raises(ValueError, match="SHA-256"):
        validate_evidence_set((evidence,))
