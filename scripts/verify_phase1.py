from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_TEST_ROOT = "tests"
EXPECTED_SOURCE_ROOT = "backend"
EXPECTED_PACKAGE_ROOT = "backend/app"
REQUIRED_ABSENT_PACKAGES = (
    "backend/app/core/ingestion",
    "backend/app/core/provenance",
    "backend/app/core/knowledge",
    "backend/app/core/serpiente",
    "backend/app/core/forecasting",
    "backend/app/core/calibration",
    "backend/app/core/learning",
    "backend/app/core/governance",
    "backend/app/core/privacy",
    "backend/app/core/decision",
    "backend/app/core/spatial",
    "backend/app/core/simulation",
    "backend/app/core/resilience",
)
REQUIRED_EXISTING_PATHS = (
    "backend/app",
    "backend/app/core",
    "tests",
    "pyproject.toml",
    ".github/workflows/ci.yml",
    "docs/architecture/PHASE_1_REPOSITORY_AUDIT.md",
)


def read_utf8(relative_path: str) -> str:
    path = REPOSITORY_ROOT / relative_path
    if not path.is_file():
        raise SystemExit(f"FAIL: required file is missing: {relative_path}")
    return path.read_text(encoding="utf-8")


def assert_contains(text: str, needle: str, source: str) -> None:
    if needle not in text:
        raise SystemExit(f"FAIL: {source} does not contain required text: {needle!r}")


def main() -> None:
    for relative_path in REQUIRED_EXISTING_PATHS:
        if not (REPOSITORY_ROOT / relative_path).exists():
            raise SystemExit(f"FAIL: required repository path is missing: {relative_path}")

    pyproject = read_utf8("pyproject.toml")
    audit = read_utf8("docs/architecture/PHASE_1_REPOSITORY_AUDIT.md")
    workflow = read_utf8(".github/workflows/ci.yml")

    assert_contains(pyproject, 'package-dir = { "" = "backend" }', "pyproject.toml")
    assert_contains(pyproject, 'testpaths = ["tests"]', "pyproject.toml")
    assert_contains(pyproject, 'include = ["app", "app.*"]', "pyproject.toml")
    assert_contains(pyproject, 'python_version = "3.12"', "pyproject.toml")
    assert_contains(pyproject, "strict = true", "pyproject.toml")

    for relative_path in REQUIRED_ABSENT_PACKAGES:
        if (REPOSITORY_ROOT / relative_path).exists():
            raise SystemExit(
                "FAIL: Phase 1 absence invariant changed; package now exists: "
                f"{relative_path}"
            )
        assert_contains(audit, f"`{relative_path}/`", "Phase 1 audit")

    required_audit_terms = (
        "## Repository and packaging facts",
        "## Existing architectural foundation",
        "## Architectural gaps confirmed in Phase 1",
        "## Reconciliation rule",
        "## P0 construction order",
        "## Explicit non-goals of Phase 1",
        "## Exit criteria",
        "## Next phase",
        "State(T) = F(observations with available_at <= T, valid versions, provenance, temporal rules)",
    )
    for term in required_audit_terms:
        assert_contains(audit, term, "Phase 1 audit")

    required_ci_terms = (
        "python -m compileall -q backend api ceuta-final",
        "python -m pip install '.[dev]'",
        "python -m pytest",
        "docker compose config -q",
    )
    for term in required_ci_terms:
        assert_contains(workflow, term, "CI workflow")

    manifest = {
        "schema_version": 1,
        "phase": "1",
        "repository": "drsalvadorroman-beep/Ceuta",
        "branch": "main",
        "source_root": EXPECTED_SOURCE_ROOT,
        "package_root": EXPECTED_PACKAGE_ROOT,
        "test_root": EXPECTED_TEST_ROOT,
        "required_existing_paths": list(REQUIRED_EXISTING_PATHS),
        "required_absent_packages": list(REQUIRED_ABSENT_PACKAGES),
    }
    canonical = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(canonical).hexdigest()
    print(json.dumps({**manifest, "manifest_sha256": digest}, indent=2, sort_keys=True))
    print("PASS: Phase 1 repository invariants are reproducibly satisfied.")


if __name__ == "__main__":
    main()
