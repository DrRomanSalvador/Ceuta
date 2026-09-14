from datetime import datetime, timezone

from app.core.scientific.early_warning_adapter import EarlyWarningGovernanceAdapter
from app.core.scientific.early_warning_governance import (
    CryWolfPolicy,
    CryWolfTracker,
    EarlyWarningGovernance,
    VulnerabilityProfile,
    WarningOutcome,
)
from app.core.scientific.governance_signals import GovernanceDisposition, ScientificGovernance


def test_early_warning_assessment_has_actual_governance_effect(tmp_path):
    path = str(tmp_path / "ew.sqlite")
    tracker = CryWolfTracker(CryWolfPolicy(false_alarm_penalty=3.0), storage_path=path)
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    for i in range(5):
        tracker.record(WarningOutcome(f"f{i}", True, False, now))

    assessment = EarlyWarningGovernance(tracker, storage_path=path).assess(
        values=[float(i) for i in range(10)],
        vulnerability=VulnerabilityProfile(0.7, 0.7, 0.2, ("institutional fragility",)),
        now=now,
    )
    adapter = EarlyWarningGovernanceAdapter("release-1", "config-1")
    governance_input = adapter.to_input(
        assessment,
        evidence_ids=("e1",),
        provenance_refs=("p1",),
        evidence_quality=0.9,
        independent_evidence_ratio=0.9,
        contradiction_ratio=0.0,
    )
    signal = ScientificGovernance().evaluate("decision-1", governance_input, created_at=now)
    assert signal.disposition is GovernanceDisposition.ABSTAIN
    assert "mechanism_unsatisfied" in {reason.value for reason in signal.reasons}
