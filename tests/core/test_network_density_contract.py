import pytest

from app.core.metrics import MetricInputError, network_density


def test_network_density_rejects_more_edges_than_simple_graph_allows():
    with pytest.raises(MetricInputError, match="edge_count|max|edges"):
        network_density(3, 4)


def test_network_density_rejects_negative_and_fractional_edge_counts():
    with pytest.raises(MetricInputError, match="tamaños|edge_count"):
        network_density(4, -1)
    with pytest.raises(MetricInputError, match="edge_count"):
        network_density(4, 2.5)


def test_network_density_returns_one_for_complete_simple_graph():
    assert network_density(4, 6) == pytest.approx(1.0)
