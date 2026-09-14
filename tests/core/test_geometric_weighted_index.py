import pytest

from app.core.metrics import geometric_weighted_index


def test_geometric_weighted_index_returns_zero_for_positive_weighted_zero_value():
    assert geometric_weighted_index([0.0, 4.0], [1.0, 1.0]) == pytest.approx(0.0)


def test_geometric_weighted_index_ignores_zero_weight_entries():
    assert geometric_weighted_index([0.0, 4.0], [0.0, 1.0]) == pytest.approx(4.0)
