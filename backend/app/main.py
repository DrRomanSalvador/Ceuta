"""CeutIA canonical FastAPI application entrypoint."""
from __future__ import annotations
import hmac, logging, os
from contextlib import asynccontextmanager
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from typing import AsyncIterator
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from app.core.decision.config_provenance import ConfigurationProvenance
from app.core.decision.control_plane import DecisionAuditChain, EvidenceAssessment, EvidenceDisposition
from app.core.decision.decision_system import DecisionContext, DecisionMode, DecisionObjective, DecisionOption, ScenarioOutcome
from app.core.decision.information_boundary import InformationVisibility
from app.core.decision.persistence import SQLiteDecisionStore
from app.core.decision.review_policy import DecisionRisk
from app.core.final_epistemic_control import EpistemicIntegrityStatus, EpistemicContract, EpistemicSelfModel, EpistemicTransformation, FinalEpistemicController, FalsifiabilityStatus, FalsificationCondition, OntologyStatus, RealityAnchorAssessment, SystemValidity
from app.core.runtime.decision_lifecycle import BitemporalRef, DecisionEvidence, DecisionLifecycleEngine
from app.core.runtime.evidence_persistence import DecisionEvidenceStore
from app.core.runtime.integrity import validate_evidence_set, validate_scenario_probabilities
from app.core.runtime.model_governance import ModelGovernanceRecord
from app.core.serpiente_boundary import SerpientePredictionEnvelope
APP_NAME="CeutIA"; APP_VERSION="0.1.0"; APP_DESCRIPTION="Evidence-based territorial intelligence, knowledge and early-warning platform for Ceuta."; STATUS_RUNNING="running"; STATUS_HEALTHY="healthy"; STATUS_NOT_READY="not_ready"; STATUS_READY="ready"; DEFAULT_HOST="0.0.0.0"; DEFAULT_PORT=8000; MIN_PORT=1; MAX_PORT=65535; DECISION_KEY_HEADER="X-CeutIA-Decision-Key"; LOGGER=logging.getLogger(APP_NAME)
def _configure_logging():
    if not logging.getLogger().handlers: logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
_configure_logging()
@dataclass(frozen=True, slots=True)
class RuntimeConfig: host:str; port:int; code_revision:str; decision_db:str
def _read_host():
    host=os.getenv("CEUTIA_HOST",DEFAULT_HOST).strip()
    if not host: raise ValueError("CEUTIA_HOST cannot be empty")
    return host
def _read_port():
    raw=os.getenv("CEUTIA_PORT",str(DEFAULT_PORT)).strip()
    try: port=int(raw)
    except ValueError as exc: raise ValueError("CEUTIA_PORT must be an integer") from exc
    if not MIN_PORT <= port <= MAX_PORT: raise ValueError(f"CEUTIA_PORT must be between {MIN_PORT} and {MAX_PORT}")
    return port
def load_runtime_config(): return RuntimeConfig(_read_host(),_read_port(),os.getenv("CEUTIA_CODE_REVISION","").strip(),os.getenv("CEUTIA_DECISION_DB","").strip())
RUNTIME_CONFIG=load_runtime_config()
@dataclass(frozen=True, slots=True)
class ReadinessState: ready:bool; reason:str|None=None
def _readiness():
    missing=[]
    if not RUNTIME_CONFIG.code_revision: missing.append("CEUTIA_CODE_REVISION")
    if not RUNTIME_CONFIG.decision_db: missing.append("CEUTIA_DECISION_DB")
    if missing: return ReadinessState(False,"required decision-runtime configuration missing: "+", ".join(missing))
    return ReadinessState(True)
@asynccontextmanager
async def lifespan(application:FastAPI)->AsyncIterator[None]:
    del application; LOGGER.info("%s starting; version=%s",APP_NAME,APP_VERSION)
    try: yield
    except Exception: LOGGER.exception("%s lifecycle terminated because of an exception",APP_NAME); raise
    finally: LOGGER.info("%s shutdown complete",APP_NAME)
