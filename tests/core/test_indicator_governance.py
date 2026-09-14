import pytest

from app.core.scientific.indicator_governance import (
    IndicatorDefinition,
    IndicatorGovernance,
    PrivacyBudget,
    PrivacyBudgetLedger,
    RedTeamFinding,
)


def defs(epoch: str):
    return (
        IndicatorDefinition("incidence", epoch, 0.6, 0.7),
        IndicatorDefinition("mobility", epoch, 0.4, 0.5),
    )


def test_preregistration_hash_is_deterministic_and_verifiable() -> None:
    governance = IndicatorGovernance()
    registration = governance.preregister("reg-1", "2026-Q4", defs("2026-Q4"), "2026-09-15T00:00:00Z")
    assert registration.configuration_hash == governance.configuration_hash(defs("2026-Q4"))
    assert governance.verify_configuration("2026-Q4", defs("2026-Q4"))
    altered = (IndicatorDefinition("incidence", "2026-Q4", 0.9, 0.7), IndicatorDefinition("mobility", "2026-Q4", 0.1, 0.5))
    assert not governance.verify_configuration("2026-Q4", altered)


def test_preregistration_rejects_duplicate_registration_identity_across_epochs() -> None:
    governance = IndicatorGovernance()
    governance.preregister("reg-1", "2026-Q3", defs("2026-Q3"), "2026-07-01T00:00:00Z")
    with pytest.raises(ValueError, match="duplicate registration_id"):
        governance.preregister("reg-1", "2026-Q4", defs("2026-Q4"), "2026-10-01T00:00:00Z")


def test_rotation_retires_previous_epoch_and_requires_new_registration() -> None:
    governance = IndicatorGovernance()
    governance.preregister("reg-1", "2026-Q3", defs("2026-Q3"), "2026-07-01T00:00:00Z")
    governance.rotate("2026-Q3", "2026-Q4", defs("2026-Q4"), "2026-10-01T00:00:00Z")
    assert all(not item.active for item in governance.definitions("2026-Q3"))
    assert all(item.active for item in governance.definitions("2026-Q4"))


def test_exploitable_red_team_finding_blocks_deployment() -> None:
    governance = IndicatorGovernance()
    governance.preregister("reg-1", "2026-Q4", defs("2026-Q4"), "2026-09-15T00:00:00Z")
    governance.record_red_team_findings("2026-Q4", (RedTeamFinding("incidence", "high", True, "rt-1", "rotate indicator"),))
    assert not governance.deployable("2026-Q4")


def test_privacy_ledger_enforces_budget_and_actor_query_limit() -> None:
    ledger = PrivacyBudgetLedger(PrivacyBudget(epsilon=1.0), max_queries_per_actor=2)
    ledger.record_release("actor-a", 0.4)
    assert ledger.remaining_epsilon == 0.6
    ledger.record_release("actor-a", 0.4)
    with pytest.raises(ValueError, match="query limit"):
        ledger.record_release("actor-a", 0.1)


def test_privacy_ledger_rejects_budget_overrun() -> None:
    ledger = PrivacyBudgetLedger(PrivacyBudget(epsilon=0.5), max_queries_per_actor=10)
    with pytest.raises(ValueError, match="budget"):
        ledger.record_release("actor-a", 0.6)
