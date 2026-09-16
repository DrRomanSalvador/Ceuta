"""Cross-cutting scientific runtime contracts."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import StrEnum
from hashlib import sha256
import json, math, sqlite3


def _canonical(value: object) -> str: return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
def _digest(value: object) -> str: return sha256(_canonical(value).encode()).hexdigest()
class RuntimeState(StrEnum): RELEASE="release"; REVIEW="review"; ABSTAIN="abstain"
@dataclass(frozen=True, slots=True)
class ReferenceClassAssessment:
    reference_class_id:str; sample_size:int; minimum_sample_size:int; support_score:float; applicability_score:float; unique_event:bool=False
    def __post_init__(self):
        if not self.reference_class_id.strip() or self.sample_size<0 or self.minimum_sample_size<1: raise ValueError("reference-class metadata is invalid")
        if any(not math.isfinite(v) or not 0<=v<=1 for v in (self.support_score,self.applicability_score)): raise ValueError("reference-class scores must be in [0,1]")
    @property
    def state(self):
        if self.unique_event and self.sample_size<self.minimum_sample_size: return RuntimeState.ABSTAIN
        return RuntimeState.REVIEW if self.support_score<0.5 or self.applicability_score<0.5 else RuntimeState.RELEASE
@dataclass(frozen=True, slots=True)
class FeatureSupport:
    feature:str; observed_min:float; observed_max:float; deployment_value:float; review_margin:float=0.05
    def __post_init__(self):
        if not self.feature.strip() or not all(math.isfinite(v) for v in (self.observed_min,self.observed_max,self.deployment_value,self.review_margin)) or self.observed_max<=self.observed_min or self.review_margin<0: raise ValueError("feature support values are invalid")
    @property
    def normalized_distance(self):
        width=self.observed_max-self.observed_min
        return (self.observed_min-self.deployment_value)/width if self.deployment_value<self.observed_min else (self.deployment_value-self.observed_max)/width if self.deployment_value>self.observed_max else 0.0
    @property
    def extrapolation(self): return self.deployment_value<self.observed_min or self.deployment_value>self.observed_max
    @property
    def near_boundary(self):
        if self.extrapolation: return True
        width=self.observed_max-self.observed_min; margin=self.review_margin*width
        return self.deployment_value-self.observed_min<=margin or self.observed_max-self.deployment_value<=margin
@dataclass(frozen=True, slots=True)
class NoveltyAssessment:
    features:tuple[FeatureSupport,...]; ood_threshold:float=0.0
    def __post_init__(self):
        if not self.features or self.ood_threshold<0 or not math.isfinite(self.ood_threshold): raise ValueError("novelty assessment is invalid")
    @property
    def extrapolation(self): return any(x.normalized_distance>self.ood_threshold for x in self.features)
    @property
    def near_boundary(self): return any(x.near_boundary for x in self.features)
    @property
    def max_distance(self): return max(x.normalized_distance for x in self.features)
    @property
    def state(self): return RuntimeState.ABSTAIN if self.extrapolation else RuntimeState.REVIEW if self.near_boundary else RuntimeState.RELEASE
class CausalIdentificationStatus(StrEnum): DESCRIPTIVE="descriptive"; CONDITIONAL="conditional"; IDENTIFIED="identified"; ABSTAIN="abstain"
@dataclass(frozen=True, slots=True)
class CausalRuntimeContract:
    estimand:str; treatment:str; outcome:str; assumptions:tuple[str,...]; causal_claim_requested:bool; sensitivity_score:float|None=None
    def __post_init__(self):
        if not self.estimand or not self.treatment or not self.outcome or not self.assumptions: raise ValueError("causal contract metadata is incomplete")
        if self.sensitivity_score is not None and not 0<=self.sensitivity_score<=1: raise ValueError("sensitivity_score must be in [0,1]")
    @property
    def status(self):
        normalized={x.strip().lower() for x in self.assumptions}; required={"consistency","conditional_exchangeability","positivity"}
        if required.issubset(normalized): return CausalIdentificationStatus.IDENTIFIED
        if self.causal_claim_requested: return CausalIdentificationStatus.ABSTAIN
        return CausalIdentificationStatus.CONDITIONAL if normalized & {"consistency","positivity","exchangeability","conditional_exchangeability"} else CausalIdentificationStatus.DESCRIPTIVE
@dataclass(frozen=True, slots=True)
class RobustnessGate:
    satisficing_rate:float; worst_case:float; max_regret:float; minimum_satisficing_rate:float; minimum_worst_case:float; maximum_regret:float
    def __post_init__(self):
        if any(not math.isfinite(v) for v in (self.satisficing_rate,self.worst_case,self.max_regret,self.minimum_satisficing_rate,self.minimum_worst_case,self.maximum_regret)) or not 0<=self.satisficing_rate<=1: raise ValueError("robustness values are invalid")
    @property
    def state(self): return RuntimeState.ABSTAIN if self.satisficing_rate<self.minimum_satisficing_rate else RuntimeState.REVIEW if self.worst_case<self.minimum_worst_case or self.max_regret>self.maximum_regret else RuntimeState.RELEASE
@dataclass(frozen=True, slots=True)
class ScientificRuntimeAssessment:
    assessment_id:str; decision_id:str; evidence_ids:tuple[str,...]; provenance_refs:tuple[str,...]; reference_class:ReferenceClassAssessment; novelty:NoveltyAssessment; causal:CausalRuntimeContract|None; robustness:RobustnessGate|None; uncertainty:float; code_revision:str; configuration_hash:str; method_version:str="scientific-runtime-v1"; created_at:str=""
    def __post_init__(self):
        if not self.assessment_id or not self.decision_id or not self.evidence_ids or not self.provenance_refs or not self.code_revision or not self.configuration_hash or not 0<=self.uncertainty<=1 or not math.isfinite(self.uncertainty): raise ValueError("scientific runtime assessment metadata is invalid")
    @property
    def state(self):
        states=[self.reference_class.state,self.novelty.state]
        if self.causal is not None and self.causal.causal_claim_requested: states.append(RuntimeState.ABSTAIN if self.causal.status is CausalIdentificationStatus.ABSTAIN else RuntimeState.REVIEW if self.causal.status is CausalIdentificationStatus.CONDITIONAL else RuntimeState.RELEASE)
        if self.robustness is not None: states.append(self.robustness.state)
        return RuntimeState.ABSTAIN if RuntimeState.ABSTAIN in states else RuntimeState.REVIEW if RuntimeState.REVIEW in states else RuntimeState.RELEASE
    @property
    def mechanism_satisfied(self): return self.state is not RuntimeState.ABSTAIN
    @property
    def model_conflict(self): return self.reference_class.state is not RuntimeState.RELEASE or self.novelty.state is not RuntimeState.RELEASE
    @property
    def effective_uncertainty(self):
        value=self.uncertainty
        if self.novelty.extrapolation: value=max(value,0.95)
        if self.reference_class.state is RuntimeState.ABSTAIN: value=max(value,0.9)
        if self.causal is not None and self.causal.status is CausalIdentificationStatus.CONDITIONAL: value=max(value,0.7)
        if self.robustness is not None and self.robustness.state is RuntimeState.REVIEW: value=max(value,0.6)
        return min(1.0,value)
    @property
    def findings(self):
        findings=[]
        if self.reference_class.state is not RuntimeState.RELEASE: findings.append("reference_class_unsupported")
        if self.novelty.extrapolation: findings.append("deployment_outside_observed_support")
        elif self.novelty.near_boundary: findings.append("deployment_near_observed_boundary")
        if self.causal is not None and self.causal.status is CausalIdentificationStatus.ABSTAIN: findings.append("causal_identification_unsatisfied")
        elif self.causal is not None and self.causal.status is CausalIdentificationStatus.CONDITIONAL: findings.append("causal_claim_conditional")
        if self.robustness is not None and self.robustness.state is not RuntimeState.RELEASE: findings.append("robustness_gate_not_met")
        return tuple(findings)
class ScientificRuntimeLedger:
    def __init__(self,storage_path:str)->None:
        if not storage_path: raise ValueError("storage_path is required")
        self.storage_path=storage_path
        with sqlite3.connect(storage_path) as db:
            db.execute("CREATE TABLE IF NOT EXISTS scientific_runtime_assessments(assessment_id TEXT PRIMARY KEY, decision_id TEXT NOT NULL, payload TEXT NOT NULL, assessment_hash TEXT NOT NULL, previous_hash TEXT NOT NULL, created_at TEXT NOT NULL)")
            columns={row[1] for row in db.execute("PRAGMA table_info(scientific_runtime_assessments)")}
            if "previous_hash" not in columns: db.execute("ALTER TABLE scientific_runtime_assessments ADD COLUMN previous_hash TEXT NOT NULL DEFAULT ''")
    def append(self,assessment):
        payload=_canonical(asdict(assessment)); created_at=assessment.created_at or datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.storage_path,timeout=10.0) as db:
            db.execute("BEGIN IMMEDIATE")
            try:
                if db.execute("SELECT 1 FROM scientific_runtime_assessments WHERE assessment_id=?",(assessment.assessment_id,)).fetchone(): raise ValueError("scientific runtime assessment already exists")
                previous=db.execute("SELECT assessment_hash FROM scientific_runtime_assessments ORDER BY rowid DESC LIMIT 1").fetchone(); previous_hash=previous[0] if previous else ""
                digest=_digest({"payload":payload,"previous_hash":previous_hash})
                db.execute("INSERT INTO scientific_runtime_assessments VALUES(?,?,?,?,?,?)",(assessment.assessment_id,assessment.decision_id,payload,digest,previous_hash,created_at)); db.commit()
            except Exception: db.rollback(); raise
    def verify_integrity(self):
        with sqlite3.connect(self.storage_path) as db: rows=db.execute("SELECT assessment_id,payload,assessment_hash,previous_hash FROM scientific_runtime_assessments ORDER BY rowid").fetchall()
        previous=""
        for assessment_id,payload,record_hash,previous_hash in rows:
            if not assessment_id or previous_hash!=previous or record_hash!=_digest({"payload":payload,"previous_hash":previous_hash}): return False
            previous=record_hash
        return True
__all__=["CausalIdentificationStatus","CausalRuntimeContract","FeatureSupport","NoveltyAssessment","ReferenceClassAssessment","RobustnessGate","RuntimeState","ScientificRuntimeAssessment","ScientificRuntimeLedger"]
