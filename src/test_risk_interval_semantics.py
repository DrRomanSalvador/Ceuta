def test_risk_result_distinguishes_heuristic_and_rate_intervals() -> None:
    from .risk_calculator import RiskResult

    result = RiskResult(
        risk_score=0.5,
        confidence_interval=(0.4, 0.6),
        confidence_level=0.95,
        standard_error=0.05,
        sample_size=10,
        component_scores={},
        alert_level="YELLOW",
        calculation_timestamp="2026-09-16T12:00:00+00:00",
        data_sources=["source"],
        audit_hash="hash",
        event_rate=0.1,
        denominator_id="denominator",
        event_rate_interval=(0.05, 0.18),
        event_rate_confidence_level=0.95,
    )
    payload = result.to_dict()
    assert payload["confidence_interval_semantics"] == "HEURISTIC_SCORE_INTERVAL_NOT_STATISTICAL_CONFIDENCE_INTERVAL"
    assert payload["event_rate_interval_semantics"] == "WILSON_BINOMIAL_PROPORTION_INTERVAL"
