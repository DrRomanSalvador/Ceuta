import pytest

from .scientific_boundaries import (
    CausalIdentificationStatus,
    DigitalTwinClassification,
    assess_causal_identification,
    assess_digital_twin,
)


def test_causal_assessment_preserves_non_identifiability() -> None:
    assessment = assess_causal_identification(
        estimand="average treatment effect",
        design="observational cohort",
        temporal_ordering=True,
        positivity=True,
        consistency=True,
        exchangeability=False,
        confounders_declared=True,
    )
    assert assessment.status == CausalIdentificationStatus.NOT_IDENTIFIABLE
    assert "exchangeability" in assessment.limitations


def test_causal_identification_requires_explicit_design_and_estimand() -> None:
    with pytest.raises(ValueError):
        assess_causal_identification(
            estimand="",
            design="cohort",
            temporal_ordering=True,
            positivity=True,
            consistency=True,
            exchangeability=True,
            confounders_declared=True,
        )


def test_simulation_cannot_be_called_digital_twin() -> None:
    assessment = assess_digital_twin(
        real_world_state=True,
        synchronization=True,
        bidirectional_coupling=False,
        parameter_updating=True,
        validation=True,
        uncertainty=True,
        intervention_simulation=True,
        outcome_comparison=True,
    )
    assert assessment.classification == DigitalTwinClassification.SIMULATION
    assert "bidirectional coupling" in assessment.requirements_missing


def test_complete_requirements_allow_digital_twin_classification() -> None:
    assessment = assess_digital_twin(
        real_world_state=True,
        synchronization=True,
        bidirectional_coupling=True,
        parameter_updating=True,
        validation=True,
        uncertainty=True,
        intervention_simulation=True,
        outcome_comparison=True,
    )
    assert assessment.classification == DigitalTwinClassification.DIGITAL_TWIN
