from app.core.decision.config_provenance import ConfigurationProvenance
from app.core.decision.persistence import SQLiteDecisionStore
from app.core.runtime.decision_lifecycle import DecisionLifecycleEngine


def configuration() -> ConfigurationProvenance:
    return ConfigurationProvenance("cfg", "v1", ("test-config",), {"mode": "test"})


def test_lifecycle_created_governance_is_bound_to_its_store(tmp_path):
    first_store = SQLiteDecisionStore(str(tmp_path / "first.sqlite"))
    first = DecisionLifecycleEngine(
        first_store,
        code_revision="abc123",
        configuration=configuration(),
    )
    second_store = SQLiteDecisionStore(str(tmp_path / "second.sqlite"))
    second = DecisionLifecycleEngine(
        second_store,
        code_revision="def456",
        configuration=configuration(),
    )

    assert first.scientific_governance.storage_path == str(tmp_path / "first.sqlite")
    assert second.scientific_governance.storage_path == str(tmp_path / "second.sqlite")
    assert first.scientific_governance.storage_path != second.scientific_governance.storage_path

    first_store.close()
    second_store.close()
