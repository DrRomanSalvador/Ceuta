from datetime import datetime, timedelta, timezone

import numpy as np

from app.core.causal.estimators import AIPWBinaryATE
from app.core.decision.optimization import DecisionOptimizer
from app.core.forecasting.probabilistic import ProbabilisticForecastEngine
from app.core.runtime.official_sources import OfficialSource, OfficialSourceRegistry, SourceSnapshot


UTC = timezone.utc


def test_official_source_freshness_is_explicit_and_monotonic() -> None:
    source = OfficialSource("n", "NIST", "https://example.invalid", "US", timedelta(hours=1))
    registry = OfficialSourceRegistry((source,))
    now = datetime(2026, 9, 13, 12, tzinfo=UTC)
    assert registry.freshness(now)[0].reason == "never_retrieved"
    registry.register_snapshot(SourceSnapshot.from_bytes("n", b"x", now, 200, verified=True))
    assert registry.freshness(now)[0].current


def test_conformal_forecast_does_not_understate_observed_residual_scale() -> None:
    forecast = ProbabilisticForecastEngine.calibrated_forecast(
        1.0, 2.0, 10.0, (-1.0, 2.0, -3.0, 1.5), 0.90, "test"
    )
    assert forecast.lower <= 7.0
    assert forecast.upper >= 10.0


def test_aipw_requires_identification_assumptions() -> None:
    result = AIPWBinaryATE.estimate(
        [0, 1, 0, 1], [1, 3, 2, 4], [0.5] * 4, [1.5] * 4, [1.0] * 4,
        consistency=False, exchangeability=True,
    )
    assert not result.identified
    assert result.estimate is None


def test_aipw_recovers_simple_constant_effect() -> None:
    treatment = np.array([0, 1, 0, 1, 0, 1, 0, 1], dtype=float)
    outcome = 2.0 + 3.0 * treatment
    result = AIPWBinaryATE.estimate(
        treatment, outcome, [0.5] * len(treatment), [2.0] * len(treatment),
        [2.0] * len(treatment), consistency=True, exchangeability=True,
    )
    assert result.identified
    assert abs(result.estimate - 3.0) < 1e-12


def test_decision_optimizer_respects_harm_constraint() -> None:
    a = DecisionOptimizer.score("a", [10, 0], [0, 0], [0.5, 0.5])
    b = DecisionOptimizer.score("b", [20, -5], [2, 20], [0.5, 0.5], max_harm=5)
    chosen = DecisionOptimizer.select((a, b), objective="expected_utility")
    assert chosen.option_id == "a"
