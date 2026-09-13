from backend.app.core.decision.objective_semantics import DecisionObjective, ObjectiveDirection, ObjectiveMetric


def test_objective_has_explicit_metric_semantics():
    metric = ObjectiveMetric("delay", "minutes", ObjectiveDirection.MINIMIZE, "24h", "time_to_resolution")
    objective = DecisionObjective("service", metric, 1.0, "public_safety")
    assert objective.metric.direction is ObjectiveDirection.MINIMIZE
