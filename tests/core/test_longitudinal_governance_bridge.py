from datetime import datetime, timedelta, timezone

import pytest

from app.core.scientific.bounded_log_score import BoundedLogScorePolicy
from app.core.scientific.governance_signals import GovernanceDisposition, GovernanceReason, ScientificGovernance
from app.core.scientific.longitudinal_governance_adapter import LongitudinalGovernanceAdapter
from app.core.scientific.longitudinal_mechanism import ForecastReport, LongitudinalIncentiveMechanism


BASE = datetime(2030, 1, 1, tzinfo=timezone.utc)


def make_report(report_id: str, supplier: str, probability: float = 0.8, evidence: str = "e1") -> ForecastReport:
    return ForecastReport(
        report_id=report_id,
        supplier_id=supplier,
        question_id=f"q-{report_id}",
        horizon="default",
        probability=probability,
        submitted_at=BASE,
        deadline=BASE + timedelta(days=1),
        outcome_due_at=BASE + timedelta(days=2),
        evidence_ids=(evidence,),
        evidence_fingerprint=f"fp:{evidence}",
        specification_hash="spec-v1",
    )


def test_restart_rebuilds_credibility_from_durable_settlements(tmp_path):
    db = tmp_path / "longitudinal.sqlite"
    first = LongitudinalIncentiveMechanism(storage_path=str(db))
    first.submit(make_report("r1", "supplier-a", 0.9))
    first.settle("r1", outcome=1, verifier_id="verifier", verified_at=BASE + timedelta(days=3))
    expected = first.credibility("supplier-a")

    restarted = LongitudinalIncentiveMechanism(storage_path=str(db))
    assert restarted.credibility("supplier-a").observations == 0

    adapter = LongitudinalGovernanceAdapter(restarted)
    restored = restarted.credibility("supplier-a")
    assert restored.observations == expected.observations
    assert restored.mean_brier == pytest.approx(expected.mean_brier)
    assert restored.credibility == pytest.approx(expected.credibility)
    assert adapter.state("supplier-a").provenance_chain_valid


def test_longitudinal_findings_change_governance_disposition(tmp_path):
    db = tmp_path / "longitudinal.sqlite"
    mechanism = LongitudinalIncentiveMechanism(storage_path=str(db), similarity_threshold=0.999)
    mechanism.submit(make_report("r1", "supplier-a", 0.9, "shared"))
    mechanism.submit(make_report("r2", "supplier-b", 0.9, "shared"))
    adapter = LongitudinalGovernanceAdapter(mechanism)
    governance = ScientificGovernance(storage_path=str(db))

    signal = adapter.evaluate(
        governance,
        "decision-collusion",
        "supplier-a",
        code_revision="test-revision",
        configuration_hash="test-config",
    )
    assert signal.disposition is GovernanceDisposition.ABSTAIN
    assert GovernanceReason.COLLUSION_FLAG in signal.reasons


def test_corrupted_chain_fails_closed(tmp_path):
    db = tmp_path / "longitudinal.sqlite"
    mechanism = LongitudinalIncentiveMechanism(storage_path=str(db))
    mechanism.submit(make_report("r1", "supplier-a"))
    mechanism.settle("r1", outcome=1, verifier_id="verifier", verified_at=BASE + timedelta(days=3))
    settlement = mechanism._settlements["r1"]
    mechanism._settlements["r1"] = type(settlement)(
        settlement.report_id,
        settlement.outcome,
        settlement.log_loss + 0.01,
        settlement.brier_score,
        settlement.transfer,
        settlement.verified_at,
        settlement.verifier_id,
        settlement.previous_hash,
        settlement.provenance_hash,
        settlement.credibility,
    )
    adapter = LongitudinalGovernanceAdapter(mechanism)
    signal = adapter.evaluate(
        ScientificGovernance(storage_path=str(db)),
        "decision-integrity",
        "supplier-a",
        code_revision="test-revision",
        configuration_hash="test-config",
    )
    assert signal.disposition is GovernanceDisposition.ABSTAIN
    assert GovernanceReason.PROVENANCE_COMPROMISED in signal.reasons


def test_bounded_log_score_preserves_strict_propriety_and_exposure_bound():
    policy = BoundedLogScorePolicy(epsilon=0.01, stake=2.0)
    assert policy.maximum_loss == pytest.approx(2.0 * -__import__("math").log(0.01))
    assert policy.strictly_proper(belief=0.7, candidate_reports=(0.2, 0.4, 0.7, 0.9))
    assert policy.truthful_report_gap(belief=0.7, report_probability=0.4) > 0
    with pytest.raises(ValueError):
        policy.validate_report(0.001)
