"""Concurrency-safe handoff lifecycle projection backed by canonical events."""
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
    fcntl=None

from .control_plane import HandoffState, validate_handoff
from .event_log import append_payload

@contextmanager
def _locked(path: Path) -> Iterator[None]:
    lock_path=path.with_suffix(path.suffix+".lock"); lock_path.parent.mkdir(parents=True,exist_ok=True)
    with lock_path.open("a+",encoding="utf-8") as lock:
        if fcntl is not None: fcntl.flock(lock.fileno(),fcntl.LOCK_EX)
        try: yield
        finally:
            if fcntl is not None: fcntl.flock(lock.fileno(),fcntl.LOCK_UN)

def _write(path: Path, data: dict[str,Any]) -> None:
    fd,tmp=tempfile.mkstemp(prefix=f".{path.name}.",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as handle:
            json.dump(data,handle,sort_keys=True,indent=2,ensure_ascii=False); handle.write("\n"); handle.flush(); os.fsync(handle.fileno())
        os.replace(tmp,path)
    except Exception:
        try: os.unlink(tmp)
        except FileNotFoundError: pass
        raise

def _load(path: Path) -> dict[str,Any]:
    if not path.exists(): return {"schema_version":"1.0.0","handoffs":{}}
    data=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data.get("handoffs"),dict): raise ValueError("Invalid handoff registry")
    return data

def transition(path: Path, event_log: Path, handoff: dict[str,Any], *, target_status: HandoffState, actor: str, timestamp: str, evidence: list[str]) -> dict[str,Any]:
    current=HandoffState(handoff["status"])
    candidate=dict(handoff)
    if current is HandoffState.VERIFIED: candidate["verification_state"]=HandoffState.VERIFIED.value
    validate_handoff(candidate)
    legal={HandoffState.CREATED:{HandoffState.VALIDATION_PENDING,HandoffState.READY,HandoffState.REJECTED},HandoffState.VALIDATION_PENDING:{HandoffState.READY,HandoffState.REJECTED},HandoffState.READY:{HandoffState.ACCEPTED,HandoffState.REJECTED},HandoffState.ACCEPTED:{HandoffState.IMPLEMENTING,HandoffState.REJECTED},HandoffState.IMPLEMENTING:{HandoffState.IMPLEMENTED,HandoffState.REJECTED},HandoffState.IMPLEMENTED:{HandoffState.VERIFIED,HandoffState.REJECTED},HandoffState.VERIFIED:{HandoffState.INTEGRATED,HandoffState.SUPERSEDED},HandoffState.INTEGRATED:{HandoffState.SUPERSEDED},HandoffState.REJECTED:{HandoffState.SUPERSEDED},HandoffState.SUPERSEDED:set()}
    if target_status not in legal[current]: raise ValueError(f"Illegal handoff transition: {current.value} -> {target_status.value}")
    if not evidence: raise ValueError("Handoff transition requires evidence")
    with _locked(path):
        data=_load(path); existing=data["handoffs"].get(handoff["handoff_id"],candidate)
        if HandoffState(existing["status"]) != current: raise ValueError("Handoff registry is stale; reconcile before retry")
        record={**existing,"status":target_status.value,"last_actor":actor,"last_timestamp":timestamp,"last_evidence":evidence}
        if target_status is HandoffState.VERIFIED: record["verification_state"]=HandoffState.VERIFIED.value
        if target_status is HandoffState.INTEGRATED: record["integrated_at"]=timestamp; record["verification_state"]=HandoffState.VERIFIED.value
        event=append_payload(event_log,event_type="HANDOFF_LIFECYCLE",mission_id=existing["destination_mission"],actor=actor,timestamp=timestamp,payload={"handoff_id":existing["handoff_id"],"from":current.value,"to":target_status.value,"evidence":evidence})
        record["mutation_event_id"]=event["event_id"]
        data["handoffs"][handoff["handoff_id"]]=record; _write(path,data); return record