app=FastAPI(title=APP_NAME,version=APP_VERSION,description=APP_DESCRIPTION,lifespan=lifespan)
class DecisionScenarioRequest(BaseModel): scenario_id:str=Field(min_length=1); probability:float=Field(ge=0.0,le=1.0); utility:float; harm:float
class DecisionOptionRequest(BaseModel): option_id:str=Field(min_length=1); scenarios:list[DecisionScenarioRequest]=Field(min_length=1); resource_cost:float=Field(default=0.0,ge=0.0); uncertainty:float=Field(default=0.0,ge=0.0,le=1.0)
class DecisionEvidenceRequest(BaseModel): evidence_id:str=Field(min_length=1); source_id:str=Field(min_length=1); claim_id:str=Field(min_length=1); content_hash:str=Field(min_length=64,max_length=64); valid_from:datetime; valid_until:datetime|None=None; recorded_from:datetime; recorded_until:datetime|None=None; base_weight:float=Field(ge=0.0,le=1.0); adversarial_risk:float=Field(default=0.0,ge=0.0,le=1.0); contradiction_weight:float=Field(default=0.0,ge=0.0,le=1.0); independent_origin:bool=True; disposition:EvidenceDisposition=EvidenceDisposition.ACCEPT; provenance_refs:list[str]=Field(min_length=1); visibility:InformationVisibility=InformationVisibility.PUBLIC
class DecisionRequest(BaseModel):
    decision_id:str=Field(min_length=1); decision_maker:str=Field(min_length=1); horizon:str=Field(min_length=1); purpose:str=Field(min_length=1); risk_class:DecisionRisk=DecisionRisk.LOW; mode:DecisionMode=DecisionMode.ROBUST; state_refs:list[str]=Field(min_length=1); evidence:list[DecisionEvidenceRequest]=Field(min_length=1); options:list[DecisionOptionRequest]=Field(min_length=1); assumptions:list[str]=Field(default_factory=list); hypothesis_refs:list[str]=Field(default_factory=list); model_refs:list[str]=Field(default_factory=list); scenario_refs:list[str]=Field(default_factory=list); transformation_refs:list[str]=Field(default_factory=list); constraint_refs:list[str]=Field(default_factory=list); restricted:bool=False; output_visibility:InformationVisibility=InformationVisibility.PUBLIC; serpiente_prediction:SerpientePredictionEnvelope|None=None
