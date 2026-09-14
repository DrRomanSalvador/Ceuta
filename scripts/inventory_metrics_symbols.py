#!/usr/bin/env python3
"""Build a reproducible AST inventory of the current CeutIA metrics module."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path


def build_inventory(path: Path) -> dict[str, object]:
    source = path.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(path))

    occurrences: defaultdict[str, list[dict[str, object]]] = defaultdict(list)
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            kind = "async_function" if isinstance(node, ast.AsyncFunctionDef) else (
                "function" if isinstance(node, ast.FunctionDef) else "class"
            )
            occurrences[node.name].append({"line": node.lineno, "kind": kind})

    counts = Counter({name: len(items) for name, items in occurrences.items()})
    duplicates = {
        name: items for name, items in sorted(occurrences.items()) if len(items) > 1
    }

    return {
        "schema_version": "1",
        "source": str(path.as_posix()),
        "sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "line_count": len(source.splitlines()),
        "top_level_definition_count": sum(counts.values()),
        "unique_symbol_count": len(counts),
        "duplicate_symbol_count": len(duplicates),
        "duplicate_definition_count": sum(len(items) for items in duplicates.values()),
        "symbols": [
            {
                "name": name,
                "count": count,
                "locations": occurrences[name],
            }
            for name, count in sorted(counts.items())
        ],
        "duplicates": [
            {
                "name": name,
                "count": len(items),
                "locations": items,
            }
            for name, items in duplicates.items()
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--path",
        type=Path,
        default=Path("backend/app/core/metrics.py"),
        help="metrics.py path",
    )
    parser.add_argument("--output", type=Path, help="optional JSON output path")
    args = parser.parse_args()

    inventory = build_inventory(args.path)
    payload = json.dumps(inventory, indent=2, ensure_ascii=False) + "\n"

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")

    print(payload, end="")


if __name__ == "__main__":
    main()
