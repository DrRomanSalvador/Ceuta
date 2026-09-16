"""Persistent attribution ledger for cross-mission scientific contributions."""
from __future__ import annotations
import json
import os
import tempfile
from pathlib import Path
from typing import Any
from .shared_standard import validate_attribution
from .event_log import append_payload

REQUIRED = ("contribution_id", "mission_id", "artifact", "claim_or_change", "evidence", "timestamp")


def _write(path: Path, data: dict[str, Any]) -> None:
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


def record(path: Path, contribution: dict[str, Any], *, event_log: Path, actor: str) -> dict[str, Any]:
    missing = [field for field in REQUIRED if field not in contribution or contribution[field] in (None, "", [])]
    if missing:
        raise ValueError(f"Contribution missing required fields: {missing}")
    if not actor:
        raise ValueError("Contribution mutation requires actor")
    validate_attribution(contribution, require_authorization=True)
    if not contribution["evidence"]:
        raise ValueError("Contribution requires evidence")
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.setdefault("items", [])
    if any(x.get("contribution_id") == contribution["contribution_id"] for x in items):
        raise ValueError("Duplicate contribution_id")
    item = dict(contribution)
    event = append_payload(
        event_log,
        event_type="MISSION_CONTRIBUTION",
        mission_id=contribution["mission_id"],
        actor=actor,
        timestamp=contribution["timestamp"],
        payload=item,
    )
    item["mutation_event_id"] = event["event_id"]
    items.append(item)
    _write(path, data)
    return item
