from datetime import datetime, timezone, timedelta

import pytest

from app.missions.founder_domain import (
    DecisionRecord,
    Evidence,
    FounderDomainError,
    RevenueEvent,
    allowed_transition,
    is_stale,
    validate_authority,
    validate_external_claim,
    validate_resource_reservation,
    validate_transition_invariants,
)


def external(source="customer:001"):
    return Evidence("E1", "CUSTOMER_BEHAVIOUR", source, "2026-09-16T10:00:00+00:00", "Observed repeated customer behaviour")


def generated():
    return Evidence("G1", "FOUNDER_GENERATED_HYPOTHESIS", "founder:analysis", "2026-09-16T10:00:00+00:00", "Generated hypothesis", independent=True)


def test_paid_pilot_cannot_become_repeatable_without_repeated_paid_outcomes():
    with pytest.raises(FounderDomainError, match="REPEATABLE_REQUIRES_REPEATED_PAID_OUTCOMES"):
        validate_transition_invariants("REPEATABLE", [external()], repeatable_outcomes=1)


def test_revenue_quality_distinguishes_pilot_from_recurring():
    with pytest.raises(FounderDomainError, match="PILOT_REVENUE_CANNOT_BE_DECLARED_RECURRING"):
        RevenueEvent("R1", "PILOT_REVENUE", "100", "2026-09-16T10:00:00+00:00", True, True, "tx:1").validate()


def test_generated_output_cannot_self_validate_as_independent_evidence():
    with pytest.raises(FounderDomainError, match="SELF_GENERATED_EVIDENCE_CANNOT_BE_INDEPENDENT"):
        generated().validate()


def test_external_claim_requires_independent_evidence_and_authority():
    with pytest.raises(FounderDomainError, match="EXTERNAL_CLAIM_AUTHORIZATION_REQUIRED"):
        validate_external_claim([external()], False)
    with pytest.raises(FounderDomainError, match="EXTERNAL_CLAIM_REQUIRES_INDEPENDENT_EVIDENCE"):
        validate_external_claim([Evidence("G2", "SYSTEM_OUTPUT", "system:1", "2026-09-16T10:00:00+00:00", "System output", False)], True)
    validate_external_claim([external()], True)


def test_authority_escalation_is_rejected():
    with pytest.raises(FounderDomainError, match="OPERATIONAL_AUTHORITY_REQUIRED"):
        validate_authority("SIGN_AGREEMENT", {"AUTHORIZED_EXECUTION": False})
    validate_authority("ANALYZE", {"AUTHORIZED_EXECUTION": False})


def test_forbidden_opportunity_jump_is_rejected():
    with pytest.raises(FounderDomainError, match="FORBIDDEN_OPPORTUNITY_TRANSITION"):
        allowed_transition("DISCOVERED", "REPEATABLE", [external()])


def test_stale_commercial_fact_is_detectable():
    old = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
    assert is_stale(old, 86400) is True


def test_resource_reservation_requires_a_complete_record():
    with pytest.raises(FounderDomainError, match="RESOURCE_RESERVATION_REQUIRED_FIELD_MISSING"):
        validate_resource_reservation("R", "", "purpose", "start", "end", "ACTIVE", "REJECT", "release", "source")


def test_abstention_requires_explicit_uncertainty():
    with pytest.raises(FounderDomainError, match="ABSTAIN_REQUIRES_EXPLICIT_UNCERTAINTY"):
        DecisionRecord("D1", "O1", 1, "SCREEN", "PAUSE", "learn", ("E1",), (), (), (), "continue", "1", "1d", "high", "medium", "medium", "reversible", "none", "x", "y", "COGNITIVE", None, "ABSTAIN_FROM_DECISION", "2026-09-20", "source").validate()
