"""Operational governance signals derived from scientific mechanism state.

The governance layer converts evidence quality, independence, provenance,
mechanism integrity, strategic-risk findings, credibility, uncertainty and
response closure into an auditable RELEASE/REVIEW_REQUIRED/ABSTAIN decision.
Prospective behavioural and outcome validation remain empirical questions.
"""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha256
import json
import os
import sqlite3
from math import isfinite

_DEFAULT_STORAGE_PATH: str | None = None


def set_default_storage_path(path: str) -> None:
    """Bind default governance persistence to the active decision store."""
    if not path:
        raise ValueError("storage path is required")
    global _DEFAULT_STORAGE_PATH
    _DEFAULT_STORAGE_PATH = path


class GovernanceDisposition(StrEnum):
    RELEASE = "release"
    REVIEW_REQUIRED = "review_required"
    ABSTAIN = "abstain"


class GovernanceReason(StrEnum):
    EVIDENCE_INSUFFICIENT = "evidence_insufficient"
    EVIDENCE_CONTRADICTORY = "evidence_contradictory"
    LOW_INDEPENDENCE = "evidence_low_independence"
    PROVENANCE_COMPROMISED = "provenance_compromised"
    MECHANISM_UNSATISFIED = "mechanism_unsatisfied"
    STRATEGIC_MANIPULATION = "strategic_manipulation"
    COLLUSION_FLAG = "collusion_flag"
    SUPPLIER_CREDIBILITY_LOW = "supplier_credibility_low"
    MODEL_CONFLICT = "model_conflict"
    UNCERTAINTY_HIGH = "uncertainty_high"
    RESPONSE_CLOSURE_INCOMPLETE = "response_closure_incomplete"
    INTEGRITY_VERIFIED = "integrity_verified"


@dataclass(frozen=True, slots=True)
class GovernanceInput:
    evidence_ids: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    evidence_quality: float
    independent_evidence_ratio: float
    contradiction_ratio: float
    credibility: float | None = None
    mechanism_satisfied: bool = True
    manipulation_flags: int = 0
    collusion_flags: int = 0
    provenance_valid: bool = True
    mechanism_integrity_valid: bool = True
    model_conflict: bool = False
    uncertainty: float = 0.0
    response_closure_complete: bool = True
    code_revision: str = ""
    configuration_hash: str = ""
    mechanism_ref: str = ""

    def __post_init__(self) -> None:
        bounded = (self.evidence_quality, self.independent_evidence_ratio, self.contradiction_ratio, self.uncertainty)
        if any(not isfinite(x) or not 0.0 <= x <= 1.0 for x in bounded):
            raise ValueError("governance ratios and uncertainty must be in [0,1]")
        if self.credibility is not None and (not isfinite(self.credibility) or not 0.0 <= self.credibility <= 1.0):
            raise ValueError("credibility must be in [0,1]")
        if min(self.manipulation_flags, self.collusion_flags) < 0:
            raise ValueError("finding counts cannot be negative")
        if not self.evidence_ids or not self.provenance_refs:
            raise ValueError("evidence and provenance references are required")
        if not self.code_revision or not self.configuration_hash:
            raise ValueError("code revision and configuration hash are required")


@dataclass(frozen=True, slots=True)
class GovernanceSignal:
    signal_id: str
    decision_id: str
    disposition: GovernanceDisposition
    reasons: tuple[GovernanceReason, ...]
    evidence_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]
    mechanism_ref: str
    created_at: datetime
    code_revision: str
    configuration_hash: str
    rule_version: str
    input_fingerprint: str
    effect: str
    audit_hash: str


