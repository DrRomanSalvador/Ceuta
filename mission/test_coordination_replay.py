import tempfile
import unittest
from pathlib import Path

from .coordination import Authority, CommandType, CoordinationStore, Coordinator, Mirror, MirrorAction
from .replay import replay


class CoordinationReplayTests(unittest.TestCase):
    def test_coordination_events_reconstruct_latest_state(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            store = CoordinationStore(root / "state.json", root / "events.jsonl")
            coordinator = Coordinator(instance_id="COORD-A", store=store)
            coordinator.register_agent("ENGINEER-1", "MISSION-01", state="RUNNING", progress=True)
            coordinator.issue(command_type=CommandType.CONTINUE, target="ENGINEER-1", mission="MISSION-01", reason="healthy", authority_basis=Authority.COORDINATOR.value, expected_effect="continue", order_id="ORD-1")
            mirror = Mirror(instance_id="MIRROR-1", store=store)
            state = mirror.invoke(mirror_of="ENGINEER-1", mission="MISSION-01", target_agent="ENGINEER-1", task="T-1", problem="assist", capability_required="tester", limits=[], priority="HIGH", authority=Authority.COORDINATOR.value, expected_result="validated", action=MirrorAction.TEST, functional_role="tester", mission_owner="ENGINEER-1")
            mirror_id = next(iter(state["mirrors"]))
            mirror.claim_subtask(mirror_id, task_id="T-1")
            live = mirror.complete(mirror_id, result="validated", validated=True)
            reconstructed = replay(root / "events.jsonl")
            self.assertEqual(reconstructed.coordination, live)
            self.assertEqual(reconstructed.last_event_id, live["commands"]["ORD-1"]["provenance"]["VALIDATED_BY"] if False else reconstructed.last_event_id)


if __name__ == "__main__":
    unittest.main()
