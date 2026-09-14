from datetime import datetime, timezone

from app.core.scientific.early_warning_adapter import EarlyWarningGovernanceAdapter
from app.core.scientific.early_warning_governance import CryWolfPolicy, CryWolfTracker, EarlyWarningGovernance, VulnerabilityProfile, WarningOutcome
from app.core.scientific.governance_signals import GovernanceDisposition, ScientificGovernance


def test_csd_insufficiency_is_review_uncertainty_not_standalone_veto(tmp_path):
    path = str(tmp_path / "ew.sqlite")
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    tracker = CryWolfTracker(CryWolfPolicy(), storage_path=path)
    for i in range(5):
        tracker.record(WarningOutcome(f"w{i}", True, True, now))
    assessment = EarlyWarningGovernance(tracker, storage_path=path).assess(
        values=[float(i) for i in range(10)],
        vulnerability=VulnerabilityProfile(0.1, 0.1, 0.9, ("driver",)),
        now=now,
    )
    assert assessment.alert_allowed
    adapter = EarlyWarningGovernanceAdapter("r1", "c1")
    value = adapter.to_input(assessment, evidence_ids=("e1",), provenance_refs=("p1",), evidence_quality=0.9, independent_evidence_ratio=0.9, contradiction_ratio=0.0)
    signal = ScientificGovernance().evaluate("d1", value, created_at=now)
    assert signal.disposition is GovernanceDisposition.REVIEW_REQUIRED
    assert "uncertainty_high" in {reason.value for reason in signal.reasons}
