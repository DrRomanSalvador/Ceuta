import unittest

from .repository_integrity import assess_head, require_reconciliation


class RepositoryIntegrityTests(unittest.TestCase):
    def test_matching_head_is_valid(self):
        assessment=assess_head(expected_head="abc", actual_head="abc", protocol_evidence=[])
        self.assertEqual(assessment.status,"MATCH")

    def test_changed_head_without_protocol_evidence_requires_reconciliation(self):
        assessment=assess_head(expected_head="abc", actual_head="def", protocol_evidence=[])
        self.assertEqual(assessment.status,"UNRECONCILED_HEAD")
        with self.assertRaises(RuntimeError):
            require_reconciliation(assessment)

    def test_changed_head_with_protocol_evidence_is_explicit(self):
        assessment=assess_head(expected_head="abc", actual_head="def", protocol_evidence=["commit:change"])
        self.assertEqual(assessment.status,"CHANGED_WITH_PROTOCOL_EVIDENCE")
        require_reconciliation(assessment)


if __name__ == "__main__":
    unittest.main()
