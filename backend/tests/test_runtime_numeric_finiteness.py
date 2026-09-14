import math

import pytest

from app.core.decision.control_plane import EvidenceAssessment, UncertaintyState
from app.core.runtime.integrity import IntegrityEngine, ProvenanceEnvelope, validate_scenario_probabilities


def test_scenario_probability_validator_rejects_nan() -> None:
    with pytest.raises(ValueError, match="finite"):
        validate_scenario_probabilities((math.nan, 1.0))


def test_scenario_probability_validator_rejects_non_finite_tolerance() -> None:
    with pytest.raises(ValueError, match="tolerance"):
        validate_scenario_probabilities((1.0,), tolerance=math.nan)


def test_provenance_trust_score_rejects_nan() -> None:
    envelope = ProvenanceEnvelope(
        record_id="r1",
        source_id="s1",
        origin_id="o1",
        content_hash="0" * 64,
        trust_score=math.nan,
    )
    result = IntegrityEngine().verify(envelope, b"payload")
    assert result.valid is False
    assert "invalid trust score" in result.reasons


def test_evidence_assessment_and_uncertainty_reject_non_finite_values() -> None:
    with pytest.raises(ValueError):
        EvidenceAssessment("e1", "s1", math.nan)
    with pytest.raises(ValueError):
        UncertaintyState(math.nan)
