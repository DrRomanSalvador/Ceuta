"""Explicit information-boundary semantics for decision inputs and outputs."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class InformationVisibility(StrEnum):
    PUBLIC = "public"
    RESTRICTED = "restricted"
    OWNER_ONLY = "owner_only"


@dataclass(frozen=True, slots=True)
class InformationBoundary:
    visibility: InformationVisibility
    owner_scope: str | None = None

    def __post_init__(self) -> None:
        if self.visibility is InformationVisibility.OWNER_ONLY and not self.owner_scope:
            raise ValueError("owner_only information requires an owner_scope")
        if self.visibility is not InformationVisibility.OWNER_ONLY and self.owner_scope:
            raise ValueError("owner_scope is only valid for owner_only information")

    def may_emit(self, target: InformationVisibility) -> bool:
        if self.visibility is InformationVisibility.OWNER_ONLY:
            return target is InformationVisibility.OWNER_ONLY
        if self.visibility is InformationVisibility.RESTRICTED:
            return target in {InformationVisibility.RESTRICTED, InformationVisibility.OWNER_ONLY}
        return target in {InformationVisibility.PUBLIC, InformationVisibility.RESTRICTED, InformationVisibility.OWNER_ONLY}

    def assert_emit(self, target: InformationVisibility) -> None:
        if not self.may_emit(target):
            raise PermissionError(f"information boundary violation: {self.visibility} -> {target}")


__all__ = ["InformationBoundary", "InformationVisibility"]
