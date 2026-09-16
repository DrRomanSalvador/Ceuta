import json
import unittest
from pathlib import Path

ROOT = Path(__file__).parent.parent
NORMATIVE_REGISTRY = ROOT / "mission" / "SCIENTIFIC_NORMATIVE_REGISTRY.json"
NORMATIVE_DOCUMENT = ROOT / "docs" / "scientific" / "SCIENTIFIC_NORMATIVE_STANDARD_001.md"
EVIDENCE_REGISTRY = ROOT / "docs" / "scientific" / "SCIENTIFIC_EVIDENCE_REGISTRY.json"
DISCOVERY_LEDGER = ROOT / "docs" / "scientific" / "SCIENTIFIC_DISCOVERY_CONSEQUENCE_LEDGER.json"


class ScientificNormativeIntegrationTests(unittest.TestCase):
    def load(self, path):
        return json.loads(path.read_text(encoding="utf-8"))

    def test_canonical_normative_document_is_registered_and_mandatory(self):
        registry = self.load(NORMATIVE_REGISTRY)
        canonical = registry["canonical_document"]
        self.assertEqual(canonical["document_id"], "SCIENTIFIC-NORMATIVE-STANDARD-001")
        self.assertEqual(canonical["path"], "docs/scientific/SCIENTIFIC_NORMATIVE_STANDARD_001.md")
        self.assertEqual(canonical["version"], "1.0.0")
        self.assertEqual(canonical["status"], "ACTIVE")
        self.assertTrue(canonical["mandatory_reading"])
        self.assertTrue(registry["zero_context_requirement"])

    def test_normative_document_contains_non_negotiable_scientific_boundaries(self):
        text = NORMATIVE_DOCUMENT.read_text(encoding="utf-8")
        required = (
            "IMPLEMENTED",
            "VERIFIED",
            "VALIDATED",
            "ESTABLISHED",
            "CI success is not scientific validation",
            "DISCOVERY -> SCIENTIFIC IMPACT -> CONSEQUENCE -> DERIVED WORK",
            "source -> observation -> measurement -> evidence -> claim -> hypothesis -> model -> forecast -> decision -> intervention -> outcome -> evaluation",
            "event_time",
            "available_at",
            "forecast -> alert -> decision -> action -> exposure -> outcome -> evaluation",
            "EXISTE -> REUTILIZAR",
            "NO_JUSTIFICADO -> RECHAZAR",
            "FIXED_POINT",
        )
        for marker in required:
            self.assertIn(marker, text)

    def test_canonical_scientific_records_are_registered(self):
        registry = self.load(NORMATIVE_REGISTRY)
        records = registry["canonical_scientific_records"]
        for key, expected in {
            "evidence_registry": "docs/scientific/SCIENTIFIC_EVIDENCE_REGISTRY.json",
            "discovery_consequence_ledger": "docs/scientific/SCIENTIFIC_DISCOVERY_CONSEQUENCE_LEDGER.json",
            "perplexity_integration_ledger": "docs/scientific/PERPLEXITY_SCIENTIFIC_INTEGRATION_LEDGER.json",
        }.items():
            self.assertEqual(records[key], expected)
            self.assertTrue((ROOT / expected).exists())

    def test_evidence_registry_is_append_only_semantic_intake(self):
        registry = self.load(EVIDENCE_REGISTRY)
        self.assertEqual(registry["status"], "ACTIVE")
        self.assertTrue(registry["intake_contract"]["every_new_source_is_pending_evaluation"])
        self.assertFalse(registry["intake_contract"]["source_is_instruction"])
        self.assertFalse(registry["intake_contract"]["source_is_validation_by_default"])
        self.assertTrue(registry["intake_contract"]["silent_architectural_change_forbidden"])
        required = set(registry["record_schema"]["required_fields"])
        self.assertTrue({"source", "evidence_quality", "affected_objects", "integration_decision", "validation_state", "contradictions", "limitations"}.issubset(required))

    def test_discovery_consequence_ledger_preserves_gap_discovery_distinction(self):
        ledger = self.load(DISCOVERY_LEDGER)
        self.assertEqual(ledger["status"], "ACTIVE")
        self.assertIn("GAP", ledger["distinctions"])
        self.assertIn("DISCOVERY", ledger["distinctions"])
        self.assertEqual(
            ledger["contradiction_flow"],
            ["DISCOVERY", "CONTRADICTION", "DEPENDENCY_ANALYSIS", "BLAST_RADIUS", "CLAIM_REVIEW", "MODEL_FORECAST_REVIEW", "REVISION_LIMITATION_RETIREMENT"],
        )
        self.assertTrue("NO_DUPLICATE" in ledger["task_explosion_controls"])


if __name__ == "__main__":
    unittest.main()
