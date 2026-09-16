from datetime import datetime, timedelta, timezone

from app.core.scientific.response_consumer import consume_serpiente_response


def payload(**overrides):
    start = datetime(2026, 1, 1, 10, tzinfo=timezone.utc)
    end = start + timedelta(hours=2)
    base = {
        "response_id": "r1",
        "alert_id": "a1",
        "response_status": "NO_RESPONSE",
        "response_eligible": True,
        "eligible_from": start.isoformat(),
        "eligible_until": end.isoformat(),
        "intended_mechanism": "activate contingency review",
        "response_horizon": "2h",
        "causal_status": "NOT_ASSESSED",
        "provenance": ["alert:a1"],
        "implementation_failure": "no decision recorded",
    }
    base.update(overrides)
    return base


def test_warning_without_response_is_accepted_as_no_response():
    result = consume_serpiente_response(payload())
    assert result.accepted
    assert result.reason == "response_accepted_without_causal_promotion"


def test_executed_response_requires_decision_and_action():
    result = consume_serpiente_response(payload(response_status="EXECUTED"))
    assert not result.accepted
    assert "executed_requires_decision_and_action" in result.reason


def test_outcome_without_intervention_is_rejected():
    result = consume_serpiente_response(payload(outcome_id="o1"))
    assert not result.accepted
    assert "outcome_without_intervention" in result.reason


def test_causal_claim_requires_counterfactual_and_ascertainment():
    result = consume_serpiente_response(
        payload(
            response_status="EXECUTED",
            decision_id="d1",
            decision_time="2026-01-01T10:00:00+00:00",
            action_id="x1",
            action_time="2026-01-01T10:10:00+00:00",
            outcome_id="o1",
            outcome_time="2026-01-01T11:00:00+00:00",
            causal_status="IDENTIFIED",
        )
    )
    assert not result.accepted
    assert "counterfactual" in result.reason


def test_naive_eligibility_timestamp_is_rejected():
    result = consume_serpiente_response(payload(eligible_from="2026-01-01T10:00:00"))
    assert not result.accepted
    assert "eligibility_window" in result.reason
