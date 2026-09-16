import unittest

try:
    from .bootstrap import (
        load_current_reconciliation,
        load_state,
        validate_current_reconciliation,
        validate_repository_layout,
        validate_state,
    )
except ImportError:  # direct execution: python mission/test_bootstrap.py
    from bootstrap import (
        load_current_reconciliation,
        load_state,
        validate_current_reconciliation,
        validate_repository_layout,
        validate_state,
    )


class MissionBootstrapTests(unittest.TestCase):
    def test_persistent_state_is_valid(self):
        state = load_state()
        validate_state(state)
        validate_repository_layout()
        validate_current_reconciliation(load_current_reconciliation())

    def test_continuity_invariants_are_present(self):
        state = load_state()
        identity = state["mission_identity"]
        self.assertTrue(identity["not_a_new_phase"])
        self.assertTrue(identity["premature_closure_forbidden"])
        self.assertEqual(
            identity["mission_type"],
            "continuous_cumulative_autonomous_scientific_engineering",
        )

    def test_scientific_status_is_not_promoted_by_engineering(self):
        state = load_state()
        self.assertEqual(state["current_state"]["GLOBAL_ENGINEERING_AUDIT"], "AUDIT_COMPLETE")
        self.assertEqual(
            state["current_state"]["PROSPECTIVE_PREDICTIVE_VALIDITY"],
            "NOT_ESTABLISHED",
        )

    def test_response_coupling_remains_open(self):
        reconciliation = load_current_reconciliation()
        response = reconciliation["corrections"]["response_coupling"]
        self.assertEqual(response["status"], "ACTIVE_FRONTIER")
        self.assertEqual(response["empirical_state"], "NOT_ESTABLISHED")


if __name__ == "__main__":
    unittest.main()
