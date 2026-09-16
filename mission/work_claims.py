"""Persistent, concurrency-safe work-claim/lease ledger.

Claims are materialized in JSON for fast recovery.  When an event log is
provided, every claim mutation is also represented in the canonical event
ledger before the projection is committed.
"""
from __future__ import annotations
import json
import os
import tempfile
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows fallback
    fcntl = None

from .event_log import append_payload


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_claims(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": "1.3.0", "claims": {}, "history": []}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data.get("claims"), dict) or not isinstance(data.get("history", []), list):
        raise ValueError("Invalid work-claim ledger")
    return data


def _atomic_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, sort_keys=True, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush(); os.fsync(handle.fileno())
        os.replace(tmp, path)
    except Exception:
        try: os.unlink(tmp)
        except FileNotFoundError: pass
        raise


@contextmanager
def _locked(path: Path) -> Iterator[None]:
    """Serialize read-modify-write operations on POSIX runners."""
    lock_path = path.with_suffix(path.suffix + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as lock:
        if fcntl is not None:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try: yield
        finally:
            if fcntl is not None: fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def _active_and_unexpired(claim: dict[str, Any], now: datetime) -> bool:
    return claim.get("status") == "ACTIVE" and _parse_time(claim["lease_expires_at"]) > now


def _event(event_log: Path | None, *, event_type: str, mission_id: str, actor: str, timestamp: str, payload: dict[str, Any]) -> str | None:
    if event_log is None: return None
    return append_payload(event_log, event_type=event_type, mission_id=mission_id, actor=actor, timestamp=timestamp, payload=payload)["event_id"]


def acquire(path: Path, *, work_id: str, mission_id: str, actor: str, lease_id: str, lease_expires_at: str, now: str | None = None, event_log: Path | None = None) -> dict[str, Any]:
    if not all((work_id, mission_id, actor, lease_id, lease_expires_at)):
        raise ValueError("Work claim identity and lease fields are required")
    current_time = _parse_time(now) if now else datetime.now(timezone.utc)
    expiry = _parse_time(lease_expires_at)
    if expiry <= current_time: raise ValueError("Lease must expire in the future")
    with _locked(path):
        data = load_claims(path); existing = data["claims"].get(work_id)
        if existing and _active_and_unexpired(existing, current_time): raise RuntimeError(f"Work {work_id} already has an active unexpired claim")
        history=[]
        if existing:
            terminal = dict(existing)
            if terminal.get("status") == "ACTIVE": terminal["status"] = "EXPIRED"; terminal["expired_at"] = now or utc_now()
            history.append(terminal)
        claim = {"work_id":work_id,"mission_id":mission_id,"actor":actor,"lease_id":lease_id,"status":"ACTIVE","acquired_at":now or utc_now(),"lease_expires_at":lease_expires_at}
        event_id=_event(event_log,event_type="WORK_CLAIM_ACQUIRED",mission_id=mission_id,actor=actor,timestamp=claim["acquired_at"],payload={"claim":claim,"expired_previous":history})
        if event_id: claim["mutation_event_id"]=event_id
        data["history"].extend(history); data["claims"][work_id]=claim; _atomic_write(path,data); return claim


def release(path: Path, *, work_id: str, actor: str, now: str | None = None, event_log: Path | None = None) -> dict[str, Any]:
    with _locked(path):
        data=load_claims(path); claim=data["claims"].get(work_id)
        if not claim or claim.get("status")!="ACTIVE": raise ValueError(f"No active claim for {work_id}")
        if claim.get("actor")!=actor: raise PermissionError("Only the claiming actor may release the claim")
        released={**claim,"status":"RELEASED","released_by":actor,"released_at":now or utc_now()}
        event_id=_event(event_log,event_type="WORK_CLAIM_RELEASED",mission_id=claim["mission_id"],actor=actor,timestamp=released["released_at"],payload={"claim":released})
        if event_id: released["mutation_event_id"]=event_id
        data["history"].append(released); data["claims"][work_id]=released; _atomic_write(path,data); return released
