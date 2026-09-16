import json
import unittest
from pathlib import Path

from .coordination import Authority, Coordinator, Mirror, MirrorAction


class RomanCoordinationIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parent
        self.registry = json.loads((self.root / "MISSION_REGISTRY.json").read_text(encoding="utf-8"))

    def test_roman_can_be_target_of_coordinator_and_mirror_without_ownership_transfer(self):
        roman = next(m for m in self.registry["missions"] if m["mission_id"] == "ROMAN")
        self.assertEqual(roman["mission_id"], "ROMAN")
        coordinator = Coordinator(instance_id="COORD-ROMAN-TEST")
        coordinator.register_agent("ROMAN-TEST", "ROMAN", state="RUNNING", progress=True)
        self.assertEqual(coordinator.detect_execution("ROMAN-TEST"), "LONG_RUNNING_PROGRESS_CONTINUE")
        command_state = coordinator.request_mirror(
            target_agent="ROMAN-TEST",
            mission="ROMAN",
            task="ROMAN-SUBTASK-001",
            problem="independent validation opportunity",
            capability_required="verifier",
            limits=["no mission ownership change", "no objective change"],
            priority="NORMAL",
            authority=Authority.COORDINATOR.value,
            expected_result="validated subtask",
        )
        order_id = next(iter(command_state["commands"]))
        mirror = Mirror(instance_id="ESPEJO-ROMAN-TEST")
        state = mirror.invoke(
            mirror_of="ROMAN-TEST",
            mission="ROMAN",
            target_agent="ROMAN-TEST",
            task="ROMAN-SUBTASK-001",
            problem="independent validation opportunity",
            capability_required="verifier",
            limits=["no mission ownership change", "no objective change"],
            priority="NORMAL",
            authority=Authority.COORDINATOR.value,
            expected_result="validated subtask",
            action=MirrorAction.VERIFY,
            functional_role="verifier",
            mission_owner="ROMAN",
        )
        mirror_id = next(iter(state["mirrors"]))
        mirror.claim_subtask(mirror_id, task_id="ROMAN-SUBTASK-001")
        final_state = mirror.complete(mirror_id, result="validated", validated=True)
        invocation = final_state["mirrors"][mirror_id]
        handoff = final_state["handoffs"][-1]
        self.assertEqual(invocation["identity"], "ESPEJO")
        self.assertEqual(invocation["mission_owner"], "ROMAN")
        self.assertEqual(invocation["subtask_owner"], "ESPEJO-ROMAN-TEST")
        self.assertEqual(invocation["mirror_of"], "ROMAN-TEST")
        self.assertEqual(handoff["mission_owner"], "ROMAN")
        self.assertEqual(handoff["subtask_owner"], "ESPEJO-ROMAN-TEST")
        self.assertTrue(handoff["control_returned"])
        self.assertEqual(command_state["commands"][order_id]["command_type"], "REQUEST_MIRROR")


if __name__ == "__main__":
    unittest.main()