class ScientificGovernance:
    """Fail-closed, persistent governance bridge."""
    RULE_VERSION = "scientific-governance-v1"

    def __init__(self, *, storage_path: str | None = None, minimum_evidence_quality: float = 0.5,
                 minimum_independence: float = 0.5, minimum_credibility: float = 0.35,
                 review_uncertainty: float = 0.5, abstain_uncertainty: float = 0.9) -> None:
        values = (minimum_evidence_quality, minimum_independence, minimum_credibility, review_uncertainty, abstain_uncertainty)
        if any(not isfinite(v) or not 0.0 <= v <= 1.0 for v in values) or review_uncertainty > abstain_uncertainty:
            raise ValueError("invalid governance thresholds")
        self.storage_path = storage_path or _DEFAULT_STORAGE_PATH or os.getenv("CEUTIA_GOVERNANCE_DB")
        self.minimum_evidence_quality = minimum_evidence_quality
        self.minimum_independence = minimum_independence
        self.minimum_credibility = minimum_credibility
        self.review_uncertainty = review_uncertainty
        self.abstain_uncertainty = abstain_uncertainty
        self._signals: dict[str, GovernanceSignal] = {}
        if self.storage_path:
            self._init_db(); self._load_db()

    def _db(self) -> sqlite3.Connection:
        if not self.storage_path:
            raise RuntimeError("storage is not configured")
        return sqlite3.connect(self.storage_path)

    def _init_db(self) -> None:
        with self._db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS scientific_governance_signals(
                signal_id TEXT PRIMARY KEY, decision_id TEXT NOT NULL, disposition TEXT NOT NULL,
                reasons TEXT NOT NULL, evidence_refs TEXT NOT NULL, provenance_refs TEXT NOT NULL,
                mechanism_ref TEXT NOT NULL, created_at TEXT NOT NULL, code_revision TEXT NOT NULL,
                configuration_hash TEXT NOT NULL, rule_version TEXT NOT NULL, input_fingerprint TEXT NOT NULL,
                effect TEXT NOT NULL, audit_hash TEXT NOT NULL)""")

    def _load_db(self) -> None:
        with self._db() as db:
            rows = db.execute("SELECT signal_id,decision_id,disposition,reasons,evidence_refs,provenance_refs,mechanism_ref,created_at,code_revision,configuration_hash,rule_version,input_fingerprint,effect,audit_hash FROM scientific_governance_signals")
            for r in rows:
                self._signals[r[0]] = GovernanceSignal(r[0], r[1], GovernanceDisposition(r[2]), tuple(GovernanceReason(x) for x in json.loads(r[3])), tuple(json.loads(r[4])), tuple(json.loads(r[5])), r[6], datetime.fromisoformat(r[7]), r[8], r[9], r[10], r[11], r[12], r[13])

    @staticmethod
    def _fingerprint(decision_id: str, value: GovernanceInput) -> str:
        payload = {"decision_id": decision_id, "input": asdict(value)}
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False)
        return sha256(canonical.encode()).hexdigest()

    @staticmethod
    def _persisted_values(signal: GovernanceSignal) -> tuple[object, ...]:
        return (
            signal.signal_id, signal.decision_id, signal.disposition.value,
            json.dumps([x.value for x in signal.reasons]),
            json.dumps(signal.evidence_refs), json.dumps(signal.provenance_refs),
            signal.mechanism_ref, signal.created_at.isoformat(), signal.code_revision,
            signal.configuration_hash, signal.rule_version, signal.input_fingerprint,
            signal.effect, signal.audit_hash,
        )

    def evaluate(self, decision_id: str, value: GovernanceInput, *, created_at: datetime | None = None) -> GovernanceSignal:
        if not decision_id:
            raise ValueError("decision_id is required")
        created_at = created_at or datetime.now(timezone.utc)
        if created_at.tzinfo is None or created_at.utcoffset() is None:
            raise ValueError("created_at must be timezone-aware")
        reasons: list[GovernanceReason] = []
        if not value.provenance_valid or not value.mechanism_integrity_valid:
            reasons.append(GovernanceReason.PROVENANCE_COMPROMISED)
        if not value.mechanism_satisfied:
            reasons.append(GovernanceReason.MECHANISM_UNSATISFIED)
        if value.evidence_quality < self.minimum_evidence_quality:
            reasons.append(GovernanceReason.EVIDENCE_INSUFFICIENT)
        if value.independent_evidence_ratio < self.minimum_independence:
            reasons.append(GovernanceReason.LOW_INDEPENDENCE)
        if value.contradiction_ratio >= 0.5:
            reasons.append(GovernanceReason.EVIDENCE_CONTRADICTORY)
        if value.model_conflict:
            reasons.append(GovernanceReason.MODEL_CONFLICT)
        if value.credibility is not None and value.credibility < self.minimum_credibility:
            reasons.append(GovernanceReason.SUPPLIER_CREDIBILITY_LOW)
        if value.manipulation_flags:
            reasons.append(GovernanceReason.STRATEGIC_MANIPULATION)
        if value.collusion_flags:
            reasons.append(GovernanceReason.COLLUSION_FLAG)
        if value.uncertainty >= self.review_uncertainty:
            reasons.append(GovernanceReason.UNCERTAINTY_HIGH)
        if not value.response_closure_complete:
            reasons.append(GovernanceReason.RESPONSE_CLOSURE_INCOMPLETE)
        hard = {GovernanceReason.PROVENANCE_COMPROMISED, GovernanceReason.MECHANISM_UNSATISFIED,
                GovernanceReason.STRATEGIC_MANIPULATION, GovernanceReason.COLLUSION_FLAG}
        if value.uncertainty >= self.abstain_uncertainty:
            reasons.append(GovernanceReason.UNCERTAINTY_HIGH)
        if any(r in hard for r in reasons) or value.uncertainty >= self.abstain_uncertainty:
            disposition = GovernanceDisposition.ABSTAIN
        elif reasons:
            disposition = GovernanceDisposition.REVIEW_REQUIRED
        else:
            reasons.append(GovernanceReason.INTEGRITY_VERIFIED)
            disposition = GovernanceDisposition.RELEASE
        effect = {GovernanceDisposition.RELEASE: "release", GovernanceDisposition.REVIEW_REQUIRED: "human_review", GovernanceDisposition.ABSTAIN: "do_not_release"}[disposition]
        fingerprint = self._fingerprint(decision_id, value)
        signal_id = sha256(f"{decision_id}:{fingerprint}:{self.RULE_VERSION}".encode()).hexdigest()
        audit_hash = sha256(json.dumps({"signal_id": signal_id, "disposition": disposition.value, "reasons": [r.value for r in reasons], "effect": effect}, sort_keys=True).encode()).hexdigest()
        signal = GovernanceSignal(signal_id, decision_id, disposition, tuple(dict.fromkeys(reasons)), value.evidence_ids, value.provenance_refs, value.mechanism_ref, created_at, value.code_revision, value.configuration_hash, self.RULE_VERSION, fingerprint, effect, audit_hash)
        if self.storage_path:
            values = self._persisted_values(signal)
            with self._db() as db:
                existing = db.execute("SELECT signal_id,decision_id,disposition,reasons,evidence_refs,provenance_refs,mechanism_ref,created_at,code_revision,configuration_hash,rule_version,input_fingerprint,effect,audit_hash FROM scientific_governance_signals WHERE signal_id=?", (signal.signal_id,)).fetchone()
                if existing is not None:
                    if tuple(existing) != values:
                        raise RuntimeError("scientific governance signal identity collision: existing signal differs")
                else:
                    db.execute("INSERT INTO scientific_governance_signals VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", values)
        self._signals[signal_id] = signal
        return signal

    def get(self, signal_id: str) -> GovernanceSignal:
        return self._signals[signal_id]

    def signals(self) -> tuple[GovernanceSignal, ...]:
        return tuple(self._signals.values())


__all__ = ["GovernanceDisposition", "GovernanceInput", "GovernanceReason", "GovernanceSignal", "ScientificGovernance", "set_default_storage_path"]
