from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Mapping, Sequence


class FounderDomainError(ValueError):
    pass


OPPORTUNITY_STATES = (
    "DISCOVERED", "SCREENED", "HYPOTHESIS", "VALIDATING", "COMMERCIAL_SIGNAL", "SELLABLE",
    "REPEATABLE", "ECONOMICALLY_VIABLE", "SCALABLE", "DEFENSIBLE", "CATEGORY_CREATING",
    "ABANDONED", "PAUSED", "SUPERSEDED", "SPUN_OUT", "LICENSED", "ACQUIRED", "PARTNERED",
)

DECISION_OUTCOMES = ("NO_DECISION_YET", "DECISION_REJECTED", "DECISION_DEFERRED", "ABSTAIN_FROM_DECISION", "DECISION_EXECUTED")
REVENUE_CLASSES = ("OPERATING_REVENUE", "PILOT_REVENUE", "RECURRING_REVENUE", "NON_RECURRING_REVENUE", "GRANT", "LOAN", "INVESTMENT", "CREDIT", "REFUND", "PASS_THROUGH", "OTHER_NON_OPERATING")
EVIDENCE_CLASSES = ("EXTERNAL_EVIDENCE", "INTERNAL_ANALYSIS", "FOUNDER_GENERATED_HYPOTHESIS", "FOUNDER_GENERATED_FORECAST", "CUSTOMER_ASSERTION", "CUSTOMER_BEHAVIOUR", "TRANSACTIONAL_EVIDENCE", "THIRD_PARTY_EVIDENCE", "SYSTEM_OUTPUT")

_TERMINAL_BRANCHES = {"ABANDONED", "PAUSED", "SUPERSEDED", "SPUN_OUT", "LICENSED", "ACQUIRED", "PARTNERED"}
_FORWARD = {state: idx for idx, state in enumerate(("DISCOVERED", "SCREENED", "HYPOTHESIS", "VALIDATING", "COMMERCIAL_SIGNAL", "SELLABLE", "REPEATABLE", "ECONOMICALLY_VIABLE", "SCALABLE", "DEFENSIBLE", "CATEGORY_CREATING"))}


@dataclass(frozen=True, slots=True)
class Evidence:
    evidence_id: str
    evidence_class: str
    source_ref: str
    observed_at: str
    statement: str
    independent: bool = True

    def validate(self) -> None:
        if self.evidence_class not in EVIDENCE_CLASSES:
            raise FounderDomainError("UNKNOWN_EVIDENCE_CLASS")
        if not self.source_ref.strip() or not self.observed_at.strip():
            raise FounderDomainError("EVIDENCE_PROVENANCE_REQUIRED")
        if self.evidence_class in {"INTERNAL_ANALYSIS", "FOUNDER_GENERATED_HYPOTHESIS", "FOUNDER_GENERATED_FORECAST", "SYSTEM_OUTPUT"} and self.independent:
            raise FounderDomainError("SELF_GENERATED_EVIDENCE_CANNOT_BE_INDEPENDENT")


@dataclass(frozen=True, slots=True)
class DecisionRecord:
    decision_id: str
    subject_id: str
    subject_version: int
    decision_type: str
    proposed_action: str
    objective: str
    evidence_for: tuple[str, ...]
    evidence_against: tuple[str, ...]
    uncertainties: tuple[str, ...]
    alternatives: tuple[str, ...]
    status_quo_consequence: str
    cost: str
    time: str
    learning_value: str
    option_value: str
    risk: str
    reversibility: str
    resource_reservation: str
    kill_criterion: str
    data_that_would_change_decision: str
    authority_level: str
    authorized_by: str | None
    result: str
    review_at: str
    provenance: str

    def validate(self) -> None:
        required = (self.decision_id, self.subject_id, self.decision_type, self.proposed_action, self.objective,
                    self.status_quo_consequence, self.cost, self.time, self.learning_value, self.option_value,
                    self.risk, self.reversibility, self.resource_reservation, self.kill_criterion,
                    self.data_that_would_change_decision, self.authority_level, self.result, self.review_at, self.provenance)
        if any(not str(value).strip() for value in required):
            raise FounderDomainError("DECISION_RECORD_REQUIRED_FIELD_MISSING")
        if not self.evidence_for and not self.evidence_against:
            raise FounderDomainError("DECISION_RECORD_REQUIRES_EVIDENCE")
        if self.result == "ABSTAIN_FROM_DECISION" and not self.uncertainties:
            raise FounderDomainError("ABSTAIN_REQUIRES_EXPLICIT_UNCERTAINTY")
        if self.authority_level == "EXTERNAL_COMMERCIAL" and not self.authorized_by:
            raise FounderDomainError("EXTERNAL_AUTHORITY_REQUIRED")


