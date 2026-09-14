from datetime import datetime, timedelta, timezone

import pytest

from app.core.scientific.mechanism import ForecastReport, ProperScoringMechanism


BASE = datetime(2026, 9, 15, tzinfo=timezone.utc)


def make_report(report_id: str = "r1", probability: float = 0.7) -> ForecastReport:
    return ForecastReport(
        report_id=report_id,
        forecaster_id="agent-a",
        question_id="q1",
        probability=probability,
        submitted_at=BASE,
        deadline=BASE + timedelta(hours=1),
        outcome_due_at=BASE + timedelta(days=1),
    )


def test_mechanism_settles_verified_report_and_computes_transfer() -> None:
    mechanism = ProperScoringMechanism(stake=10.0)
    mechanism.submit(make_report(probability=0.8))
    settlement = mechanism.settle(
        "r1", outcome=1, verified_at=BASE + timedelta(days=1), verifier_id="verifier-1"
    )
    assert settlement.outcome == 1
    assert settlement.transfer < 0
    assert mechanism.settlement("r1") == settlement


def test_persistent_state_survives_mechanism_restart(tmp_path) -> None:
    path = str(tmp_path / "mechanism.sqlite")
    first = ProperScoringMechanism(stake=2.0, storage_path=path)
    first.submit(make_report(probability=0.8))
    first.settle("r1", outcome=1, verified_at=BASE + timedelta(days=1), verifier_id="v1")

    second = ProperScoringMechanism(stake=2.0, storage_path=path)
    assert second.report("r1") == first.report("r1")
    assert second.settlement("r1") == first.settlement("r1")


def test_duplicate_forecaster_question_is_rejected() -> None:
    mechanism = ProperScoringMechanism()
    mechanism.submit(make_report())
    with pytest.raises(ValueError):
        mechanism.submit(make_report("r2", probability=0.6))


def test_settlement_cannot_precede_outcome_due_time() -> None:
    mechanism = ProperScoringMechanism()
    mechanism.submit(make_report())
    with pytest.raises(ValueError):
        mechanism.settle("r1", outcome=1, verified_at=BASE, verifier_id="verifier-1")


def test_log_score_rejects_probability_endpoints() -> None:
    with pytest.raises(ValueError, match="strictly between"):
        make_report(probability=0.0)
    with pytest.raises(ValueError, match="strictly between"):
        ProperScoringMechanism.expected_log_loss(1.0, 0.7)


def test_log_score_rejects_endpoint_candidates() -> None:
    with pytest.raises(ValueError, match="strictly between"):
        ProperScoringMechanism.verify_strict_propriety(
            belief=0.7, candidate_reports=(0.0, 0.7, 0.8)
        )


def test_log_score_is_strictly_proper_on_grid() -> None:
    candidates = tuple(i / 10 for i in range(1, 10))
    assert ProperScoringMechanism.verify_strict_propriety(belief=0.7, candidate_reports=candidates)
    assert not ProperScoringMechanism.verify_strict_propriety(belief=0.75, candidate_reports=candidates)


def test_expected_log_loss_is_minimized_at_truthful_belief() -> None:
    belief = 0.8
    truthful = ProperScoringMechanism.expected_log_loss(belief, belief)
    nearby = ProperScoringMechanism.expected_log_loss(0.7, belief)
    assert truthful < nearby
