import json
import sqlite3

import pytest

from app.core.scientific.scientific_method_registry import ScientificMethodRegistry, ScientificMethodRelease


def test_method_release_persists_preprocessing_assumptions_and_sources(tmp_path):
    registry = ScientificMethodRegistry(str(tmp_path / "methods.sqlite"))
    release = ScientificMethodRelease(
        "csd", "2", "critical_slowing_down",
        ("detrend:linear", "window:0.5"),
        ("stationary_noise", "adequate_sampling"),
        "prospective-window-2026",
        "supporting resilience diagnostic only",
        ("dakos-2012-csd-robustness", "dakos-2026-ews-overview"),
        "test-revision", "config-hash",
    )
    registry.register(release)
    assert len(release.fingerprint) == 64
    assert registry.verify_integrity()


def test_method_registry_rejects_tampered_payload_on_read(tmp_path):
    database = tmp_path / "methods-tampered.sqlite"
    registry = ScientificMethodRegistry(str(database))
    release = ScientificMethodRelease(
        "csd", "3", "critical_slowing_down",
        ("window:0.5",),
        ("adequate_sampling",),
        "prospective-window-2026",
        "supporting diagnostic",
        ("source-a",),
        "revision-a", "config-a",
    )
    registry.register(release)

    connection = sqlite3.connect(database)
    try:
        payload = json.loads(connection.execute("SELECT payload FROM scientific_method_releases WHERE method_id=? AND version=?", ("csd", "3")).fetchone()[0])
        payload["applicability_boundary"] = "tampered"
        connection.execute(
            "UPDATE scientific_method_releases SET payload=? WHERE method_id=? AND version=?",
            (json.dumps(payload, sort_keys=True, separators=(",", ":")), "csd", "3"),
        )
        connection.commit()
    finally:
        connection.close()

    with pytest.raises(RuntimeError, match="integrity mismatch"):
        registry.get("csd", "3")
    assert not registry.verify_integrity()
