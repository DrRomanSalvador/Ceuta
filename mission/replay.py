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
    lifecycle: list[dict[str, Any]] = field(default_factory=list)
    last_event_id: str | None = None
    last_hash: str = "0" * 64


def apply_event(state: ReplayState, event: dict[str, Any]) -> None:
    kind=event["event_type"]; payload=event["payload"]
    if kind == "CONTROL_PLANE_GENESIS":
        pass
    elif kind == "MISSION_ADMISSION":
        mission_id=event["mission_id"]
        state.missions[mission_id]={"mission_id":mission_id, **payload, "event_id":event["event_id"]}
    elif kind == "WORK_CLAIM_ACQUIRED":
        work_id=payload["work_id"]
        state.claims[work_id]={**payload,"status":"ACTIVE","event_id":event["event_id"]}
    elif kind == "WORK_CLAIM_RELEASED":
        work_id=payload["work_id"]
        if work_id not in state.claims: raise ValueError(f"Release references unknown claim: {work_id}")
        state.claims[work_id]={**state.claims[work_id],**payload,"status":"RELEASED","event_id":event["event_id"]}
    elif kind == "HANDOFF_STATE":
        handoff_id=payload["handoff_id"]
        state.handoffs[handoff_id]={**payload,"event_id":event["event_id"]}
    elif kind == "CONTRIBUTION_RECORDED":
        contribution_id=payload["contribution_id"]
        state.contributions[contribution_id]={**payload,"event_id":event["event_id"]}
    elif kind == "CONTRADICTION_RECORDED":
        contradiction_id=payload["contradiction_id"]
        state.contradictions[contradiction_id]={**payload,"event_id":event["event_id"]}
    elif kind.startswith("MISSION_LIFECYCLE_"):
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
