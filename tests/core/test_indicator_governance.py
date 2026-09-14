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
    altered = (
        IndicatorDefinition("incidence", "2026-Q4", 0.9, 0.7),
        IndicatorDefinition("mobility", "2026-Q4", 0.1, 0.5),
    )
    assert not governance.verify_configuration("2026-Q4", altered)


def test_rotation_retires_previous_epoch_and_requires_new_registration() -> None:
    governance = IndicatorGovernance()
    governance.preregister("reg-1", "2026-Q3", defs("2026-Q3"), "2026-07-01T00:00:00Z")
    governance.rotate("2026-Q3", "2026-Q4", defs("2026-Q4"), "2026-10-01T00:00:00Z")
    assert all(not item.active for item in governance.definitions("2026-Q3"))
    assert all(item.active for item in governance.definitions("2026-Q4"))


def test_exploitable_red_team_finding_blocks_deployment() -> None:
    governance = IndicatorGovernance()
    governance.preregister("reg-1", "2026-Q4", defs("2026-Q4"), "2026-09-15T00:00:00Z")
    governance.record_red_team_findings(
        "2026-Q4",
        (RedTeamFinding("incidence", "high", True, "rt-1", "rotate indicator"),),
    )
    assert not governance.deployable("2026-Q4")


def test_privacy_ledger_enforces_budget_and_actor_query_limit() -> None:
    ledger = PrivacyBudgetLedger(PrivacyBudget(epsilon=1.0), max_queries_per_actor=2)
    assert ledger.noisy_sum("actor-a", (1.0, 2.0), sensitivity=1.0, epsilon=0.4, noise=0.0) == 3.0
    assert ledger.remaining_epsilon == 0.6
    ledger.noisy_sum("actor-a", (2.0,), sensitivity=1.0, epsilon=0.4, noise=0.0)
    try:
        ledger.noisy_sum("actor-a", (3.0,), sensitivity=1.0, epsilon=0.1, noise=0.0)
    except ValueError as exc:
        assert "query limit" in str(exc)
    else:
        raise AssertionError("expected actor query limit")


def test_privacy_ledger_rejects_budget_overrun() -> None:
    ledger = PrivacyBudgetLedger(PrivacyBudget(epsilon=0.5), max_queries_per_actor=10)
    try:
        ledger.consume("actor-a", 0.6)
    except ValueError as exc:
        assert "budget" in str(exc)
    else:
        raise AssertionError("expected privacy budget exhaustion")
