import tempfile
import unittest
from pathlib import Path

from .coordination import Authority, CommandConflict, CommandType, CoordinationStore, Coordinator, Mirror, MirrorAction


class CoordinationIdempotencyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.store = CoordinationStore(root / "state.json", root / "events.jsonl")
        self.coordinator = Coordinator(instance_id="COORD-A", store=self.store)

    def tearDown(self):
        self.tmp.cleanup()

    def test_duplicate_order_id_is_idempotent(self):
        first = self.coordinator.issue(
            command_type=CommandType.CONTINUE, target="ENGINEER-1", mission="MISSION-01",
            reason="same", authority_basis=Authority.COORDINATOR.value, expected_effect="continue",
            order_id="ORD-IDEMPOTENT",
        )
        second = self.coordinator.issue(
            command_type=CommandType.CONTINUE, target="ENGINEER-1", mission="MISSION-01",
            reason="same", authority_basis=Authority.COORDINATOR.value, expected_effect="continue",
            order_id="ORD-IDEMPOTENT",
        )
        self.assertEqual(first["state_version"], second["state_version"])
        self.assertEqual(len(second["commands"]), 1)

    def test_reused_order_id_with_changed_effect_is_conflict(self):
        self.coordinator.issue(
            command_type=CommandType.CONTINUE, target="ENGINEER-1", mission="MISSION-01",
            reason="same", authority_basis=Authority.COORDINATOR.value, expected_effect="continue",
            order_id="ORD-CONFLICT",
        )
        with self.assertRaises(CommandConflict):
            self.coordinator.issue(
                command_type=CommandType.PAUSE, target="ENGINEER-1", mission="MISSION-01",
                reason="changed", authority_basis=Authority.COORDINATOR.value, expected_effect="pause",
                order_id="ORD-CONFLICT",
            )

    def test_command_and_mirror_provenance_are_persisted(self):
        state = self.coordinator.issue(
            command_type=CommandType.REQUEST_MIRROR, target="ENGINEER-1", mission="MISSION-01",
            reason="assist", authority_basis=Authority.COORDINATOR.value, expected_effect="assistance",
            order_id="ORD-PROV",
        )
        self.assertEqual(state["commands"]["ORD-PROV"]["provenance"]["COMMAND_ISSUER"], "COORD-A")
        mirror = Mirror(instance_id="MIRROR-1", store=self.store)
        state = mirror.invoke(
            mirror_of="ENGINEER-1", mission="MISSION-01", target_agent="ENGINEER-1", task="T-1",
            problem="assist", capability_required="tester", limits=[], priority="HIGH",
            authority=Authority.COORDINATOR.value, expected_result="validated", action=MirrorAction.TEST,
            functional_role="tester", mission_owner="ENGINEER-1",
        )
        invocation = next(iter(state["mirrors"].values()))
        self.assertEqual(invocation["provenance"]["MIRROR_OF"], "ENGINEER-1")
        self.assertEqual(invocation["mission_owner"], "ENGINEER-1")
        self.assertEqual(invocation["subtask_owner"], "MIRROR-1")


if __name__ == "__main__":
    unittest.main()
