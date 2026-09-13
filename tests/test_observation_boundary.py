from datetime import datetime, timedelta, timezone

import pytest

from app.core.observation_boundary import (
    ObservationBoundaryError,
    admit_observation,
    available_at,
)
from app.core.p0_contracts import EvidenceContract, EpistemicStatus, SourceRelation, Uncertainty


T0 = datetime(2026, 9, 13, 8, 0, tzinfo=timezone.utc)


def evidence(**overrides: object) -> EvidenceContract:
    data: dict[str, object] = {
        "evidence_id": "OBS-1",
        "claim": "A documented event occurred",
        "source_id": "SRC-1",
        "observed_at": T0,
        "ingestion_time": T0 + timedelta(minutes=1),
        "uncertainty": Uncertainty(
            kind="interval", lower=0.1, upper=0.2, description="test uncertainty"
        ),
        "epistemic_status": EpistemicStatus.ATTRIBUTED_CLAIM,
        "source_relation": SourceRelation.INDEPENDENT,
    }
    data.update(overrides)
    return EvidenceContract.model_validate(data)


def test_event_time_is_not_used_as_availability_time():
    item = evidence(event_time=T0 - timedelta(days=30))
    assert available_at(item) == T0


def test_publication_time_controls_availability_when_present():
    publication = T0 + timedelta(hours=2)
    item = evidence(
        event_time=T0 - timedelta(days=30),
        publication_time=publication,
        observed_at=publication,
        ingestion_time=publication + timedelta(minutes=1),
    )
    assert available_at(item) == publication


def test_future_publication_cannot_enter_historical_analysis():
    item = evidence(
        publication_time=T0 + timedelta(hours=1),
        observed_at=T0 + timedelta(hours=1),
        ingestion_time=T0 + timedelta(hours=1, minutes=1),
    )
    with pytest.raises(ObservationBoundaryError, match="not eligible"):
        admit_observation(item, evaluation_time=T0)


def test_current_observation_is_admitted_without_epistemic_upgrade():
    item = evidence()
    admitted, eligibility = admit_observation(item, evaluation_time=T0 + timedelta(minutes=5))
    assert admitted.evidence_id == item.evidence_id
    assert admitted.epistemic_status == EpistemicStatus.ATTRIBUTED_CLAIM
    assert eligibility.eligible is True


def test_boundary_does_not_resolve_contradiction():
    item = evidence(epistemic_status=EpistemicStatus.CONTRADICTED)
    admitted, _ = admit_observation(item, evaluation_time=T0 + timedelta(minutes=5))
    assert admitted.epistemic_status == EpistemicStatus.CONTRADICTED
