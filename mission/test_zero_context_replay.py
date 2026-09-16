"""Zero-context continuity test: a fresh Python process must reconstruct the mission."""
from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path


def test_zero_context_bootstrap_reconstructs_control_plane() -> None:
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
    assert result.returncode == 0, result.stderr
    assert "MISSION_STATE=VALID" in result.stdout
    assert "CONTROL_PLANE_MISSIONS=15" in result.stdout
    assert "CONTROL_PLANE_EVENTS=" in result.stdout
    assert "RESPONSE_COUPLING=ACTIVE_FRONTIER" in result.stdout
