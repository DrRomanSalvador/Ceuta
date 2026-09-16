import tempfile
import unittest
from pathlib import Path

from .event_log import load_jsonl, validate_chain
from .work_claims import acquire, load_claims, release


class WorkClaimLedgerTests(unittest.TestCase):
    def _paths(self, tmp):
        return Path(tmp) / "claims.json", Path(tmp) / "events.jsonl"

    def test_claim_persists_and_duplicate_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, events = self._paths(tmp)
            claim = acquire(path, work_id="W1", mission_id="MISSION-01", actor="agent-1", lease_id="L1", lease_expires_at="2026-09-16T12:00:00Z", now="2026-09-16T11:00:00Z", event_log=events)
            self.assertEqual(load_claims(path)["claims"]["W1"]["status"], "ACTIVE")
            self.assertEqual(claim["lease_id"], "L1")
            self.assertEqual(claim["mutation_event_id"], "EV-0001")
            with self.assertRaises(RuntimeError):
                acquire(path, work_id="W1", mission_id="MISSION-01", actor="agent-2", lease_id="L2", lease_expires_at="2026-09-16T13:00:00Z", now="2026-09-16T11:30:00Z", event_log=events)

    def test_expired_claim_can_be_reacquired_and_event_lineage_preserves_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, events = self._paths(tmp)
            acquire(path, work_id="W1", mission_id="MISSION-01", actor="agent-1", lease_id="L1", lease_expires_at="2026-09-16T12:00:00Z", now="2026-09-16T11:00:00Z", event_log=events)
            claim = acquire(path, work_id="W1", mission_id="MISSION-01", actor="agent-2", lease_id="L2", lease_expires_at="2026-09-16T14:00:00Z", now="2026-09-16T12:01:00Z", event_log=events)
            self.assertEqual(claim["lease_id"], "L2")
            self.assertEqual(load_claims(path)["claims"]["W1"]["status"], "ACTIVE")
            self.assertEqual(len(load_jsonl(events)), 2)
            validate_chain(load_jsonl(events))

    def test_only_claiming_actor_can_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, events = self._paths(tmp)
            acquire(path, work_id="W1", mission_id="MISSION-01", actor="agent-1", lease_id="L1", lease_expires_at="2026-09-16T13:00:00Z", now="2026-09-16T11:00:00Z", event_log=events)
            with self.assertRaises(PermissionError):
                release(path, work_id="W1", actor="agent-2", now="2026-09-16T11:30:00Z", event_log=events)
            released = release(path, work_id="W1", actor="agent-1", now="2026-09-16T11:30:00Z", event_log=events)
            self.assertEqual(released["status"], "RELEASED")
            self.assertTrue(released["mutation_event_id"])

    def test_expired_lease_is_not_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, events = self._paths(tmp)
            with self.assertRaises(ValueError):
                acquire(path, work_id="W1", mission_id="MISSION-01", actor="agent-1", lease_id="L1", lease_expires_at="2026-09-16T10:00:00Z", now="2026-09-16T11:00:00Z", event_log=events)

    def test_event_log_is_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            path, _events = self._paths(tmp)
            with self.assertRaises(TypeError):
                acquire(path, work_id="W1", mission_id="MISSION-01", actor="agent-1", lease_id="L1", lease_expires_at="2026-09-16T12:00:00Z")


if __name__ == "__main__":
    unittest.main()
