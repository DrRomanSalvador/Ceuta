import tempfile
import unittest
from pathlib import Path

from .coordination import Authority, CommandConflict, CommandType, CoordinationError, CoordinationStore, Coordinator, Mirror, MirrorAction, OwnershipConflict


class CoordinationControlTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.store = CoordinationStore(root / "state.json", root / "events.jsonl")
        self.coordinator = Coordinator(instance_id="COORD-A", store=self.store)
        self.coordinator.register_agent("ENGINEER-1", "MISSION-01", state="RUNNING", progress=True)

    def tearDown(self):
        self.tmp.cleanup()

    def test_pause_without_checkpoint_persists_explicit_recovery_risk(self):
        state = self.coordinator.pause(target="ENGINEER-1", mission="MISSION-01")
        self.assertEqual(state["recovery"][-1]["type"], "PAUSE_WITHOUT_CHECKPOINT_RISK")

    def test_standby_and_resume_preserve_recovery_semantics(self):
        state = self.coordinator.checkpoint_then_pause(target="ENGINEER-1", mission="MISSION-01", checkpoint_id="CP-1")
        pause_order = next(reversed(state["commands"]))
        state = self.coordinator.record_execution(pause_order, result="paused", success=True)
        state = self.coordinator.standby(target="ENGINEER-1", mission="MISSION-01", checkpoint_id="CP-1")
        self.assertEqual(state["standby"]["ENGINEER-1"]["checkpoint_id"], "CP-1")
        state = self.coordinator.resume(target="ENGINEER-1", mission="MISSION-01")
        self.assertNotIn("ENGINEER-1", state["standby"])

    def test_contradictory_active_commands_create_coordination_conflict(self):
        self.coordinator.issue(command_type=CommandType.PAUSE, target="ENGINEER-1", mission="MISSION-01", reason="pause", authority_basis=Authority.COORDINATOR.value, expected_effect="pause")
        with self.assertRaises(CommandConflict):
            self.coordinator.issue(command_type=CommandType.RESUME, target="ENGINEER-1", mission="MISSION-01", reason="resume", authority_basis=Authority.COORDINATOR.value, expected_effect="resume")
        self.assertEqual(self.store.load()["conflicts"][-1]["type"], "COORDINATION_CONFLICT")

    def test_mirror_preflight_rejects_unknown_target(self):
        mirror = Mirror(instance_id="MIRROR-1", store=self.store)
        with self.assertRaises(CoordinationError):
            mirror.invoke(mirror_of="ENGINEER-2", mission="MISSION-01", target_agent="ENGINEER-2", task="T-1", problem="x", capability_required="tester", limits=[], priority="HIGH", authority=Authority.COORDINATOR.value, expected_result="x", action=MirrorAction.TEST, functional_role="tester", mission_owner="ENGINEER-2")

    def test_mirror_preflight_rejects_already_owned_task(self):
        mirror = Mirror(instance_id="MIRROR-1", store=self.store)
        state = mirror.invoke(mirror_of="ENGINEER-1", mission="MISSION-01", target_agent="ENGINEER-1", task="T-1", problem="x", capability_required="tester", limits=[], priority="HIGH", authority=Authority.COORDINATOR.value, expected_result="x", action=MirrorAction.TEST, functional_role="tester", mission_owner="ENGINEER-1")
        mirror_id = next(iter(state["mirrors"]))
        mirror.claim_subtask(mirror_id, task_id="T-1")
        mirror2 = Mirror(instance_id="MIRROR-2", store=self.store)
        with self.assertRaises(OwnershipConflict):
            mirror2.invoke(mirror_of="ENGINEER-1", mission="MISSION-01", target_agent="ENGINEER-1", task="T-1", problem="duplicate", capability_required="tester", limits=[], priority="HIGH", authority=Authority.COORDINATOR.value, expected_result="x", action=MirrorAction.TEST, functional_role="tester", mission_owner="ENGINEER-1")


if __name__ == "__main__":
    unittest.main()
