from __future__ import annotations

import unittest

from app.core.scientific.governance_contracts import (
    Identifiability,
    InvestigationTaskContract,
    ResearchPriority,
    VOIInputs,
    ValidationAssessment,
    ValidationLayer,
    VariableSemantics,
)


class GovernanceContractTests(unittest.TestCase):
    def test_voi_refuses_fabricated_identifiability(self):
        voi = VOIInputs("D1", "uncertainty", None, None, None, None, Identifiability.UNKNOWN)
        self.assertFalse(voi.identifiable)
        self.assertEqual(voi.status, "NVOI_NOT_IDENTIFIABLE")

    def test_voi_can_be_identifiable_only_with_utility_and_cost_inputs(self):
        voi = VOIInputs("D1", "uncertainty", "U(a,theta)", 1.0, 2.0, 3.0, Identifiability.PARTIALLY_IDENTIFIABLE)
        self.assertTrue(voi.identifiable)

    def test_research_task_requires_stopping_rule(self):
        task = InvestigationTaskContract("T1", "u", "decision", "change", "discriminate", "low", "low", "low", "stop at replication", (), ResearchPriority.T3_CONTRADICTION_SEEKING)
        self.assertEqual(task.priority, ResearchPriority.T3_CONTRADICTION_SEEKING)

    def test_validation_is_layer_specific(self):
        assessment = ValidationAssessment(ValidationLayer.SOFTWARE_CORRECTNESS, "PASS", ("TEST-1",), ("No real-world validity claimed",))
        self.assertEqual(assessment.layer, ValidationLayer.SOFTWARE_CORRECTNESS)

    def test_variable_semantics_preserve_denominator(self):
        variable = VariableSemantics("incidence", "observed cases", "cases/1000", "present", "Ceuta", "daily", "ascertainment", "population_present", "explicit", "measurement", "source-1", "rate-normalization")
        self.assertEqual(variable.denominator, "population_present")


if __name__ == "__main__":
    unittest.main()
