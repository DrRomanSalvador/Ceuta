"""CeutIA boundary for warning-response lifecycle records from SERPIENTE."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class ResponseAcceptance:
    accepted: bool
    reason: str
    response_id: str | None


def _timestamp(value: object, field: str) -> datetime | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def consume_serpiente_response(payload: Mapping[str, Any], *, as_of: datetime | None = None) -> ResponseAcceptance:
    """Accept only explicitly complete response records; infer no missing lifecycle stage."""
    required = (
        "response_id", "alert_id", "response_status", "response_eligible",
        "eligible_from", "eligible_until", "intended_mechanism", "response_horizon",
        "causal_status", "provenance",
    )
    missing = tuple(field for field in required if field not in payload)
    if missing:
        return ResponseAcceptance(False, "response_incomplete:missing=" + ",".join(missing), None)
    response_id = str(payload["response_id"])
    if not response_id.strip():
        return ResponseAcceptance(False, "response_invalid:empty_response_id", None)
    provenance = payload["provenance"]
    if not isinstance(provenance, (list, tuple)) or not provenance or any(not isinstance(ref, str) or not ref for ref in provenance):
        return ResponseAcceptance(False, "response_invalid:provenance", response_id)
    start = _timestamp(payload["eligible_from"], "eligible_from")
    end = _timestamp(payload["eligible_until"], "eligible_until")
    if start is None or end is None or end <= start:
        return ResponseAcceptance(False, "response_invalid:eligibility_window", response_id)

    status = str(payload["response_status"])
    decision_id = payload.get("decision_id")
    action_id = payload.get("action_id")
    decision_time = _timestamp(payload.get("decision_time"), "decision_time")
    action_time = _timestamp(payload.get("action_time"), "action_time")
    outcome_id = payload.get("outcome_id")
    outcome_time = _timestamp(payload.get("outcome_time"), "outcome_time")

    if status == "EXECUTED" and not (decision_id and decision_time and action_id and action_time):
        return ResponseAcceptance(False, "response_invalid:executed_requires_decision_and_action", response_id)
    if action_id and not decision_id:
        return ResponseAcceptance(False, "response_invalid:action_without_decision", response_id)
    if action_time and not decision_time:
        return ResponseAcceptance(False, "response_invalid:action_time_without_decision_time", response_id)
    if decision_time and action_time and action_time < decision_time:
        return ResponseAcceptance(False, "response_invalid:action_before_decision", response_id)
    if status == "NO_RESPONSE" and (action_id or action_time):
        return ResponseAcceptance(False, "response_invalid:no_response_contains_action", response_id)
    if status == "NO_RESPONSE" and bool(payload["response_eligible"]) and not payload.get("implementation_failure"):
        return ResponseAcceptance(False, "response_invalid:eligible_no_response_requires_reason", response_id)
    if outcome_id and not action_id:
        return ResponseAcceptance(False, "response_invalid:outcome_without_intervention", response_id)
    if outcome_time and not outcome_id:
        return ResponseAcceptance(False, "response_invalid:outcome_time_without_outcome", response_id)
    if outcome_time and action_time and outcome_time < action_time:
        return ResponseAcceptance(False, "response_invalid:outcome_before_action", response_id)

    if as_of is not None:
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            return ResponseAcceptance(False, "response_invalid:as_of_not_timezone_aware", response_id)
        moment = as_of.astimezone(timezone.utc)
        if start > moment:
            return ResponseAcceptance(False, "response_temporally_ineligible:window_not_started", response_id)

    causal_status = str(payload["causal_status"])
    if causal_status == "IDENTIFIED" and not payload.get("counterfactual_ref"):
        return ResponseAcceptance(False, "response_invalid:causal_identification_requires_counterfactual", response_id)
    if causal_status == "IDENTIFIED" and not payload.get("outcome_ascertainment_ref"):
        return ResponseAcceptance(False, "response_invalid:causal_identification_requires_outcome_ascertainment", response_id)

    return ResponseAcceptance(True, "response_accepted_without_causal_promotion", response_id)


__all__ = ["ResponseAcceptance", "consume_serpiente_response"]
