import pytest

from backend.app.core.evidence.epistemic import (
    EpistemicClaim,
    EpistemicStatus,
    epistemic_distance,
    may_support_decision,
)


def test_forecast_is_not_observation() -> None:
    assert EpistemicStatus.FORECAST is not EpistemicStatus.OBSERVED
    assert epistemic_distance(EpistemicStatus.FORECAST) > epistemic_distance(EpistemicStatus.OBSERVED)


def test_unknown_and_insufficient_evidence_cannot_support_decision() -> None:
    assert not may_support_decision(EpistemicStatus.UNKNOWN)
    assert not may_support_decision(EpistemicStatus.INSUFFICIENT_EVIDENCE)


def test_evidence_bearing_claim_requires_sources() -> None:
    with pytest.raises(ValueError):
        EpistemicClaim("claim-1", "reported event", EpistemicStatus.REPORTED)


def test_hypothesis_remains_explicit() -> None:
    claim = EpistemicClaim(
        "claim-2",
        "possible escalation",
        EpistemicStatus.HYPOTHESIS,
        source_refs=("source-1",),
    )
    assert claim.status is EpistemicStatus.HYPOTHESIS
