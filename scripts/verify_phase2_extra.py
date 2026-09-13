"""Additional deterministic Phase 2 ownership check."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
assert (ROOT / "backend/app/core/errors.py").is_file()
assert (ROOT / "tests/test_foundational_errors.py").is_file()
print("PASS: Phase 2 ownership files exist")
