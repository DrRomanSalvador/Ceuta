from datetime import datetime, timezone

from app.core.epistemology_p0.operational.evidence_decision_bridge import (
    EpistemicStatus,
    EvidenceDecisionBridge,
    EvidenceRecord,
)


UTC = timezone.utc


def test_stale_current_value_is_estimated_with_interval_and_provenance():
    bridge = EvidenceDecisionBridge()
    evidence = tuple(
        EvidenceRecord(
            evidence_id=f"e{i}",
            source_id="official",
            observed_at=datetime(2026, 1 + i, 1, tzinfo=UTC),
            quality=0.95,
        )
        for i in range(3)
    )
    observations = tuple(
        (item.observed_at, float(100 + 5 * i), item.evidence_id)
        for i, item in enumerate(evidence)
    )
    result = bridge.resolve_current_value(
        observations=observations,
        evidence=evidence,
        as_of=datetime(2026, 5, 1, tzinfo=UTC),
        half_life_days=365,
    )

    assert result.status is EpistemicStatus.ESTIMATED
    assert result.value is not None
    assert result.interval_lower is not None
    assert result.interval_upper is not None
    assert result.interval_lower <= result.value <= result.interval_upper
    assert result.interval_confidence == 0.95
    assert result.evidence_refs == ("e0", "e1", "e2")


def test_direct_current_observation_is_not_relabelled_as_estimate():
    bridge = EvidenceDecisionBridge()
    at = datetime(2026, 9, 13, tzinfo=UTC)
    evidence = EvidenceRecord("e1", "official", at, quality=1.0)
    result = bridge.resolve_current_value(
        observations=((at, 42.0, "e1"),),
        evidence=(evidence,),
        as_of=at,
        half_life_days=365,
    )

    assert result.status is EpistemicStatus.OBSERVED
    assert result.value == 42.0
    assert result.uncertainty == 0.0


def test_decision_uncertainty_uses_conservative_epistemic_maximum():
    bridge = EvidenceDecisionBridge()
    assert bridge.combine_decision_uncertainty(0.30, 0.70) == 0.70
    assert bridge.combine_decision_uncertainty(0.80, 0.20) == 0.80
