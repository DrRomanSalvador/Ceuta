"""Append-only, hash-chained control-plane event log primitives."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from typing import Any

GENESIS_HASH = "0" * 64


def canonical_event(event: dict[str, Any]) -> bytes:
    return json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def event_hash(event: dict[str, Any], previous_hash: str) -> str:
    payload = previous_hash.encode("ascii") + b"\n" + canonical_event(event)
    return hashlib.sha256(payload).hexdigest()


def make_event(*, event_id: str, event_type: str, mission_id: str, actor: str,
               timestamp: str, payload: dict[str, Any], previous_hash: str = GENESIS_HASH) -> dict[str, Any]:
    if not all((event_id, event_type, mission_id, actor, timestamp)):
        raise ValueError("Event identity fields are required")
    if len(previous_hash) != 64:
        raise ValueError("previous_hash must be a SHA-256 hex digest")
    body = {"event_id":event_id,"event_type":event_type,"mission_id":mission_id,"actor":actor,"timestamp":timestamp,"payload":payload}
    return {**body,"previous_hash":previous_hash,"hash":event_hash(body, previous_hash)}


def validate_chain(events: list[dict[str, Any]]) -> str:
    previous = GENESIS_HASH
    seen: set[str] = set()
    for index, event in enumerate(events):
        required={"event_id","event_type","mission_id","actor","timestamp","payload","previous_hash","hash"}
        missing=required-set(event)
        if missing: raise ValueError(f"Event {index} missing fields: {sorted(missing)}")
        if event["event_id"] in seen: raise ValueError(f"Duplicate event_id: {event['event_id']}")
        seen.add(event["event_id"])
        if event["previous_hash"] != previous: raise ValueError(f"Broken event chain at index {index}")
        body={k:event[k] for k in ("event_id","event_type","mission_id","actor","timestamp","payload")}
        expected=event_hash(body, previous)
        if event["hash"] != expected: raise ValueError(f"Invalid event hash at index {index}")
        previous=event["hash"]
    return previous


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists(): return []
    events=[]
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip(): events.append(json.loads(line))
    return events


def append_event(path: Path, event: dict[str, Any]) -> str:
    events=load_jsonl(path)
    last=validate_chain(events)
    if event["previous_hash"] != last: raise ValueError("Event does not extend current chain")
    validate_chain(events+[event])
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
    return event["hash"]
