"""Operational response-closure contract for early-warning decisions."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
import sqlite3

RESPONSE_STATUSES = {"UNRECORDED", "PLANNED", "EXECUTED", "NO_ACTION", "FAILED", "NOT_FEASIBLE"}

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
    response_status: str = "EXECUTED"
    non_execution_reason: str = ""
    capacity_constraint: str = ""
    response_delay_seconds: float | None = None
    intervention_exposure_id: str = ""
    counterfactual_status: str = "NOT_ASSESSED"

    def __post_init__(self) -> None:
        if not self.path_id or not self.prediction_id:
            raise ValueError("path and prediction identity are required")
        if self.response_status not in RESPONSE_STATUSES:
            raise ValueError(f"unsupported response status: {self.response_status}")
        if self.response_status in {"EXECUTED", "PLANNED", "FAILED"} and not self.action_id:
            raise ValueError("action_id is required when an action exists")
        if self.response_status == "NO_ACTION" and self.action_id:
            raise ValueError("NO_ACTION cannot carry an action_id")
        _aware(self.created_at, "created_at")
        _aware(self.expected_outcome_due_at, "expected_outcome_due_at")
        if self.expected_outcome_due_at <= self.created_at:
            raise ValueError("outcome due time must follow path creation")
        if not self.evidence_ids:
            raise ValueError("response path requires evidence linkage")
        if self.response_status in {"NO_ACTION", "FAILED", "NOT_FEASIBLE"} and not (self.non_execution_reason or self.capacity_constraint):
            raise ValueError("non-execution requires a reason or capacity constraint")
        if self.response_delay_seconds is not None and self.response_delay_seconds < 0:
            raise ValueError("response delay cannot be negative")

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
            self._init_db(); self._load()
    def _db(self) -> sqlite3.Connection:
        if not self._storage_path: raise RuntimeError("storage is not configured")
        return sqlite3.connect(self._storage_path)
    def _init_db(self) -> None:
        with self._db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS response_paths(
                path_id TEXT PRIMARY KEY, prediction_id TEXT NOT NULL, decision_id TEXT NOT NULL,
                action_id TEXT NOT NULL, policy_id TEXT NOT NULL, feasible INTEGER NOT NULL,
                created_at TEXT NOT NULL, expected_outcome_due_at TEXT NOT NULL,
                evidence_ids TEXT NOT NULL, integrity_hash TEXT NOT NULL,
                response_status TEXT NOT NULL DEFAULT 'EXECUTED',
                non_execution_reason TEXT NOT NULL DEFAULT '', capacity_constraint TEXT NOT NULL DEFAULT '',
                response_delay_seconds REAL, intervention_exposure_id TEXT NOT NULL DEFAULT '',
                counterfactual_status TEXT NOT NULL DEFAULT 'NOT_ASSESSED')""")
            columns = {r[1] for r in db.execute("PRAGMA table_info(response_paths)")}
            additions = {
                "response_status":"TEXT NOT NULL DEFAULT 'EXECUTED'", "non_execution_reason":"TEXT NOT NULL DEFAULT ''",
                "capacity_constraint":"TEXT NOT NULL DEFAULT ''", "response_delay_seconds":"REAL",
                "intervention_exposure_id":"TEXT NOT NULL DEFAULT ''", "counterfactual_status":"TEXT NOT NULL DEFAULT 'NOT_ASSESSED'"}
            for name, definition in additions.items():
                if name not in columns: db.execute(f"ALTER TABLE response_paths ADD COLUMN {name} {definition}")
            db.execute("""CREATE TABLE IF NOT EXISTS response_outcomes(
                path_id TEXT PRIMARY KEY, outcome_id TEXT NOT NULL, observed_at TEXT NOT NULL,
                value REAL NOT NULL, source_id TEXT NOT NULL)""")
    def _load(self) -> None:
        with self._db() as db:
            rows = db.execute("SELECT path_id,prediction_id,decision_id,action_id,policy_id,feasible,created_at,expected_outcome_due_at,evidence_ids,response_status,non_execution_reason,capacity_constraint,response_delay_seconds,intervention_exposure_id,counterfactual_status FROM response_paths")
            for r in rows:
                p = ResponsePath(r[0],r[1],r[2],r[3],r[4],bool(r[5]),datetime.fromisoformat(r[6]),datetime.fromisoformat(r[7]),tuple(json.loads(r[8])),r[9],r[10],r[11],r[12],r[13],r[14]); self._paths[p.path_id] = p
            for r in db.execute("SELECT path_id,outcome_id,observed_at,value,source_id FROM response_outcomes"):
                self._outcomes[r[0]] = ObservedOutcome(r[0],r[1],datetime.fromisoformat(r[2]),r[3],r[4])
    def register(self, path: ResponsePath) -> None:
        if path.path_id in self._paths: raise ValueError("duplicate response path")
        if self._storage_path:
            with self._db() as db:
                db.execute("""INSERT INTO response_paths
                (path_id,prediction_id,decision_id,action_id,policy_id,feasible,created_at,expected_outcome_due_at,evidence_ids,integrity_hash,response_status,non_execution_reason,capacity_constraint,response_delay_seconds,intervention_exposure_id,counterfactual_status)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (path.path_id,path.prediction_id,path.decision_id,path.action_id,path.policy_id,int(path.feasible),path.created_at.isoformat(),path.expected_outcome_due_at.isoformat(),json.dumps(path.evidence_ids),self._path_hash(path),path.response_status,path.non_execution_reason,path.capacity_constraint,path.response_delay_seconds,path.intervention_exposure_id,path.counterfactual_status))
        self._paths[path.path_id] = path
    def record_outcome(self, outcome: ObservedOutcome) -> None:
        if outcome.path_id not in self._paths: raise KeyError(outcome.path_id)
        if outcome.path_id in self._outcomes: raise ValueError("response path already has an observed outcome")
        if self._storage_path:
            with self._db() as db: db.execute("INSERT INTO response_outcomes VALUES(?,?,?,?,?)", (outcome.path_id,outcome.outcome_id,outcome.observed_at.isoformat(),outcome.value,outcome.source_id))
        self._outcomes[outcome.path_id] = outcome
    def assess(self, path_id: str) -> ClosureAssessment:
        p = self._paths[path_id]; missing = []
        if p.response_status == "UNRECORDED": missing.append("response_status")
        if p.response_status == "PLANNED": missing.append("response_execution")
        if not p.feasible and p.response_status != "NOT_FEASIBLE": missing.append("feasible_response")
        if p.path_id not in self._outcomes: missing.append("observed_outcome")
        return ClosureAssessment(path_id, not missing, tuple(missing), self._path_hash(p))
    def _path_hash(self, p: ResponsePath) -> str:
        return _hash({"path_id":p.path_id,"prediction_id":p.prediction_id,"decision_id":p.decision_id,"action_id":p.action_id,"policy_id":p.policy_id,"feasible":p.feasible,"created_at":p.created_at.isoformat(),"expected_outcome_due_at":p.expected_outcome_due_at.isoformat(),"evidence_ids":p.evidence_ids,"response_status":p.response_status,"non_execution_reason":p.non_execution_reason,"capacity_constraint":p.capacity_constraint,"response_delay_seconds":p.response_delay_seconds,"intervention_exposure_id":p.intervention_exposure_id,"counterfactual_status":p.counterfactual_status})
    def path(self, path_id: str) -> ResponsePath: return self._paths[path_id]
    def outcome(self, path_id: str) -> ObservedOutcome: return self._outcomes[path_id]

__all__ = ["ClosureAssessment", "ObservedOutcome", "RESPONSE_STATUSES", "ResponseClosureRegistry", "ResponsePath"]
