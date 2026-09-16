"""Static audit that every canonical event writer has replay coverage."""
from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path

EXACT_REPLAY_TYPES = {
    "CONTROL_PLANE_GENESIS", "MISSION_ADMISSION", "MISSION_STATE_TRANSITION",
    "WORK_CLAIM_ACQUIRED", "WORK_CLAIM_RELEASED", "HANDOFF_LIFECYCLE", "HANDOFF_STATE",
    "MISSION_CONTRIBUTION", "CONTRIBUTION_RECORDED", "MISSION_CONTRADICTION",
    "CONTRADICTION_RECORDED", "RESPONSE_COUPLING_RECORDED", "MATERIALIZED_STATE_CAS",
    "MISSION_RETIREMENT", "MISSION_RECOVERY",
}


@dataclass(frozen=True)
class Writer:
    path: str
    line: int
    event_type: str
    replay_supported: bool
    negative_test: bool = False


def _python_files(root: Path):
    excluded = {".git", ".venv", "venv", "build", "dist", "__pycache__"}
    for path in root.rglob("*.py"):
        if not any(part in excluded for part in path.parts):
            yield path


def _replay_supported(event_type: str) -> bool:
    return event_type in EXACT_REPLAY_TYPES or event_type.startswith("MISSION_LIFECYCLE_")


def _enclosing_function(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> ast.FunctionDef | ast.AsyncFunctionDef | None:
    current: ast.AST | None = node
    while current is not None:
        current = parents.get(current)
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return current
    return None


def _event_type_keyword(node: ast.Call) -> str | None:
    keyword = next((kw for kw in node.keywords if kw.arg == "event_type"), None)
    if keyword is None or not isinstance(keyword.value, ast.Constant) or not isinstance(keyword.value.value, str):
        return None
    return keyword.value.value


def audit(root: Path) -> dict:
    writers: list[Writer] = []
    parse_errors: list[str] = []
    dynamic_event_types: list[dict[str, object]] = []
    for path in _python_files(root):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError) as exc:
            parse_errors.append(f"{path}: {exc}")
            continue
        parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            function_name = node.func.id if isinstance(node.func, ast.Name) else node.func.attr if isinstance(node.func, ast.Attribute) else None
            if function_name == "append_payload":
                event_type = _event_type_keyword(node)
                enclosing = _enclosing_function(node, parents)
                if event_type is None:
                    # lifecycle_governance._event is a canonical wrapper whose
                    # callers supply the concrete event type; audit those callers below.
                    if enclosing is not None and enclosing.name == "_event":
                        continue
                    dynamic_event_types.append({"path": str(path.relative_to(root)), "line": node.lineno})
                    continue
                negative_test = path.name.startswith("test_") and enclosing is not None and "rejects_unknown_event_type" in enclosing.name
                writers.append(Writer(str(path.relative_to(root)), node.lineno, event_type, _replay_supported(event_type), negative_test))
            elif function_name == "_event":
                event_type = _event_type_keyword(node)
                if event_type is not None:
                    writers.append(Writer(str(path.relative_to(root)), node.lineno, event_type, _replay_supported(event_type)))
                else:
                    dynamic_event_types.append({"path": str(path.relative_to(root)), "line": node.lineno})

    unsupported = [writer for writer in writers if not writer.replay_supported and not writer.negative_test]
    result = {
        "schema_version": "1.1.0",
        "writers": [writer.__dict__ for writer in writers],
        "dynamic_event_types": dynamic_event_types,
        "unsupported_event_types": [writer.__dict__ for writer in unsupported],
        "parse_errors": parse_errors,
        "status": "PASS" if not unsupported and not dynamic_event_types and not parse_errors else "FAIL",
    }
    return result


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    result = audit(root)
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
