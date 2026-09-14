from datetime import datetime, timedelta, timezone

from app.core.epistemology_p0.evidence.models import Evidence, EpistemicStatus
from app.core.epistemology_p0.registry import ClaimRegistry


def _evidence(version: int, revision_time: datetime) -> Evidence:
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    return Evidence(
        evidence_id="e1", version=version, source_id="source-1", document_id="doc-1", claim_id="claim-1",
        event_id=None, value=float(version), unit=None, semantic_definition="test evidence", location=None,
        event_time=base, publication_time=base, ingestion_time=base + timedelta(hours=1), revision_time=revision_time,
        detection_time=None, assessment_time=None, impact_time=None, methodology=None,
        source_reliability=1.0, source_independence="independent", uncertainty=None, provenance=[],
        transformation_history=[], corroboration=[], contradictions=[],
        epistemic_status=EpistemicStatus.OBSERVED_FACT,
    )


def test_registry_backtest_uses_version_available_at_historical_cutoff():
    base = datetime(2026, 1, 1, tzinfo=timezone.utc)
    first = _evidence(1, base + timedelta(hours=1))
    second = _evidence(2, base + timedelta(hours=3))
    registry = ClaimRegistry()
    registry.add_evidence(first)
    registry.add_evidence_version(second)
    historical = registry.get_evidences_for_backtest(base + timedelta(hours=2))
    current = registry.get_evidences_for_backtest(base + timedelta(hours=4))
    assert historical == [first]
    assert current == [second]
