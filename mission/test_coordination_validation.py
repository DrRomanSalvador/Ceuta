import unittest

from .coordination_validation import validate


class CoordinationValidationTests(unittest.TestCase):
    def test_constitutional_registration_and_persistence_gate(self):
        result = validate()
        self.assertEqual(result["status"], "REPOSITORY_GATE_VALID")
        self.assertEqual(result["external_live_orchestration"], "NOT_ESTABLISHED")


if __name__ == "__main__":
    unittest.main()
