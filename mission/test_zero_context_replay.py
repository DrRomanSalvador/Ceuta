"""Zero-context continuity test: a fresh Python process must reconstruct the mission."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path


class ZeroContextReplayTests(unittest.TestCase):
    def test_zero_context_bootstrap_reconstructs_control_plane(self) -> None:
        root = Path(__file__).resolve().parents[1]
        env = os.environ.copy()
        env.pop("CEUTIA_MISSION_STATE", None)
        env.pop("MISSION_STATE", None)
        result = subprocess.run(
            [sys.executable, "-m", "mission.bootstrap"],
            cwd=root,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("MISSION_STATE=VALID", result.stdout)
        registry = json.loads((root / "mission" / "MISSION_CONTROL_PLANE_STATE.json").read_text(encoding="utf-8"))
        expected_missions = registry["mission_registry_source_evidence"]["mission_count_evidenced_in_source"]
        self.assertIn(f"CONTROL_PLANE_MISSIONS={expected_missions}", result.stdout)
        self.assertIn("CONTROL_PLANE_EVENTS=", result.stdout)
        self.assertIn("RESPONSE_COUPLING=ACTIVE_FRONTIER", result.stdout)


if __name__ == "__main__":
    unittest.main()
