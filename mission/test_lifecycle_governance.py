import tempfile
import unittest
from pathlib import Path

from .event_log import load_jsonl, validate_chain
from .lifecycle_governance import OPERATING_STANDARD_VERSION, admit, load_ledger, record_conflict, recover, retire


class LifecycleGovernanceTests(unittest.TestCase):
    def contract(self, mission_id="MISSION-99"):
        return {"mission_id":mission_id,"mission_name":"TEST","purpose":"x","scope":["x"],"authority":"TEST","owner":mission_id,"inputs":[],"outputs":[],"dependencies":[],"handoff_contract":"x","validation_contract":"x","recovery_policy":"x","retirement_conditions":["x"],"operating_standard_version":OPERATING_STANDARD_VERSION}

    def test_admission_requires_complete_contract_and_persists(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"ledger.json"; path.write_text('{"admissions":[],"retirements":[],"recoveries":[],"conflicts":[]}',encoding="utf-8")
            admit(path,self.contract(),authorized_by="HUMAN_AUTHORITY",evidence=["review"])
            self.assertEqual(load_ledger(path)["admissions"][0]["status"],"ADMITTED")

    def test_event_backed_lifecycle_mutation_is_replayable(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"ledger.json"; events=Path(tmp)/"events.jsonl"; path.write_text('{"admissions":[],"retirements":[],"recoveries":[],"conflicts":[]}',encoding="utf-8")
            admit(path,self.contract(),authorized_by="HUMAN_AUTHORITY",evidence=["review"],event_log=events,timestamp="2026-09-16T12:00:00Z")
            record_conflict(path,conflict_id="C1",claim_a="A",claim_b="B",category="factual",owner="MISSION-99",evidence_a=["ea"],evidence_b=["eb"],event_log=events,timestamp="2026-09-16T12:01:00Z")
            chain=load_jsonl(events); self.assertEqual([e["event_type"] for e in chain],["MISSION_ADMISSION","MISSION_CONTRADICTION"]); validate_chain(chain)
            records=load_ledger(path); self.assertTrue(all("mutation_event_id" in r for r in records["admissions"]+records["conflicts"]))

    def test_roman_admission_is_explicitly_runtime_pending(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"ledger.json"; path.write_text('{"admissions":[],"retirements":[],"recoveries":[],"conflicts":[]}',encoding="utf-8")
            admit(path,self.contract("ROMAN"),authorized_by="MISSION-01",evidence=["main:MISSION_REGISTRY","main:ROMAN_MISSION_STATE"])
            record=load_ledger(path)["admissions"][0]
            self.assertEqual(record["status"],"ADMITTED_REPOSITORY_RUNTIME_PENDING")

    def test_retirement_is_persistent_and_authorized(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"ledger.json"; path.write_text('{"admissions":[],"retirements":[],"recoveries":[],"conflicts":[]}',encoding="utf-8")
            record=retire(path,mission_id="MISSION-99",owner="MISSION-99",authorized_by="HUMAN_AUTHORITY",evidence=["e"],reason="superseded")
            self.assertEqual(record["status"],"RETIRED")

    def test_recovery_is_persistent(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"ledger.json"; path.write_text('{"admissions":[],"retirements":[],"recoveries":[],"conflicts":[]}',encoding="utf-8")
            recover(path,mission_id="MISSION-99",trigger="checkpoint-loss",evidence=["event-chain"],restored_state="ACTIVE")
            self.assertEqual(load_ledger(path)["recoveries"][0]["status"],"RECOVERED")

    def test_conflict_preserves_both_claims(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=Path(tmp)/"ledger.json"; path.write_text('{"admissions":[],"retirements":[],"recoveries":[],"conflicts":[]}',encoding="utf-8")
            record=record_conflict(path,conflict_id="C1",claim_a="A",claim_b="B",category="factual",owner="MISSION-02",evidence_a=["ea"],evidence_b=["eb"])
            self.assertEqual(record["status"],"OPEN"); self.assertEqual(len(load_ledger(path)["conflicts"]),1)


if __name__ == "__main__": unittest.main()
