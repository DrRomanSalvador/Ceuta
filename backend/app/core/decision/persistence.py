"""Durable persistence adapters for CeutIA decision audit and outcomes."""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
import sqlite3
from typing import Mapping, Sequence

from .control_plane import DecisionAuditEvent, DecisionOutcome, HumanDecisionReview
from .lineage import DecisionLineage
from ..evidence.citation_trace import CitationTrace, CitationTraceRegistry
from ..evidence.conflict_resolution import EvidenceResolution
from ..evidence.source_registry import (
    ClaimEvidenceLink,
    SourceRecord,
    SourceRegistry,
    SourceRole,
    SourceVerification,
)
from ..scientific.governance_signals import set_default_storage_path


class SQLiteDecisionStore:
    SCHEMA_VERSION = 4

    def __init__(self, path: str) -> None:
        self.path = path
        set_default_storage_path(path)
        self.connection = sqlite3.connect(path, timeout=10.0)
        self.connection.execute("PRAGMA journal_mode=WAL")
        self.connection.execute("PRAGMA busy_timeout=10000")
        self.connection.execute("PRAGMA foreign_keys=ON")
        self._migrate()

    @staticmethod
    def _json(value: object, *, default: object | None = None) -> str:
        kwargs = {
            "sort_keys": True,
            "separators": (",", ":"),
            "ensure_ascii": False,
            "allow_nan": False,
        }
        if default is not None:
            kwargs["default"] = default
        return json.dumps(value, **kwargs)

    def _migrate(self) -> None:
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS ceutia_schema_version (version INTEGER NOT NULL)"
        )
        row = self.connection.execute(
            "SELECT version FROM ceutia_schema_version LIMIT 1"
        ).fetchone()
        current = 0 if row is None else int(row[0])
        if current > self.SCHEMA_VERSION:
            raise RuntimeError(
                f"database schema version {current} is newer than supported {self.SCHEMA_VERSION}"
            )
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            if current < 1:
                self.connection.executescript(
                    """CREATE TABLE IF NOT EXISTS decision_audit (event_id TEXT PRIMARY KEY, decision_id TEXT NOT NULL, event_type TEXT NOT NULL, payload_json TEXT NOT NULL, previous_hash TEXT NOT NULL, event_hash TEXT NOT NULL UNIQUE, timestamp TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_decision_audit_decision ON decision_audit(decision_id, timestamp);
CREATE TABLE IF NOT EXISTS decision_reviews (review_id TEXT PRIMARY KEY, decision_id TEXT NOT NULL, payload_json TEXT NOT NULL, timestamp TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS decision_outcomes (decision_id TEXT NOT NULL, option_id TEXT NOT NULL, outcome_at TEXT NOT NULL, payload_json TEXT NOT NULL, PRIMARY KEY(decision_id, option_id, outcome_at));
CREATE INDEX IF NOT EXISTS idx_decision_outcomes_decision ON decision_outcomes(decision_id, outcome_at);
CREATE TABLE IF NOT EXISTS decision_cycles (system_id TEXT NOT NULL, as_of TEXT NOT NULL, decision_id TEXT, option_id TEXT, disposition TEXT, lineage_json TEXT NOT NULL, stages_json TEXT NOT NULL, PRIMARY KEY(system_id, as_of));"""
                )
                if row is None:
                    self.connection.execute(
                        "INSERT INTO ceutia_schema_version(version) VALUES (1)"
                    )
                else:
                    self.connection.execute(
                        "UPDATE ceutia_schema_version SET version=1"
                    )
                current = 1
            if current < 2:
                self.connection.executescript(
                    """CREATE TABLE IF NOT EXISTS decision_lineage (decision_id TEXT PRIMARY KEY, semantic_fingerprint TEXT NOT NULL, execution_fingerprint TEXT NOT NULL, payload_json TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_decision_lineage_semantic ON decision_lineage(semantic_fingerprint);"""
                )
                self.connection.execute("UPDATE ceutia_schema_version SET version=2")
                current = 2
            if current < 3:
                self.connection.executescript(
                    """CREATE TABLE IF NOT EXISTS decision_conflict_resolutions (conflict_id TEXT PRIMARY KEY, decision_id TEXT NOT NULL, disposition TEXT NOT NULL, selected_refs_json TEXT NOT NULL, rationale TEXT NOT NULL, policy_version TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_conflict_resolutions_decision ON decision_conflict_resolutions(decision_id);"""
                )
                self.connection.execute("UPDATE ceutia_schema_version SET version=3")
                current = 3
            if current < 4:
                self.connection.executescript(
                    """CREATE TABLE IF NOT EXISTS evidence_sources (source_id TEXT PRIMARY KEY, payload_json TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS claim_evidence_links (claim_id TEXT NOT NULL, source_id TEXT NOT NULL, relation TEXT NOT NULL, excerpt_ref TEXT, supports_claim INTEGER NOT NULL, PRIMARY KEY(claim_id, source_id, relation));
CREATE INDEX IF NOT EXISTS idx_claim_evidence_links_claim ON claim_evidence_links(claim_id);
CREATE TABLE IF NOT EXISTS citation_traces (claim_id TEXT NOT NULL, source_id TEXT NOT NULL, locator TEXT NOT NULL, captured_text_hash TEXT NOT NULL, captured_at TEXT NOT NULL, PRIMARY KEY(claim_id, source_id, locator, captured_text_hash));
CREATE INDEX IF NOT EXISTS idx_citation_traces_claim ON citation_traces(claim_id);"""
                )
                self.connection.execute("UPDATE ceutia_schema_version SET version=4")
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    @property
    def schema_version(self) -> int:
        row = self.connection.execute(
            "SELECT version FROM ceutia_schema_version LIMIT 1"
        ).fetchone()
        if row is None:
            raise RuntimeError("schema version is missing")
        return int(row[0])

    def append(self, event: DecisionAuditEvent) -> None:
        self.connection.commit()
        self.connection.execute("BEGIN IMMEDIATE")
        try:
            row = self.connection.execute(
                "SELECT event_hash FROM decision_audit WHERE decision_id=? ORDER BY rowid DESC LIMIT 1",
                (event.decision_id,),
            ).fetchone()
            actual_previous = "GENESIS" if row is None else str(row[0])
            if event.previous_hash != actual_previous:
                raise RuntimeError(
                    "decision audit chain changed concurrently; stale predecessor hash"
                )
            canonical = self._json(dict(event.payload), default=str)
            self.connection.execute(
                "INSERT INTO decision_audit(event_id,decision_id,event_type,payload_json,previous_hash,event_hash,timestamp) VALUES(?,?,?,?,?,?,?)",
                (
                    event.event_id,
                    event.decision_id,
                    event.event_type,
                    canonical,
                    event.previous_hash,
                    event.event_hash,
                    event.timestamp,
                ),
            )
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def events(self, decision_id: str) -> tuple[DecisionAuditEvent, ...]:
        rows = self.connection.execute(
            "SELECT event_id,decision_id,event_type,payload_json,previous_hash,event_hash,timestamp FROM decision_audit WHERE decision_id=? ORDER BY rowid",
            (decision_id,),
        ).fetchall()
        return tuple(DecisionAuditEvent(r[0], r[1], r[2], json.loads(r[3]), r[4], r[5], r[6]) for r in rows)

    def record_review(self, review: HumanDecisionReview) -> None:
        payload = self._json(asdict(review))
        self.connection.execute(
            "INSERT INTO decision_reviews(review_id,decision_id,payload_json,timestamp) VALUES(?,?,?,?)",
            (review.review_id, review.decision_id, payload, review.timestamp),
        )
        self.connection.commit()

    def record_outcome(self, outcome: DecisionOutcome) -> None:
        payload = self._json(asdict(outcome))
        existing = self.connection.execute(
            "SELECT payload_json FROM decision_outcomes WHERE decision_id=? AND option_id=? AND outcome_at=?",
            (outcome.decision_id, outcome.option_id, outcome.outcome_at),
        ).fetchone()
        if existing is not None:
            if existing[0] != payload:
                raise RuntimeError("decision outcome identity collision: existing outcome differs")
            return
        self.connection.execute(
            "INSERT INTO decision_outcomes(decision_id,option_id,outcome_at,payload_json) VALUES(?,?,?,?)",
            (outcome.decision_id, outcome.option_id, outcome.outcome_at, payload),
        )
        self.connection.commit()

    def outcome(self, decision_id: str) -> DecisionOutcome | None:
        row = self.connection.execute(
            "SELECT payload_json FROM decision_outcomes WHERE decision_id=? ORDER BY outcome_at DESC LIMIT 1",
            (decision_id,),
        ).fetchone()
        return None if row is None else DecisionOutcome(**json.loads(row[0]))

    def outcomes(self, decision_id: str) -> tuple[DecisionOutcome, ...]:
        rows = self.connection.execute(
            "SELECT payload_json FROM decision_outcomes WHERE decision_id=? ORDER BY outcome_at",
            (decision_id,),
        ).fetchall()
        return tuple(DecisionOutcome(**json.loads(row[0])) for row in rows)

    def record_lineage(self, lineage: DecisionLineage) -> None:
        payload = self._json(lineage.execution_payload())
        semantic = lineage.semantic_fingerprint()
        execution = lineage.execution_fingerprint()
        existing = self.connection.execute(
            "SELECT semantic_fingerprint,execution_fingerprint,payload_json FROM decision_lineage WHERE decision_id=?",
            (lineage.decision_id,),
        ).fetchone()
        if existing is not None:
            if existing != (semantic, execution, payload):
                raise RuntimeError("decision lineage identity collision: existing lineage differs")
            return
        self.connection.execute(
            "INSERT INTO decision_lineage(decision_id,semantic_fingerprint,execution_fingerprint,payload_json) VALUES(?,?,?,?)",
            (lineage.decision_id, semantic, execution, payload),
        )
        self.connection.commit()

    def lineage(self, decision_id: str) -> DecisionLineage | None:
        row = self.connection.execute(
            "SELECT payload_json FROM decision_lineage WHERE decision_id=?",
            (decision_id,),
        ).fetchone()
        if row is None:
            return None
        payload = json.loads(row[0])
        from .lineage import LineageNode

        return DecisionLineage(
            decision_id=payload["decision_id"],
            nodes=tuple(LineageNode(**node) for node in payload["nodes"]),
            terminal_disposition=payload["terminal_disposition"],
            semantic_identity=payload["semantic_identity"],
        )

    def record_conflict_resolution(
        self, decision_id: str, resolution: EvidenceResolution
    ) -> None:
        values = (
            resolution.conflict_id,
            decision_id,
            resolution.disposition.value,
            self._json(resolution.selected_refs),
            resolution.rationale,
            resolution.policy_version,
        )
        existing = self.connection.execute(
            "SELECT decision_id,disposition,selected_refs_json,rationale,policy_version FROM decision_conflict_resolutions WHERE conflict_id=?",
            (resolution.conflict_id,),
        ).fetchone()
        if existing is not None:
            if existing != values[1:]:
                raise RuntimeError(
                    "conflict resolution identity collision: existing resolution differs"
                )
            return
        self.connection.execute(
            "INSERT INTO decision_conflict_resolutions(conflict_id,decision_id,disposition,selected_refs_json,rationale,policy_version) VALUES(?,?,?,?,?,?)",
            values,
        )
        self.connection.commit()

    def conflict_resolutions(self, decision_id: str) -> tuple[EvidenceResolution, ...]:
        rows = self.connection.execute(
            "SELECT conflict_id,disposition,selected_refs_json,rationale,policy_version FROM decision_conflict_resolutions WHERE decision_id=? ORDER BY conflict_id",
            (decision_id,),
        ).fetchall()
        from ..evidence.conflict_resolution import ResolutionDisposition

        return tuple(
            EvidenceResolution(
                r[0], ResolutionDisposition(r[1]), tuple(json.loads(r[2])), r[3], r[4]
            )
            for r in rows
        )

    def record_source(self, source: SourceRecord) -> None:
        payload = self._json(asdict(source), default=lambda value: value.value)
        existing = self.connection.execute(
            "SELECT payload_json FROM evidence_sources WHERE source_id=?",
            (source.source_id,),
        ).fetchone()
        if existing is not None:
            if existing[0] != payload:
                raise RuntimeError("source identity collision: existing source metadata differs")
            return
        self.connection.execute(
            "INSERT INTO evidence_sources(source_id,payload_json) VALUES(?,?)",
            (source.source_id, payload),
        )
        self.connection.commit()

    @staticmethod
    def _source_from_payload(payload: dict[str, object]) -> SourceRecord:
        payload = dict(payload)
        payload["verification"] = SourceVerification(payload["verification"])
        payload["role"] = SourceRole(payload["role"])
        payload["assumptions"] = tuple(payload.get("assumptions", ()))
        payload["limitations"] = tuple(payload.get("limitations", ()))
        return SourceRecord(**payload)

    def source(self, source_id: str) -> SourceRecord | None:
        row = self.connection.execute(
            "SELECT payload_json FROM evidence_sources WHERE source_id=?", (source_id,)
        ).fetchone()
        return None if row is None else self._source_from_payload(json.loads(row[0]))

    def source_registry(self) -> SourceRegistry:
        registry = SourceRegistry()
        rows = self.connection.execute(
            "SELECT payload_json FROM evidence_sources ORDER BY source_id"
        ).fetchall()
        for row in rows:
            registry.register(self._source_from_payload(json.loads(row[0])))
        links = self.connection.execute(
            "SELECT claim_id,source_id,relation,excerpt_ref,supports_claim FROM claim_evidence_links ORDER BY claim_id,source_id,relation"
        ).fetchall()
        for row in links:
            registry.link_claim(ClaimEvidenceLink(row[0], row[1], row[2], row[3], bool(row[4])))
        return registry

    def record_claim_evidence_link(self, link: ClaimEvidenceLink) -> None:
        if self.source(link.source_id) is None:
            raise KeyError(f"unknown source_id: {link.source_id}")
        values = (
            link.claim_id,
            link.source_id,
            link.relation,
            link.excerpt_ref,
            int(link.supports_claim),
        )
        existing = self.connection.execute(
            "SELECT excerpt_ref,supports_claim FROM claim_evidence_links WHERE claim_id=? AND source_id=? AND relation=?",
            (link.claim_id, link.source_id, link.relation),
        ).fetchone()
        if existing is not None:
            if existing != values[3:]:
                raise RuntimeError("claim evidence identity collision: existing link differs")
            return
        self.connection.execute(
            "INSERT INTO claim_evidence_links(claim_id,source_id,relation,excerpt_ref,supports_claim) VALUES(?,?,?,?,?)",
            values,
        )
        self.connection.commit()

    def record_citation_trace(self, trace: CitationTrace) -> None:
        values = (
            trace.claim_id,
            trace.source_id,
            trace.locator,
            trace.captured_text_hash,
            trace.captured_at,
        )
        existing = self.connection.execute(
            "SELECT captured_at FROM citation_traces WHERE claim_id=? AND source_id=? AND locator=? AND captured_text_hash=?",
            values[:4],
        ).fetchone()
        if existing is not None:
            if existing[0] != trace.captured_at:
                raise RuntimeError("citation trace identity collision: captured_at differs")
            return
        self.connection.execute(
            "INSERT INTO citation_traces(claim_id,source_id,locator,captured_text_hash,captured_at) VALUES(?,?,?,?,?)",
            values,
        )
        self.connection.commit()

    def citation_registry(self) -> CitationTraceRegistry:
        registry = CitationTraceRegistry()
        rows = self.connection.execute(
            "SELECT claim_id,source_id,locator,captured_text_hash,captured_at FROM citation_traces ORDER BY claim_id,source_id,locator,captured_text_hash"
        ).fetchall()
        for row in rows:
            registry.add(CitationTrace(*row))
        return registry

    def record_cycle(
        self,
        *,
        system_id: str,
        as_of: str,
        decision_id: str | None,
        option_id: str | None,
        disposition: str | None,
        lineage: Sequence[str],
        stages: Sequence[Mapping[str, object]],
    ) -> None:
        lineage_json = self._json(tuple(lineage))
        stages_json = self._json(tuple(stages), default=str)
        values = (
            system_id,
            as_of,
            decision_id,
            option_id,
            disposition,
            lineage_json,
            stages_json,
        )
        existing = self.connection.execute(
            "SELECT decision_id,option_id,disposition,lineage_json,stages_json FROM decision_cycles WHERE system_id=? AND as_of=?",
            (system_id, as_of),
        ).fetchone()
        if existing is not None:
            if existing != values[2:]:
                raise RuntimeError("decision cycle identity collision: existing snapshot differs")
            return
        self.connection.execute(
            "INSERT INTO decision_cycles(system_id,as_of,decision_id,option_id,disposition,lineage_json,stages_json) VALUES(?,?,?,?,?,?,?)",
            values,
        )
        self.connection.commit()

    def cycles(self, system_id: str) -> tuple[dict[str, object], ...]:
        rows = self.connection.execute(
            "SELECT system_id,as_of,decision_id,option_id,disposition,lineage_json,stages_json FROM decision_cycles WHERE system_id=? ORDER BY as_of",
            (system_id,),
        ).fetchall()
        return tuple(
            {
                "system_id": r[0],
                "as_of": r[1],
                "decision_id": r[2],
                "option_id": r[3],
                "disposition": r[4],
                "lineage": tuple(json.loads(r[5])),
                "stages": tuple(json.loads(r[6])),
            }
            for r in rows
        )

    def verify_chain(self, decision_id: str) -> bool:
        previous = "GENESIS"
        for event in self.events(decision_id):
            canonical = self._json(dict(event.payload), default=str)
            expected = hashlib.sha256(
                f"{previous}|{event.event_id}|{canonical}".encode()
            ).hexdigest()
            if event.previous_hash != previous or event.event_hash != expected:
                return False
            previous = event.event_hash
        return True

    def close(self) -> None:
        self.connection.close()


__all__ = ["SQLiteDecisionStore"]
