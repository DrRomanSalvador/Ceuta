"""Authorized downstream action boundary for decision outputs."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
from typing import Mapping, Protocol

from app.core.decision.control_plane import DecisionAuditChain
from app.core.decision.information_boundary import InformationVisibility
from .decision_lifecycle import DecisionLifecycleResult


class ActionStatus(StrEnum):
    PROPOSED = "proposed"
    BLOCKED = "blocked"
    EXECUTED = "executed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True, slots=True)
class ActionRequest:
    action_id: str
    decision_id: str
    option_id: str
    target: str
    parameters: Mapping[str, object]
    requested_at: datetime
    valid_until: datetime | None
    visibility: InformationVisibility
    status: ActionStatus = ActionStatus.PROPOSED

    def __post_init__(self) -> None:
        if not self.action_id or not self.decision_id or not self.option_id or not self.target:
            raise ValueError("action request requires identity and target")
        if self.requested_at.tzinfo is None or self.requested_at.utcoffset() is None:
            raise ValueError("requested_at must be timezone-aware")
        if self.valid_until is not None and self.valid_until <= self.requested_at:
            raise ValueError("valid_until must be after requested_at")


class ActionExecutor(Protocol):
    def execute(self, action: ActionRequest) -> ActionRequest: ...


class DecisionActionGateway:
    """Converts only authorized recommendations into traceable action requests."""

    def __init__(self, audit: DecisionAuditChain) -> None:
        self.audit = audit

    def propose(
        self,
        result: DecisionLifecycleResult,
        *,
        target: str,
        parameters: Mapping[str, object] = (),
        visibility: InformationVisibility = InformationVisibility.RESTRICTED,
        actor_authorized: bool = False,
        valid_until: datetime | None = None,
    ) -> ActionRequest:
        now = datetime.now(timezone.utc)
        if result.disposition.value != "recommend":
            raise PermissionError("only an authorized recommendation can produce a downstream action")
        if not actor_authorized:
            raise PermissionError("downstream action requires explicit actor/system authorization")
        action = ActionRequest(
            action_id=f"action:{result.decision_id}:{result.recommendation.option_id}",
            decision_id=result.decision_id,
            option_id=result.recommendation.option_id,
            target=target,
            parameters=dict(parameters),
            requested_at=now,
            valid_until=valid_until,
            visibility=visibility,
        )
        self.audit.append(result.decision_id, "action_proposed", {
            "action_id": action.action_id,
            "option_id": action.option_id,
            "target": action.target,
            "visibility": action.visibility.value,
            "status": action.status.value,
        })
        return action


__all__ = ["ActionExecutor", "ActionRequest", "ActionStatus", "DecisionActionGateway"]
