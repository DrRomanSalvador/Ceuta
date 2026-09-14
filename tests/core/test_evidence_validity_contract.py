from datetime import datetime, timedelta, timezone

import pytest

from app.core.epistemology_p0.evidence.models import Evidence, EpistemicStatus


def _evidence(**kwargs):
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    defaults = dict(
        evidence_id="e1", version=1, source_id="source-1", document_id="doc-1", claim_id="claim-1",
        event_id=None, value=1.0, unit=None, semantic_definition="test evidence", location=None,
        event_time=base, publication_time=base, ingestion_time=base + timedelta(hours=1), revision_time=None,
        detection_time=None, assessment_time=None, impact_time=None, methodology=None,
        source_reliability=1.0, source_independence="independent", uncertainty=None, provenance=[],
        transformation_history=[], corroboration=[], contradictions=[],
        epistemic_status=EpistemicStatus.OBSERVED_FACT,
    )
    defaults.update(kwargs)
    return Evidence(**defaults)


def test_evidence_effective_validity_is_point_in_time_aware():
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    evidence = _evidence(valid_from=base + timedelta(hours=1), valid_to=base + timedelta(hours=3))
    assert not evidence.is_valid_at(base)
    assert evidence.is_valid_at(base + timedelta(hours=2))
    assert not evidence.is_valid_at(base + timedelta(hours=3))


def test_evidence_rejects_reversed_effective_interval():
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="valid_from"):
        _evidence(valid_from=base + timedelta(hours=3), valid_to=base + timedelta(hours=1))
