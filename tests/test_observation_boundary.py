from datetime import UTC, datetime, timedelta

import pytest

from app.core.observation_boundary import (
    ObservationBoundaryError,
    admit_observation,
    available_at,
)
from app.core.p0_contracts import (
    EpistemicStatus,
    EvidenceContract,
    SourceRelation,
    Uncertainty,
)

T0 = datetime(2026, 9, 13, 8, 0, tzinfo=UTC)


def evidence(**overrides: object) -> EvidenceContract:
    data: dict[str, object] = {
        "evidence_id": "E-1",
        "claim": "documented claim",
        "source_id": "S-1",
        "observed_at": T0,
        "ingestion_time": T0 + timedelta(minutes=1),
        "uncertainty": Uncertainty(kind="unknown", description="not quantified"),
        "epistemic_status": EpistemicStatus.UNKNOWN,
        "source_relation": SourceRelation.UNKNOWN,
    }
    data.update(overrides)
    return EvidenceContract.model_validate(data)


def test_event_time_never_controls_availability() -> None:
    ev = evidence(
        event_time=T0 - timedelta(days=30),
        publication_time=T0 + timedelta(days=1),
        ingestion_time=T0 + timedelta(days=1, minutes=1),
    )
    assert available_at(ev) == T0 + timedelta(days=1)


def test_publication_time_controls_availability_when_present() -> None:
    ev = evidence(publication_time=T0 - timedelta(hours=1))
    assert available_at(ev) == T0 - timedelta(hours=1)


def test_revision_time_controls_exact_version_availability() -> None:
    ev = evidence(
        publication_time=T0 - timedelta(days=2),
        revision_time=T0 + timedelta(hours=2),
        ingestion_time=T0 + timedelta(hours=3),
    )
    assert available_at(ev) == T0 + timedelta(hours=2)


def test_future_publication_is_rejected() -> None:
    ev = evidence(
        publication_time=T0 + timedelta(hours=1),
        ingestion_time=T0 + timedelta(hours=1, minutes=1),
    )
    with pytest.raises(ObservationBoundaryError):
        admit_observation(ev, evaluation_time=T0)


def test_revision_after_evaluation_is_rejected() -> None:
    ev = evidence(
        publication_time=T0 - timedelta(days=1),
        revision_time=T0 + timedelta(hours=1),
        ingestion_time=T0 + timedelta(hours=2),
    )
    with pytest.raises(ObservationBoundaryError):
        admit_observation(ev, evaluation_time=T0)


def test_current_observation_is_admitted_without_epistemic_upgrade() -> None:
    ev = evidence()
    admitted, eligibility = admit_observation(ev, evaluation_time=T0 + timedelta(minutes=1))
    assert admitted.epistemic_status is EpistemicStatus.UNKNOWN
    assert eligibility.eligible is True


def test_unknown_status_is_preserved() -> None:
    ev = evidence(epistemic_status=EpistemicStatus.UNKNOWN)
    admitted, _ = admit_observation(ev, evaluation_time=T0 + timedelta(minutes=1))
    assert admitted.epistemic_status is EpistemicStatus.UNKNOWN


def test_contradicted_status_is_preserved() -> None:
    ev = evidence(epistemic_status=EpistemicStatus.CONTRADICTED)
    admitted, _ = admit_observation(ev, evaluation_time=T0 + timedelta(minutes=1))
    assert admitted.epistemic_status is EpistemicStatus.CONTRADICTED
