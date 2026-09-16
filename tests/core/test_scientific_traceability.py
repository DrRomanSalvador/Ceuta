from app.core.scientific.cross_repo_consumer import consume_serpiente_prediction
from app.core.scientific.cross_repo_contract import CANONICAL_CONTRACT_HASH, CONTRACT_ID, CONTRACT_VERSION, ScientificPredictionMessage
from app.core.scientific.method_compatibility import CompatibilityStatus, DataCompatibilityContext, ScientificMethodCompatibility, ScientificMethodContract
from app.core.scientific.scientific_traceability import ScientificTraceGraph, TraceEdge, TraceNode, stable_id


def _payload(ood="IN_DOMAIN", calibration="CALIBRATED", independence="INDEPENDENT"):
    message = ScientificPredictionMessage(
        "DrRomanSalvador/SERPIENTE", "serpiente-runtime", CONTRACT_VERSION, "p1",
        __import__("datetime").datetime.fromisoformat("2026-09-15T00:00:00+00:00"),
        __import__("datetime").datetime.fromisoformat("2026-09-15T00:01:00+00:00"), "1d", "risk", 0.7, 0.4, 0.9,
        {"epistemic": 0.1}, 0.05, "model-1", "longitudinal-forecast", "1", "2026-train", "risk-class-v1",
        ood, "DESCRIPTIVE", calibration, "observational", independence, ("observation:o1",), "cfg", "rev", "pt-fp", "placeholder",
    )
    payload = message.payload_without_integrity()
    import hashlib, json
    payload["integrity_hash"] = hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
    return payload


def test_trace_graph_supports_forward_and_reverse_edges(tmp_path):
    graph = ScientificTraceGraph(str(tmp_path / "trace.sqlite"))
    source = stable_id("source", "sawada-2022-cry-wolf")
    claim = stable_id("claim", source, "false alarms reduce credibility")
    method = stable_id("method", "cry-wolf-v1")
    runtime = stable_id("runtime", "decision-lifecycle")
    for node in (TraceNode(source, "source", "Sawada 2022", "IMPLEMENTED"), TraceNode(claim, "claim", "false alarms reduce credibility", "DOCUMENTED"), TraceNode(method, "method", "cry-wolf-v1", "COMPUTATIONALLY_TESTED"), TraceNode(runtime, "runtime", "DecisionLifecycleEngine", "IMPLEMENTED")):
        graph.add_node(node)
    graph.add_edge(TraceEdge(source, claim, "supports", "IMPLEMENTED"))
    graph.add_edge(TraceEdge(claim, method, "justifies", "IMPLEMENTED"))
    graph.add_edge(TraceEdge(method, runtime, "consumed_by", "IMPLEMENTED"))
    assert graph.verify_integrity()
    assert graph.edges_from(source)[0].to_id == claim
    assert graph.edges_to(runtime)[0].from_id == method


def test_method_data_schema_valid_but_scientifically_incompatible(tmp_path):
    method = ScientificMethodContract("csd", "1", ("dakos-2012-csd-robustness",), "time-series:v1", ("x",), (("x", "mm"),), "daily", 30, "<=20%", ("stationary_noise",), "same_location", "independent_sources_required", (), "complex_systems", ("false_positive",), "csd-output:v1", "uncertainty:v1", ("prospective_transition_validation",), "rev", "cfg")
    data = DataCompatibilityContext("time-series:v1", ("x",), (("x", "m"),), "daily", 40, 0.0, "in_domain", "same_location", "independent", True, True)
    result = ScientificMethodCompatibility().evaluate(method, data)
    assert not result.scientifically_applicable
    assert result.status is CompatibilityStatus.ASSUMPTION_VIOLATION
    assert result.schema_valid


def test_cross_repo_consumer_rejects_schema_valid_ood_message():
    payload = _payload(ood="OUT_OF_DISTRIBUTION")
    accepted = consume_serpiente_prediction(payload)
    assert not accepted.accepted
    assert accepted.reason.endswith("out_of_distribution")
    assert payload["contract_id"] == CONTRACT_ID
    assert payload["contract_hash"] == CANONICAL_CONTRACT_HASH
