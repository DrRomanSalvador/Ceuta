from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from app.core.p0_contracts import (
    EpistemicStatus,
    EvidenceContract,
    ProvenanceLink,
    SourceRelation,
    Uncertainty,
    evaluate_temporal_eligibility,
    independent_source_count,
)

T0 = datetime(2026, 9, 13, 8, 0, tzinfo=UTC)


def uncertainty() -> Uncertainty:
    return Uncertainty(kind="interval", lower=0.1, upper=0.2, description="test interval")


def evidence(**overrides: object) -> EvidenceContract:
    data: dict[str, object] = {
        "evidence_id": "E-1",
        "claim": "A documented observation exists",
        "source_id": "S-1",
        "observed_at": T0,
        "ingestion_time": T0 + timedelta(minutes=1),
        "uncertainty": uncertainty(),
        "epistemic_status": EpistemicStatus.ATTRIBUTED_CLAIM,
        "source_relation": SourceRelation.INDEPENDENT,
    }
    data.update(overrides)
    return EvidenceContract.model_validate(data)


def test_single_source_cannot_be_corrobated():
    with pytest.raises(ValidationError, match="at least two independent sources"):
        evidence(
            epistemic_status=EpistemicStatus.CORROBORATED_FACT,
            independent_source_count=1,
            corroborating_evidence_ids=("E-2",),
        )


def test_dependent_sources_do_not_count_as_independent():
    assert independent_source_count(
        [SourceRelation.DEPENDENT, SourceRelation.COPY, SourceRelation.AMPLIFIER]
    ) == 0


def test_two_independent_sources_can_support_corrobation():
    result = evidence(
        epistemic_status=EpistemicStatus.CORROBORATED_FACT,
        independent_source_count=2,
        corroborating_evidence_ids=("E-2",),
    )
    assert result.epistemic_status == EpistemicStatus.CORROBORATED_FACT


def test_contradiction_is_preserved_as_status():
    result = evidence(epistemic_status=EpistemicStatus.CONTRADICTED)
    assert result.epistemic_status == EpistemicStatus.CONTRADICTED


def test_correction_is_a_new_version_not_silent_overwrite():
    original = evidence(evidence_id="E-1")
    corrected = evidence(evidence_id="E-1-v2", limitations=("corrected source value",))
    assert original.evidence_id != corrected.evidence_id
    assert corrected.limitations == ("corrected source value",)


def test_publication_may_postdate_event():
    result = evidence(
        event_time=T0 - timedelta(days=1),
        publication_time=T0,
        observed_at=T0 + timedelta(minutes=1),
        ingestion_time=T0 + timedelta(minutes=2),
    )
    assert result.event_time < result.publication_time


def test_ingestion_before_publication_is_rejected():
    with pytest.raises(ValidationError, match="cannot precede publication"):
        evidence(
            publication_time=T0 + timedelta(hours=1),
            observed_at=T0,
            ingestion_time=T0 + timedelta(minutes=1),
        )


def test_backtest_without_temporal_leakage_is_eligible():
    result = evaluate_temporal_eligibility(
        evidence_id="E-1", available_at=T0 - timedelta(minutes=1), evaluation_time=T0
    )
    assert result.eligible is True


def test_backtest_with_future_information_is_rejected():
    result = evaluate_temporal_eligibility(
        evidence_id="E-future", available_at=T0 + timedelta(seconds=1), evaluation_time=T0
    )
    assert result.eligible is False


def test_synthetic_or_manipulated_content_is_not_implicitly_truthful():
    result = evidence(
        source_relation=SourceRelation.UNKNOWN,
        limitations=("content origin requires verification",),
    )
    assert result.epistemic_status == EpistemicStatus.ATTRIBUTED_CLAIM
    assert result.source_relation == SourceRelation.UNKNOWN


def test_missing_uncertainty_is_rejected():
    data = {
        "evidence_id": "E-missing-uncertainty",
        "claim": "Claim",
        "source_id": "S-1",
        "observed_at": T0,
        "ingestion_time": T0,
        "epistemic_status": EpistemicStatus.UNVERIFIED,
        "source_relation": SourceRelation.UNKNOWN,
    }
    with pytest.raises(ValidationError):
        EvidenceContract.model_validate(data)


def test_unknown_remains_unknown_until_evidence_supports_transition():
    result = evidence(epistemic_status=EpistemicStatus.UNKNOWN)
    assert result.epistemic_status == EpistemicStatus.UNKNOWN


def test_observation_after_ingestion_is_rejected():
    with pytest.raises(ValidationError, match="observed_at cannot be later"):
        evidence(observed_at=T0 + timedelta(minutes=2), ingestion_time=T0 + timedelta(minutes=1))


def test_timezone_is_mandatory():
    with pytest.raises(ValidationError, match="timezone-aware"):
        evidence(observed_at=datetime(2026, 9, 13, 8, 0))  # noqa: DTZ001


def test_provenance_requires_transformation_and_source_version():
    result = evidence(
        provenance=(
            ProvenanceLink(
                source_id="S-1",
                source_version="2026-09-13",
                relation=SourceRelation.INDEPENDENT,
                transformation="raw-document-to-observation",
            ),
        )
    )
    assert result.provenance[0].transformation == "raw-document-to-observation"
