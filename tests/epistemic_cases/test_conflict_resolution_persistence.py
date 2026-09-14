from backend.app.core.decision.persistence import SQLiteDecisionStore
from backend.app.core.evidence.conflict_resolution import EvidenceResolution, ResolutionDisposition


def test_conflict_resolution_round_trip(tmp_path):
    store = SQLiteDecisionStore(str(tmp_path / "decisions.db"))
    resolution = EvidenceResolution("c1", ResolutionDisposition.HUMAN_REVIEW, (), "requires comparative appraisal", "policy-1")
    store.record_conflict_resolution("d1", resolution)
    assert store.schema_version == 4
    assert store.conflict_resolutions("d1") == (resolution,)
    store.close()
