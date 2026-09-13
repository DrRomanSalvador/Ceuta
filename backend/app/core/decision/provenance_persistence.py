"""Durable policy/configuration provenance persistence for CeutIA."""
from __future__ import annotations

import json
import sqlite3

from .config_provenance import ConfigurationProvenance
from .policy import PolicyProvenance


class DecisionProvenanceStore:
    """Append-only versioned persistence for policy and execution configuration provenance."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self.connection = connection
        self.connection.executescript("""
CREATE TABLE IF NOT EXISTS decision_policy_provenance (
    policy_id TEXT NOT NULL,
    version TEXT NOT NULL,
    semantic_fingerprint TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    PRIMARY KEY(policy_id, version)
);
CREATE TABLE IF NOT EXISTS decision_configuration_provenance (
    configuration_id TEXT NOT NULL,
    version TEXT NOT NULL,
    fingerprint TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    PRIMARY KEY(configuration_id, version)
);
""")
        self.connection.commit()

    def record_policy(self, policy: PolicyProvenance) -> None:
        self.connection.execute(
            "INSERT OR REPLACE INTO decision_policy_provenance(policy_id,version,semantic_fingerprint,payload_json) VALUES(?,?,?,?)",
            (policy.policy_id, policy.version, policy.semantic_fingerprint(), json.dumps(policy.semantic_payload(), sort_keys=True, ensure_ascii=False, separators=(",", ":"))),
        )
        self.connection.commit()

    def policy(self, policy_id: str, version: str) -> PolicyProvenance | None:
        row = self.connection.execute("SELECT payload_json FROM decision_policy_provenance WHERE policy_id=? AND version=?", (policy_id, version)).fetchone()
        if row is None:
            return None
        payload = json.loads(row[0])
        payload["source_refs"] = tuple(payload["source_refs"])
        return PolicyProvenance(**payload)

    def record_configuration(self, configuration: ConfigurationProvenance) -> None:
        self.connection.execute(
            "INSERT OR REPLACE INTO decision_configuration_provenance(configuration_id,version,fingerprint,payload_json) VALUES(?,?,?,?)",
            (configuration.configuration_id, configuration.version, configuration.fingerprint(), json.dumps(configuration.canonical_payload(), sort_keys=True, ensure_ascii=False, separators=(",", ":"))),
        )
        self.connection.commit()

    def configuration(self, configuration_id: str, version: str) -> ConfigurationProvenance | None:
        row = self.connection.execute("SELECT payload_json FROM decision_configuration_provenance WHERE configuration_id=? AND version=?", (configuration_id, version)).fetchone()
        if row is None:
            return None
        payload = json.loads(row[0])
        payload["source_refs"] = tuple(payload["source_refs"])
        return ConfigurationProvenance(**payload)


__all__ = ["DecisionProvenanceStore"]
