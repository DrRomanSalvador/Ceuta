"""Build deterministic trace edges from the existing ScientificSourceCorpus.

This is an adapter over the corpus, not a second registry. It makes the existing
source findings/limitations/mechanisms/validation requirements executable graph
nodes while preserving their source identity.
"""
from __future__ import annotations

from .scientific_traceability import ScientificTraceGraph, TraceEdge, TraceNode, stable_id
from .source_corpus import ScientificImpactMap, ScientificSourceRecord


def trace_source(graph: ScientificTraceGraph, source: ScientificSourceRecord) -> None:
    source_node = stable_id("source", source.source_id, str(source.version))
    graph.add_node(TraceNode(source_node, "source", source.source_id, "IMPLEMENTED", (("version", str(source.version)), ("evidence_level", source.evidence_level.value))))
    for finding in source.findings:
        claim = stable_id("claim", source.source_id, finding)
        graph.add_node(TraceNode(claim, "claim", finding, "DOCUMENTED", (("source_id", source.source_id),)))
        graph.add_edge(TraceEdge(source_node, claim, "supports", "DOCUMENTED", "source finding"))
    for limitation in source.limitations:
        constraint = stable_id("constraint", source.source_id, limitation)
        graph.add_node(TraceNode(constraint, "constraint", limitation, "IMPLEMENTED", (("source_id", source.source_id),)))
        graph.add_edge(TraceEdge(source_node, constraint, "constrained_by", "IMPLEMENTED", "source limitation"))
    for mechanism in source.relevant_mechanism:
        node = stable_id("mechanism", source.source_id, mechanism)
        graph.add_node(TraceNode(node, "mechanism", mechanism, "DOCUMENTED", (("source_id", source.source_id),)))
        graph.add_edge(TraceEdge(source_node, node, "specifies", "DOCUMENTED", "relevant mechanism"))
    for requirement in source.validation_requirements:
        node = stable_id("validation", source.source_id, requirement)
        graph.add_node(TraceNode(node, "validation", requirement, "PROSPECTIVELY_VALIDATED" if False else "DOCUMENTED", (("source_id", source.source_id),)))
        graph.add_edge(TraceEdge(source_node, node, "requires", "DOCUMENTED", "validation requirement"))


def trace_impact(graph: ScientificTraceGraph, impact: ScientificImpactMap) -> None:
    impact_node = stable_id("constraint", "impact", impact.impact_id)
    graph.add_node(TraceNode(impact_node, "constraint", impact.supported_claim, "DOCUMENTED", (("impact_id", impact.impact_id), ("validation_status", impact.validation_status.value))))
    for source_id in impact.source_ids:
        source_node = stable_id("source", source_id, "1")
        graph.add_node(TraceNode(source_node, "source", source_id, "IMPLEMENTED"))
        graph.add_edge(TraceEdge(source_node, impact_node, "contributes_to", "DOCUMENTED", impact.phenomenon))
    for mechanism in impact.mechanism:
        method_node = stable_id("method", impact.impact_id, mechanism)
        graph.add_node(TraceNode(method_node, "method", mechanism, "IMPLEMENTED" if mechanism in impact.existing_components else "DOCUMENTED"))
        graph.add_edge(TraceEdge(impact_node, method_node, "translates_to", "IMPLEMENTED", "impact mechanism"))
    for missing in impact.missing_capabilities:
        node = stable_id("implementation", impact.impact_id, missing)
        graph.add_node(TraceNode(node, "implementation", missing, "BLOCKED"))
        graph.add_edge(TraceEdge(impact_node, node, "missing_capability", "BLOCKED", "declared by corpus impact"))


__all__ = ["trace_source", "trace_impact"]
