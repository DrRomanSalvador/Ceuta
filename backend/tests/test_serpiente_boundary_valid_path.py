from datetime import datetime, timezone

from app.main import DecisionRequest, _final_epistemic_assessment
from app.core.decision.control_plane import EvidenceAssessment, EvidenceDisposition
from app.core.decision.information_boundary import InformationVisibility
from app.core.final_epistemic_control import EpistemicIntegrityStatus, SystemValidity
from app.core.runtime.decision_lifecycle import BitemporalRef, DecisionEvidence
from app.core.serpiente_boundary import SerpientePredictionEnvelope


def test_valid_prediction_enters_final_epistemic_dependency_graph():
    prediction = SerpientePredictionEnvelope(schema_version="1.0", prediction_id="p1", origin_time=datetime(2026,9,14,tzinfo=timezone.utc), horizon="24h", target="risk", probability=0.7, lower=0.4, upper=0.9, uncertainty={"epistemic":0.2}, model_disagreement=0.1, regime="STABLE", provenance=["official:aemet"], point_in_time_fingerprint="a"*64)
    request = DecisionRequest(decision_id="d1",decision_maker="owner",horizon="24h",purpose="territorial support",state_refs=["state"],evidence=[{"evidence_id":"e1","source_id":"s1","claim_id":"c1","content_hash":"a"*64,"valid_from":datetime(2026,9,13,tzinfo=timezone.utc),"recorded_from":datetime(2026,9,13,tzinfo=timezone.utc),"base_weight":1.0,"adversarial_risk":0.0,"contradiction_weight":0.0,"independent_origin":True,"disposition":EvidenceDisposition.ACCEPT,"provenance_refs":["source:s1"],"visibility":InformationVisibility.PUBLIC}],options=[{"option_id":"o1","scenarios":[{"scenario_id":"s","probability":1.0,"utility":1.0,"harm":0.0}]}],transformation_refs=["t1"],serpiente_prediction=prediction)
    item=request.evidence[0]; evidence=[DecisionEvidence("e1","s1","c1","a"*64,("source:s1",),BitemporalRef(item.valid_from,item.valid_until,item.recorded_from,item.recorded_until,"e1"),EvidenceAssessment("e1","s1",1.0,0.0,0.0,True,EvidenceDisposition.ACCEPT),InformationVisibility.PUBLIC)]
    assessment=_final_epistemic_assessment(request,evidence)
    assert assessment.validity is SystemValidity.SUPPORTED
    assert assessment.composition is EpistemicIntegrityStatus.PRESERVED
    assert "serpiente:prediction:p1" in assessment.reality_anchor.external_evidence_refs
