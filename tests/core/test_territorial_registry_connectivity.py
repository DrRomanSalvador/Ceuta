from app.core.metrics import (
    METRIC_REGISTRY,
    STRATEGIC_RISK_REGISTRY,
    TERRITORIAL_SYSTEMIC_METRICS,
    get_metric_definition,
)


def test_every_territorial_catalog_metric_has_epistemic_definition():
    missing = [
        metric_id
        for metric_id in TERRITORIAL_SYSTEMIC_METRICS
        if metric_id not in METRIC_REGISTRY and metric_id not in STRATEGIC_RISK_REGISTRY
    ]
    assert missing == []


def test_every_territorial_catalog_metric_resolves_to_its_own_definition():
    for metric_id in TERRITORIAL_SYSTEMIC_METRICS:
        assert get_metric_definition(metric_id).id == metric_id
