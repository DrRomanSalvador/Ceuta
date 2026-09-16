import tempfile
import unittest
from pathlib import Path

from .cas_audit import audit


class CasAuditTests(unittest.TestCase):
    def test_repository_has_no_legacy_direct_cas_call_sites(self):
        root = Path(__file__).resolve().parents[1]
        result = audit(root)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["parse_errors"], [])
        self.assertEqual(result["legacy_call_sites"], [])
        self.assertGreaterEqual(len(result["call_sites"]), 1)

    def test_audit_rejects_unbacked_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "bad.py").write_text(
                "compare_and_swap_mission(path, 'ROMAN', 0, {})\n",
                encoding="utf-8",
            )
            result = audit(root)
            self.assertEqual(result["status"], "FAIL")
            self.assertEqual(len(result["legacy_call_sites"]), 1)

    def test_audit_accepts_canonical_call(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "good.py").write_text(
                "compare_and_swap_mission(path, 'ROMAN', 0, {}, event_log=events, actor='A', timestamp='T')\n",
                encoding="utf-8",
            )
            result = audit(root)
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["legacy_call_sites"], [])


if __name__ == "__main__":
    unittest.main()
