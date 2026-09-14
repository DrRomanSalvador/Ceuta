import pytest

from app.core.privacy.aggregation_layer import PrivacyAggregationLayer


def test_minimum_group_size_is_an_explicit_suppression_boundary() -> None:
    layer = PrivacyAggregationLayer()

    with pytest.raises(PermissionError, match="privacy minimum size"):
        layer.aggregate((1.0, 2.0), minimum_group_size=3)


def test_aggregation_is_deterministic_and_has_no_pseudo_noise_contract() -> None:
    result = PrivacyAggregationLayer().aggregate(
        tuple(float(value) for value in range(10)),
        minimum_group_size=10,
    )

    assert result.count == 10
    assert result.mean == 4.5
    assert not hasattr(result, "noise_scale")


def test_invalid_group_size_and_nonfinite_values_are_rejected() -> None:
    layer = PrivacyAggregationLayer()

    with pytest.raises(ValueError, match="minimum_group_size"):
        layer.aggregate((1.0,), minimum_group_size=0)
    with pytest.raises(ValueError, match="finite"):
        layer.aggregate((1.0, float("nan")), minimum_group_size=1)
