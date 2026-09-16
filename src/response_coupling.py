"""Explicit warning-to-response binding without inventing decision semantics.

The existing alert path produces prediction/notification data only. This module
provides the narrow integration contract needed to bind an emitted Alert to a
real response record when an external decision/action producer supplies the
canonical identities and execution evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Optional

EXECUTION_STATES = {"NO_RESPONSE", "EXECUTED", "DELAYED_OUTSIDE_WINDOW", "NOT_EXECUTED"}
CAUSAL_STATUSES = {"NOT_ASSESSED", "DESCRIPTIVE_ONLY", "IDENTIFICATION_INSUFFICIENT", "IDENTIFICATION_SUPPORTED"}
COUNTERFACTUAL_STATUSES = {"ABSENT", "UNDEFINED", "INSUFFICIENT", "SUPPORTED"}

@dataclass(frozen=True)
class ResponseBinding:
    response_id: str
    prediction_identity: str
    decision_identity: Optional[str]
    decision_time: Optional[str]
    action_identity: Optional[str]
    execution_time: Optional[str]
    responsible_actor: str
    response_eligibility: Mapping[str, Any]
    intended_mechanism: Optional[str]
    response_delay: Optional[float]
    intervention_exposure_intensity: Any
    implementation_failure: Any
    resource_capacity_constraints: Any
    outcome_ascertainment_identity: Optional[str]
    response_horizon: Optional[str]
    counterfactual_causal_status: str
    execution_status: str
    causal_status: str

    def validate(self) -> None:
        if not self.response_id:
            raise ValueError("response_id is required")
        if not self.prediction_identity:
            raise ValueError("prediction_identity is required")
        if not self.responsible_actor:
            raise ValueError("responsible_actor is required")
        if self.execution_status not in EXECUTION_STATES:
            raise ValueError("Unknown execution status")
        if self.causal_status not in CAUSAL_STATUSES:
            raise ValueError("Unknown causal status")
        if self.counterfactual_causal_status not in COUNTERFACTUAL_STATUSES:
            raise ValueError("Unknown counterfactual status")
        if self.decision_identity and not self.decision_time:
            raise ValueError("decision_time is required when decision_identity is supplied")
        if self.action_identity and not self.execution_time:
            raise ValueError("execution_time is required when action_identity is supplied")
        if self.execution_time and not self.action_identity:
            raise ValueError("action_identity is required when execution_time is supplied")
        if self.execution_status in {"EXECUTED", "DELAYED_OUTSIDE_WINDOW"}:
            if not self.action_identity or not self.execution_time:
                raise ValueError("Executed response requires action identity and execution time")
            if self.response_delay is None:
                raise ValueError("Executed response requires response delay")
        if self.execution_status == "NO_RESPONSE" and self.action_identity:
            raise ValueError("action_identity cannot be supplied for NO_RESPONSE")
        if self.causal_status == "IDENTIFICATION_SUPPORTED":
            if self.counterfactual_causal_status != "SUPPORTED":
                raise ValueError("Causal effectiveness requires supported counterfactual status")
            if not self.outcome_ascertainment_identity:
                raise ValueError("Causal effectiveness requires outcome ascertainment identity")
            if self.intervention_exposure_intensity is None:
                raise ValueError("Causal effectiveness requires intervention exposure/intensity")
            if not self.response_horizon:
                raise ValueError("Causal effectiveness requires a predeclared response horizon")

    def to_record(self, *, mission_id: str, alert: Any) -> dict[str, Any]:
        if not mission_id:
            raise ValueError("mission_id is required")
        self.validate()
        return {
            "mission_id": mission_id,
            "response_id": self.response_id,
            "warning_presence": "PRESENT",
            "warning_or_prediction_identity": self.prediction_identity,
            "decision_identity": self.decision_identity,
            "decision_time": self.decision_time,
            "action_identity": self.action_identity,
            "execution_time": self.execution_time,
            "responsible_actor": self.responsible_actor,
            "response_eligibility": dict(self.response_eligibility),
            "intended_mechanism": self.intended_mechanism,
            "response_delay": self.response_delay,
            "intervention_exposure_intensity": self.intervention_exposure_intensity,
            "implementation_failure": self.implementation_failure,
            "resource_capacity_constraints": self.resource_capacity_constraints,
            "outcome_ascertainment_identity": self.outcome_ascertainment_identity,
            "response_horizon": self.response_horizon,
            "counterfactual_causal_status": self.counterfactual_causal_status,
            "execution_status": self.execution_status,
            "causal_status": self.causal_status,
            "warning_audit_hash": alert.audit_hash,
            "warning_timestamp": alert.timestamp,
        }

class ResponseCouplingSink:
    def __init__(self, writer: Callable[..., dict[str, Any]], mission_id: str):
        if not callable(writer):
            raise TypeError("writer must be callable")
        if not mission_id:
            raise ValueError("mission_id is required")
        self._writer = writer
        self.mission_id = mission_id

    def record(self, alert: Any, binding: ResponseBinding, *, actor: str, timestamp: str) -> dict[str, Any]:
        if not actor:
            raise ValueError("actor is required")
        if not timestamp:
            raise ValueError("timestamp is required")
        if actor != binding.responsible_actor:
            raise ValueError("actor must match binding.responsible_actor")
        record = binding.to_record(mission_id=self.mission_id, alert=alert)
        return self._writer(record=record, actor=actor, timestamp=timestamp)
