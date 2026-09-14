"""Longitudinal incentive, credibility, and integrity layer.

This module is intentionally isolated from the actively hardened temporal
mechanism. It consumes stable report/evidence identifiers and therefore can be
integrated without competing with point-in-time evidence changes.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import sqlite3
from math import isfinite, log
from statistics import fmean
from typing import Iterable

_EPS = 1e-15


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _digest(value: object) -> str:
    return sha256(_canonical(value).encode()).hexdigest()


def _aware(value: datetime, name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must be timezone-aware")


def log_loss(probability: float, outcome: int) -> float:
    if not isfinite(probability) or not 0.0 < probability < 1.0:
        raise ValueError("probability must be finite and strictly between 0 and 1")
    if outcome not in (0, 1):
        raise ValueError("outcome must be 0 or 1")
    return -(outcome * log(probability) + (1 - outcome) * log(1 - probability))


def brier_score(probability: float, outcome: int) -> float:
    if not isfinite(probability) or not 0.0 <= probability <= 1.0:
        raise ValueError("probability must be finite and in [0,1]")
    if outcome not in (0, 1):
        raise ValueError("outcome must be 0 or 1")
    return (probability - outcome) ** 2


@dataclass(frozen=True, slots=True)
class HorizonPolicy:
    horizon: str
    weight: float = 1.0

    def __post_init__(self) -> None:
        if not self.horizon or not isfinite(self.weight) or self.weight <= 0:
            raise ValueError("horizon and positive finite weight are required")


@dataclass(frozen=True, slots=True)
class ForecastReport:
    report_id: str
    supplier_id: str
    question_id: str
    horizon: str
    probability: float
    submitted_at: datetime
    deadline: datetime
    outcome_due_at: datetime
    evidence_ids: tuple[str, ...] = ()
    evidence_fingerprint: str = ""
    specification_hash: str = ""

    def __post_init__(self) -> None:
        if not all((self.report_id, self.supplier_id, self.question_id, self.horizon)):
            raise ValueError("report identity is required")
        if not isfinite(self.probability) or not 0.0 < self.probability < 1.0:
            raise ValueError("probability must be finite and strictly between 0 and 1")
        _aware(self.submitted_at, "submitted_at")
        _aware(self.deadline, "deadline")
        _aware(self.outcome_due_at, "outcome_due_at")
        if self.submitted_at > self.deadline or self.outcome_due_at <= self.deadline:
            raise ValueError("invalid reporting/outcome chronology")
        if self.evidence_ids and not self.evidence_fingerprint:
            raise ValueError("evidence_fingerprint is required when evidence_ids are supplied")

    @property
    def report_hash(self) -> str:
        return _digest({
            "report_id": self.report_id, "supplier_id": self.supplier_id,
            "question_id": self.question_id, "horizon": self.horizon,
            "probability": self.probability, "submitted_at": self.submitted_at.isoformat(),
            "deadline": self.deadline.isoformat(), "outcome_due_at": self.outcome_due_at.isoformat(),
            "evidence_ids": self.evidence_ids, "evidence_fingerprint": self.evidence_fingerprint,
            "specification_hash": self.specification_hash,
        })


@dataclass(frozen=True, slots=True)
class Settlement:
    report_id: str
    outcome: int
    log_loss: float
    brier_score: float
    transfer: float
    verified_at: datetime
    verifier_id: str
    previous_hash: str
    provenance_hash: str
    credibility: float


@dataclass(frozen=True, slots=True)
class CredibilityState:
    supplier_id: str
    observations: int
    mean_brier: float
    credibility: float
    alpha: float
    beta: float


@dataclass(frozen=True, slots=True)
class ManipulationFinding:
    finding_id: str
    report_id: str
    rule: str
    severity: str
    reason: str


@dataclass(frozen=True, slots=True)
class CollusionFinding:
    finding_id: str
    supplier_ids: tuple[str, ...]
    question_id: str
    horizon: str
    similarity: float
    reason: str


class LongitudinalIncentiveMechanism:
    """Strict-proper, multi-horizon mechanism with durable integrity controls.

    Credibility is a reputation statistic based on realized forecast quality,
    not a claim of latent ability. Collusion/manipulation detection is a flagging
    control, not proof of misconduct. Both distinctions are preserved in audit
    records so the mechanism cannot silently convert heuristics into facts.
    """

    def __init__(
        self,
        *,
        stake: float = 1.0,
        policies: Iterable[HorizonPolicy] = (HorizonPolicy("default"),),
        credibility_prior: tuple[float, float] = (1.0, 1.0),
        similarity_threshold: float = 0.999999,
        storage_path: str | None = None,
    ) -> None:
        if not isfinite(stake) or stake <= 0:
            raise ValueError("stake must be positive and finite")
        if any(not isfinite(v) or v <= 0 for v in credibility_prior):
            raise ValueError("credibility prior must be positive and finite")
        if not 0 < similarity_threshold <= 1:
            raise ValueError("similarity_threshold must be in (0,1]")
        self.stake = stake
        self.policies = tuple(policies)
        if not self.policies or len({p.horizon for p in self.policies}) != len(self.policies):
            raise ValueError("horizon policies must be non-empty and unique")
        self._weights = {p.horizon: p.weight for p in self.policies}
        self._prior = credibility_prior
        self._similarity_threshold = similarity_threshold
        self._reports: dict[str, ForecastReport] = {}
        self._settlements: dict[str, Settlement] = {}
        self._quality: dict[str, list[float]] = {}
        self._findings: list[ManipulationFinding | CollusionFinding] = []
        self._storage_path = storage_path
        if storage_path:
            self._init_db()
            self._load_db()

    def _db(self) -> sqlite3.Connection:
        if not self._storage_path:
            raise RuntimeError("storage is not configured")
        return sqlite3.connect(self._storage_path)

    def _init_db(self) -> None:
        with self._db() as db:
            db.execute("""CREATE TABLE IF NOT EXISTS longitudinal_reports(
                report_id TEXT PRIMARY KEY, supplier_id TEXT NOT NULL, question_id TEXT NOT NULL,
                horizon TEXT NOT NULL, probability REAL NOT NULL, submitted_at TEXT NOT NULL,
                deadline TEXT NOT NULL, outcome_due_at TEXT NOT NULL, evidence_ids TEXT NOT NULL,
                evidence_fingerprint TEXT NOT NULL, specification_hash TEXT NOT NULL,
                report_hash TEXT NOT NULL, UNIQUE(supplier_id, question_id, horizon))""")
            db.execute("""CREATE TABLE IF NOT EXISTS longitudinal_settlements(
                report_id TEXT PRIMARY KEY, outcome INTEGER NOT NULL, log_loss REAL NOT NULL,
                brier_score REAL NOT NULL, transfer REAL NOT NULL, verified_at TEXT NOT NULL,
                verifier_id TEXT NOT NULL, previous_hash TEXT NOT NULL, provenance_hash TEXT NOT NULL,
                credibility REAL NOT NULL)""")
            db.execute("CREATE TABLE IF NOT EXISTS longitudinal_findings(finding_id TEXT PRIMARY KEY, finding_type TEXT NOT NULL, payload TEXT NOT NULL)")

    def _load_db(self) -> None:
        with self._db() as db:
            for r in db.execute("SELECT report_id,supplier_id,question_id,horizon,probability,submitted_at,deadline,outcome_due_at,evidence_ids,evidence_fingerprint,specification_hash FROM longitudinal_reports"):
                self._reports[r[0]] = ForecastReport(r[0],r[1],r[2],r[3],r[4],datetime.fromisoformat(r[5]),datetime.fromisoformat(r[6]),datetime.fromisoformat(r[7]),tuple(json.loads(r[8])),r[9],r[10])
            for r in db.execute("SELECT report_id,outcome,log_loss,brier_score,transfer,verified_at,verifier_id,previous_hash,provenance_hash,credibility FROM longitudinal_settlements"):
                self._settlements[r[0]] = Settlement(r[0],r[1],r[2],r[3],r[4],datetime.fromisoformat(r[5]),r[6],r[7],r[8],r[9])
            for r in db.execute("SELECT finding_id,finding_type,payload FROM longitudinal_findings"):
                p=json.loads(r[2]); self._findings.append(ManipulationFinding(**p) if r[1]=='manipulation' else CollusionFinding(**p))

    def _record(self, finding: ManipulationFinding | CollusionFinding) -> None:
        if any(f.finding_id == finding.finding_id for f in self._findings):
            return
        self._findings.append(finding)
        if self._storage_path:
            payload={k:getattr(finding,k) for k in finding.__dataclass_fields__}
            with self._db() as db:
                db.execute("INSERT OR IGNORE INTO longitudinal_findings VALUES(?,?,?)",(finding.finding_id,'manipulation' if isinstance(finding,ManipulationFinding) else 'collusion',_canonical(payload)))

    def submit(self, report: ForecastReport) -> None:
        if report.report_id in self._reports:
            raise ValueError("duplicate report_id")
        if report.horizon not in self._weights:
            raise ValueError("unregistered horizon")
        if any(r.supplier_id==report.supplier_id and r.question_id==report.question_id and r.horizon==report.horizon for r in self._reports.values()):
            raise ValueError("one report per supplier, question and horizon")
        if self._storage_path:
            with self._db() as db:
                db.execute("INSERT INTO longitudinal_reports VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",(report.report_id,report.supplier_id,report.question_id,report.horizon,report.probability,report.submitted_at.isoformat(),report.deadline.isoformat(),report.outcome_due_at.isoformat(),json.dumps(report.evidence_ids),report.evidence_fingerprint,report.specification_hash,report.report_hash))
        self._reports[report.report_id]=report
        self._detect(report)

    def _detect(self, report: ForecastReport) -> None:
        if report.probability in (0.0,1.0):
            self._record(ManipulationFinding(_digest((report.report_id,'boundary')),report.report_id,'boundary_probability','medium','boundary probability creates maximal loss exposure if wrong'))
        for peer in self._reports.values():
            if peer.report_id==report.report_id or peer.question_id!=report.question_id or peer.horizon!=report.horizon:
                continue
            similarity=1-abs(report.probability-peer.probability)
            shared=bool(report.evidence_fingerprint and report.evidence_fingerprint==peer.evidence_fingerprint)
            if shared and similarity>=self._similarity_threshold:
                ids=tuple(sorted((report.supplier_id,peer.supplier_id)))
                self._record(CollusionFinding(_digest((ids,report.question_id,report.horizon)),ids,report.question_id,report.horizon,similarity,'near-identical forecast with shared evidence fingerprint'))

    def _credibility_preview(self, supplier_id: str, brier: float) -> float:
        a,b=self._prior; history=self._quality.get(supplier_id,[])
        return (a+sum(1-x for x in history)+(1-brier))/(a+b+len(history)+1)

    def settle(self, report_id: str, *, outcome: int, verifier_id: str, verified_at: datetime | None = None) -> Settlement:
        if report_id not in self._reports: raise KeyError(report_id)
        if report_id in self._settlements: raise ValueError("already settled")
        if outcome not in (0,1) or not verifier_id: raise ValueError("valid outcome and verifier are required")
        report=self._reports[report_id]; verified_at=verified_at or datetime.now(timezone.utc); _aware(verified_at,'verified_at')
        if verified_at < report.outcome_due_at: raise ValueError("settlement precedes outcome_due_at")
        ll=log_loss(report.probability,outcome); bs=brier_score(report.probability,outcome); credibility=self._credibility_preview(report.supplier_id,bs)
        previous='GENESIS' if not self._settlements else max(self._settlements.values(),key=lambda s:s.verified_at).provenance_hash
        payload={'report_hash':report.report_hash,'report_id':report_id,'outcome':outcome,'log_loss':ll,'brier_score':bs,'transfer':-self.stake*ll,'verified_at':verified_at.isoformat(),'verifier_id':verifier_id,'previous_hash':previous,'credibility':credibility}
        settlement=Settlement(report_id,outcome,ll,bs,-self.stake*ll,verified_at,verifier_id,previous,_digest(payload),credibility)
        if self._storage_path:
            with self._db() as db:
                db.execute("INSERT INTO longitudinal_settlements VALUES(?,?,?,?,?,?,?,?,?,?)",(settlement.report_id,settlement.outcome,settlement.log_loss,settlement.brier_score,settlement.transfer,settlement.verified_at.isoformat(),settlement.verifier_id,settlement.previous_hash,settlement.provenance_hash,settlement.credibility))
        self._settlements[report_id]=settlement; self._quality.setdefault(report.supplier_id,[]).append(bs)
        return settlement

    def credibility(self, supplier_id: str) -> CredibilityState:
        history=self._quality.get(supplier_id,[]); a,b=self._prior
        pa=a+sum(1-x for x in history); pb=b+sum(history)
        return CredibilityState(supplier_id,len(history),fmean(history) if history else 0.0,pa/(pa+pb),pa,pb)

    def score_question(self, question_id: str) -> dict[str, float]:
        settled=[s for s in self._settlements.values() if self._reports[s.report_id].question_id==question_id]
        if not settled: raise ValueError("question has no settlements")
        result={}; weighted_ll=weighted_bs=total=0.0
        for horizon,weight in self._weights.items():
            xs=[s for s in settled if self._reports[s.report_id].horizon==horizon]
            if not xs: continue
            result[f'{horizon}.mean_log_loss']=fmean(s.log_loss for s in xs); result[f'{horizon}.mean_brier']=fmean(s.brier_score for s in xs)
            weighted_ll+=weight*result[f'{horizon}.mean_log_loss']; weighted_bs+=weight*result[f'{horizon}.mean_brier']; total+=weight
        if not total: raise ValueError("no covered horizon")
        result['weighted_log_loss']=weighted_ll/total; result['weighted_brier']=weighted_bs/total; return result

    def longitudinal_score(self, supplier_id: str) -> dict[str,float]:
        xs=[s for s in self._settlements.values() if self._reports[s.report_id].supplier_id==supplier_id]
        if not xs: raise ValueError("supplier has no settlements")
        return {'mean_log_loss':fmean(s.log_loss for s in xs),'mean_brier':fmean(s.brier_score for s in xs),'total_transfer':sum(s.transfer for s in xs),'settled_reports':float(len(xs))}

    def audit_chain_valid(self) -> bool:
        previous='GENESIS'
        for s in sorted(self._settlements.values(),key=lambda x:x.verified_at):
            r=self._reports[s.report_id]
            if s.previous_hash!=previous: return False
            expected=_digest({'report_hash':r.report_hash,'report_id':s.report_id,'outcome':s.outcome,'log_loss':s.log_loss,'brier_score':s.brier_score,'transfer':s.transfer,'verified_at':s.verified_at.isoformat(),'verifier_id':s.verifier_id,'previous_hash':s.previous_hash,'credibility':s.credibility})
            if expected!=s.provenance_hash: return False
            previous=s.provenance_hash
        return True

    def findings(self) -> tuple[ManipulationFinding|CollusionFinding,...]: return tuple(self._findings)

    @staticmethod
    def expected_log_loss(probability: float, belief: float) -> float:
        if not all(isfinite(v) and 0<v<1 for v in (probability,belief)): raise ValueError('probability and belief must be strictly between 0 and 1')
        return -(belief*log(probability)+(1-belief)*log(1-probability))

    @classmethod
    def truthful_report_gap(cls, *, belief: float, report_probability: float) -> float:
        return cls.expected_log_loss(report_probability,belief)-cls.expected_log_loss(belief,belief)

    @classmethod
    def verify_strict_propriety(cls, *, belief: float, candidate_reports: tuple[float,...], tolerance: float=1e-12) -> bool:
        if not candidate_reports or belief not in candidate_reports: return False
        if not all(isfinite(p) and 0<p<1 for p in candidate_reports): raise ValueError('candidate reports must be strictly between 0 and 1')
        truthful=cls.expected_log_loss(belief,belief)
        return all(truthful < cls.expected_log_loss(p,belief)-tolerance for p in candidate_reports if p!=belief)

    def incentive_compatible(self, belief: float, candidate_reports: tuple[float,...]) -> bool:
        return self.verify_strict_propriety(belief=belief,candidate_reports=candidate_reports)

    def evidence_trace(self, report_id: str) -> dict[str,object]:
        report=self._reports[report_id]
        return {'report_id':report.report_id,'evidence_ids':report.evidence_ids,'evidence_fingerprint':report.evidence_fingerprint,'specification_hash':report.specification_hash}


__all__=['CollusionFinding','CredibilityState','ForecastReport','HorizonPolicy','ManipulationFinding','LongitudinalIncentiveMechanism','Settlement','brier_score','log_loss']
