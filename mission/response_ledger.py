"""Fail-closed response-coupling persistence for warning/decision/action evaluation."""
from __future__ import annotations
import json
import os
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

try:
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None

from .event_log import append_payload

EXECUTION_STATES={"NO_RESPONSE","EXECUTED","DELAYED_OUTSIDE_WINDOW","NOT_EXECUTED"}
CAUSAL_STATUSES={"NOT_ASSESSED","DESCRIPTIVE_ONLY","IDENTIFICATION_INSUFFICIENT","IDENTIFICATION_SUPPORTED"}
COUNTERFACTUAL_STATUSES={"ABSENT","UNDEFINED","INSUFFICIENT","SUPPORTED"}

@contextmanager
def _locked(path:Path)->Iterator[None]:
    lock_path=path.with_suffix(path.suffix+".lock"); lock_path.parent.mkdir(parents=True,exist_ok=True)
    with lock_path.open("a+",encoding="utf-8") as lock:
        if fcntl is not None: fcntl.flock(lock.fileno(),fcntl.LOCK_EX)
        try: yield
        finally:
            if fcntl is not None: fcntl.flock(lock.fileno(),fcntl.LOCK_UN)

def _load(path:Path)->dict[str,Any]:
    if not path.exists(): return {"schema_version":"1.0.0","records":[]}
    data=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data.get("records"),list): raise ValueError("Invalid response ledger")
    return data

def _write(path:Path,data:dict[str,Any])->None:
    fd,tmp=tempfile.mkstemp(prefix=f".{path.name}.",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as handle:
            json.dump(data,handle,sort_keys=True,indent=2,ensure_ascii=False); handle.write("\n"); handle.flush(); os.fsync(handle.fileno())
        os.replace(tmp,path)
    except Exception:
        try: os.unlink(tmp)
        except FileNotFoundError: pass
        raise

def validate_response_record(record:dict[str,Any])->None:
    required={"mission_id","response_id","warning_presence","warning_or_prediction_identity","decision_identity","decision_time","action_identity","execution_time","responsible_actor","response_eligibility","intended_mechanism","response_delay","intervention_exposure_intensity","implementation_failure","resource_capacity_constraints","outcome_ascertainment_identity","response_horizon","counterfactual_causal_status","execution_status","causal_status"}
    missing=required-set(record)
    if missing: raise ValueError(f"Response record missing fields: {sorted(missing)}")
    if not record["mission_id"] or not record["response_id"]: raise ValueError("mission_id and response_id are required")
    if record["warning_presence"] not in {"PRESENT","ABSENT"}: raise ValueError("warning_presence must be PRESENT or ABSENT")
    if record["warning_presence"]=="PRESENT" and not record["warning_or_prediction_identity"]: raise ValueError("A present warning requires a canonical prediction identity")
    if record["warning_presence"]=="ABSENT" and record["warning_or_prediction_identity"] is not None: raise ValueError("Absent warning cannot carry a warning identity")
    if record["execution_status"] not in EXECUTION_STATES: raise ValueError("Unknown execution status")
    if record["causal_status"] not in CAUSAL_STATUSES: raise ValueError("Unknown causal status")
    if record["counterfactual_causal_status"] not in COUNTERFACTUAL_STATUSES: raise ValueError("Unknown counterfactual status")
    executed=record["execution_status"] in {"EXECUTED","DELAYED_OUTSIDE_WINDOW"}
    if executed and (not record["action_identity"] or not record["execution_time"]): raise ValueError("Executed response requires action identity and execution time")
    if executed and record["response_delay"] is None: raise ValueError("Executed response requires response delay")
    if record["execution_status"]=="NO_RESPONSE" and record["action_identity"] is not None: raise ValueError("NO_RESPONSE cannot carry an executed action identity")
    if record["causal_status"]=="IDENTIFICATION_SUPPORTED":
        if record["counterfactual_causal_status"]!="SUPPORTED": raise ValueError("Causal effectiveness cannot be supported without a supported counterfactual status")
        if not record["outcome_ascertainment_identity"]: raise ValueError("Causal effectiveness requires outcome ascertainment identity")
        if record["intervention_exposure_intensity"] is None: raise ValueError("Causal effectiveness requires intervention exposure/intensity")
        if not record["response_horizon"]: raise ValueError("Causal effectiveness requires a predeclared response horizon")
    if record["causal_status"] in {"IDENTIFICATION_SUPPORTED","IDENTIFICATION_INSUFFICIENT"} and record["execution_status"]=="NO_RESPONSE":
        raise ValueError("Response effectiveness cannot be evaluated as an executed intervention when no response occurred")

def append_response(path:Path,event_log:Path,record:dict[str,Any],*,actor:str,timestamp:str)->dict[str,Any]:
    validate_response_record(record)
    with _locked(path):
        data=_load(path)
        if any(x.get("response_id")==record["response_id"] for x in data["records"]): raise ValueError("Duplicate response_id")
        event=append_payload(event_log,event_type="RESPONSE_COUPLING_RECORDED",mission_id=record["mission_id"],actor=actor,timestamp=timestamp,payload=dict(record))
        persisted={**record,"mutation_event_id":event["event_id"]}
        data["records"].append(persisted); _write(path,data); return persisted
