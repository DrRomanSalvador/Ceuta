"""P2 — Capacidad avanzada CeutIA (grafo, ingesta, backtesting, modelos acotados)."""

from .semantic_graph import SemanticGraph, NodeKind, EdgeKind, GraphNode, GraphEdge
from .ingestion import BulkIngestionPipeline, IngestionBatch, IngestionResult
from .backtesting import BacktestRunner, BacktestConfig, BacktestReport
from .predictive_stub import PredictiveConsumerStub, PredictionRequest, PredictionResult

__all__ = [
    "SemanticGraph",
    "NodeKind",
    "EdgeKind",
    "GraphNode",
    "GraphEdge",
    "BulkIngestionPipeline",
    "IngestionBatch",
    "IngestionResult",
    "BacktestRunner",
    "BacktestConfig",
    "BacktestReport",
    "PredictiveConsumerStub",
    "PredictionRequest",
    "PredictionResult",
]
