import unittest

from .bootstrap import _validate_event_backing


class EventBackingTests(unittest.TestCase):
    def test_event_backing_accepts_existing_mutation_event(self):
        _validate_event_backing([{"handoff_id": "HF-1", "mutation_event_id": "EV-0003"}], {"EV-0003"}, "handoff")

    def test_event_backing_rejects_silent_mutation(self):
        with self.assertRaisesRegex(ValueError, "lacks canonical mutation_event_id"):
            _validate_event_backing([{"handoff_id": "HF-1"}], {"EV-0003"}, "handoff")

    def test_event_backing_rejects_missing_event_reference(self):
        with self.assertRaisesRegex(ValueError, "references missing mutation event"):
            _validate_event_backing([{"handoff_id": "HF-1", "mutation_event_id": "EV-9999"}], {"EV-0003"}, "handoff")


if __name__ == "__main__":
    unittest.main()
