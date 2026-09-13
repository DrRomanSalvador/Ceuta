"""P2 — Tests: grafo semántico, ingesta masiva, backtesting, stub predictivo."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta

from backend.app.core.epistemology_p0.registry import ClaimRegistry
from backend.app.core.epistemology_p0.advanced.semantic_graph import (
    SemanticGraph,
    NodeKind,
    EdgeKind,
)
from backend.app.core.epistemology_p0.advanced.ingestion import (
    BulkIngestionPipeline,
    IngestionRecord,
    IngestionBatch,
)
from backend.app.core.epistemology_p0.advanced.backtesting import (
    BacktestRunner,
    BacktestConfig,
)
from backend.app.core.epistemology_p0.advanced.predictive_stub import (
    PredictiveConsumerStub,
    PredictionRequest,
)
from backend.app.core.epistemology_p0.operational.bridge import ObservationBridge
from backend.app.core.epistemology_p0.evidence.models import create_evidence


def test_semantic_graph_chain():
    g = SemanticGraph()
    g.link_evidence_chain(
        source_id="src-1",
        source_label="INE",
        document_id="doc-1",
        document_label="Boletín",
        claim_id="claim-1",
        claim_label="Tasa 12%",
        evidence_id="ev-1",
        evidence_label="12%",
        variable="unemployment",
    )
    stats = g.stats()
    assert stats["nodes"] >= 5
    assert stats["edges"] >= 4
    sub = g.subgraph_for_claim("claim-1")
    assert len(sub["nodes"]) >= 2


def test_bulk_ingestion_accepts_and_rejects():
    reg = ClaimRegistry()
    pipe = BulkIngestionPipeline(reg)
    good = IngestionRecord(
        source_id="s1",
        document_id="d1",
        statement="Valor A es 10",
        value=10,
        semantic_definition="Definición oficial A",
        source_reliability=0.7,
        variable="A",
        geography="CE",
    )
    bad = IngestionRecord(
        source_id="s2",
        document_id="d2",
        statement="Sin definición",
        value=1,
        semantic_definition="",
        source_reliability=0.5,
    )
    result = pipe.ingest_records([good, bad])
    assert result.accepted == 1
    assert result.rejected == 1
    assert len(result.claim_ids) == 1
    assert pipe.graph.stats()["nodes"] >= 4


def test_backtest_blocks_future():
    reg = ClaimRegistry()
    t_old = datetime(2024, 1, 1, tzinfo=timezone.utc)
    t_new = datetime(2024, 6, 1, tzinfo=timezone.utc)
    t_sim = datetime(2024, 3, 1, tzinfo=timezone.utc)

    c1 = reg.register_claim("old", "s1", "d1")
    e1 = create_evidence(
        source_id="s1", document_id="d1", claim_id=c1,
        value=10, semantic_definition="v",
        source_reliability=0.8, source_independence="primary",
    )
    object.__setattr__(e1, "ingestion_time", t_old)
    reg.add_evidence(e1)

    c2 = reg.register_claim("future", "s2", "d2")
    e2 = create_evidence(
        source_id="s2", document_id="d2", claim_id=c2,
        value=99, semantic_definition="v",
        source_reliability=0.8, source_independence="primary",
    )
    object.__setattr__(e2, "ingestion_time", t_new)
    reg.add_evidence(e2)

    runner = BacktestRunner(reg)
    report = runner.run(
        BacktestConfig(simulation_times=[t_sim], variable="v", require_no_future_leak=True)
    )
    assert report.ok
    assert report.slices[0].n_available == 1
    assert report.slices[0].n_rejected_future == 1
    assert report.total_future_leaks_blocked == 1


def test_predictive_stub_rejects_naked_and_marks_hypothesis():
    reg = ClaimRegistry()
    pipe = BulkIngestionPipeline(reg)
    pipe.ingest_records([
        IngestionRecord(
            source_id="s1", document_id="d1", statement="x=10",
            value=10, semantic_definition="x oficial", source_reliability=0.9,
            variable="x",
        ),
        IngestionRecord(
            source_id="s2", document_id="d2", statement="x=12",
            value=12, semantic_definition="x oficial", source_reliability=0.7,
            variable="x",
        ),
    ])
    bridge = ObservationBridge()
    obs_list = [
        bridge.emit(reg.evidences[eid], variable="x")
        for eid in list(reg.evidences.keys())
    ]
    stub = PredictiveConsumerStub()
    result = stub.predict(
        PredictionRequest(target_variable="x", horizon_steps=2, observations=obs_list)
    )
    d = result.to_dict()
    assert d["point_estimate"] is not None
    assert d["epistemic_status"] in ("HYPOTHESIS", "UNVERIFIED")
    assert "disclaimer" in d
    assert d["n_observations_used"] == 2


def test_p2_closed_loop():
    """Ingesta → grafo → backtest → predicción hipotética."""
    reg = ClaimRegistry()
    pipe = BulkIngestionPipeline(reg)
    base = datetime(2024, 1, 15, tzinfo=timezone.utc)
    records = []
    for i in range(5):
        records.append(
            IngestionRecord(
                source_id=f"src-{i%2}",
                document_id=f"doc-{i}",
                statement=f"ocupacion={60+i}",
                value=60 + i,
                semantic_definition="Ocupación hospitalaria %",
                source_reliability=0.75,
                variable="hospital_occupancy",
                geography="CE",
                event_time=(base + timedelta(days=i * 30)).isoformat(),
            )
        )
    result = pipe.ingest_records(records)
    assert result.accepted == 5

    # fijar ingestion_time creciente
    for i, eid in enumerate(result.evidence_ids):
        object.__setattr__(
            reg.evidences[eid],
            "ingestion_time",
            base + timedelta(days=i * 30),
        )

    runner = BacktestRunner(reg)
    mid = base + timedelta(days=60)
    report = runner.run(
        BacktestConfig(
            simulation_times=[mid],
            variable="hospital_occupancy",
            geography="CE",
        )
    )
    assert report.slices[0].n_available >= 1

    bridge = ObservationBridge()
    obs = [
        bridge.emit(reg.evidences[eid], variable="hospital_occupancy", geography="CE")
        for eid in result.evidence_ids
        if reg.evidences[eid].ingestion_time <= mid
    ]
    pred = PredictiveConsumerStub().predict(
        PredictionRequest(
            target_variable="hospital_occupancy",
            horizon_steps=1,
            observations=obs,
            geography="CE",
        )
    )
    assert pred.point_estimate is not None
    assert pred.epistemic_status in ("HYPOTHESIS", "UNVERIFIED")
    assert pipe.graph.stats()["nodes"] > 0
