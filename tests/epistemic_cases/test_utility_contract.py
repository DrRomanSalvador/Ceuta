from backend.app.core.decision.utility_contract import UtilityContract, UtilityDirection


def test_predictive_metrics_are_not_utility():
    contract = UtilityContract("u1", "outcome", "QALY", UtilityDirection.MAXIMIZE, "1y", "population", "adverse_event", ())
    assert not contract.accepts_predictive_metric("auc")
