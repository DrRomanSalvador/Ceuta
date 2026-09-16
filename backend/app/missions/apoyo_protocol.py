from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

APOYO_REPLICATION_REQUIREMENT = "INFINITE_CONTINUITY"
MEETING_POINT_COVERAGE_REQUIRED = True
MINIMUM_READY_SUPPORT_INSTANCES = 1
MEETING_POINT_ID = "APOYO-MEETING-POINT"
INGENIERO_MISSION_ID = "MISSION-01"
INGENIERO_NAME = "INGENIERO"
ROMAN_NAME = "ROMÁN"

NON_INTRUSIVE_STATES = {
    "IDLE",
    "WAITING",
    "WAITING_FOR_INSTRUCTION",
    "CHECKPOINT",
    "NATURAL_RETURN",
    "TASK_TRANSITION",
    "SAFE_PAUSE",
}
OCCUPIED_STATES = {
    "EXECUTING",
    "RUNNING",
    "WRITING",
    "TESTING",
    "DEBUGGING",
    "MERGING",
    "ANALYZING",
    "PROCESSING",
}
ACTIVE_STATES = {
    "ACTIVE",
    "WORKING",
    "INVOKED",
    "ASSISTING",
    "RUNNING",
    "WAITING_FOR_INSTRUCTION",
    "CHECKPOINT",
}


@dataclass(frozen=True, slots=True)
class GreetingDecision:
    target: str
    allowed: bool
    reason: str


def greeting_window(activity: str, state: str) -> GreetingDecision:
    """Decide whether a greeting can occur without treating contact as a task takeover."""
    activity_u = activity.strip().upper()
    state_u = state.strip().upper()
    if state_u in NON_INTRUSIVE_STATES or activity_u in NON_INTRUSIVE_STATES:
        return GreetingDecision(target="", allowed=True, reason="NON_INTRUSIVE_WINDOW")
    if state_u in OCCUPIED_STATES or activity_u in OCCUPIED_STATES:
        return GreetingDecision(target="", allowed=False, reason="OCCUPIED_AGENT")
    return GreetingDecision(target="", allowed=False, reason="WINDOW_NOT_ESTABLISHED")


def completion_blocked_by_agents(agents: Iterable[Mapping[str, str]], *, roman_active: bool = False) -> bool:
    """Return True whenever any relevant active agent prevents APOYO completion."""
    if roman_active:
        return True
    return any(str(agent.get("state", "")).upper() in ACTIVE_STATES for agent in agents)


def assign_support_task(*, task_id: str, owner: str, existing_claims: Mapping[str, str]) -> None:
    """Fail closed if a task is already claimed by another APOYO instance."""
    if not task_id.strip() or not owner.strip():
        raise ValueError("TASK_ID_AND_OWNER_REQUIRED")
    claimant = existing_claims.get(task_id)
    if claimant and claimant != owner:
        raise ValueError("DUPLICATE_SUPPORT_TASK")


def successor_exit_allowed(*, successor_verified: bool, state_transferred: bool, coverage_verified: bool) -> bool:
    return successor_verified and state_transferred and coverage_verified
