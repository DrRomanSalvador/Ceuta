"""Persistence adapter for decision-evidence lineage on the existing SQLite store."""
from __future__ import annotations

import json
from dataclasses import asdict

from app.core.decision.persistence import SQLiteDecisionStore
from .decision_lifecycle import DecisionEvidence


class DecisionEvidenceStore:
    """Extends the existing decision database without introducing a second store."""

    def __init__(self, store: SQLiteDecisionStore) -> None:
        self.store = store
        self.store.connection.execute(
            """CREATE TABLE IF NOT EXISTS decision_evidence (
                evidence_id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                claim_id TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                provenance_json TEXT NOT NULL,
                temporal_json TEXT NOT NULL,
                assessment_json TEXT NOT NULL,
                visibility TEXT NOT NULL
            )"""
        )
        self.store.connection.execute("CREATE INDEX IF NOT EXISTS idx_decision_evidence_source ON decision_evidence(source_id)")
        self.store.connection.execute("CREATE INDEX IF NOT EXISTS idx_decision_evidence_claim ON decision_evidence(claim_id)")
        self.store.connection.commit()

    def record(self, evidence: DecisionEvidence) -> None:
        self.store.connection.execute(
            """INSERT OR REPLACE INTO decision_evidence(
                evidence_id,source_id,claim_id,content_hash,provenance_json,
                temporal_json,assessment_json,visibility
            ) VALUES(?,?,?,?,?,?,?,?)""",
            (
                evidence.evidence_id,
                evidence.source_id,
                evidence.claim_id,
                evidence.content_hash,
                json.dumps(evidence.provenance_refs, sort_keys=True),
                json.dumps(asdict(evidence.temporal), sort_keys=True, default=str),
                json.dumps(asdict(evidence.assessment), sort_keys=True, default=lambda value: value.value),
                evidence.visibility.value,
            ),
        )
        self.store.connection.commit()

    def exists(self, evidence_id: str) -> bool:
        row = self.store.connection.execute("SELECT 1 FROM decision_evidence WHERE evidence_id=?", (evidence_id,)).fetchone()
        return row is not None


__all__ = ["DecisionEvidenceStore"]
