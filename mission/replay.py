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
    coordination: dict[str, Any] | None = None
    last_event_id: str | None = None
    last_hash: str = "0" * 64


def apply_event(state: ReplayState, event: dict[str, Any]) -> None:
    kind=event["event_type"]; payload=event["payload"]
    if kind == "CONTROL_PLANE_GENESIS": pass
    elif kind == "MISSION_ADMISSION":
        mission_id=event["mission_id"]; state.missions[mission_id]={"mission_id":mission_id,**payload,"event_id":event["event_id"]}
    elif kind == "MISSION_STATE_TRANSITION":
        mission_id=event["mission_id"]; state.missions.setdefault(mission_id,{"mission_id":mission_id})["status"]=payload["to"]; state.missions[mission_id]["event_id"]=event["event_id"]
    elif kind == "WORK_CLAIM_ACQUIRED":
        claim=payload.get("claim",payload); work_id=claim["work_id"]; state.claims[work_id]={**claim,"status":"ACTIVE","event_id":event["event_id"]}
    elif kind == "WORK_CLAIM_RELEASED":
        claim=payload.get("claim",payload); work_id=claim["work_id"]
        if work_id not in state.claims: raise ValueError(f"Release references unknown claim: {work_id}")
        state.claims[work_id]={**state.claims[work_id],**claim,"status":"RELEASED","event_id":event["event_id"]}
    elif kind in {"HANDOFF_STATE","HANDOFF_LIFECYCLE","HANDOFF_STATE_MIGRATION"}:
        handoff_id=payload["handoff_id"]; state.handoffs[handoff_id]={**state.handoffs.get(handoff_id,{}),**payload,"event_id":event["event_id"]}
    elif kind in {"CONTRIBUTION_RECORDED","MISSION_CONTRIBUTION"}:
        contribution_id=payload["contribution_id"]; state.contributions[contribution_id]={**payload,"event_id":event["event_id"]}
    elif kind in {"CONTRADICTION_RECORDED","MISSION_CONTRADICTION"}:
        contradiction_id=payload.get("contradiction_id",payload.get("conflict_id"))
        if contradiction_id is None: raise ValueError("Contradiction event has no identity")
        state.contradictions[contradiction_id]={**payload,"event_id":event["event_id"]}
    elif kind.startswith("MISSION_LIFECYCLE_") or kind in {"MISSION_RETIREMENT","MISSION_RECOVERY"}:
        state.lifecycle.append({**payload,"event_id":event["event_id"],"event_type":kind})
    elif kind.startswith("COORDINATOR_") or kind.startswith("MIRROR_") or kind in {"COORDINATION_CONFLICT","PAUSE_WITHOUT_CHECKPOINT_RISK","DEFERRED_HYPOTHESIS"}:
        coordination=payload.get("coordination_state")
        if not isinstance(coordination,dict): raise ValueError(f"Coordination event lacks replayable state: {kind}")
        state.coordination=coordination
    else:
        raise ValueError(f"Unknown replay event type: {kind}")
    state.last_event_id=event["event_id"]; state.last_hash=event["hash"]


def replay(path: Path) -> ReplayState:
    events=load_jsonl(path); validate_chain(events); state=ReplayState()
    for event in events: apply_event(state,event)
    return state


def assert_replay_deterministic(path: Path) -> None:
    first=replay(path); second=replay(path)
    if first!=second: raise AssertionError("Deterministic replay diverged across identical event streams")
