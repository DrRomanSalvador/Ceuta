"""Persistent work-claim/lease ledger for multi-mission coordination."""
from __future__ import annotations
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_claims(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": "1.0.0", "claims": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data.get("claims"), dict):
        raise ValueError("Invalid work-claim ledger")
    return data


def _atomic_write(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, sort_keys=True, indent=2, ensure_ascii=False)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass
        raise


def acquire(path: Path, *, work_id: str, mission_id: str, actor: str, lease_id: str, lease_expires_at: str) -> dict[str, Any]:
    data = load_claims(path)
    existing = data["claims"].get(work_id)
    if existing and existing.get("status") == "ACTIVE":
        raise RuntimeError(f"Work {work_id} already has an active claim")
    claim = {
        "work_id": work_id,
        "mission_id": mission_id,
        "actor": actor,
        "lease_id": lease_id,
        "status": "ACTIVE",
        "acquired_at": utc_now(),
        "lease_expires_at": lease_expires_at,
    }
    data["claims"][work_id] = claim
    _atomic_write(path, data)
    return claim


def release(path: Path, *, work_id: str, actor: str) -> dict[str, Any]:
    data = load_claims(path)
    claim = data["claims"].get(work_id)
    if not claim or claim.get("status") != "ACTIVE":
        raise ValueError(f"No active claim for {work_id}")
    if claim.get("actor") != actor:
        raise PermissionError("Only the claiming actor may release the claim")
    claim = {**claim, "status": "RELEASED", "released_by": actor, "released_at": utc_now()}
    data["claims"][work_id] = claim
    _atomic_write(path, data)
    return claim
