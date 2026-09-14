from datetime import datetime, timezone

import pytest

from app.core.system_intelligence import (
    IdentifiabilityAnalyzer,
    InformationAnalyzer,
    MissingnessAnalyzer,
    MissingnessMechanism,
    ModelAlternative,
    ModelDisagreementAnalyzer,
    NetworkAnalyzer,
    ObservabilityAnalyzer,
    PredictabilityAnalyzer,
    Regime,
    RegimeDetector,
    Scale,
    SpatialRelation,
    StateEstimator,
    StateHypothesis,
    StateKind,
)


def test_state_estimator_preserves_competing_hypotheses() -> None:
    covariance = ((0.1, 0.0), (0.0, 0.1))
    result = StateEstimator.combine(
        (
            StateHypothesis("a", (1.0, 2.0), covariance, StateKind.LATENT, 0.6),
            StateHypothesis("b", (3.0, 4.0), covariance, StateKind.LATENT, 0.4),
        )
    )
    assert result.estimate == pytest.approx((1.8, 2.8))
    assert result.identifiable is False
    assert "competing" in result.uncertainty_note


def test_linear_observability_detects_unobserved_dimension() -> None:
    assessment = ObservabilityAnalyzer.linear(((1.0, 0.0), (0.0, 1.0)), ((1.0, 0.0),))
    assert assessment.observable is False
    assert assessment.rank == 1


def test_identifiability_rejects_collinear_parameter_sensitivity() -> None:
    assessment = IdentifiabilityAnalyzer.from_sensitivity(((1.0, 2.0), (2.0, 4.0)))
    assert assessment.identifiable is False
    assert assessment.rank == 1


def test_missingness_risk_is_monotone() -> None:
    assert MissingnessAnalyzer.risk((MissingnessMechanism.MNAR,)) > MissingnessAnalyzer.risk((MissingnessMechanism.MAR,))


def test_network_cascade_represents_interaction_failure() -> None:
    active = NetworkAnalyzer.cascade(("a", "b", "c"), (("a", "b", 1.0), ("b", "c", 1.0)), ("a",), threshold=0.5)
    assert active == ("a", "b", "c")


def test_information_gain_zero_for_independent_constant_relation() -> None:
    assert InformationAnalyzer.mutual_information((0, 0, 0), (0, 1, 1)) == pytest.approx(0.0)


def test_predictability_abstains_after_mechanism_change() -> None:
    assessment = PredictabilityAnalyzer.assess((0.1, 0.2), mechanism_changed=True)
    assert assessment.abstain_recommended is True


def test_model_disagreement_is_preserved() -> None:
    result = ModelDisagreementAnalyzer.compare(
        (
            ModelAlternative("m1", "1", 0.1, 0.1, "valid"),
            ModelAlternative("m2", "1", 0.5, 0.1, "valid"),
        )
    )
    assert result is not None
    assert result.material is True
    assert result.spread == pytest.approx(0.4)


def test_regime_requires_dwell() -> None:
    current = Regime("normal", "normal", upper_bound=1.0)
    candidate = Regime("stress", "stress", lower_bound=2.0, minimum_dwell=3)
    result = RegimeDetector.detect(2.5, current, candidate, dwell=2)
    assert result.changed is False
    result = RegimeDetector.detect(2.5, current, candidate, dwell=3)
    assert result.changed is True


def test_temporal_and_spatial_contracts_require_aware_timestamps() -> None:
    now = datetime.now(timezone.utc)
    assert now.tzinfo is not None
    relation = SpatialRelation("north", "south", 1.0, "adjacent")
    assert relation.source_id != relation.target_id
    assert Scale.CITY.value == "city"
