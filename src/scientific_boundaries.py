"""Fail-closed epistemic boundaries for causal claims and digital twins."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class CausalIdentificationStatus(StrEnum):
    IDENTIFIED = "IDENTIFIED"
    NOT_IDENTIFIABLE = "NOT_IDENTIFIABLE"


@dataclass(frozen=True)
class CausalIdentificationAssessment:
    estimand: str
    design: str
    temporal_ordering: bool
    positivity: bool
    consistency: bool
    exchangeability: bool
    confounders_declared: bool
    status: CausalIdentificationStatus
    limitations: tuple[str, ...]


def assess_causal_identification(
    *,
    estimand: str,
    design: str,
    temporal_ordering: bool,
    positivity: bool,
    consistency: bool,
    exchangeability: bool,
    confounders_declared: bool,
) -> CausalIdentificationAssessment:
    """Preserve non-identifiability instead of upgrading association to causation."""
    if not estimand.strip() or not design.strip():
        raise ValueError("causal assessment requires an estimand and design")
    checks = {
        "temporal ordering": temporal_ordering,
        "positivity": positivity,
        "consistency": consistency,
        "exchangeability": exchangeability,
        "confounders declared": confounders_declared,
    }
    limitations = tuple(name for name, passed in checks.items() if not passed)
    status = CausalIdentificationStatus.IDENTIFIED if not limitations else CausalIdentificationStatus.NOT_IDENTIFIABLE
    return CausalIdentificationAssessment(
        estimand=estimand,
        design=design,
        temporal_ordering=temporal_ordering,
        positivity=positivity,
        consistency=consistency,
        exchangeability=exchangeability,
        confounders_declared=confounders_declared,
        status=status,
        limitations=limitations,
    )


class DigitalTwinClassification(StrEnum):
    DIGITAL_TWIN = "DIGITAL_TWIN"
    SIMULATION = "SIMULATION"


@dataclass(frozen=True)
class DigitalTwinAssessment:
    classification: DigitalTwinClassification
    requirements_missing: tuple[str, ...]


def assess_digital_twin(
    *,
    real_world_state: bool,
    synchronization: bool,
    bidirectional_coupling: bool,
    parameter_updating: bool,
    validation: bool,
    uncertainty: bool,
    intervention_simulation: bool,
    outcome_comparison: bool,
) -> DigitalTwinAssessment:
    """A simulation is not promoted to digital twin without all required links."""
    checks = {
        "real-world state": real_world_state,
        "synchronization": synchronization,
        "bidirectional coupling": bidirectional_coupling,
        "parameter updating": parameter_updating,
        "validation": validation,
        "uncertainty": uncertainty,
        "intervention simulation": intervention_simulation,
        "outcome comparison": outcome_comparison,
    }
    missing = tuple(name for name, passed in checks.items() if not passed)
    return DigitalTwinAssessment(
        classification=(DigitalTwinClassification.DIGITAL_TWIN if not missing else DigitalTwinClassification.SIMULATION),
        requirements_missing=missing,
    )
