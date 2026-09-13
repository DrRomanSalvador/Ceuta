import pytest

from backend.app.core.decision.outcome_semantics import (
    OutcomeDefinition,
    OutcomeObservation,
    OutcomeSemantics,
    OutcomeStatus,
)


def _definition() -> OutcomeDefinition:
    return OutcomeDefinition(
        outcome_id="outcome-1",
        target="decision utility",
        estimand="realized utility over decision horizon",
        measurement="utility score",
        unit="points",
        direction="higher_is_better",
        time_zero="decision execution",
        horizon="30d",
        observation_window="day-30",
    )


def test_observed_outcome_is_comparable_only_with_matching_window() -> None:
    definition = _definition()
    observation = OutcomeObservation(
        outcome_id="outcome-1",
        value=0.8,
        status=OutcomeStatus.OBSERVED,
        observed_at="2026-09-13T10:00:00+00:00",
        source_refs=("source:1",),
        observation_window="day-30",
    )
    assert OutcomeSemantics(definition, observation).decision_comparable()


def test_reported_or_mismatched_outcome_cannot_be_treated_as_observed() -> None:
    definition = _definition()
    observation = OutcomeObservation(
        outcome_id="outcome-1",
        value=0.8,
        status=OutcomeStatus.REPORTED,
        observed_at="2026-09-13T10:00:00+00:00",
        source_refs=("source:1",),
        observation_window="day-30",
    )
    assert not OutcomeSemantics(definition, observation).decision_comparable()


def test_observed_value_requires_source_reference() -> None:
    with pytest.raises(ValueError):
        OutcomeObservation(
            outcome_id="outcome-1",
            value=0.8,
            status=OutcomeStatus.OBSERVED,
            observed_at="2026-09-13T10:00:00+00:00",
            observation_window="day-30",
        )
