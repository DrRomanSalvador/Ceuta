"""Semantic compatibility checks for registered scientific methods and data."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from math import isfinite
from typing import Mapping, Sequence


class CompatibilityStatus(StrEnum):
    COMPATIBLE = "compatible"
    WARNING = "warning"
    INSUFFICIENT_DATA = "insufficient_data"
    ASSUMPTION_VIOLATION = "assumption_violation"
    OUT_OF_DOMAIN = "out_of_domain"
    NON_IDENTIFIABLE = "non_identifiable"
    METHOD_NOT_JUSTIFIED = "method_not_justified"
    ABSTAIN = "abstain"


@dataclass(frozen=True, slots=True)
class ScientificMethodContract:
    method_id: str
    method_version: str
    source_ids: tuple[str, ...]
    input_schema: str
    required_variables: tuple[str, ...]
    units: tuple[tuple[str, str], ...]
    temporal_resolution: str
    minimum_observations: int
    missingness_constraints: str
    distributional_assumptions: tuple[str, ...]
    spatial_requirements: str
    independence_assumptions: str
    identifiability_requirements: tuple[str, ...]
    applicability_domain: str
    failure_modes: tuple[str, ...]
    output_schema: str
    uncertainty_schema: str
    validation_requirements: tuple[str, ...]
    code_revision: str
    configuration_hash: str

    def __post_init__(self) -> None:
        if not self.method_id or not self.method_version or not self.source_ids or not self.input_schema or not self.output_schema:
            raise ValueError("method identity, provenance and schemas are required")
        if self.minimum_observations < 1 or not self.required_variables or not self.temporal_resolution:
            raise ValueError("method data requirements are incomplete")
        if not self.distributional_assumptions or not self.validation_requirements or not self.code_revision or not self.configuration_hash:
            raise ValueError("method assumptions, validation and reproducibility metadata are required")


@dataclass(frozen=True, slots=True)
class DataCompatibilityContext:
    schema_id: str
    variables: tuple[str, ...]
    units: tuple[tuple[str, str], ...]
    temporal_resolution: str
    observations: int
    missingness_rate: float
    distribution_state: str
    spatial_context: str
    independence_state: str
    point_in_time_valid: bool
    provenance_valid: bool
    intervention_contaminated: bool = False
    domain: str = ""

    def __post_init__(self) -> None:
        if not self.schema_id or not self.variables or self.observations < 0:
            raise ValueError("data compatibility identity is incomplete")
        if not 0 <= self.missingness_rate <= 1:
            raise ValueError("missingness_rate must be in [0,1]")


@dataclass(frozen=True, slots=True)
class CompatibilityAssessment:
    method_id: str
    method_version: str
    status: CompatibilityStatus
    reasons: tuple[str, ...]
    schema_valid: bool
    scientifically_applicable: bool
    method_fingerprint: str


class ScientificMethodCompatibility:
    """Deterministic semantic gate; schema validity is never treated as applicability."""

    def evaluate(self, method: ScientificMethodContract, data: DataCompatibilityContext) -> CompatibilityAssessment:
        reasons: list[str] = []
        schema_valid = data.schema_id == method.input_schema and set(method.required_variables).issubset(data.variables)
        if not schema_valid:
            reasons.append("schema_or_required_variables_mismatch")
        if data.observations < method.minimum_observations:
            reasons.append("insufficient_observations")
        required_units = dict(method.units)
        observed_units = dict(data.units)
        for variable, unit in required_units.items():
            if observed_units.get(variable) != unit:
                reasons.append(f"unit_mismatch:{variable}")
        if data.temporal_resolution != method.temporal_resolution:
            reasons.append("temporal_resolution_mismatch")
        if data.missingness_rate > 0.2:
            reasons.append("missingness_exceeds_default_tolerance")
        if data.distribution_state in {"ood", "extrapolated"}:
            reasons.append("distribution_out_of_domain")
        if data.spatial_context != method.spatial_requirements:
            reasons.append("spatial_requirement_mismatch")
        if data.independence_state not in {"independent", "partially_dependent"}:
            reasons.append("source_independence_unknown")
        if not data.point_in_time_valid:
            reasons.append("point_in_time_invalid")
        if not data.provenance_valid:
            reasons.append("provenance_invalid")
        if data.intervention_contaminated:
            reasons.append("intervention_contamination_requires_independent_validation")
        if "identified" in method.identifiability_requirements and data.independence_state == "unknown":
            reasons.append("identifiability_requirement_not_demonstrated")
        if data.domain and data.domain not in method.applicability_domain.split(","):
            reasons.append("applicability_domain_mismatch")
        hard = {"schema_or_required_variables_mismatch", "insufficient_observations", "distribution_out_of_domain", "spatial_requirement_mismatch", "point_in_time_invalid", "provenance_invalid", "unit_mismatch", "temporal_resolution_mismatch"}
        if any(r == "schema_or_required_variables_mismatch" for r in reasons):
            status = CompatibilityStatus.METHOD_NOT_JUSTIFIED
        elif any(r.startswith("unit_mismatch") for r in reasons) or "temporal_resolution_mismatch" in reasons:
            status = CompatibilityStatus.ASSUMPTION_VIOLATION
        elif "distribution_out_of_domain" in reasons or "applicability_domain_mismatch" in reasons:
            status = CompatibilityStatus.OUT_OF_DOMAIN
        elif "insufficient_observations" in reasons:
            status = CompatibilityStatus.INSUFFICIENT_DATA
        elif "point_in_time_invalid" in reasons or "provenance_invalid" in reasons:
            status = CompatibilityStatus.ABSTAIN
        elif "identifiability_requirement_not_demonstrated" in reasons:
            status = CompatibilityStatus.NON_IDENTIFIABLE
        elif reasons:
            status = CompatibilityStatus.WARNING
        else:
            status = CompatibilityStatus.COMPATIBLE
        applicable = status in {CompatibilityStatus.COMPATIBLE, CompatibilityStatus.WARNING}
        return CompatibilityAssessment(method.method_id, method.method_version, status, tuple(reasons), schema_valid, applicable, _method_fingerprint(method))


def _method_fingerprint(method: ScientificMethodContract) -> str:
    import hashlib, json
    return hashlib.sha256(json.dumps(method.__dict__ if hasattr(method, "__dict__") else {name: getattr(method, name) for name in method.__dataclass_fields__}, sort_keys=True, default=str).encode()).hexdigest()


__all__ = ["CompatibilityAssessment", "CompatibilityStatus", "DataCompatibilityContext", "ScientificMethodCompatibility", "ScientificMethodContract"]
