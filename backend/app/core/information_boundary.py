"""CeutIA information-flow confidentiality boundary.

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
