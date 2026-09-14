"""Operational response-closure contract for early-warning decisions.

An alert is not operationally complete merely because a signal was produced.
This module makes the socio-technical chain explicit: signal -> interpretation
-> decision -> feasible response -> observed outcome. It is isolated from the
primary action gateway so existing temporal and execution work is untouched.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
import sqlite3


def _hash(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return sha256(payload.encode()).hexdigest()


def _aware(value: datetime, name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")


@dataclass(frozen=True, slots=True)
class ResponsePath:
    path_id: str
    prediction_id: str
    decision_id: str
    action_id: str
    policy_id: str
    feasible: bool
    created_at: datetime
    expected_outcome_due_at: datetime
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not all((self.path_id, self.prediction_id, self.decision_id, self.action_id, self.policy_id)):
            raise ValueError("response path identity is required")
        _aware(self.created_at, "created_at")
        _aware(self.expected_outcome_due_at, "expected_outcome_due_at")
        if self.expected_outcome_due_at <= self.created_at:
            raise ValueError("outcome due time must follow path creation")
        if not self.evidence_ids:
            raise ValueError("response path requires evidence linkage")


@dataclass(frozen=True, slots=True)
class ObservedOutcome:
    path_id: str
    outcome_id: str
    observed_at: datetime
    value: float
    source_id: str

    def __post_init__(self) -> None:
        if not self.path_id or not self.outcome_id or not self.source_id:
            raise ValueError("outcome identity and source are required")
        _aware(self.observed_at, "observed_at")


@dataclass(frozen=True, slots=True)
class ClosureAssessment:
    path_id: str
    complete: bool
    missing: tuple[str, ...]
    integrity_hash: str


class ResponseClosureRegistry:
    """Durable registry enforcing end-to-end response closure."""

    def __init__(self, storage_path: str | None = None) -> None:
        self._paths: dict[str, ResponsePath] = {}
        self._outcomes: dict[str, ObservedOutcome] = {}
        self._storage_path = storage_path
        if storage_path:
            self._init_db()
            self._load()

    def _db(self) -> sqlite3.Connection:
        if not self._storage_path:
            raise RuntimeError("storage is not configured")
        return sqlite3.connect(self._storage_path)

    def _init_db(self) -> None:
        with self._db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS response_paths(
                path_id TEXT PRIMARY KEY, prediction_id TEXT NOT NULL, decision_id TEXT NOT NULL,
                action_id TEXT NOT NULL, policy_id TEXT NOT NULL, feasible INTEGER NOT NULL,
                created_at TEXT NOT NULL, expected_outcome_due_at TEXT NOT NULL,
                evidence_ids TEXT NOT NULL, integrity_hash TEXT NOT NULL)""")
            db.execute("""CREATE TABLE IF NOT EXISTS response_outcomes(
                path_id TEXT PRIMARY KEY, outcome_id TEXT NOT NULL, observed_at TEXT NOT NULL,
                value REAL NOT NULL, source_id TEXT NOT NULL)""")

    def _load(self) -> None:
        with self._db() as db:
            for row in db.execute("SELECT path_id,prediction_id,decision_id,action_id,policy_id,feasible,created_at,expected_outcome_due_at,evidence_ids FROM response_paths"):
                path = ResponsePath(row[0],row[1],row[2],row[3],row[4],bool(row[5]),datetime.fromisoformat(row[6]),datetime.fromisoformat(row[7]),tuple(json.loads(row[8])))
                self._paths[path.path_id] = path
            for row in db.execute("SELECT path_id,outcome_id,observed_at,value,source_id FROM response_outcomes"):
                self._outcomes[row[0]] = ObservedOutcome(row[0],row[1],datetime.fromisoformat(row[2]),row[3],row[4])

    def register(self, path: ResponsePath) -> None:
        if path.path_id in self._paths:
            raise ValueError("duplicate response path")
        if self._storage_path:
            with self._db() as db:
                db.execute("INSERT INTO response_paths VALUES(?,?,?,?,?,?,?,?,?,?)",(
                    path.path_id,path.prediction_id,path.decision_id,path.action_id,path.policy_id,
                    int(path.feasible),path.created_at.isoformat(),path.expected_outcome_due_at.isoformat(),
                    json.dumps(path.evidence_ids),self._path_hash(path)))
        self._paths[path.path_id] = path

    def record_outcome(self, outcome: ObservedOutcome) -> None:
        if outcome.path_id not in self._paths:
            raise KeyError(outcome.path_id)
        if outcome.path_id in self._outcomes:
            raise ValueError("response path already has an observed outcome")
        if self._storage_path:
            with self._db() as db:
                db.execute("INSERT INTO response_outcomes VALUES(?,?,?,?,?)",(outcome.path_id,outcome.outcome_id,outcome.observed_at.isoformat(),outcome.value,outcome.source_id))
        self._outcomes[outcome.path_id] = outcome

    def assess(self, path_id: str) -> ClosureAssessment:
        path=self._paths[path_id]
        missing=[]
        if not path.feasible: missing.append("feasible_response")
        if path.path_id not in self._outcomes: missing.append("observed_outcome")
        return ClosureAssessment(path_id,not missing,tuple(missing),self._path_hash(path))

    def _path_hash(self, path: ResponsePath) -> str:
        return _hash({'path_id':path.path_id,'prediction_id':path.prediction_id,'decision_id':path.decision_id,'action_id':path.action_id,'policy_id':path.policy_id,'feasible':path.feasible,'created_at':path.created_at.isoformat(),'expected_outcome_due_at':path.expected_outcome_due_at.isoformat(),'evidence_ids':path.evidence_ids})

    def path(self, path_id: str) -> ResponsePath:
        return self._paths[path_id]

    def outcome(self, path_id: str) -> ObservedOutcome:
        return self._outcomes[path_id]


__all__=["ClosureAssessment","ObservedOutcome","ResponseClosureRegistry","ResponsePath"]
