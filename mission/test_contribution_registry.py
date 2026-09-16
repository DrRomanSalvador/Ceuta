import json
import tempfile
import unittest
from pathlib import Path

from .contribution_registry import record


class ContributionRegistryTests(unittest.TestCase):
    def test_attribution_is_persisted_and_duplicates_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"registry.json"
            path.write_text(json.dumps({"items":[]}), encoding="utf-8")
            contribution={
                "contribution_id":"C1", "artifact":"mission/x", "claim_or_change":"x", "evidence":["commit"], "timestamp":"2026-09-16T12:00:00Z",
                "DISCOVERED_BY":"MISSION-01", "PROPOSED_BY":"MISSION-01", "IMPLEMENTED_BY":"MISSION-02", "REVIEWED_BY":"MISSION-03", "VALIDATED_BY":"MISSION-03", "AUTHORIZED_BY":"HUMAN",
            }
            record(path, contribution)
            self.assertEqual(json.loads(path.read_text())["items"][0]["IMPLEMENTED_BY"], "MISSION-02")
            with self.assertRaises(ValueError):
                record(path, contribution)

    def test_missing_attribution_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"registry.json"
            path.write_text(json.dumps({"items":[]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                record(path, {"contribution_id":"C1", "artifact":"x", "claim_or_change":"x", "evidence":["e"], "timestamp":"t"})


if __name__ == "__main__":
    unittest.main()
