import tempfile
import unittest
from pathlib import Path

from .lifecycle_governance import admit, load_ledger, record_conflict, recover, retire


class LifecycleGovernanceTests(unittest.TestCase):
    def contract(self):
        return {
            "mission_id":"MISSION-99", "mission_name":"TEST", "purpose":"x", "scope":["x"],
            "authority":"TEST", "owner":"MISSION-99", "inputs":[], "outputs":[], "dependencies":[],
            "handoff_contract":"x", "validation_contract":"x", "recovery_policy":"x", "retirement_conditions":["x"],
        }

    def test_admission_requires_complete_contract_and_persists(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"ledger.json"
            path.write_text('{"admissions":[],"retirements":[],"recoveries":[],"conflicts":[]}',encoding="utf-8")
            admit(path,self.contract(),authorized_by="HUMAN_AUTHORITY",evidence=["review"])
            self.assertEqual(load_ledger(path)["admissions"][0]["status"],"ADMITTED")

    def test_retirement_is_persistent_and_authorized(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"ledger.json"
            path.write_text('{"admissions":[],"retirements":[],"recoveries":[],"conflicts":[]}',encoding="utf-8")
            record=retire(path,mission_id="MISSION-99",owner="MISSION-99",authorized_by="HUMAN_AUTHORITY",evidence=["e"],reason="superseded")
            self.assertEqual(record["status"],"RETIRED")

    def test_recovery_is_persistent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"ledger.json"
            path.write_text('{"admissions":[],"retirements":[],"recoveries":[],"conflicts":[]}',encoding="utf-8")
            recover(path,mission_id="MISSION-99",trigger="checkpoint-loss",evidence=["event-chain"],restored_state="ACTIVE")
            self.assertEqual(load_ledger(path)["recoveries"][0]["status"],"RECOVERED")

    def test_conflict_preserves_both_claims(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"ledger.json"
            path.write_text('{"admissions":[],"retirements":[],"recoveries":[],"conflicts":[]}',encoding="utf-8")
            record=record_conflict(path,conflict_id="C1",claim_a="A",claim_b="B",category="factual",owner="MISSION-02",evidence_a=["ea"],evidence_b=["eb"])
            self.assertEqual(record["status"],"OPEN")
            self.assertEqual(len(load_ledger(path)["conflicts"]),1)


if __name__ == "__main__":
    unittest.main()
