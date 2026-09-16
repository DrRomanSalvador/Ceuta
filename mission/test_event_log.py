import tempfile
import unittest
from pathlib import Path

from .event_log import GENESIS_HASH, append_event, make_event, validate_chain


class EventLogTests(unittest.TestCase):
    def test_genesis_event_is_hash_valid(self):
        event = make_event(event_id="E1", event_type="GENESIS", mission_id="MISSION-01", actor="MISSION-01", timestamp="2026-09-16T00:00:00Z", payload={})
        self.assertEqual(validate_chain([event]), event["hash"])

    def test_append_requires_exact_predecessor(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            first = make_event(event_id="E1", event_type="GENESIS", mission_id="MISSION-01", actor="MISSION-01", timestamp="2026-09-16T00:00:00Z", payload={})
            append_event(path, first)
            bad = make_event(event_id="E2", event_type="TEST", mission_id="MISSION-01", actor="MISSION-01", timestamp="2026-09-16T00:01:00Z", payload={}, previous_hash=GENESIS_HASH)
            with self.assertRaises(ValueError):
                append_event(path, bad)

    def test_tampering_breaks_chain(self):
        first = make_event(event_id="E1", event_type="GENESIS", mission_id="MISSION-01", actor="MISSION-01", timestamp="2026-09-16T00:00:00Z", payload={})
        tampered = dict(first, payload={"tampered": True})
        with self.assertRaises(ValueError):
            validate_chain([tampered])


if __name__ == "__main__":
    unittest.main()
