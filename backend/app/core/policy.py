from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Iterable, Mapping


class PolicyDecision(str, Enum):
    ALLOW = "ALLOW"
    ALLOW_WITH_CONTROLS = "ALLOW_WITH_CONTROLS"
    HUMAN_REVIEW_REQUIRED = "HUMAN_REVIEW_REQUIRED"
    BLOCK = "BLOCK"


class RiskTier(str, Enum):
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class DataClass(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    PERSONAL = "PERSONAL"
    SENSITIVE_PERSONAL = "SENSITIVE_PERSONAL"
    MEDICAL = "MEDICAL"
    SECURITY_RESTRICTED = "SECURITY_RESTRICTED"


class Purpose(str, Enum):
    PUBLIC_KNOWLEDGE = "PUBLIC_KNOWLEDGE"
    EPISTEMIC_ANALYSIS = "EPISTEMIC_ANALYSIS"
    TERRITORIAL_MONITORING = "TERRITORIAL_MONITORING"
    EARLY_WARNING = "EARLY_WARNING"
    RESEARCH = "RESEARCH"
    MEDICAL_ASSISTANCE = "MEDICAL_ASSISTANCE"
    LAW_ENFORCEMENT = "LAW_ENFORCEMENT"
    BORDER_CONTROL = "BORDER_CONTROL"
    POLITICAL_TARGETING = "POLITICAL_TARGETING"
    INDIVIDUAL_RISK_PROFILING = "INDIVIDUAL_RISK_PROFILING"
    COERCIVE_ACTION = "COERCIVE_ACTION"


class SensitiveAttribute(str, Enum):
    HEALTH = "health"
    BIOMETRIC = "biometric"
    GENETIC = "genetic"
    RELIGION = "religion"
    POLITICAL_OPINION = "political_opinion"
    TRADE_UNION = "trade_union"
    ETHNIC_ORIGIN = "ethnic_origin"
    SEX_LIFE = "sex_life"
    SEXUAL_ORIENTATION = "sexual_orientation"
    CRIMINAL_HISTORY = "criminal_history"
    PRECISE_LOCATION = "precise_location"


FORBIDDEN_INDIVIDUAL_PURPOSES = {
    Purpose.POLITICAL_TARGETING,
    Purpose.INDIVIDUAL_RISK_PROFILING,
    Purpose.COERCIVE_ACTION,
}

FORBIDDEN_ACTIONS = {
    "arrest",
    "detain",
    "search",
    "deport",
    "deny_service",
    "deny_benefit",
    "restrict_freedom",
    "punish",
    "surveil_individual",
    "identify_suspect",
    "rank_people_by_dangerousness",
}


@dataclass(frozen=True, slots=True)
class PolicyRequest:
    purpose: Purpose
    actor_role: str
    data_classes: frozenset[DataClass] = frozenset({DataClass.PUBLIC})
    sensitive_attributes: frozenset[SensitiveAttribute] = frozenset()
    target_is_individual: bool = False
    target_is_group: bool = False
    target_is_territory: bool = True
    requested_action: str | None = None
    automated_decision: bool = False
    affects_rights_or_freedoms: bool = False
    uses_medical_data: bool = False
    exports_personal_data: bool = False
    minimum_group_size: int | None = None
    observed_group_size: int | None = None
    external_model: bool = False


@dataclass(frozen=True, slots=True)
class PolicyFinding:
    code: str
    severity: RiskTier
    message: str
    blocking: bool = False


@dataclass(frozen=True, slots=True)
class PolicyResult:
    decision: PolicyDecision
    risk_tier: RiskTier
    findings: tuple[PolicyFinding, ...] = ()
    required_controls: tuple[str, ...] = ()

    @property
    def blocked(self) -> bool:
        return self.decision == PolicyDecision.BLOCK


@dataclass(slots=True)
class PolicyEngine:
    minimum_k: int = 10

    allowed_roles: frozenset[str] = frozenset(
        {
            "PUBLIC",
            "OWNER",
            "ADMIN",
            "ANALYST",
            "RESEARCHER",
            "MEDICAL",
        }
    )

    def evaluate(self, request: PolicyRequest) -> PolicyResult:
        findings: list[PolicyFinding] = []
        controls: list[str] = []

        if request.actor_role not in self.allowed_roles:
            findings.append(
                PolicyFinding(
                    "UNKNOWN_ACTOR_ROLE",
                    RiskTier.HIGH,
                    "Actor role is not authorized by the policy engine.",
                    True,
                )
            )

        if (
            request.purpose in FORBIDDEN_INDIVIDUAL_PURPOSES
            and request.target_is_individual
        ):
            findings.append(
                PolicyFinding(
                    "INDIVIDUAL_HIGH_RISK_PURPOSE",
                    RiskTier.CRITICAL,
                    "Individual political targeting, individual risk profiling or coercive use is blocked.",
                    True,
                )
            )

        if request.target_is_individual and request.automated_decision:
            findings.append(
                PolicyFinding(
                    "AUTOMATED_INDIVIDUAL_DECISION",
                    RiskTier.CRITICAL,
                    "Automated decisions concerning an individual are blocked by the core safety policy.",
                    True,
                )
            )

        if request.affects_rights_or_freedoms and request.automated_decision:
            findings.append(
                PolicyFinding(
                    "AUTOMATED_RIGHTS_IMPACT",
                    RiskTier.CRITICAL,
                    "Automated action with potentially significant effects on rights or freedoms is blocked.",
                    True,
                )
            )

        if (
            request.requested_action
            and request.requested_action.lower() in FORBIDDEN_ACTIONS
        ):
            findings.append(
                PolicyFinding(
                    "COERCIVE_ACTION",
                    RiskTier.CRITICAL,
                    "Coercive or individual-surveillance action is not an allowed CEUTIA output.",
                    True,
                )
            )

        if request.uses_medical_data or DataClass.MEDICAL in request.data_classes:
            if request.purpose != Purpose.MEDICAL_ASSISTANCE:
                findings.append(
                    PolicyFinding(
                        "MEDICAL_DATA_CROSS_DOMAIN",
                        RiskTier.CRITICAL,
                        "Medical data cannot enter territorial intelligence or non-medical analysis.",
                        True,
                    )
                )
            else:
                controls.extend(
                    (
                        "MEDICAL_DOMAIN_ISOLATION",
                        "STRICT_ACCESS_CONTROL",
                        "AUDIT_ALL_ACCESS",
                    )
                )

        if request.sensitive_attributes and request.target_is_individual:
            findings.append(
                PolicyFinding(
                    "SENSITIVE_INDIVIDUAL_PROFILING",
                    RiskTier.CRITICAL,
                    "Sensitive attributes cannot be used to rank or profile individuals.",
                    True,
                )
            )

        if request.exports_personal_data:
            controls.extend(
                (
                    "DATA_EXPORT_REVIEW",
                    "PURPOSE_LIMITATION",
                    "MINIMIZATION",
                )
            )

            findings.append(
                PolicyFinding(
                    "PERSONAL_DATA_EXPORT",
                    RiskTier.HIGH,
                    "Personal-data export requires explicit review and purpose limitation.",
                    False,
                )
            )

        if request.target_is_group and request.observed_group_size is not None:
            k = request.minimum_group_size or self.minimum_k

            if request.observed_group_size < k:
                findings.append(
                    PolicyFinding(
                        "REIDENTIFICATION_RISK",
                        RiskTier.HIGH,
                        f"Group size {request.observed_group_size} is below minimum aggregation threshold {k}.",
                        True,
                    )
                )

        if request.purpose in {
            Purpose.TERRITORIAL_MONITORING,
            Purpose.EARLY_WARNING,
        }:
            controls.extend(
                (
                    "AGGREGATION",
                    "PROVENANCE_REQUIRED",
                    "CONTRADICTION_REQUIRED",
                    "HUMAN_REVIEW_FOR_HIGH_ALERTS",
                )
            )

            if request.target_is_individual:
                findings.append(
                    PolicyFinding(
                        "TERRITORIAL_TO_INDIVIDUAL_CROSSOVER",
                        RiskTier.CRITICAL,
                        "Territorial monitoring cannot be converted into individual profiling.",
                        True,
                    )
                )

        if request.external_model:
            controls.extend(
                (
                    "PROVIDER_POLICY_CHECK",
                    "NO_SENSITIVE_DATA_TO_UNAPPROVED_MODEL",
                    "MODEL_VERSION_AUDIT",
                )
            )

        if not findings:
            decision = (
                PolicyDecision.ALLOW_WITH_CONTROLS
                if controls
                else PolicyDecision.ALLOW
            )
            tier = RiskTier.MODERATE if controls else RiskTier.LOW

        elif any(f.blocking for f in findings):
            decision = PolicyDecision.BLOCK
            tier = max(
                (f.severity for f in findings),
                key=_tier_rank,
            )

        else:
            decision = PolicyDecision.HUMAN_REVIEW_REQUIRED
            tier = max(
                (f.severity for f in findings),
                key=_tier_rank,
            )

        return PolicyResult(
            decision=decision,
            risk_tier=tier,
            findings=tuple(findings),
            required_controls=tuple(dict.fromkeys(controls)),
        )


def _tier_rank(value: RiskTier) -> int:
    return {
        RiskTier.LOW: 0,
        RiskTier.MODERATE: 1,
        RiskTier.HIGH: 2,
        RiskTier.CRITICAL: 3,
    }[value]


def normalize_attributes(
    values: Iterable[str | SensitiveAttribute],
) -> frozenset[SensitiveAttribute]:
    normalized: set[SensitiveAttribute] = set()

    for value in values:
        if isinstance(value, SensitiveAttribute):
            normalized.add(value)
            continue

        try:
            normalized.add(
                SensitiveAttribute(value.lower().strip())
            )
        except ValueError:
            continue

    return frozenset(normalized)


def sanitize_metadata(
    metadata: Mapping[str, Any],
) -> dict[str, Any]:
    secret_words = {
        "password",
        "passwd",
        "secret",
        "token",
        "api_key",
        "authorization",
        "cookie",
    }

    return {
        str(key): (
            "[REDACTED]"
            if str(key).lower() in secret_words
            else value
        )
        for key, value in metadata.items()
    }