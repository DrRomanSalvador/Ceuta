"""Atomic per-mission compare-and-swap for materialized control-plane projections."""
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

@contextmanager
def _locked(path:Path)->Iterator[None]:
    lock_path=path.with_suffix(path.suffix+".lock"); lock_path.parent.mkdir(parents=True,exist_ok=True)
    with lock_path.open("a+",encoding="utf-8") as lock:
        if fcntl is not None: fcntl.flock(lock.fileno(),fcntl.LOCK_EX)
        try: yield
        finally:
            if fcntl is not None: fcntl.flock(lock.fileno(),fcntl.LOCK_UN)

def _load(path:Path)->dict[str,Any]:
    if not path.exists(): return {"schema_version":"1.0.0","missions":{}}
    data=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data.get("missions"),dict): raise ValueError("Invalid materialized state registry")
    return data

def _atomic_write(path:Path,data:dict[str,Any])->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=f".{path.name}.",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as handle:
            json.dump(data,handle,sort_keys=True,indent=2,ensure_ascii=False); handle.write("\n"); handle.flush(); os.fsync(handle.fileno())
        os.replace(tmp,path)
    except Exception:
        try: os.unlink(tmp)
        except FileNotFoundError: pass
        raise

def read_mission(path:Path,mission_id:str)->dict[str,Any]:
    data=_load(path); record=data["missions"].get(mission_id)
    if record is None: return {"mission_id":mission_id,"revision":0,"projection":{}}
    return dict(record)

def compare_and_swap_mission(path:Path,mission_id:str,expected_revision:int,new_projection:dict[str,Any])->dict[str,Any]:
    if not mission_id: raise ValueError("mission_id is required")
    if expected_revision<0: raise ValueError("expected_revision cannot be negative")
    with _locked(path):
        data=_load(path); current=data["missions"].get(mission_id,{"mission_id":mission_id,"revision":0,"projection":{}})
        if current["revision"]!=expected_revision:
            raise ValueError(f"Stale materialized-state writer for {mission_id}: expected revision {expected_revision}, current {current['revision']}")
        updated={"mission_id":mission_id,"revision":expected_revision+1,"projection":dict(new_projection)}
        data["missions"][mission_id]=updated; _atomic_write(path,data); return updated
