"""Deterministic replay/projection helpers for the control-plane event ledger."""
from __future__ import annotations
from typing import Any
from .event_log import validate_chain

HANDOFF_EVENT_TYPES={"HANDOFF_LIFECYCLE","HANDOFF_STATE_MIGRATION"}


def replay_events(events: list[dict[str, Any]]) -> dict[str, Any]:
    validate_chain(events)
    state={"mission_states":{},"admissions":{},"retirements":{},"recoveries":{},"conflicts":{},"contributions":{},"claims":{},"handoffs":{}}
    for event in events:
        typ=event["event_type"]; payload=event["payload"]
        if typ=="MISSION_STATE_TRANSITION":
            state["mission_states"][event["mission_id"]]=payload["to"]
        elif typ=="MISSION_ADMISSION":
            state["admissions"][event["mission_id"]]=payload
        elif typ=="MISSION_RETIREMENT":
            state["retirements"][event["mission_id"]]=payload
        elif typ=="MISSION_RECOVERY":
            state["recoveries"][event["mission_id"]]=payload
        elif typ=="MISSION_CONTRADICTION":
            state["conflicts"][payload["conflict_id"]]=payload
        elif typ=="MISSION_CONTRIBUTION":
            state["contributions"][payload["contribution_id"]]=payload
        elif typ in {"WORK_CLAIM_ACQUIRED","WORK_CLAIM_RELEASED"}:
            claim=payload.get("claim",payload)
            state["claims"][claim["work_id"]]=claim
        elif typ in HANDOFF_EVENT_TYPES:
            state["handoffs"][payload["handoff_id"]]=payload
    return state


def replay_projection(events: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    validate_chain(events)
    projections={"admissions":[],"retirements":[],"recoveries":[],"conflicts":[],"contributions":[],"claims":[],"handoffs":[]}
    mapping={"MISSION_ADMISSION":"admissions","MISSION_RETIREMENT":"retirements","MISSION_RECOVERY":"recoveries","MISSION_CONTRADICTION":"conflicts","MISSION_CONTRIBUTION":"contributions","WORK_CLAIM_ACQUIRED":"claims","WORK_CLAIM_RELEASED":"claims","HANDOFF_LIFECYCLE":"handoffs","HANDOFF_STATE_MIGRATION":"handoffs"}
    for event in events:
        target=mapping.get(event["event_type"])
        if target: projections[target].append({"event_id":event["event_id"],"payload":event["payload"]})
    return projections


def assert_replay_deterministic(events: list[dict[str, Any]]) -> None:
    first=replay_events(events); second=replay_events(events)
    if first!=second: raise AssertionError("Deterministic replay diverged across identical event streams")
