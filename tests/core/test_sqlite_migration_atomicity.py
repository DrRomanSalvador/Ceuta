import sqlite3

import pytest

from app.core.decision.persistence import SQLiteDecisionStore


def test_new_store_migrates_atomically_and_reaches_current_schema(tmp_path):
    path = tmp_path / "decision.sqlite"
    store = SQLiteDecisionStore(str(path))
    assert store.schema_version == SQLiteDecisionStore.SCHEMA_VERSION
    tables = {row[0] for row in store.connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"decision_audit", "decision_outcomes", "decision_lineage", "decision_conflict_resolutions", "evidence_sources", "claim_evidence_links", "citation_traces"} <= tables
    store.close()


def test_newer_schema_version_fails_closed_before_writes(tmp_path):
    path = tmp_path / "future.sqlite"
    connection = sqlite3.connect(path)
    connection.execute("CREATE TABLE ceutia_schema_version (version INTEGER NOT NULL)")
    connection.execute("INSERT INTO ceutia_schema_version(version) VALUES (?)", (SQLiteDecisionStore.SCHEMA_VERSION + 1,))
    connection.commit()
    connection.close()

    with pytest.raises(RuntimeError, match="newer than supported"):
        SQLiteDecisionStore(str(path))
