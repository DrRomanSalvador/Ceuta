from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from .founder_domain import FounderDomainError

HANDOFF_STATES = ("DRAFT", "SENT", "ACK", "ACCEPT", "REJECT", "RESULT", "VERIFIED")
_HANDOFF_NEXT = {
    "DRAFT": {"SENT"},
    "SENT": {"ACK"},
    "ACK": {"ACCEPT", "REJECT"},
    "ACCEPT": {"RESULT"},
    "REJECT": {"RESULT"},
    "RESULT": {"VERIFIED"},
    "VERIFIED": set(),
}


@dataclass(frozen=True, slots=True)
class HandoffRecord:
    handoff_id: str
    source_mission: str
    target_mission: str
    state: str
    operational_object: str
    engineering_object: str
    current_state: str
    desired_state: str
    repository_location: str
    schema_change: str
    code_change: str
    dependencies: tuple[str, ...]
    tests: tuple[str, ...]
    acceptance_criteria: tuple[str, ...]
    failure_criteria: tuple[str, ...]
    validation_requirements: tuple[str, ...]
    persistence_requirements: tuple[str, ...]
    next_action: str

    def transition(self, target: str) -> "HandoffRecord":
        if self.state not in HANDOFF_STATES or target not in HANDOFF_STATES:
            raise FounderDomainError("UNKNOWN_HANDOFF_STATE")
        if target not in _HANDOFF_NEXT[self.state]:
            raise FounderDomainError("FORBIDDEN_HANDOFF_TRANSITION")
        return HandoffRecord(**{**self.__dict__, "state": target}) if hasattr(self, "__dict__") else HandoffRecord(
            self.handoff_id, self.source_mission, self.target_mission, target, self.operational_object,
            self.engineering_object, self.current_state, self.desired_state, self.repository_location,
            self.schema_change, self.code_change, self.dependencies, self.tests, self.acceptance_criteria,
            self.failure_criteria, self.validation_requirements, self.persistence_requirements, self.next_action)

    def validate(self) -> None:
        if self.state not in HANDOFF_STATES:
            raise FounderDomainError("UNKNOWN_HANDOFF_STATE")
        required = (self.handoff_id, self.source_mission, self.target_mission, self.operational_object,
                    self.engineering_object, self.current_state, self.desired_state, self.repository_location,
                    self.schema_change, self.code_change, self.next_action)
        if any(not value.strip() for value in required):
            raise FounderDomainError("HANDOFF_REQUIRED_FIELD_MISSING")
        if self.state == "VERIFIED" and (not self.validation_requirements or not self.persistence_requirements):
            raise FounderDomainError("VERIFIED_HANDOFF_REQUIRES_VALIDATION_AND_PERSISTENCE")


@dataclass(frozen=True, slots=True)
class FixedPointCertificate:
    certificate_id: str
    scope: str
    state_version: str
    no_executable_work: bool
    no_repairs: bool
    no_regressions: bool
    no_pending_integrations: bool
    persistence_consistent: bool
    recovery_verified: bool
    evidence_refs: tuple[str, ...]
    external_boundaries: tuple[str, ...]

    def is_valid(self) -> bool:
        if self.scope not in {"FOUNDER_LOCAL_FIXED_POINT", "MISSION_FIXED_POINT", "GLOBAL_SYSTEM_FIXED_POINT"}:
            raise FounderDomainError("UNKNOWN_FIXED_POINT_SCOPE")
        return all((self.no_executable_work, self.no_repairs, self.no_regressions, self.no_pending_integrations, self.persistence_consistent, self.recovery_verified)) and bool(self.evidence_refs)


def can_retire(current: str, *, history_preserved: bool, replacement_or_reason: str) -> bool:
    if current not in {"ACTIVE", "PAUSED", "SUPERSEDED"}:
        raise FounderDomainError("INVALID_RETIREMENT_SOURCE_STATE")
    if not history_preserved or not replacement_or_reason.strip():
        raise FounderDomainError("RETIREMENT_REQUIRES_HISTORY_AND_REASON")
    return True


def validate_fixed_point_hierarchy(founder: FixedPointCertificate, mission: FixedPointCertificate | None, global_system: FixedPointCertificate | None) -> Mapping[str, bool]:
    founder_ok = founder.scope == "FOUNDER_LOCAL_FIXED_POINT" and founder.is_valid()
    mission_ok = mission is not None and mission.scope == "MISSION_FIXED_POINT" and mission.is_valid()
    global_ok = global_system is not None and global_system.scope == "GLOBAL_SYSTEM_FIXED_POINT" and global_system.is_valid()
    return {"FOUNDER_LOCAL_FIXED_POINT": founder_ok, "MISSION_FIXED_POINT": mission_ok, "GLOBAL_SYSTEM_FIXED_POINT": global_ok}
