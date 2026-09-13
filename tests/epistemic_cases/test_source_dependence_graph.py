from backend.app.core.evidence.dependence_graph import SourceDependenceGraph, SourceDependency


def test_common_origin_is_not_counted_as_independent() -> None:
    graph = SourceDependenceGraph()
    graph.add(SourceDependency("a", common_origin="wire-service"))
    graph.add(SourceDependency("b", common_origin="wire-service"))
    graph.add(SourceDependency("c", common_origin="primary-record"))

    assert graph.is_dependent("a", "b")
    assert graph.independent_sources(("a", "b", "c")) == ("a", "c")


def test_transitive_dependency_is_detected() -> None:
    graph = SourceDependenceGraph()
    graph.add(SourceDependency("a"))
    graph.add(SourceDependency("b", depends_on=("a",)))
    graph.add(SourceDependency("c", depends_on=("b",)))

    assert graph.is_dependent("c", "a")