def _final_epistemic_assessment(payload,evidence):
    prediction=payload.serpiente_prediction
    if prediction is not None: prediction.validate_at(datetime.now(timezone.utc))
    provenance_refs=tuple(ref for item in evidence for ref in item.provenance_refs)
    if prediction is not None: provenance_refs=tuple(dict.fromkeys(provenance_refs + tuple(prediction.provenance) + (f"serpiente:prediction:{prediction.prediction_id}",)))
    external_evidence_refs=tuple(item.evidence_id for item in evidence)
    if prediction is not None: external_evidence_refs=tuple(dict.fromkeys(external_evidence_refs + (f"serpiente:prediction:{prediction.prediction_id}",)))
    independent_refs=tuple(item.evidence_id for item in evidence if item.assessment.independent_origin)
    global_doubt=(not evidence or not independent_refs or any(item.assessment.disposition is not EvidenceDisposition.ACCEPT for item in evidence) or any(item.assessment.contradiction_weight>0.5 for item in evidence))
    condition=FalsificationCondition(condition_id=f"{payload.decision_id}:evidence-integrity",target_id=payload.decision_id,expected_observation="cited evidence and any SERPIENTE forecast remain temporally valid, provenance-complete and decision-eligible",falsifying_observation="material contradiction, provenance failure, temporal invalidity or future SERPIENTE prediction is detected",independent_evidence_refs=independent_refs,assumptions=("bitemporal validity is enforced before decision execution","SERPIENTE forecasts are predictive rather than causal"),testable=bool(independent_refs))
    anchor=RealityAnchorAssessment(target_id=payload.decision_id,status=FalsifiabilityStatus.PARTIAL,conditions=(condition,),external_evidence_refs=external_evidence_refs,common_mode_dependencies=(),divergence_score=0.0,global_model_doubt=global_doubt,reasons=("reality anchoring is operationally represented but not independently established",))
    contract=EpistemicContract(contract_id=f"{payload.decision_id}:epistemic-contract",semantic_meaning=f"decision support for: {payload.purpose}",assumptions=tuple(payload.assumptions) or ("decision evidence is explicitly represented",),provenance_refs=provenance_refs,temporal_reference=payload.horizon,spatial_reference="ceuta",denominator=None,population=None,identification_conditions=("bitemporal validity checked","provenance references present"),causal_interpretation="non-causal decision support; SERPIENTE prediction is not a causal effect",evidence_status="runtime decision evidence plus optional SERPIENTE forecast",calibration_conditions=("prospective effectiveness is not inferred from execution",),validity_domain=payload.horizon,uncertainty_semantics="conservative maximum adversarial evidence risk plus explicit predictive uncertainty",dependency_refs=tuple(payload.model_refs) + ((f"serpiente:prediction:{prediction.prediction_id}",) if prediction is not None else ()))
    transformations=tuple(EpistemicTransformation(transformation_id=ref,source_contract=contract,output_contract=contract,preserves=("provenance","temporal_reference","uncertainty_semantics","non_causal_interpretation"),justification=f"declared runtime transformation reference: {ref}") for ref in payload.transformation_refs)
    self_model=EpistemicSelfModel(version="runtime-1",assumptions=("decision inputs are schema-validated","evidence provenance is explicit","SERPIENTE output is treated as prediction, not causation"),limitations=("no prospective effectiveness is established","external evidence quality is not equivalent to causal identification","SERPIENTE forecast validity depends on its point-in-time fingerprint and calibration evidence"),identification_limits=("causal effect is not identified by this decision endpoint",),ontology_status=OntologyStatus.NORMAL,ontology_version="runtime-1",unexplained_signals=(),global_validity=SystemValidity.DOUBT if global_doubt else SystemValidity.SUPPORTED)
    return FinalEpistemicController().assess(reality_anchor=anchor,transformations=transformations,self_model=self_model)
@app.get("/",tags=["system"],summary="CeutIA service information")
async def root(): return {"service":APP_NAME,"version":APP_VERSION,"status":STATUS_RUNNING}
@app.get("/health",tags=["system"],summary="Process liveness check")
async def health(): return {"status":STATUS_HEALTHY,"service":APP_NAME,"version":APP_VERSION}
@app.get("/ready",tags=["system"],summary="Application readiness check")
async def ready():
    state=_readiness()
    if state.ready: return JSONResponse(status_code=200,content={"status":STATUS_READY,"service":APP_NAME,"version":APP_VERSION})
    return JSONResponse(status_code=503,content={"status":STATUS_NOT_READY,"service":APP_NAME,"version":APP_VERSION,"reason":state.reason})
