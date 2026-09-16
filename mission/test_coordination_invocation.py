import json
import unittest
from pathlib import Path

from .invocation_runtime import authorize_invocation, fresh_chat_discovery


class CoordinationInvocationTests(unittest.TestCase):
    def setUp(self):
        registry_path = Path(__file__).with_name("MISSION_REGISTRY.json")
        self.registry = json.loads(registry_path.read_text(encoding="utf-8"))

    def test_coordinator_is_discoverable_and_authorizable(self):
        mission = fresh_chat_discovery(self.registry, "MISSION-COORDINATOR")
        self.assertEqual(mission["canonical_name"], "COORDINATOR")
        authorize_invocation(
            mission={**mission, "current_status": "ACTIVE"},
            envelope=type("Envelope", (), {"mission_id": "MISSION-COORDINATOR", "authority_context": {"CAN_INVOKE": True}})(),
        )

    def test_mirror_is_discoverable(self):
        mission = fresh_chat_discovery(self.registry, "MISSION-ESPEJO")
        self.assertEqual(mission["canonical_name"], "ESPEJO")


if __name__ == "__main__":
    unittest.main()