@dataclass(frozen=True, slots=True)
class RevenueEvent:
    revenue_id: str
    revenue_class: str
    amount: str
    observed_at: str
    customer_acceptance: bool
    recurring: bool
    provenance: str

    def validate(self) -> None:
        if self.revenue_class not in REVENUE_CLASSES:
            raise FounderDomainError("UNKNOWN_REVENUE_CLASS")
        if not self.provenance.strip() or not self.observed_at.strip():
            raise FounderDomainError("REVENUE_PROVENANCE_REQUIRED")
        if self.revenue_class == "PILOT_REVENUE" and self.recurring:
            raise FounderDomainError("PILOT_REVENUE_CANNOT_BE_DECLARED_RECURRING")


def allowed_transition(current: str, target: str, evidence: Sequence[Evidence]) -> bool:
    if current not in OPPORTUNITY_STATES or target not in OPPORTUNITY_STATES:
        raise FounderDomainError("UNKNOWN_OPPORTUNITY_STATE")
    if current == target:
        return True
    if target in _TERMINAL_BRANCHES:
        return True
    if current in _TERMINAL_BRANCHES:
        raise FounderDomainError("TERMINAL_BRANCH_CANNOT_PROMOTE")
    if target not in _FORWARD or current not in _FORWARD or _FORWARD[target] != _FORWARD[current] + 1:
        raise FounderDomainError("FORBIDDEN_OPPORTUNITY_TRANSITION")
    for item in evidence:
        item.validate()
    if not evidence:
        raise FounderDomainError("OPPORTUNITY_TRANSITION_REQUIRES_EVIDENCE")
    return True


def validate_transition_invariants(target: str, evidence: Sequence[Evidence], *, repeatable_outcomes: int = 0, economic_support: bool = False, scale_support: bool = False, moat_support: bool = False, category_support: bool = False) -> None:
    if target == "REPEATABLE" and repeatable_outcomes < 2:
        raise FounderDomainError("REPEATABLE_REQUIRES_REPEATED_PAID_OUTCOMES")
    if target == "ECONOMICALLY_VIABLE" and not economic_support:
        raise FounderDomainError("ECONOMICALLY_VIABLE_REQUIRES_ECONOMIC_SUPPORT")
    if target == "SCALABLE" and not scale_support:
        raise FounderDomainError("SCALABLE_REQUIRES_SCALE_SUPPORT")
    if target == "DEFENSIBLE" and not moat_support:
        raise FounderDomainError("DEFENSIBLE_REQUIRES_REPLICATION_TEST")
    if target == "CATEGORY_CREATING" and not category_support:
        raise FounderDomainError("CATEGORY_CREATING_REQUIRES_CATEGORY_EVIDENCE")
    for item in evidence:
        item.validate()


def validate_external_claim(evidence: Sequence[Evidence], authorized: bool) -> None:
    if not authorized:
        raise FounderDomainError("EXTERNAL_CLAIM_AUTHORIZATION_REQUIRED")
    if not evidence:
        raise FounderDomainError("EXTERNAL_CLAIM_REQUIRES_EVIDENCE")
    for item in evidence:
        item.validate()
        if item.evidence_class in {"INTERNAL_ANALYSIS", "FOUNDER_GENERATED_HYPOTHESIS", "FOUNDER_GENERATED_FORECAST", "SYSTEM_OUTPUT"}:
            raise FounderDomainError("EXTERNAL_CLAIM_REQUIRES_INDEPENDENT_EVIDENCE")


def is_stale(observed_at: str, stale_after_seconds: int, *, now: datetime | None = None) -> bool:
    observed = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
    reference = now or datetime.now(timezone.utc)
    return (reference - observed).total_seconds() > stale_after_seconds


def validate_resource_reservation(resource_id: str, owner: str, purpose: str, start: str, expected_end: str, status: str, conflict_policy: str, release_condition: str, provenance: str) -> None:
    if not all(value.strip() for value in (resource_id, owner, purpose, start, expected_end, status, conflict_policy, release_condition, provenance)):
        raise FounderDomainError("RESOURCE_RESERVATION_REQUIRED_FIELD_MISSING")


def validate_authority(operation: str, authority: Mapping[str, bool]) -> None:
    external = {"CONTACT_CUSTOMER", "SPEND_MONEY", "COMMIT_CAPITAL", "SIGN_AGREEMENT", "CHANGE_PRODUCTION", "PUBLISH_EXTERNAL_CLAIM", "CHANGE_SECURITY_POLICY"}
    if operation in external and not authority.get("AUTHORIZED_EXECUTION", False):
        raise FounderDomainError("OPERATIONAL_AUTHORITY_REQUIRED")