@app.post("/decision/evaluate",tags=["decision"],summary="Execute the integrated evidence-to-decision lifecycle")
async def evaluate_decision(payload:DecisionRequest,request:Request):
    configured_key=os.getenv("CEUTIA_DECISION_API_KEY","").strip(); provided_key=request.headers.get(DECISION_KEY_HEADER,"")
    if not configured_key: return JSONResponse(status_code=503,content={"status":STATUS_NOT_READY,"reason":"high-impact decision endpoint is not provisioned with CEUTIA_DECISION_API_KEY"})
    if not provided_key or not hmac.compare_digest(provided_key,configured_key): return JSONResponse(status_code=401,content={"error":"unauthorized","reason":"valid decision API key required"})
    state=_readiness()
    if not state.ready: return JSONResponse(status_code=503,content={"status":STATUS_NOT_READY,"reason":state.reason})
    for option in payload.options: validate_scenario_probabilities([scenario.probability for scenario in option.scenarios])
    store=SQLiteDecisionStore(RUNTIME_CONFIG.decision_db)
    try:
        configuration=ConfigurationProvenance(configuration_id="ceutia-decision-runtime",version="1",source_refs=("environment:decision-runtime",),values={"risk_class":payload.risk_class.value,"mode":payload.mode.value}); lifecycle=DecisionLifecycleEngine(store,code_revision=RUNTIME_CONFIG.code_revision,configuration=configuration); evidence=[]
        for item in payload.evidence:
            temporal=BitemporalRef(item.valid_from,item.valid_until,item.recorded_from,item.recorded_until,item.evidence_id); assessment=EvidenceAssessment(evidence_id=item.evidence_id,source_id=item.source_id,base_weight=item.base_weight,adversarial_risk=item.adversarial_risk,contradiction_weight=item.contradiction_weight,independent_origin=item.independent_origin,disposition=item.disposition); evidence.append(DecisionEvidence(item.evidence_id,item.source_id,item.claim_id,item.content_hash,tuple(item.provenance_refs),temporal,assessment,item.visibility))
        try: validate_evidence_set(evidence,source_registry=store.source_registry(),as_of=datetime.now(timezone.utc))
        except ValueError as exc: return JSONResponse(status_code=422,content={"decision_id":payload.decision_id,"disposition":"abstain","control_reason":"evidence integrity validation failed","reason":str(exc)})
        try: final_epistemic=_final_epistemic_assessment(payload,evidence)
        except ValueError as exc: return JSONResponse(status_code=422,content={"decision_id":payload.decision_id,"disposition":"abstain","control_reason":"cross-system prediction integrity validation failed","reason":str(exc)})
        gate_event=DecisionAuditChain(store).append(payload.decision_id,"final_epistemic_gate",{"validity":final_epistemic.validity.value,"composition":final_epistemic.composition.value,"reasons":final_epistemic.reasons,"anchor_status":final_epistemic.reality_anchor.status.value,"anchor_established":False,"serpiente_prediction_id":payload.serpiente_prediction.prediction_id if payload.serpiente_prediction else None})
        if final_epistemic.validity is not SystemValidity.SUPPORTED: return JSONResponse(status_code=409,content={"decision_id":payload.decision_id,"disposition":"abstain","control_reason":"final epistemic controller suspended decision eligibility","epistemic_validity":final_epistemic.validity.value,"epistemic_composition":final_epistemic.composition.value,"epistemic_reasons":final_epistemic.reasons,"audit_event_id":gate_event.event_id})
        if final_epistemic.composition is not EpistemicIntegrityStatus.PRESERVED: return JSONResponse(status_code=409,content={"decision_id":payload.decision_id,"disposition":"abstain","control_reason":"final epistemic composition is not preserved","epistemic_composition":final_epistemic.composition.value,"audit_event_id":gate_event.event_id})
        evidence_store=DecisionEvidenceStore(store)
        for item in evidence: evidence_store.record(item)
        options=tuple(DecisionOption(item.option_id,tuple(ScenarioOutcome(s.scenario_id,s.probability,s.utility,s.harm) for s in item.scenarios),item.resource_cost,item.uncertainty) for item in payload.options); scenario_refs=tuple(payload.scenario_refs) or tuple(s.scenario_id for option in options for s in option.outcomes); model_refs=tuple(payload.model_refs); model_releases={}
        if not model_refs:
            deterministic=ModelGovernanceRecord(model_id="deterministic:decision-system",version="1",code_hash=RUNTIME_CONFIG.code_revision,data_snapshot_hash=configuration.fingerprint(),assumptions=("deterministic decision rules only",),valid_from=datetime.now(timezone.utc),calibrated=True,validation_ref="governance:deterministic-rules",calibration_ref="governance:deterministic-rules",approval_ref="governance:decision-policy"); deterministic=replace(deterministic,release_hash=deterministic.fingerprint()); model_releases[deterministic.model_id]=deterministic; model_refs=(deterministic.model_id,)
        context=DecisionContext(decision_id=payload.decision_id,decision_maker=payload.decision_maker,horizon=payload.horizon,objectives=(DecisionObjective("expected_utility",1.0,1),),assumptions=tuple(payload.assumptions),risk_class=payload.risk_class)
        result=lifecycle.execute(context,options,evidence,state_refs=payload.state_refs,hypothesis_refs=payload.hypothesis_refs,model_refs=model_refs,scenario_refs=scenario_refs,assumption_refs=payload.assumptions,transformation_refs=payload.transformation_refs,constraint_refs=payload.constraint_refs,purpose=payload.purpose,restricted=payload.restricted,output_visibility=payload.output_visibility,mode=payload.mode,model_releases=model_releases)
        return {"decision_id":result.decision_id,"disposition":result.disposition.value,"recommendation":{"option_id":result.recommendation.option_id,"score":result.recommendation.score,"expected_utility":result.recommendation.expected_utility,"expected_harm":result.recommendation.expected_harm,"maximum_regret":result.recommendation.maximum_regret,"reasons":result.recommendation.reasons},"control_reason":result.control_reason,"audit_event_id":result.audit_event_id,"epistemic_gate_event_id":gate_event.event_id,"serpiente_prediction_id":payload.serpiente_prediction.prediction_id if payload.serpiente_prediction else None,"lineage_fingerprint":result.lineage.semantic_fingerprint(),"uncertainty":result.uncertainty.value,"degraded_reasons":result.degraded_reasons}
    finally: store.close()
