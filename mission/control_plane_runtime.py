"""Runtime integration between control-plane decisions and persistent event lineage."""
from __future__ import annotations
from pathlib import Path
from typing import Any

from .control_plane import MissionState, transition
from .event_log import append_event, load_jsonl, make_event, validate_chain


def _next_event_id(events: list[dict[str, Any]]) -> str:
    return f"EV-{len(events) + 1:04d}"


def persist_transition(*, event_log: Path, current: MissionState, target: MissionState,
                       authorized_actor: str, evidence: list[str], payload: dict[str, Any] | None = None,
                       timestamp: str) -> dict[str, Any]:
    record = transition(current, target, authorized_actor=authorized_actor, evidence=evidence)
    events = load_jsonl(event_log)
    previous = validate_chain(events)
    event = make_event(
        event_id=_next_event_id(events),
        event_type="MISSION_STATE_TRANSITION",
        mission_id=authorized_actor,
        actor=authorized_actor,
        timestamp=timestamp,
        payload={**record, "payload": payload or {}},
        previous_hash=previous,
    )
    append_event(event_log, event)
    return event


def persist_handoff_event(*, event_log: Path, mission_id: str, actor: str, handoff_id: str,
                          status: str, evidence: list[str], timestamp: str) -> dict[str, Any]:
    events = load_jsonl(event_log)
    previous = validate_chain(events)
    event = make_event(
        event_id=_next_event_id(events),
        event_type="HANDOFF_LIFECYCLE",
        mission_id=mission_id,
        actor=actor,
        timestamp=timestamp,
        payload={"handoff_id": handoff_id, "status": status, "evidence": evidence},
        previous_hash=previous,
    )
    append_event(event_log, event)
    return event


def replay_state(events: list[dict[str, Any]]) -> dict[str, str]:
    """Reconstruct mission states from transition events; fail closed on illegal replay."""
    validate_chain(events)
    states: dict[str, str] = {}
    for event in events:
        if event["event_type"] != "MISSION_STATE_TRANSITION":
            continue
        payload = event["payload"]
        source = payload["from"]
        target = MissionState(payload["to"])
        previous = MissionState(states[event["mission_id"]]) if event["mission_id"] in states else MissionState(source)
        if previous != MissionState(source):
            raise ValueError(f"Replay divergence for {event['mission_id']}: expected {previous.value}, got {source}")
        states[event["mission_id"]] = target.value
    return states
