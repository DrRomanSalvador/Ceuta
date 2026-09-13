from backend.app.core.decision.longitudinal import LongitudinalEvaluation, LongitudinalObservation


def test_training_and_evaluation_observations_are_temporally_separated() -> None:
    observations = (
        LongitudinalObservation("entity-1", "decision-1", "2026-09-01T10:00:00+00:00", 0.5),
        LongitudinalObservation("entity-1", "decision-2", "2026-09-20T10:00:00+00:00", 0.7),
    )
    evaluation = LongitudinalEvaluation(
        observations=observations,
        training_cutoff="2026-09-10T00:00:00+00:00",
        evaluation_start="2026-09-15T00:00:00+00:00",
    )
    assert tuple(item.decision_id for item in evaluation.training_observations()) == ("decision-1",)
    assert tuple(item.decision_id for item in evaluation.evaluation_observations()) == ("decision-2",)