@app.get("/version",tags=["system"],summary="Application version")
async def version(): return {"service":APP_NAME,"version":APP_VERSION}
@app.get("/diagnostics",tags=["system"],summary="Minimal non-sensitive runtime diagnostics")
async def diagnostics():
    state=_readiness(); return {"service":APP_NAME,"version":APP_VERSION,"application":STATUS_RUNNING,"liveness":STATUS_HEALTHY,"readiness":STATUS_READY if state.ready else STATUS_NOT_READY,"runtime":{"host_configured":bool(RUNTIME_CONFIG.host),"port_configured":MIN_PORT<=RUNTIME_CONFIG.port<=MAX_PORT,"code_revision_configured":bool(RUNTIME_CONFIG.code_revision),"decision_persistence_configured":bool(RUNTIME_CONFIG.decision_db),"decision_api_key_configured":bool(os.getenv("CEUTIA_DECISION_API_KEY",""))}}
@app.get("/diagnostics/config",tags=["system"],summary="Non-sensitive runtime configuration validation")
async def diagnostics_config():
    state=_readiness(); return {"status":"valid" if state.ready else "incomplete","host_configured":bool(RUNTIME_CONFIG.host),"port_valid":MIN_PORT<=RUNTIME_CONFIG.port<=MAX_PORT,"code_revision_configured":bool(RUNTIME_CONFIG.code_revision),"decision_persistence_configured":bool(RUNTIME_CONFIG.decision_db),"decision_api_key_configured":bool(os.getenv("CEUTIA_DECISION_API_KEY",""))}
@app.exception_handler(Exception)
async def unhandled_exception_handler(request:Request,exc:Exception):
    LOGGER.exception("Unhandled exception: method=%s path=%s",request.method,request.url.path,exc_info=exc); return JSONResponse(status_code=500,content={"error":"internal_server_error","service":APP_NAME,"version":APP_VERSION})
def main():
    import uvicorn; uvicorn.run("app.main:app",host=RUNTIME_CONFIG.host,port=RUNTIME_CONFIG.port)
if __name__=="__main__": main()
