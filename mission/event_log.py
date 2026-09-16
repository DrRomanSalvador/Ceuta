"""Append-only, hash-chained control-plane event log primitives."""
from __future__ import annotations
import hashlib
import json
import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

try:
    import fcntl
except ImportError:  # pragma: no cover - Windows fallback
    fcntl = None

GENESIS_HASH = "0" * 64


def canonical_event(event: dict[str, Any]) -> bytes:
    return json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def event_hash(event: dict[str, Any], previous_hash: str) -> str:
    payload = previous_hash.encode("ascii") + b"\n" + canonical_event(event)
    return hashlib.sha256(payload).hexdigest()


def make_event(
    *,
    event_id: str,
    event_type: str,
    mission_id: str,
    actor: str,
    timestamp: str,
    payload: dict[str, Any],
    previous_hash: str = GENESIS_HASH,
) -> dict[str, Any]:
    if not all((event_id, event_type, mission_id, actor, timestamp)):
        raise ValueError("Event identity fields are required")
    if len(previous_hash) != 64:
        raise ValueError("previous_hash must be a SHA-256 hex digest")
    body = {
        "event_id": event_id,
        "event_type": event_type,
        "mission_id": mission_id,
        "actor": actor,
        "timestamp": timestamp,
        "payload": payload,
    }
    return {**body, "previous_hash": previous_hash, "hash": event_hash(body, previous_hash)}


def validate_chain(events: list[dict[str, Any]]) -> str:
    previous = GENESIS_HASH
    seen: set[str] = set()
    for index, event in enumerate(events):
        required = {
            "event_id",
            "event_type",
            "mission_id",
            "actor",
            "timestamp",
            "payload",
            "previous_hash",
            "hash",
        }
        missing = required - set(event)
        if missing:
            raise ValueError(f"Event {index} missing fields: {sorted(missing)}")
        if event["event_id"] in seen:
            raise ValueError(f"Duplicate event_id: {event['event_id']}")
        seen.add(event["event_id"])
        if event["previous_hash"] != previous:
            raise ValueError(f"Broken event chain at index {index}")
        body = {k: event[k] for k in ("event_id", "event_type", "mission_id", "actor", "timestamp", "payload")}
        expected = event_hash(body, previous)
        if event["hash"] != expected:
            raise ValueError(f"Invalid event hash at index {index}")
        previous = event["hash"]
    return previous


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


@contextmanager
def _locked(path: Path) -> Iterator[None]:
    lock_path = path.with_suffix(path.suffix + ".lock")
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    with lock_path.open("a+", encoding="utf-8") as lock:
        if fcntl is not None:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            yield
        finally:
            if fcntl is not None:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


def _durable_append(path: Path, event: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True, separators=(",", ":"), ensure_ascii=False) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def append_event(path: Path, event: dict[str, Any]) -> str:
    with _locked(path):
        events = load_jsonl(path)
        last = validate_chain(events)
        if event["previous_hash"] != last:
            raise ValueError("Event does not extend current chain; caller must reload and retry")
        validate_chain(events + [event])
        _durable_append(path, event)
        return event["hash"]


def append_payload(
    path: Path,
    *,
    event_type: str,
    mission_id: str,
    actor: str,
    timestamp: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Create and durably append a transition event atomically under the log lock."""
    with _locked(path):
        events = load_jsonl(path)
        previous = validate_chain(events)
        event_id = f"EV-{len(events) + 1:04d}"
        if any(event["event_id"] == event_id for event in events):
            raise ValueError("Event ID collision; chain must be reconciled")
        event = make_event(
            event_id=event_id,
            event_type=event_type,
            mission_id=mission_id,
            actor=actor,
            timestamp=timestamp,
            payload=payload,
            previous_hash=previous,
        )
        validate_chain(events + [event])
        _durable_append(path, event)
        return event
