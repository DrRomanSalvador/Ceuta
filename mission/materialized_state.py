"""Atomic event-backed compare-and-swap for materialized control-plane projections."""
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

from .event_log import append_payload, load_jsonl, validate_chain


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


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"schema_version": "1.1.0", "missions": {}}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data.get("missions"), dict):
        raise ValueError("Invalid materialized state registry")
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


def read_mission(path: Path, mission_id: str) -> dict[str, Any]:
    data = _load(path)
    record = data["missions"].get(mission_id)
    if record is None:
        return {"mission_id": mission_id, "revision": 0, "projection": {}}
    return dict(record)


def _recover_projection_from_events(event_log: Path) -> dict[str, dict[str, Any]]:
    events = load_jsonl(event_log)
    validate_chain(events)
    missions: dict[str, dict[str, Any]] = {}
    for event in events:
        if event["event_type"] != "MATERIALIZED_STATE_CAS":
            continue
        mission_id = event["mission_id"]
        payload = event["payload"]
        expected = payload["expected_revision"]
        new_revision = payload["new_revision"]
        current_revision = missions.get(mission_id, {"revision": 0})["revision"]
        if expected != current_revision or new_revision != expected + 1:
            raise ValueError(f"Materialized-state recovery revision divergence for {mission_id}")
        missions[mission_id] = {
            "mission_id": mission_id,
            "revision": new_revision,
            "projection": dict(payload["projection"]),
            "mutation_event_id": event["event_id"],
        }
    return missions


def _matching_persisted_mutation(
    event_log: Path,
    *,
    mission_id: str,
    expected_revision: int,
    new_projection: dict[str, Any],
    actor: str,
    timestamp: str,
) -> dict[str, Any] | None:
    """Return an already-persisted mutation when the retry is byte-semantically equivalent."""
    if not event_log.exists():
        return None
    for event in load_jsonl(event_log):
        if event["event_type"] != "MATERIALIZED_STATE_CAS" or event["mission_id"] != mission_id:
            continue
        payload = event["payload"]
        if (
            event["actor"] == actor
            and event["timestamp"] == timestamp
            and payload["expected_revision"] == expected_revision
            and payload["new_revision"] == expected_revision + 1
            and payload["projection"] == dict(new_projection)
        ):
            return {
                "mission_id": mission_id,
                "revision": payload["new_revision"],
                "projection": dict(payload["projection"]),
                "mutation_event_id": event["event_id"],
            }
    return None


def compare_and_swap_mission(
    path: Path,
    mission_id: str,
    expected_revision: int,
    new_projection: dict[str, Any],
    *,
    event_log: Path,
    actor: str,
    timestamp: str,
) -> dict[str, Any]:
    """Apply one canonical event-backed materialized-state mutation.

    The event is the source of truth. If the event was durably appended but the
    projection write was interrupted, an identical retry reuses that event and
    repairs the projection instead of allocating a second mutation.
    """
    if not mission_id:
        raise ValueError("mission_id is required")
    if expected_revision < 0:
        raise ValueError("expected_revision cannot be negative")
    if not actor:
        raise ValueError("actor is required")
    if not timestamp:
        raise ValueError("timestamp is required")

    with _locked(path):
        data = _load(path)
        recovered = _recover_projection_from_events(event_log) if event_log.exists() else {}
        if recovered:
            data["missions"].update(recovered)

        current = data["missions"].get(
            mission_id,
            {"mission_id": mission_id, "revision": 0, "projection": {}},
        )
        if current["revision"] != expected_revision:
            persisted = _matching_persisted_mutation(
                event_log,
                mission_id=mission_id,
                expected_revision=expected_revision,
                new_projection=new_projection,
                actor=actor,
                timestamp=timestamp,
            )
            if persisted is None:
                raise ValueError(
                    f"Stale materialized-state writer for {mission_id}: "
                    f"expected {expected_revision}, current {current['revision']}"
                )
            data["missions"][mission_id] = persisted
            _atomic_write(path, data)
            return persisted

        new_revision = expected_revision + 1
        event = append_payload(
            event_log,
            event_type="MATERIALIZED_STATE_CAS",
            mission_id=mission_id,
            actor=actor,
            timestamp=timestamp,
            payload={
                "expected_revision": expected_revision,
                "new_revision": new_revision,
                "projection": dict(new_projection),
            },
        )
        updated = {
            "mission_id": mission_id,
            "revision": new_revision,
            "projection": dict(new_projection),
            "mutation_event_id": event["event_id"],
        }
        data["missions"][mission_id] = updated
        _atomic_write(path, data)
        return updated


def recover_materialized_state(path: Path, event_log: Path) -> dict[str, Any]:
    """Rebuild materialized state from canonical CAS events."""
    recovered = {"schema_version": "1.1.0", "missions": _recover_projection_from_events(event_log)}
    _atomic_write(path, recovered)
    return recovered
