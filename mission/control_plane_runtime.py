"""Runtime integration between control-plane decisions and persistent event lineage."""
from __future__ import annotations
from pathlib import Path
from typing import Any

from .control_plane import MissionState, transition
from .event_log import append_payload, validate_chain


def persist_transition(*, event_log: Path, current: MissionState, target: MissionState,
                       authorized_actor: str, evidence: list[str], timestamp: str,
                       mission_id: str | None = None, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Persist a state transition with explicit mission identity when supplied.

    Legacy callers may omit mission_id; the established authorized_actor identity
    is retained as the deterministic fallback rather than inventing a new identity.
    """
    record = transition(current, target, authorized_actor=authorized_actor, evidence=evidence)
    resolved_mission_id = mission_id or authorized_actor
    if not resolved_mission_id:
        raise ValueError("Mission identity is required for state-transition persistence")
    return append_payload(event_log, event_type="MISSION_STATE_TRANSITION", mission_id=resolved_mission_id,
                          actor=authorized_actor, timestamp=timestamp,
                          payload={**record, "payload": payload or {}})


def persist_handoff_event(*, event_log: Path, mission_id: str, actor: str, handoff_id: str,
                          status: str, evidence: list[str], timestamp: str) -> dict[str, Any]:
    return append_payload(event_log, event_type="HANDOFF_LIFECYCLE", mission_id=mission_id,
                          actor=actor, timestamp=timestamp,
                          payload={"handoff_id":handoff_id,"status":status,"evidence":evidence})


def replay_state(events: list[dict[str, Any]]) -> dict[str, str]:
    validate_chain(events)
    states: dict[str, str] = {}
    for event in events:
        if event["event_type"] != "MISSION_STATE_TRANSITION": continue
        payload=event["payload"]; source=MissionState(payload["from"]); target=MissionState(payload["to"])
        previous=MissionState(states[event["mission_id"]]) if event["mission_id"] in states else source
        if previous != source: raise ValueError(f"Replay divergence for {event['mission_id']}: expected {previous.value}, got {source.value}")
        states[event["mission_id"]]=target.value
    return states


def replay_projection(events: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    validate_chain(events)
    projections={"admissions":[],"retirements":[],"recoveries":[],"conflicts":[],"contributions":[],"claims":[],"handoffs":[]}
    mapping={"MISSION_ADMISSION":"admissions","MISSION_RETIREMENT":"retirements","MISSION_RECOVERY":"recoveries","MISSION_CONTRADICTION":"conflicts","MISSION_CONTRIBUTION":"contributions","WORK_CLAIM_ACQUIRED":"claims","WORK_CLAIM_RELEASED":"claims","HANDOFF_LIFECYCLE":"handoffs"}
    for event in events:
        target=mapping.get(event["event_type"])
        if target: projections[target].append({"event_id":event["event_id"],"payload":event["payload"]})
    return projections


def event_backed_mutation_types(events: list[dict[str, Any]]) -> set[str]:
    validate_chain(events)
    return {event["event_type"] for event in events if event["event_type"] in {"MISSION_STATE_TRANSITION","MISSION_ADMISSION","MISSION_RETIREMENT","MISSION_RECOVERY","MISSION_CONTRADICTION","MISSION_CONTRIBUTION","WORK_CLAIM_ACQUIRED","WORK_CLAIM_RELEASED","HANDOFF_LIFECYCLE"}}
