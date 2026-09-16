import unittest

from .scientific_boundaries import CausalIdentificationStatus, DigitalTwinClassification, assess_causal_identification, assess_digital_twin


class ScientificBoundaryTests(unittest.TestCase):
    def test_causal_assessment_preserves_non_identifiability(self) -> None:
        assessment = assess_causal_identification(estimand="average treatment effect", design="observational cohort", temporal_ordering=True, positivity=True, consistency=True, exchangeability=False, confounders_declared=True)
        self.assertEqual(assessment.status, CausalIdentificationStatus.NOT_IDENTIFIABLE)
        self.assertIn("exchangeability", assessment.limitations)

    def test_causal_identification_requires_explicit_design_and_estimand(self) -> None:
        with self.assertRaises(ValueError):
            assess_causal_identification(estimand="", design="cohort", temporal_ordering=True, positivity=True, consistency=True, exchangeability=True, confounders_declared=True)

    def test_simulation_cannot_be_called_digital_twin(self) -> None:
        assessment = assess_digital_twin(real_world_state=True, synchronization=True, bidirectional_coupling=False, parameter_updating=True, validation=True, uncertainty=True, intervention_simulation=True, outcome_comparison=True)
        self.assertEqual(assessment.classification, DigitalTwinClassification.SIMULATION)
        self.assertIn("bidirectional coupling", assessment.requirements_missing)

    def test_complete_requirements_allow_digital_twin_classification(self) -> None:
        assessment = assess_digital_twin(real_world_state=True, synchronization=True, bidirectional_coupling=True, parameter_updating=True, validation=True, uncertainty=True, intervention_simulation=True, outcome_comparison=True)
        self.assertEqual(assessment.classification, DigitalTwinClassification.DIGITAL_TWIN)
