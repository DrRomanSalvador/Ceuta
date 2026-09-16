import unittest

from .ceutia.core_formula import MasterSusceptibilityEngine, SystemicVariables


class CoreFormulaTests(unittest.TestCase):
    def test_engine_returns_bounded_risk_and_oversight(self):
        variables = SystemicVariables(
            shock_magnitude=2.0,
            sensitivity=0.8,
            adaptive_reserve=2.0,
            coupling_index=0.7,
            propagation_rate=0.5,
            confidence_interval=(0.1, 0.3),
        )
        result = MasterSusceptibilityEngine.compute_systemic_susceptibility(variables)
        self.assertGreaterEqual(result["systemic_susceptibility_index"], 0.0)
        self.assertLessEqual(result["systemic_susceptibility_index"], 1.0)
        self.assertTrue(result["human_oversight_required"])
        self.assertFalse(result["coercive_action_permitted"])

    def test_invalid_confidence_interval_is_rejected(self):
        with self.assertRaises(ValueError):
            SystemicVariables(
                shock_magnitude=1.0,
                sensitivity=0.5,
                adaptive_reserve=1.0,
                coupling_index=0.5,
                propagation_rate=1.0,
                confidence_interval=(0.9, 0.1),
            )


if __name__ == "__main__":
    unittest.main()
