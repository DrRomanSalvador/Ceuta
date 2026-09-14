import pytest

from app.core.complex_systems.state_space import GaussianState, LinearStateSpace, StateSpaceEngine


def model() -> LinearStateSpace:
    return LinearStateSpace(
        transition=((1.0,),),
        process_covariance=((0.1,),),
        observation=((1.0,),),
        observation_covariance=((0.2,),),
    )


def test_predict_increases_variance_with_process_noise() -> None:
    state = GaussianState((1.0,), ((0.5,),))
    predicted = StateSpaceEngine.predict(model(), state)
    assert predicted.mean == pytest.approx((1.0,))
    assert predicted.covariance[0][0] == pytest.approx(0.6)


def test_update_moves_state_toward_observation() -> None:
    state = GaussianState((1.0,), ((0.5,),))
    updated = StateSpaceEngine.update(model(), state, (2.0,))
    assert 1.0 < updated.mean[0] < 2.0
    assert updated.covariance[0][0] < state.covariance[0][0]


def test_singular_observation_covariance_is_rejected() -> None:
    bad = LinearStateSpace(((1.0,),), ((0.0,),), ((1.0,),), ((0.0,),))
    with pytest.raises(ValueError, match="singular"):
        StateSpaceEngine.update(bad, GaussianState((1.0,), ((0.0,),)), (1.0,))
