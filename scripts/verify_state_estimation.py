from datetime import datetime, timezone

from app.core.pipeline.contracts import ObservationRecord
from app.core.state.estimation import ScalarKalmanFilter


def make_observation(observation_id: str, value: float, second: int) -> ObservationRecord:
    timestamp = datetime(2026, 1, 1, 0, 0, second, tzinfo=timezone.utc)
    return ObservationRecord(
        observation_id=observation_id,
        variable="signal",
        value=value,
        unit="u",
        event_time=timestamp,
        available_at=timestamp,
        source_ids=("synthetic-source",),
        evidence_ids=(observation_id,),
        domain="synthetic",
        quality=1.0,
        provenance_hash=f"synthetic-{observation_id}",
    )


def main() -> None:
    estimator = ScalarKalmanFilter("signal", 0.0, 4.0, 0.1)
    series = estimator.filter(
        (make_observation("o1", 10.0, 0), make_observation("o2", 14.0, 10)),
        (1.0, 1.0),
    )
    assert len(series.estimates) == 2
    assert series.estimates[0].mean == 8.0
    assert series.estimates[1].prior_variance == 1.8
    assert series.estimates[1].variance >= 0.0
    print("STATE_ESTIMATION_VERIFIER: PASS")


if __name__ == "__main__":
    main()
