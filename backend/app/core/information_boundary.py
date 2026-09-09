"""# CeutIA — Information Boundary
#
# Policy enforcement point for information-flow control.
# This module enforces the architectural separation between
# PUBLIC, INTERNAL, PRIVATE/OWNER and RESTRICTED information.
#
# It does NOT replace authentication, database ACLs, network
# segmentation, encryption, audit storage or legal controls.
#
# Core invariant:
#
#     INTERNAL_INTELLIGENCE ∉ PUBLIC_OUTPUT
#
# unless an explicit, auditable public-release policy authorizes
# a controlled transformation.

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import FrozenSet, Iterable, Mapping


class InformationBoundaryError(Exception):
    """Base exception for information-boundary violations."""


class ClassificationViolation(InformationBoundaryError):
    """Raised when information would cross an unauthorized boundary."""


class AuthorizationViolation(InformationBoundaryError):
    """Raised when an actor lacks the required capability."""


class PublicReleaseViolation(InformationBoundaryError):
    """Raised when internal information cannot be released publicly."""


class InformationClass(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    PRIVATE = "PRIVATE"
    RESTRICTED = "RESTRICTED"


class ActorDomain(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    OWNER = "OWNER"
    RESTRICTED = "RESTRICTED"


class Operation(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    TRANSFORM = "TRANSFORM"
    DECISION_USE = "DECISION_USE"
    RELEASE_PUBLIC = "RELEASE_PUBLIC"


class SensitivityTag(str, Enum):
    PERSONAL_DATA = "PERSONAL_DATA"
    HEALTH_DATA = "HEALTH_DATA"
    INDIVIDUAL_RISK = "INDIVIDUAL_RISK"
    STRATEGIC_INTELLIGENCE = "STRATEGIC_INTELLIGENCE"
    SECURITY_INFORMATION = "SECURITY_INFORMATION"
    SECRET = "SECRET"
    INTERNAL_MODEL_STATE = "INTERNAL_MODEL_STATE"
    PREDICTION = "PREDICTION"
    HYPOTHESIS = "HYPOTHESIS"
    SCENARIO = "SCENARIO"
    ALERT = "ALERT"


PUBLIC_FORBIDDEN_TAGS: FrozenSet[SensitivityTag] = frozenset(
    {
        SensitivityTag.INDIVIDUAL_RISK,
        SensitivityTag.STRATEGIC_INTELLIGENCE,
        SensitivityTag.SECURITY_INFORMATION,
        SensitivityTag.SECRET,
        SensitivityTag.INTERNAL_MODEL_STATE,
    }
)


@dataclass(frozen=True, slots=True)
class InformationObject:
    """
    Immutable representation of an information-bearing object.

    Classification describes access sensitivity.

    Sensitivity tags describe properties that may survive
    transformations and therefore require conservative propagation.
    """

    object_id: str
    classification: InformationClass
    sensitivity: FrozenSet[SensitivityTag] = frozenset()
    source_object_ids: tuple[str, ...] = ()
    purpose: str | None = None
    owner: str | None = None
    policy_version: str = "1"
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.object_id.strip():
            raise ValueError("object_id must not be empty")

        if any(not source_id.strip() for source_id in self.source_object_ids):
            raise ValueError("source_object_ids cannot contain empty identifiers")


@dataclass(frozen=True, slots=True)
class AuthorizationContext:
    actor_domain: ActorDomain
    actor_id: str
    capabilities: FrozenSet[Operation] = frozenset()
    purpose: str | None = None
    human_approval: bool = False

    def __post_init__(self) -> None:
        if not self.actor_id.strip():
            raise ValueError("actor_id must not be empty")


@dataclass(frozen=True, slots=True)
class PublicReleaseRequest:
    """
    Explicit request to transform information into public-safe output.

    Internal information is never released merely because an API caller
    asks for it. Release requires explicit authorization and all safety
    checks.
    """

    source_object_ids: tuple[str, ...]
    requested_by: str
    purpose: str
    human_approval: bool = False
    policy_version: str = "1"

    def __post_init__(self) -> None:
        if not self.source_object_ids:
            raise ValueError("at least one source object is required")

        if not self.requested_by.strip():
            raise ValueError("requested_by must not be empty")

        if not self.purpose.strip():
            raise ValueError("purpose must not be empty")


@dataclass(frozen=True, slots=True)
class PublicSafeOutput:
    """
    Output that has explicitly crossed the information boundary.

    The object intentionally contains no internal risk score,
    strategic intelligence or restricted source material.
    """

    output_id: str
    content: Mapping[str, object]
    source_object_ids: tuple[str, ...]
    policy_version: str
    public_safe: bool = True

    def __post_init__(self) -> None:
        if not self.output_id.strip():
            raise ValueError("output_id must not be empty")

        if not self.source_object_ids:
            raise ValueError("source_object_ids must not be empty")

        if not self.public_safe:
            raise ValueError("PublicSafeOutput must be public_safe=True")


@dataclass(frozen=True, slots=True)
class BoundaryDecision:
    allowed: bool
    operation: Operation
    actor_domain: ActorDomain
    object_id: str
    reason: str
    policy_version: str


@dataclass(frozen=True, slots=True)
class ReleaseDecision:
    allowed: bool
    reason: str
    policy_version: str
    source_object_ids: tuple[str, ...]


def _classification_rank(
    classification: InformationClass,
) -> int:
    return {
        InformationClass.PUBLIC: 0,
        InformationClass.INTERNAL: 1,
        InformationClass.PRIVATE: 2,
        InformationClass.RESTRICTED: 3,
    }[classification]


def _maximum_classification(
    objects: Iterable[InformationObject],
) -> InformationClass:
    objects = tuple(objects)

    if not objects:
        raise ValueError("at least one information object is required")

    return max(
        (obj.classification for obj in objects),
        key=_classification_rank,
    )


def propagate_classification(
    objects: Iterable[InformationObject],
) -> InformationClass:
    """
    Conservative classification propagation.

    A transformation cannot silently downgrade the classification
    of its inputs.
    """

    return _maximum_classification(objects)


def propagate_sensitivity(
    objects: Iterable[InformationObject],
) -> FrozenSet[SensitivityTag]:
    """
    Sensitivity propagation is monotonic.

    Derived objects inherit all relevant sensitivity tags from
    their source objects.
    """

    tags: set[SensitivityTag] = set()

    for obj in objects:
        tags.update(obj.sensitivity)

    return frozenset(tags)


def derive_information_object(
    *,
    object_id: str,
    sources: Iterable[InformationObject],
    purpose: str,
    policy_version: str = "1",
    metadata: Mapping[str, str] | None = None,
) -> InformationObject:
    """
    Create a derived object while conservatively propagating
    classification and sensitivity.
    """

    source_objects = tuple(sources)

    if not source_objects:
        raise ValueError("derived object requires source objects")

    return InformationObject(
        object_id=object_id,
        classification=propagate_classification(source_objects),
        sensitivity=propagate_sensitivity(source_objects),
        source_object_ids=tuple(obj.object_id for obj in source_objects),
        purpose=purpose,
        policy_version=policy_version,
        metadata=metadata or {},
    )


def _actor_can_access_classification(
    actor: AuthorizationContext,
    classification: InformationClass,
) -> bool:
    """
    Coarse domain boundary.

    Fine-grained authorization must still be applied by the caller.
    """

    if actor.actor_domain is ActorDomain.PUBLIC:
        return classification is InformationClass.PUBLIC

    if actor.actor_domain is ActorDomain.INTERNAL:
        return classification in {
            InformationClass.PUBLIC,
            InformationClass.INTERNAL,
        }

    if actor.actor_domain is ActorDomain.OWNER:
        return classification in {
            InformationClass.PUBLIC,
            InformationClass.INTERNAL,
            InformationClass.PRIVATE,
        }

    if actor.actor_domain is ActorDomain.RESTRICTED:
        return True

    return False


def authorize(
    *,
    actor: AuthorizationContext,
    operation: Operation,
    information: InformationObject,
) -> BoundaryDecision:
    """
    Evaluate a single information-flow operation.

    This function fails closed: anything not explicitly permitted
    is denied.
    """

    if operation not in actor.capabilities:
        return BoundaryDecision(
            allowed=False,
            operation=operation,
            actor_domain=actor.actor_domain,
            object_id=information.object_id,
            reason="actor lacks required capability",
            policy_version=information.policy_version,
        )

    if not _actor_can_access_classification(
        actor,
        information.classification,
    ):
        return BoundaryDecision(
            allowed=False,
            operation=operation,
            actor_domain=actor.actor_domain,
            object_id=information.object_id,
            reason="actor domain cannot access information classification",
            policy_version=information.policy_version,
        )

    if actor.actor_domain is ActorDomain.PUBLIC:
        if information.sensitivity & PUBLIC_FORBIDDEN_TAGS:
            return BoundaryDecision(
                allowed=False,
                operation=operation,
                actor_domain=actor.actor_domain,
                object_id=information.object_id,
                reason="sensitive information is forbidden in PUBLIC domain",
                policy_version=information.policy_version,
            )

    if operation is Operation.RELEASE_PUBLIC:
        return BoundaryDecision(
            allowed=False,
            operation=operation,
            actor_domain=actor.actor_domain,
            object_id=information.object_id,
            reason="public release requires explicit release policy",
            policy_version=information.policy_version,
        )

    return BoundaryDecision(
        allowed=True,
        operation=operation,
        actor_domain=actor.actor_domain,
        object_id=information.object_id,
        reason="operation authorized",
        policy_version=information.policy_version,
    )


def assert_authorized(
    *,
    actor: AuthorizationContext,
    operation: Operation,
    information: InformationObject,
) -> None:
    decision = authorize(
        actor=actor,
        operation=operation,
        information=information,
    )

    if not decision.allowed:
        raise AuthorizationViolation(decision.reason)


def validate_public_release(
    *,
    request: PublicReleaseRequest,
    sources: Iterable[InformationObject],
) -> ReleaseDecision:
    """
    Evaluate whether internal information may cross into PUBLIC.

    This deliberately does NOT automatically permit release.

    A caller must perform an explicit public-safe transformation and
    provide human approval where policy requires it.
    """

    source_objects = tuple(sources)

    if not source_objects:
        return ReleaseDecision(
            allowed=False,
            reason="no source objects supplied",
            policy_version=request.policy_version,
            source_object_ids=(),
        )

    supplied_ids = {obj.object_id for obj in source_objects}

    if not set(request.source_object_ids).issubset(supplied_ids):
        return ReleaseDecision(
            allowed=False,
            reason="release request references unavailable source objects",
            policy_version=request.policy_version,
            source_object_ids=request.source_object_ids,
        )

    if not request.human_approval:
        return ReleaseDecision(
            allowed=False,
            reason="explicit human approval is required for internal-to-public release",
            policy_version=request.policy_version,
            source_object_ids=request.source_object_ids,
        )

    for source in source_objects:
        if source.classification is InformationClass.RESTRICTED:
            return ReleaseDecision(
                allowed=False,
                reason="RESTRICTED information cannot cross the public boundary",
                policy_version=request.policy_version,
                source_object_ids=request.source_object_ids,
            )

        forbidden = source.sensitivity & PUBLIC_FORBIDDEN_TAGS

        if forbidden:
            return ReleaseDecision(
                allowed=False,
                reason=(
                    "source contains information explicitly forbidden "
                    f"from public release: {sorted(tag.value for tag in forbidden)}"
                ),
                policy_version=request.policy_version,
                source_object_ids=request.source_object_ids,
            )

    return ReleaseDecision(
        allowed=True,
        reason="release may proceed to an explicit public-safe transformation",
        policy_version=request.policy_version,
        source_object_ids=request.source_object_ids,
    )


def create_public_safe_output(
    *,
    request: PublicReleaseRequest,
    sources: Iterable[InformationObject],
    output_id: str,
    content: Mapping[str, object],
) -> PublicSafeOutput:
    """
    Create the only supported public-facing representation of
    internally derived information.

    The function is intentionally strict.
    """

    source_objects = tuple(sources)

    release = validate_public_release(
        request=request,
        sources=source_objects,
    )

    if not release.allowed:
        raise PublicReleaseViolation(release.reason)

    if not output_id.strip():
        raise ValueError("output_id must not be empty")

    return PublicSafeOutput(
        output_id=output_id,
        content=dict(content),
        source_object_ids=request.source_object_ids,
        policy_version=request.policy_version,
    )


def assert_no_public_intelligence_leak(
    output: Mapping[str, object],
) -> None:
    """
    Defensive inspection of a candidate public payload.

    This is not a substitute for schema-level output contracts.
    """

    forbidden_keys = {
        "risk_score",
        "individual_risk",
        "strategic_intelligence",
        "internal_alert",
        "internal_prediction",
        "private_source",
        "internal_model_state",
        "hidden_state",
        "scenario_internal",
        "hypothesis_internal",
    }

    leaked = forbidden_keys.intersection(output.keys())

    if leaked:
        raise PublicReleaseViolation(
            "candidate public output contains forbidden internal fields: "
            + ", ".join(sorted(leaked))
        )


def assert_public_safe_output(
    output: PublicSafeOutput,
) -> None:
    """
    Final invariant check before a public response is emitted.
    """

    if not output.public_safe:
        raise PublicReleaseViolation(
            "output is not explicitly marked public_safe"
        )

    assert_no_public_intelligence_leak(output.content)


def assert_no_identity_based_risk_signal(
    *,
    feature_names: Iterable[str],
) -> None:
    """
    Prevent direct identity-based dangerousness/risk modelling.

    This is deliberately conservative and intended as a final
    policy guard, not as a complete fairness framework.
    """

    forbidden = {
        "nationality",
        "ethnicity",
        "race",
        "religion",
        "migrant_status",
        "migration_status",
        "origin",
    }

    supplied = {
        name.strip().lower()
        for name in feature_names
    }

    illegal = supplied.intersection(forbidden)

    if illegal:
        raise ClassificationViolation(
            "identity/protected attributes cannot be used as automatic "
            "dangerousness or individual-risk signals: "
            + ", ".join(sorted(illegal))
        )


INFORMATION_BOUNDARY_INVARIANTS: tuple[str, ...] = (
    "PUBLIC cannot directly read INTERNAL intelligence.",
    "PUBLIC cannot directly read PRIVATE intelligence.",
    "PUBLIC cannot directly read RESTRICTED information.",
    "Internal information cannot be downgraded implicitly.",
    "Derived information inherits source sensitivity.",
    "Public release requires an explicit release policy.",
    "Failure of an authorization check results in denial.",
    "Failure of a public-release check results in denial.",
    "LLM instructions cannot override information-boundary policy.",
    "Internal intelligence is not itself a public output.",
    "Individual risk must not be exposed through public output.",
    "Strategic intelligence must not be exposed through public output.",
    "Identity attributes must not become automatic dangerousness signals.",
    "Decision use does not imply public disclosure.",
    "All public releases must remain auditable through source identifiers.",
)


__all__ = [
    "ActorDomain",
    "AuthorizationContext",
    "AuthorizationViolation",
    "BoundaryDecision",
    "ClassificationViolation",
    "InformationBoundaryError",
    "InformationClass",
    "InformationObject",
    "INFORMATION_BOUNDARY_INVARIANTS",
    "Operation",
    "PublicReleaseRequest",
    "PublicReleaseViolation",
    "PublicSafeOutput",
    "ReleaseDecision",
    "SensitivityTag",
    "assert_authorized",
    "assert_no_identity_based_risk_signal",
    "assert_no_public_intelligence_leak",
    "assert_public_safe_output",
    "authorize",
    "create_public_safe_output",
    "derive_information_object",
    "propagate_classification",
    "propagate_sensitivity",
    "validate_public_release",
]

CeutIA information-flow confidentiality boundary.

This module enforces the separation between public services and internal
intelligence. It is intentionally policy-oriented and does not implement
authentication itself; the application/service layer must supply the actor
and authorization context.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Final, FrozenSet, Iterable, Mapping


class InformationClass(StrEnum):
    """Sensitivity class carried by every protected information object."""

    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    PRIVATE = "PRIVATE"
    RESTRICTED = "RESTRICTED"


class ActorDomain(StrEnum):
    """Security domain of the component requesting access."""

    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    OWNER = "OWNER"
    RESTRICTED = "RESTRICTED"


class BoundaryAction(StrEnum):
    """Actions controlled by the information boundary."""

    READ = "READ"
    WRITE = "WRITE"
    TRANSFORM = "TRANSFORM"
    RELEASE_PUBLIC = "RELEASE_PUBLIC"
    DECISION_USE = "DECISION_USE"


class BoundaryDecision(StrEnum):
    ALLOW = "ALLOW"
    DENY = "DENY"


class BoundaryError(RuntimeError):
    """Base exception for information-boundary violations."""


class InformationClassificationError(BoundaryError):
    """Raised when classification metadata are invalid or unsafe."""


class InformationAccessDenied(BoundaryError):
    """Raised when an actor is not authorized for an operation."""


class PublicReleaseDenied(BoundaryError):
    """Raised when an internal object cannot cross the public boundary."""


@dataclass(frozen=True, slots=True)
class InformationObject:
    """Metadata envelope attached to an information object.

    The actual payload is deliberately not stored here. Classification must
    travel with database records, messages, model artifacts, embeddings,
    caches and other representations handled by higher layers.
    """

    object_id: str
    classification: InformationClass
    source_object_ids: tuple[str, ...] = ()
    purpose: str = ""
    owner: str | None = None
    contains_personal_data: bool = False
    contains_individual_risk: bool = False
    contains_strategic_intelligence: bool = False
    contains_restricted_security_information: bool = False
    provenance_complete: bool = True
    policy_version: str = "1.0"

    def __post_init__(self) -> None:
        if not self.object_id.strip():
            raise InformationClassificationError("object_id cannot be empty")
        if not self.provenance_complete and self.classification != InformationClass.PUBLIC:
            raise InformationClassificationError(
                "non-public objects require complete provenance metadata"
            )


@dataclass(frozen=True, slots=True)
class BoundaryContext:
    """Authorization context supplied by the application layer."""

    actor_domain: ActorDomain
    actor_id: str | None = None
    purposes: FrozenSet[str] = frozenset()
    explicit_public_release: bool = False
    human_approval: bool = False


@dataclass(frozen=True, slots=True)
class PublicSafeOutput:
    """Explicit contract for information permitted to reach PUBLIC."""

    object_id: str
    content: object
    source_object_ids: tuple[str, ...]
    policy_version: str
    privacy_checked: bool
    security_checked: bool
    epistemic_checked: bool
    reidentification_checked: bool
    internal_intelligence_included: bool = False
    individual_risk_included: bool = False
    strategic_information_included: bool = False
    private_source_exposed: bool = False

    def validate(self) -> None:
        if not self.object_id.strip():
            raise PublicReleaseDenied("public output requires an object_id")
        checks = (
            self.privacy_checked,
            self.security_checked,
            self.epistemic_checked,
            self.reidentification_checked,
        )
        if not all(checks):
            raise PublicReleaseDenied("all public-safety checks must pass")
        if self.internal_intelligence_included:
            raise PublicReleaseDenied("internal intelligence cannot enter PUBLIC")
        if self.individual_risk_included:
            raise PublicReleaseDenied("individual risk cannot enter PUBLIC")
        if self.strategic_information_included:
            raise PublicReleaseDenied("strategic information cannot enter PUBLIC")
        if self.private_source_exposed:
            raise PublicReleaseDenied("private source identity cannot enter PUBLIC")


# Classification ordering is deliberately conservative. Higher values are
# more restrictive; transformations cannot silently downgrade an object.
_CLASSIFICATION_RANK: Final[Mapping[InformationClass, int]] = {
    InformationClass.PUBLIC: 0,
    InformationClass.INTERNAL: 1,
    InformationClass.PRIVATE: 2,
    InformationClass.RESTRICTED: 3,
}


_ALLOWED_READ: Final[Mapping[ActorDomain, FrozenSet[InformationClass]]] = {
    ActorDomain.PUBLIC: frozenset({InformationClass.PUBLIC}),
    ActorDomain.INTERNAL: frozenset({InformationClass.PUBLIC, InformationClass.INTERNAL}),
    ActorDomain.OWNER: frozenset(
        {
            InformationClass.PUBLIC,
            InformationClass.INTERNAL,
            InformationClass.PRIVATE,
        }
    ),
    ActorDomain.RESTRICTED: frozenset(
        {
            InformationClass.PUBLIC,
            InformationClass.INTERNAL,
            InformationClass.PRIVATE,
            InformationClass.RESTRICTED,
        }
    ),
}


BOUNDARY_INVARIANTS: Final[tuple[str, ...]] = (
    "PUBLIC cannot directly read INTERNAL intelligence.",
    "PUBLIC cannot directly read PRIVATE intelligence.",
    "PUBLIC cannot directly read RESTRICTED information.",
    "Internal intelligence cannot become PUBLIC by implicit serialization.",
    "Classification cannot be downgraded without an explicit release policy.",
    "Public release fails closed when any required safety check is unavailable.",
    "Individual risk is never a public output of the intelligence engine.",
    "Strategic intelligence is never a direct public output.",
    "LLM output does not override the information boundary.",
    "All boundary-crossing transformations must be auditable.",
)


def can_read(actor: ActorDomain, information: InformationObject) -> bool:
    """Return whether the actor domain may read the information class."""

    return information.classification in _ALLOWED_READ[actor]


def authorize_read(actor: ActorDomain, information: InformationObject) -> None:
    """Fail closed unless the actor is authorized to read the object."""

    if not can_read(actor, information):
        raise InformationAccessDenied(
            f"{actor.value} cannot READ {information.classification.value} "
            f"object {information.object_id}"
        )


def highest_classification(objects: Iterable[InformationObject]) -> InformationClass:
    """Return the most restrictive classification among input objects."""

    items = tuple(objects)
    if not items:
        raise InformationClassificationError("at least one source object is required")
    return max(items, key=lambda item: _CLASSIFICATION_RANK[item.classification]).classification


def propagate_classification(
    sources: Iterable[InformationObject],
    *,
    explicit_release: bool = False,
) -> InformationClass:
    """Propagate the most restrictive source class.

    Explicit release does not itself make an object PUBLIC. It only permits a
    separate public-output policy to evaluate a deliberate transformation.
    """

    classification = highest_classification(sources)
    if classification != InformationClass.PUBLIC and explicit_release:
        return classification
    return classification


def assert_no_unauthorized_downgrade(
    sources: Iterable[InformationObject],
    target: InformationClass,
    *,
    explicit_release: bool,
) -> None:
    """Reject silent downgrades of information classification."""

    source_class = highest_classification(sources)
    source_rank = _CLASSIFICATION_RANK[source_class]
    target_rank = _CLASSIFICATION_RANK[target]
    if target_rank < source_rank and not explicit_release:
        raise InformationClassificationError(
            f"classification downgrade {source_class.value} -> {target.value} "
            "requires explicit release authorization"
        )


def authorize_decision_use(
    actor: ActorDomain,
    information: InformationObject,
    *,
    purpose: str,
) -> None:
    """Authorize use of information by the internal decision engine."""

    if actor not in {ActorDomain.INTERNAL, ActorDomain.OWNER, ActorDomain.RESTRICTED}:
        raise InformationAccessDenied("PUBLIC cannot invoke private decision intelligence")
    if not purpose.strip():
        raise InformationAccessDenied("decision use requires a declared purpose")
    authorize_read(actor, information)


def build_public_safe_output(
    source: InformationObject,
    *,
    content: object,
    context: BoundaryContext,
    privacy_checked: bool,
    security_checked: bool,
    epistemic_checked: bool,
    reidentification_checked: bool,
    source_object_ids: Iterable[str] | None = None,
) -> PublicSafeOutput:
    """Create a public output only through an explicit release decision."""

    if context.actor_domain not in {
        ActorDomain.INTERNAL,
        ActorDomain.OWNER,
        ActorDomain.RESTRICTED,
    }:
        raise PublicReleaseDenied("PUBLIC cannot authorize its own intelligence release")

    if not context.explicit_public_release:
        raise PublicReleaseDenied("explicit public-release authorization is required")

    if source.contains_individual_risk:
        raise PublicReleaseDenied("individual-risk intelligence cannot be released publicly")
    if source.contains_strategic_intelligence:
        raise PublicReleaseDenied("strategic intelligence cannot be released publicly")
    if source.contains_restricted_security_information:
        raise PublicReleaseDenied("restricted security information cannot be released publicly")

    output = PublicSafeOutput(
        object_id=f"public-safe:{source.object_id}",
        content=content,
        source_object_ids=tuple(source_object_ids or (source.object_id,)),
        policy_version=source.policy_version,
        privacy_checked=privacy_checked,
        security_checked=security_checked,
        epistemic_checked=epistemic_checked,
        reidentification_checked=reidentification_checked,
    )
    output.validate()
    return output


def assert_public_output_allowed(output: PublicSafeOutput) -> None:
    """Final server-side gate before PUBLIC serialization."""

    output.validate()


__all__ = [
    "ActorDomain",
    "BOUNDARY_INVARIANTS",
    "BoundaryAction",
    "BoundaryContext",
    "BoundaryDecision",
    "BoundaryError",
    "InformationAccessDenied",
    "InformationClass",
    "InformationClassificationError",
    "InformationObject",
    "PublicReleaseDenied",
    "PublicSafeOutput",
    "assert_no_unauthorized_downgrade",
    "assert_public_output_allowed",
    "authorize_decision_use",
    "authorize_read",
    "build_public_safe_output",
    "can_read",
    "highest_classification",
    "propagate_classification",
]
