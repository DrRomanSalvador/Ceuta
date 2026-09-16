"""Deterministic zero-context replay of the control-plane event stream."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from .event_log import load_jsonl, validate_chain

@dataclass
class ReplayState:
    missions: dict[str, dict[str, Any]] = field(default_factory=dict)
    claims: dict[str, dict[str, Any]] = field(default_factory=dict)
    handoffs: dict[str, dict[str, Any]] = field(default_factory=dict)
    contributions: dict[str, dict[str, Any]] = field(default_factory=dict)
    contradictions: dict[str, dict[str, Any]] = field(default_factory=dict)
    responses: dict[str, dict[str, Any]] = field(default_factory=dict)
    materialized_state: dict[str, dict[str, Any]] = field(default_factory=dict)
    lifecycle: list[dict[str, Any]] = field(default_factory=list)
    mission_states: dict[str, str] = field(default_factory=dict)
    last_event_id: str | None = None
    last_hash: str = "0" * 64


def _payload_record(payload: dict[str, Any]) -> dict[str, Any]:
    record = payload.get("claim") if isinstance(payload.get("claim"), dict) else payload
    return dict(record)


def apply_event(state: ReplayState, event: dict[str, Any]) -> None:
    kind=event["event_type"]; payload=event["payload"]
    if kind == "CONTROL_PLANE_GENESIS":
        pass
    elif kind == "MISSION_ADMISSION":
        mission_id=event["mission_id"]
        state.missions[mission_id]={"mission_id":mission_id, **payload, "event_id":event["event_id"]}
    elif kind == "MISSION_STATE_TRANSITION":
        mission_id=event["mission_id"]
        source=payload["from"]; target=payload["to"]
        previous=state.mission_states.get(mission_id, source)
        if previous != source: raise ValueError(f"Replay divergence for {mission_id}: expected {previous}, got {source}")
        state.mission_states[mission_id]=target
    elif kind == "WORK_CLAIM_ACQUIRED":
        record=_payload_record(payload); work_id=record["work_id"]
        state.claims[work_id]={**record,"status":"ACTIVE","event_id":event["event_id"]}
    elif kind == "WORK_CLAIM_RELEASED":
        record=_payload_record(payload); work_id=record["work_id"]
        if work_id not in state.claims: raise ValueError(f"Release references unknown claim: {work_id}")
        state.claims[work_id]={**state.claims[work_id],**record,"status":"RELEASED","event_id":event["event_id"]}
    elif kind in {"HANDOFF_LIFECYCLE", "HANDOFF_STATE"}:
        handoff_id=payload["handoff_id"]
        state.handoffs[handoff_id]={**payload,"event_id":event["event_id"]}
    elif kind in {"MISSION_CONTRIBUTION", "CONTRIBUTION_RECORDED"}:
        contribution_id=payload["contribution_id"]
        state.contributions[contribution_id]={**payload,"event_id":event["event_id"]}
    elif kind in {"MISSION_CONTRADICTION", "CONTRADICTION_RECORDED"}:
        contradiction_id=payload["conflict_id"] if "conflict_id" in payload else payload["contradiction_id"]
        state.contradictions[contradiction_id]={**payload,"event_id":event["event_id"]}
    elif kind == "RESPONSE_COUPLING_RECORDED":
        response_id=payload["response_id"]
        if response_id in state.responses: raise ValueError(f"Duplicate response replay: {response_id}")
        state.responses[response_id]={**payload,"event_id":event["event_id"]}
    elif kind == "MATERIALIZED_STATE_CAS":
        mission_id=event["mission_id"]
        expected=payload["expected_revision"]
        new_revision=payload["new_revision"]
        previous=state.materialized_state.get(mission_id,{"revision":0})
        if previous["revision"] != expected:
            raise ValueError(f"Materialized-state replay divergence for {mission_id}: expected {previous['revision']}, got {expected}")
        if new_revision != expected + 1:
            raise ValueError(f"Invalid materialized-state revision transition for {mission_id}")
        state.materialized_state[mission_id]={"revision":new_revision,"projection":dict(payload["projection"]),"event_id":event["event_id"]}
    elif kind.startswith("MISSION_LIFECYCLE_") or kind in {"MISSION_RETIREMENT", "MISSION_RECOVERY"}:
        state.lifecycle.append({**payload,"event_id":event["event_id"],"event_type":kind})
    else:
        raise ValueError(f"Unknown replay event type: {kind}")
    state.last_event_id=event["event_id"]; state.last_hash=event["hash"]


def replay(path: Path) -> ReplayState:
    events=load_jsonl(path)
    validate_chain(events)
    state=ReplayState()
    for event in events: apply_event(state,event)
    return state
