"""Durable persistence adapters for CeutIA decision audit and outcomes."""
from __future__ import annotations

from dataclasses import asdict
import json
import sqlite3
from typing import Mapping, Sequence

from .control_plane import DecisionAuditEvent, DecisionOutcome, HumanDecisionReview


class SQLiteDecisionStore:
    """Append-only SQLite store with explicit schema-version control."""

    SCHEMA_VERSION = 1

    def __init__(self, path: str) -> None:
        self.connection = sqlite3.connect(path)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA foreign_keys=ON")
        self._migrate()

    def _migrate(self) -> None:
        self.connection.execute("CREATE TABLE IF NOT EXISTS ceutia_schema_version (version INTEGER NOT NULL)")
        row = self.connection.execute("SELECT version FROM ceutia_schema_version LIMIT 1").fetchone()
        current = 0 if row is None else int(row[0])
        if current > self.SCHEMA_VERSION:
            raise RuntimeError(f"database schema version {current} is newer than supported {self.SCHEMA_VERSION}")
        if current < 1:
            self.connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS decision_audit (
                    event_id TEXT PRIMARY KEY, decision_id TEXT NOT NULL, event_type TEXT NOT NULL,
                    payload_json TEXT NOT NULL, previous_hash TEXT NOT NULL, event_hash TEXT NOT NULL UNIQUE,
                    timestamp TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS idx_decision_audit_decision ON decision_audit(decision_id, timestamp);
                CREATE TABLE IF NOT EXISTS decision_reviews (
                    review_id TEXT PRIMARY KEY, decision_id TEXT NOT NULL, payload_json TEXT NOT NULL, timestamp TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS decision_outcomes (
                    decision_id TEXT NOT NULL, option_id TEXT NOT NULL, outcome_at TEXT NOT NULL,
                    payload_json TEXT NOT NULL, PRIMARY KEY(decision_id, option_id, outcome_at)
                );
                CREATE INDEX IF NOT EXISTS idx_decision_outcomes_decision ON decision_outcomes(decision_id, outcome_at);
                CREATE TABLE IF NOT EXISTS decision_cycles (
                    system_id TEXT NOT NULL, as_of TEXT NOT NULL, decision_id TEXT, option_id TEXT,
                    disposition TEXT, lineage_json TEXT NOT NULL, stages_json TEXT NOT NULL,
                    PRIMARY KEY(system_id, as_of)
                );
                CREATE INDEX IF NOT EXISTS idx_decision_cycles_decision ON decision_cycles(decision_id, as_of);
                """
            )
            if row is None:
                self.connection.execute("INSERT INTO ceutia_schema_version(version) VALUES (?)", (1,))
            else:
                self.connection.execute("UPDATE ceutia_schema_version SET version=?", (1,))
        self.connection.commit()

    @property
    def schema_version(self) -> int:
        row = self.connection.execute("SELECT version FROM ceutia_schema_version LIMIT 1").fetchone()
        if row is None:
            raise RuntimeError("schema version is missing")
        return int(row[0])

    def append(self, event: DecisionAuditEvent) -> None:
        self.connection.execute("INSERT INTO decision_audit(event_id,decision_id,event_type,payload_json,previous_hash,event_hash,timestamp) VALUES(?,?,?,?,?,?,?)", (event.event_id, event.decision_id, event.event_type, json.dumps(dict(event.payload), sort_keys=True, default=str), event.previous_hash, event.event_hash, event.timestamp))
        self.connection.commit()

    def events(self, decision_id: str) -> tuple[DecisionAuditEvent, ...]:
        rows = self.connection.execute("SELECT event_id,decision_id,event_type,payload_json,previous_hash,event_hash,timestamp FROM decision_audit WHERE decision_id=? ORDER BY timestamp,event_id", (decision_id,)).fetchall()
        return tuple(DecisionAuditEvent(r[0], r[1], r[2], json.loads(r[3]), r[4], r[5], r[6]) for r in rows)

    def record_review(self, review: HumanDecisionReview) -> None:
        self.connection.execute("INSERT INTO decision_reviews(review_id,decision_id,payload_json,timestamp) VALUES(?,?,?,?)", (review.review_id, review.decision_id, json.dumps(asdict(review), sort_keys=True), review.timestamp))
        self.connection.commit()

    def record_outcome(self, outcome: DecisionOutcome) -> None:
        self.connection.execute("INSERT OR REPLACE INTO decision_outcomes(decision_id,option_id,outcome_at,payload_json) VALUES(?,?,?,?)", (outcome.decision_id, outcome.option_id, outcome.outcome_at, json.dumps(asdict(outcome), sort_keys=True)))
        self.connection.commit()

    def outcome(self, decision_id: str) -> DecisionOutcome | None:
        row = self.connection.execute("SELECT payload_json FROM decision_outcomes WHERE decision_id=? ORDER BY outcome_at DESC LIMIT 1", (decision_id,)).fetchone()
        if row is None:
            return None
        return DecisionOutcome(**json.loads(row[0]))

    def outcomes(self, decision_id: str) -> tuple[DecisionOutcome, ...]:
        rows = self.connection.execute("SELECT payload_json FROM decision_outcomes WHERE decision_id=? ORDER BY outcome_at", (decision_id,)).fetchall()
        return tuple(DecisionOutcome(**json.loads(row[0])) for row in rows)

    def record_cycle(self, *, system_id: str, as_of: str, decision_id: str | None, option_id: str | None, disposition: str | None, lineage: Sequence[str], stages: Sequence[Mapping[str, object]]) -> None:
        self.connection.execute("INSERT OR REPLACE INTO decision_cycles(system_id,as_of,decision_id,option_id,disposition,lineage_json,stages_json) VALUES(?,?,?,?,?,?,?)", (system_id, as_of, decision_id, option_id, disposition, json.dumps(tuple(lineage), sort_keys=True), json.dumps(tuple(stages), sort_keys=True, default=str)))
        self.connection.commit()

    def cycles(self, system_id: str) -> tuple[dict[str, object], ...]:
        rows = self.connection.execute("SELECT system_id,as_of,decision_id,option_id,disposition,lineage_json,stages_json FROM decision_cycles WHERE system_id=? ORDER BY as_of", (system_id,)).fetchall()
        return tuple({"system_id": r[0], "as_of": r[1], "decision_id": r[2], "option_id": r[3], "disposition": r[4], "lineage": tuple(json.loads(r[5])), "stages": tuple(json.loads(r[6]))} for r in rows)

    def verify_chain(self, decision_id: str) -> bool:
        previous = "GENESIS"
        import hashlib
        for event in self.events(decision_id):
            canonical = json.dumps(dict(event.payload), sort_keys=True, default=str, separators=(",", ":"))
            expected = hashlib.sha256(f"{previous}|{event.event_id}|{canonical}".encode()).hexdigest()
            if event.previous_hash != previous or event.event_hash != expected:
                return False
            previous = event.event_hash
        return True

    def close(self) -> None:
        self.connection.close()


__all__ = ["SQLiteDecisionStore"]
