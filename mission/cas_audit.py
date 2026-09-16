"""Static audit of all direct materialized-state CAS call sites."""
from __future__ import annotations

import ast
import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

CAS_NAME = "compare_and_swap_mission"


@dataclass(frozen=True)
class CASCall:
    path: str
    line: int
    column: int
    form: str
    event_backed: bool


def _python_files(root: Path):
    excluded = {".git", ".venv", "venv", "build", "dist", "__pycache__"}
    for path in root.rglob("*.py"):
        if any(part in excluded for part in path.parts):
            continue
        yield path


def _callee_name(node: ast.Call) -> tuple[str, str] | None:
    if isinstance(node.func, ast.Name) and node.func.id == CAS_NAME:
        return node.func.id, "direct"
    if isinstance(node.func, ast.Attribute) and node.func.attr == CAS_NAME:
        return node.func.attr, "attribute"
    return None


def audit(root: Path) -> dict:
    calls: list[CASCall] = []
    parse_errors: list[str] = []
    for path in _python_files(root):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError) as exc:
            parse_errors.append(f"{path}: {exc}")
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            callee = _callee_name(node)
            if callee is None:
                continue
            keywords = {keyword.arg for keyword in node.keywords if keyword.arg is not None}
            calls.append(
                CASCall(
                    path=str(path.relative_to(root)),
                    line=node.lineno,
                    column=node.col_offset,
                    form=callee[1],
                    event_backed={"event_log", "actor", "timestamp"}.issubset(keywords),
                )
            )

    legacy = [call for call in calls if not call.event_backed]
    result = {
        "schema_version": "1.0.0",
        "writer": "compare_and_swap_mission",
        "python_files_scanned": sum(1 for _ in _python_files(root)),
        "call_sites": [asdict(call) for call in calls],
        "legacy_call_sites": [asdict(call) for call in legacy],
        "parse_errors": parse_errors,
        "status": "PASS" if not legacy and not parse_errors else "FAIL",
    }
    return result


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    result = audit(root)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
