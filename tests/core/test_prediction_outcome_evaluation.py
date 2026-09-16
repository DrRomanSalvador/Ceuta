from __future__ import annotations
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json, math, sqlite3
import pytest
from app.core.scientific.prediction_outcome_evaluation import get_prediction_outcome, record_prediction_outcome
from app.core.scientific.prediction_persistence import record_prediction

def _prediction() -> dict[str, object]:
    return {"contract_id":"ceutia-serpiente-scientific-prediction","contract_hash":"672dfa6b60d2e8c0854a024e83acf6b23eed44f2cd3293708aee533d7a9dc1f0","producer_repository":"DrRomanSalvador/SERPIENTE","producer_component":"test","schema_version":"1.1","prediction_id":"prediction-outcome-1","origin_time":"2026-09-15T06:00:00+00:00","available_at":"2026-09-15T06:05:00+00:00","horizon":"PT1H","target":"target.binary","probability":0.75,"lower":0.6,"upper":0.9,"uncertainty":{"aleatoric":0.1},"model_disagreement":0.05,"model_id":"model-1","method_id":"method-1","method_version":"1","training_window":"2026-01-01/2026-09-01","reference_class":"ceuta","ood_state":"IN_DOMAIN","causal_status":"ABSTAIN","calibration_status":"CALIBRATED","evidence_level":"TEST","source_independence":"INDEPENDENT","provenance":["test:source"],"configuration_hash":"config","code_revision":"revision","point_in_time_fingerprint":"fingerprint","integrity_hash":"integrity"}

def _ascertainment(now: datetime | None = None) -> dict[str, object]:
    now=now or datetime.now(timezone.utc).replace(microsecond=0)
    return {"source_id":"outcome:source-a","source_version":"2026.09","observation_time":now-timedelta(minutes=10),"availability_time":now-timedelta(minutes=5),"ascertainment_time":now,"revision_id":"rev-1","measurement_process_id":"measurement-v1","outcome_definition_version":"target.binary:v1","transformation_id":"identity:v1","censoring_status":"NONE","missingness_status":"OBSERVED","selection_status":"NONE","intervention_exposure_id":None}

def _record(connection: sqlite3.Connection, **overrides: object) -> dict[str, object]:
    now=datetime.now(timezone.utc).replace(microsecond=0); prediction=_prediction(); prediction["origin_time"]=(now-timedelta(hours=2)).isoformat(); prediction["available_at"]=(now-timedelta(hours=1,minutes=55)).isoformat(); unsigned=dict(prediction); unsigned.pop("integrity_hash",None); prediction["integrity_hash"]=sha256(json.dumps(unsigned,sort_keys=True,separators=(",",":"),default=str).encode()).hexdigest(); record_prediction(connection,prediction,decision_id="decision-1")
    args={"prediction_id":"prediction-outcome-1","decision_id":"decision-1","action_id":"option-1","outcome_id":"outcome-1","target":"target.binary","outcome_time":now,"observed":1,"provenance":("outcome:test",),**_ascertainment(now)}; args.update(overrides); return record_prediction_outcome(connection,**args)

def test_prediction_outcome_is_linked_and_evaluated():
    connection=sqlite3.connect(":memory:"); result=_record(connection); assert result["brier_error"]==pytest.approx(0.0625); assert result["log_loss_error"]==pytest.approx(-math.log(0.75)); stored=get_prediction_outcome(connection,"prediction-outcome-1"); assert stored["action_id"]=="option-1" and stored["source_version"]=="2026.09" and stored["outcome_definition_version"]=="target.binary:v1"

def test_outcome_cannot_precede_prediction_availability():
    connection=sqlite3.connect(":memory:")
    with pytest.raises(ValueError,match="availability"): _record(connection,outcome_time=datetime(2026,9,15,6,1,tzinfo=timezone.utc))

def test_outcome_cannot_precede_prediction_target_time():
    connection=sqlite3.connect(":memory:"); now=datetime.now(timezone.utc).replace(microsecond=0)
    with pytest.raises(ValueError,match="target time"): _record(connection,outcome_time=now-timedelta(hours=1,seconds=1))

def test_outcome_requires_prediction_decision_alignment():
    connection=sqlite3.connect(":memory:")
    with pytest.raises(ValueError,match="does not belong"): _record(connection,decision_id="decision-2")

def test_outcome_rejects_unordered_ascertainment_timestamps():
    connection=sqlite3.connect(":memory:"); now=datetime.now(timezone.utc).replace(microsecond=0)
    with pytest.raises(ValueError,match="must be ordered"): _record(connection,observation_time=now,availability_time=now-timedelta(seconds=1))

def test_outcome_rejects_non_observed_or_selected_records_from_scoring():
    connection=sqlite3.connect(":memory:")
    with pytest.raises(ValueError,match="not eligible"): _record(connection,missingness_status="MISSING")
    with pytest.raises(ValueError,match="not eligible"): _record(connection,selection_status="OBSERVABLE_ONLY")

def test_outcome_revision_creates_identity_distinction_and_collision_is_rejected():
    connection=sqlite3.connect(":memory:"); _record(connection)
    with pytest.raises(RuntimeError,match="identity collision"): _record(connection,revision_id="rev-2")

def test_outcome_cannot_be_ascertained_before_prediction_is_available():
    connection=sqlite3.connect(":memory:"); now=datetime.now(timezone.utc).replace(microsecond=0)
    with pytest.raises(ValueError,match="cannot precede prediction availability"): _record(connection,observation_time=now-timedelta(hours=3,minutes=1),availability_time=now-timedelta(hours=3),ascertainment_time=now)
