"""Static audit that every canonical append_payload event type is replayable."""
from __future__ import annotations

import ast
import json
from pathlib import Path

EXACT_REPLAY_TYPES = {
    "CONTROL_PLANE_GENESIS",
    "MISSION_ADMISSION",
    "MISSION_STATE_TRANSITION",
    "WORK_CLAIM_ACQUIRED",
    "WORK_CLAIM_RELEASED",
    "HANDOFF_LIFECYCLE",
    "HANDOFF_STATE",
    "MISSION_CONTRIBUTION",
    "CONTRIBUTION_RECORDED",
    "MISSION_CONTRADICTION",
    "CONTRADICTION_RECORDED",
    "RESPONSE_COUPLING_RECORDED",
    "MATERIALIZED_STATE_CAS",
    "MISSION_RETIREMENT",
    "MISSION_RECOVERY",
}


def _python_files(root: Path):
    excluded = {".git", ".venv", "venv", "build", "dist", "__pycache__"}
    for path in root.rglob("*.py"):
        if not any(part in excluded for part in path.parts):
            yield path


def _replay_supported(event_type: str) -> bool:
    return event_type in EXACT_REPLAY_TYPES or event_type.startswith("MISSION_LIFECYCLE_")


def audit(root: Path) -> dict:
    writers: list[dict[str, object]] = []
    parse_errors: list[str] = []
    dynamic_event_types: list[dict[str, object]] = []
    for path in _python_files(root):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (OSError, SyntaxError) as exc:
            parse_errors.append(f"{path}: {exc}")
            continue
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            function_name = None
            if isinstance(node.func, ast.Name):
                function_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                function_name = node.func.attr
            if function_name != "append_payload":
                continue
            event_keyword = next((kw for kw in node.keywords if kw.arg == "event_type"), None)
            if event_keyword is None or not isinstance(event_keyword.value, ast.Constant) or not isinstance(event_keyword.value.value, str):
                dynamic_event_types.append({"path": str(path.relative_to(root)), "line": node.lineno})
                continue
            event_type = event_keyword.value.value
            writers.append({
                "path": str(path.relative_to(root)),
                "line": node.lineno,
                "event_type": event_type,
                "replay_supported": _replay_supported(event_type),
            })

    unsupported = [writer for writer in writers if not writer["replay_supported"]]
    result = {
        "schema_version": "1.0.0",
        "writer": "append_payload",
        "writers": writers,
        "dynamic_event_types": dynamic_event_types,
        "unsupported_event_types": unsupported,
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
