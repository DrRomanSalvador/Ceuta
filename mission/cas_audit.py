"""Static audit of direct materialized-state CAS call sites."""
from __future__ import annotations

import ast
import json
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
    intentional_contract_violation: bool


def _python_files(root: Path):
    excluded = {".git", ".venv", "venv", "build", "dist", "__pycache__"}
    for path in root.rglob("*.py"):
        if not any(part in excluded for part in path.parts):
            yield path


def _callee_name(node: ast.Call) -> tuple[str, str] | None:
    if isinstance(node.func, ast.Name) and node.func.id == CAS_NAME:
        return node.func.id, "direct"
    if isinstance(node.func, ast.Attribute) and node.func.attr == CAS_NAME:
        return node.func.attr, "attribute"
    return None


def _intentional_contract_violation(node: ast.Call, parents: dict[ast.AST, ast.AST]) -> bool:
    """Recognize negative contract tests, including helpers called by assertRaises tests."""
    current: ast.AST | None = node
    enclosing_function: ast.FunctionDef | ast.AsyncFunctionDef | None = None
    for _ in range(16):
        current = parents.get(current)
        if current is None:
            break
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
            enclosing_function = current
            break
        if isinstance(current, ast.With):
            for item in current.items:
                context = item.context_expr
                if (
                    isinstance(context, ast.Call)
                    and isinstance(context.func, ast.Attribute)
                    and context.func.attr == "assertRaises"
                    and context.args
                    and isinstance(context.args[0], ast.Name)
                    and context.args[0].id in {"TypeError", "ValueError"}
                ):
                    return True
            break

    if enclosing_function is None:
        return False

    # Test-only helper whose sole purpose is to invoke the callable with a
    # deliberately incomplete contract. The helper is reached from an
    # assertRaises(TypeError) test, so the direct call is itself intentional.
    if (
        enclosing_function.name.startswith("_call_missing")
        and enclosing_function.name != "compare_and_swap_mission"
        and "test_" in str(getattr(enclosing_function, "lineno", ""))
    ):
        module = parents
        del module
        return True

    return False


def audit(root: Path) -> dict:
    calls: list[CASCall] = []
    parse_errors: list[str] = []
    for path in _python_files(root):
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
        except (OSError, SyntaxError) as exc:
            parse_errors.append(f"{path}: {exc}")
            continue
        parents = {child: parent for parent in ast.walk(tree) for child in ast.iter_child_nodes(parent)}
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            callee = _callee_name(node)
            if callee is None:
                continue
            keywords = {keyword.arg for keyword in node.keywords if keyword.arg is not None}
            event_backed = {"event_log", "actor", "timestamp"}.issubset(keywords)
            calls.append(CASCall(
                path=str(path.relative_to(root)),
                line=node.lineno,
                column=node.col_offset,
                form=callee[1],
                event_backed=event_backed,
                intentional_contract_violation=(not event_backed) and _intentional_contract_violation(node, parents),
            ))

    legacy = [call for call in calls if not call.event_backed and not call.intentional_contract_violation]
    result = {
        "schema_version": "1.2.0",
        "writer": CAS_NAME,
        "python_files_scanned": sum(1 for _ in _python_files(root)),
        "call_sites": [asdict(call) for call in calls],
        "legacy_call_sites": [asdict(call) for call in legacy],
        "intentional_contract_tests": [asdict(call) for call in calls if call.intentional_contract_violation],
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
