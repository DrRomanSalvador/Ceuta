from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class SemanticClassification(StrEnum):
    """Classification used when comparing two implementations."""

    IDENTICAL = "IDÉNTICA"
    EQUIVALENT = "EQUIVALENTE"
    PARTIAL = "PARCIAL"
    DISTINCT = "DISTINTA"
    INCOMPATIBLE = "INCOMPATIBLE"


class MissingDataPolicy(StrEnum):
    """Explicit policy for missing values; silent imputation is not allowed."""

    PRESERVE = "PRESERVE"
    REJECT = "REJECT"
    EXPLICIT_IMPUTATION = "EXPLICIT_IMPUTATION"


@dataclass(frozen=True, slots=True)
class SemanticContract:
    """Machine-readable contract for a metric or transformation.

    A contract captures the semantic surface that must remain stable when an
    implementation is refactored or reconstructed. Numerical agreement alone
    is insufficient for compatibility.
    """

    name: str
    canonical_name: str
    formula: str
    input_domain: str
    output_domain: str
    units: str | None
    normalization: str | None
    missing_data_policy: MissingDataPolicy
    nan_policy: str
    zero_policy: str
    error_policy: str
    temporal_semantics: str
    spatial_semantics: str
    epistemic_role: str
    dependencies: tuple[str, ...] = ()
    version: str = "1"

    def __post_init__(self) -> None:
        for field_name in (
            "name",
            "canonical_name",
            "formula",
            "input_domain",
            "output_domain",
            "nan_policy",
            "zero_policy",
            "error_policy",
            "temporal_semantics",
            "spatial_semantics",
            "epistemic_role",
        ):
            value = getattr(self, field_name)
            if not value.strip():
                raise ValueError(f"{field_name} must not be empty")

        if not self.version.strip():
            raise ValueError("version must not be empty")

    def compatibility_reasons(self, other: SemanticContract) -> tuple[str, ...]:
        """Return contract-level reasons why two implementations differ."""
        differences: list[str] = []
        fields = (
            "formula",
            "input_domain",
            "output_domain",
            "units",
            "normalization",
            "missing_data_policy",
            "nan_policy",
            "zero_policy",
            "error_policy",
            "temporal_semantics",
            "spatial_semantics",
            "epistemic_role",
            "dependencies",
        )
        for field_name in fields:
            left = getattr(self, field_name)
            right = getattr(other, field_name)
            if left != right:
                differences.append(field_name)
        return tuple(differences)

    def is_semantically_compatible_with(self, other: SemanticContract) -> bool:
        """Whether the contracts are interchangeable without semantic loss."""
        return not self.compatibility_reasons(other)


__all__ = [
    "MissingDataPolicy",
    "SemanticClassification",
    "SemanticContract",
]
