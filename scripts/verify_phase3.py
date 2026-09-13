"""Reproducible verifier for CeutIA Phase 3 Shadow Mode."""

from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / "backend/app/core/pipeline/sources/shadow_engine.py"
LEGACY = ROOT / "backend/app/core/pipeline/shadow_mode.py"
TESTS = ROOT / "tests/test_phase3_shadow_isolation.py"
DOC = ROOT / "docs/architecture/PHASE_3_SHADOW_MODE.md"


def classes(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return {node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)}


def main() -> None:
    required = [ENGINE, LEGACY, TESTS, DOC]
    missing = [str(p.relative_to(ROOT)) for p in required if not p.is_file()]
    if missing:
        raise SystemExit(f"FAIL: missing Phase 3 files: {missing}")

    engine_classes = classes(ENGINE)
    required_classes = {"ShadowLedger", "ShadowLedgerRecord", "ShadowExecutionResult", "ShadowEngine"}
    if not required_classes <= engine_classes:
        raise SystemExit(f"FAIL: Shadow engine classes missing: {sorted(required_classes - engine_classes)}")

    engine_text = ENGINE.read_text(encoding="utf-8")
    for token in (
        "available_at <= cutoff_time",
        "TemporalLeakageError",
        "SHADOW_EVALUATION",
        "production_mutation_supported",
        "replace(forecast, status=\"SHADOW_EVALUATION\")",
    ):
        if token not in engine_text:
            raise SystemExit(f"FAIL: Phase 3 invariant missing: {token}")

    legacy_text = LEGACY.read_text(encoding="utf-8")
    if "ForecastLedger" in legacy_text:
        raise SystemExit("FAIL: legacy ShadowModeExecutor still references production ForecastLedger")
    if "ShadowEngine" not in legacy_text or "ShadowLedger" not in legacy_text:
        raise SystemExit("FAIL: legacy ShadowModeExecutor is not routed through isolated shadow infrastructure")

    test_text = TESTS.read_text(encoding="utf-8")
    for token in (
        "test_only_available_observations_reach_forecaster",
        "test_shadow_has_no_production_mutation_capability",
        "test_legacy_executor_uses_secondary_ledger",
        "test_invalid_temporal_observation_fails_closed",
    ):
        if token not in test_text:
            raise SystemExit(f"FAIL: Phase 3 test coverage missing {token}")

    doc_text = DOC.read_text(encoding="utf-8")
    for token in ("Invariants", "Exit criteria", "ShadowLedger", "available_at <= cutoff_time"):
        if token not in doc_text:
            raise SystemExit(f"FAIL: Phase 3 audit criterion missing: {token}")

    print("PASS: Phase 3 Shadow Mode verifier")


if __name__ == "__main__":
    main()
