import tempfile
import unittest
from pathlib import Path

from .work_claims import acquire, load_claims, release


class WorkClaimLedgerTests(unittest.TestCase):
    def test_claim_persists_and_duplicate_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "claims.json"
            claim = acquire(path, work_id="W1", mission_id="MISSION-01", actor="agent-1", lease_id="L1", lease_expires_at="2026-09-16T12:00:00Z")
            self.assertEqual(load_claims(path)["claims"]["W1"]["status"], "ACTIVE")
            self.assertEqual(claim["lease_id"], "L1")
            with self.assertRaises(RuntimeError):
                acquire(path, work_id="W1", mission_id="MISSION-01", actor="agent-2", lease_id="L2", lease_expires_at="2026-09-16T12:00:00Z")

    def test_only_claiming_actor_can_release(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "claims.json"
            acquire(path, work_id="W1", mission_id="MISSION-01", actor="agent-1", lease_id="L1", lease_expires_at="2026-09-16T12:00:00Z")
            with self.assertRaises(PermissionError):
                release(path, work_id="W1", actor="agent-2")
            released = release(path, work_id="W1", actor="agent-1")
            self.assertEqual(released["status"], "RELEASED")


if __name__ == "__main__":
    unittest.main()
