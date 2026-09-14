import pytest

from app.core.forecasting.scoring import brier_score, logarithmic_score, mean_brier_score


def test_brier_score_is_zero_for_perfect_binary_forecast() -> None:
    assert brier_score(1.0, 1) == 0.0
    assert brier_score(0.0, 0) == 0.0


def test_brier_score_penalizes_confident_wrong_forecast() -> None:
    assert brier_score(1.0, 0) == 1.0


def test_logarithmic_score_rewards_higher_probability_for_observed_event() -> None:
    assert logarithmic_score(0.9, 1) < logarithmic_score(0.6, 1)


def test_mean_brier_score_requires_aligned_non_empty_inputs() -> None:
    assert mean_brier_score((0.9, 0.1), (1, 0)) == pytest.approx(0.01)
    with pytest.raises(ValueError):
        mean_brier_score((), ())
    with pytest.raises(ValueError):
        mean_brier_score((0.5,), (0, 1))


def test_scoring_rejects_invalid_inputs() -> None:
    with pytest.raises(ValueError):
        brier_score(1.1, 1)
    with pytest.raises(ValueError):
        brier_score(0.5, 2)
