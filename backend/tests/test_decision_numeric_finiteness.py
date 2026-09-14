import math

import pytest

from app.core.decision.decision_system import ScenarioOutcome, DecisionOption


def test_scenario_outcome_rejects_nan_probability() -> None:
    with pytest.raises(ValueError, match="finite"):
        ScenarioOutcome("s1", math.nan, 0.0, 0.0)


def test_decision_option_rejects_nan_uncertainty() -> None:
    outcome = ScenarioOutcome("s1", 1.0, 0.0, 0.0)
    with pytest.raises(ValueError, match="finite"):
        DecisionOption("o1", (outcome,), uncertainty=math.nan)
