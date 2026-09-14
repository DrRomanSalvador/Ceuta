from datetime import datetime, timedelta, timezone

import pytest

from app.core.scientific.longitudinal_mechanism import (
    ForecastReport,
    HorizonPolicy,
    LongitudinalIncentiveMechanism,
)


BASE = datetime(2030, 1, 1, tzinfo=timezone.utc)


def report(report_id, supplier, question, horizon, probability, evidence="e1"):
    return ForecastReport(
        report_id=report_id,
        supplier_id=supplier,
        question_id=question,
        horizon=horizon,
        probability=probability,
        submitted_at=BASE,
        deadline=BASE + timedelta(days=1),
        outcome_due_at=BASE + timedelta(days=2),
        evidence_ids=(evidence,),
        evidence_fingerprint=f"fp:{evidence}",
        specification_hash="spec-v1",
    )


def test_multihorizon_scoring_and_supplier_credibility_update():
    mechanism = LongitudinalIncentiveMechanism(
        policies=(HorizonPolicy("short", 2.0), HorizonPolicy("long", 1.0))
    )
    mechanism.submit(report("r1", "supplier-a", "q1", "short", 0.9))
    mechanism.submit(report("r2", "supplier-a", "q1", "long", 0.6))
    mechanism.settle("r1", outcome=1, verifier_id="verifier", verified_at=BASE + timedelta(days=3))
    mechanism.settle("r2", outcome=0, verifier_id="verifier", verified_at=BASE + timedelta(days=4))

    score = mechanism.score_question("q1")
    assert score["weighted_brier"] == pytest.approx((2 * 0.01 + 0.36) / 3)
    assert mechanism.credibility("supplier-a").observations == 2
    assert 0 < mechanism.credibility("supplier-a").credibility < 1


def test_provenance_chain_detects_tampering():
    mechanism = LongitudinalIncentiveMechanism()
    mechanism.submit(report("r1", "supplier-a", "q1", "default", 0.8))
    mechanism.settle("r1", outcome=1, verifier_id="verifier", verified_at=BASE + timedelta(days=3))
    assert mechanism.audit_chain_valid()

    settlement = mechanism._settlements["r1"]
    mechanism._settlements["r1"] = type(settlement)(
        settlement.report_id, settlement.outcome, settlement.log_loss + 0.1,
        settlement.brier_score, settlement.transfer, settlement.verified_at,
        settlement.verifier_id, settlement.previous_hash, settlement.provenance_hash,
        settlement.credibility,
    )
    assert not mechanism.audit_chain_valid()


def test_collusion_and_boundary_manipulation_are_flagged():
    mechanism = LongitudinalIncentiveMechanism()
    mechanism.submit(report("r1", "supplier-a", "q1", "default", 0.999999, "shared"))
    mechanism.submit(report("r2", "supplier-b", "q1", "default", 0.999999, "shared"))
    findings = mechanism.findings()
    assert any(f.__class__.__name__ == "CollusionFinding" for f in findings)


def test_strict_propriety_and_truthful_reporting_gap():
    candidates = (0.2, 0.4, 0.7, 0.9)
    assert LongitudinalIncentiveMechanism.verify_strict_propriety(
        belief=0.7, candidate_reports=candidates
    )
    assert LongitudinalIncentiveMechanism.truthful_report_gap(
        belief=0.7, report_probability=0.7
    ) == pytest.approx(0.0)
    assert LongitudinalIncentiveMechanism.truthful_report_gap(
        belief=0.7, report_probability=0.4
    ) > 0


def test_duplicate_supplier_question_horizon_is_rejected():
    mechanism = LongitudinalIncentiveMechanism()
    mechanism.submit(report("r1", "supplier-a", "q1", "default", 0.5))
    with pytest.raises(ValueError):
        mechanism.submit(report("r2", "supplier-a", "q1", "default", 0.6))
