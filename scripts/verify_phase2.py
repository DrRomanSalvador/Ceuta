"""Reproducible verifier for CeutIA Phase 2 foundational contracts."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ERRORS = ROOT / "backend/app/core/errors.py"
TESTS = ROOT / "tests/test_foundational_errors.py"
DOC = ROOT / "docs/architecture/PHASE_2_FOUNDATIONAL_CONTRACTS.md"
CONTRACTS = ROOT / "backend/app/core/pipeline/contracts.py"

REQUIRED_ERRORS = {
    "CeutIAError",
    "ContractViolation",
    "TemporalViolation",
    "ProvenanceViolation",
    "ValidationFailure",
    "RuntimeBoundaryError",
}


def classes(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}


def main() -> None:
    required = [ERRORS, TESTS, DOC, CONTRACTS]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if missing:
        raise SystemExit(f"FAIL: missing Phase 2 files: {missing}")

    error_classes = classes(ERRORS)
    if error_classes != REQUIRED_ERRORS:
        raise SystemExit(
            "FAIL: foundational error taxonomy mismatch: "
            f"expected={sorted(REQUIRED_ERRORS)} actual={sorted(error_classes)}"
        )

    duplicate = REQUIRED_ERRORS & classes(CONTRACTS)
    if duplicate:
        raise SystemExit(
            "FAIL: foundational errors duplicated in canonical pipeline contracts: "
            f"{sorted(duplicate)}"
        )

    test_text = TESTS.read_text(encoding="utf-8")
    for token in REQUIRED_ERRORS:
        if token not in test_text:
            raise SystemExit(f"FAIL: test coverage missing {token}")

    doc_text = DOC.read_text(encoding="utf-8")
    for token in ("Exit criteria", "invalid contract states", "CI workflow", "commit SHA"):
        if token not in doc_text:
            raise SystemExit(f"FAIL: Phase 2 audit criterion missing: {token}")

    print("PASS: Phase 2 foundational contract verifier")


if __name__ == "__main__":
    main()
