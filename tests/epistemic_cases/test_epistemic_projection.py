from backend.app.core.evidence.epistemic import EpistemicClaim, EpistemicStatus
from backend.app.core.evidence.epistemic_projection import is_fact, is_forecast, is_reported, project_claim


def test_forecast_and_reported_claims_remain_distinct_from_observation():
    observed = project_claim(EpistemicClaim("o", "observed", EpistemicStatus.OBSERVED, ("s",)))
    forecast = project_claim(EpistemicClaim("f", "forecast", EpistemicStatus.FORECAST, ("s",)))
    reported = project_claim(EpistemicClaim("r", "reported", EpistemicStatus.REPORTED, ("s",)))
    assert is_fact(observed)
    assert is_forecast(forecast)
    assert is_reported(reported)
    assert not is_fact(forecast)
    assert not is_fact(reported)
