import json
import tempfile
import unittest
from pathlib import Path

from .contribution_registry import record
from .event_log import load_jsonl, validate_chain


class ContributionRegistryTests(unittest.TestCase):
    def _contribution(self):
        return {
            "contribution_id": "C1",
            "mission_id": "MISSION-01",
            "artifact": "mission/x",
            "claim_or_change": "x",
            "evidence": ["commit"],
            "timestamp": "2026-09-16T12:00:00Z",
            "DISCOVERED_BY": "MISSION-01",
            "PROPOSED_BY": "MISSION-01",
            "IMPLEMENTED_BY": "MISSION-02",
            "REVIEWED_BY": "MISSION-03",
            "VALIDATED_BY": "MISSION-03",
            "AUTHORIZED_BY": "HUMAN",
        }

    def test_attribution_is_persisted_and_duplicates_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.json"
            events = Path(tmp) / "events.jsonl"
            path.write_text(json.dumps({"items": []}), encoding="utf-8")
            contribution = self._contribution()
            record(path, contribution, event_log=events, actor="MISSION-01")
            persisted = json.loads(path.read_text())["items"][0]
            self.assertEqual(persisted["IMPLEMENTED_BY"], "MISSION-02")
            self.assertEqual(persisted["mutation_event_id"], "EV-0001")
            with self.assertRaises(ValueError):
                record(path, contribution, event_log=events, actor="MISSION-01")
            validate_chain(load_jsonl(events))

    def test_missing_attribution_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.json"
            events = Path(tmp) / "events.jsonl"
            path.write_text(json.dumps({"items": []}), encoding="utf-8")
            contribution = self._contribution()
            contribution.pop("AUTHORIZED_BY")
            with self.assertRaises(ValueError):
                record(path, contribution, event_log=events, actor="MISSION-01")

    def test_missing_event_contract_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.json"
            path.write_text(json.dumps({"items": []}), encoding="utf-8")
            with self.assertRaises(TypeError):
                record(path, self._contribution())


if __name__ == "__main__":
    unittest.main()
