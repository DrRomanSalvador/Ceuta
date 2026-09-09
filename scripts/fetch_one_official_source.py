#!/usr/bin/env python3
"""Descarga UNA fuente pública y registra [fuente][fecha][método][hash]."""

from __future__ import annotations

import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "backend"))

from app.core.source_registry import (
    SourceType,
    register_source,
    update_fetch,
    list_sources,
)

# Ampliar solo con URLs públicas reales
SOURCES = [
    {
        "id": "eu_ai_act",
        "url": "https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai",
        "type": SourceType.INSTITUTIONAL,
    },
]


def fetch(url: str) -> tuple[int | None, bytes, str]:
    req = Request(url, headers={"User-Agent": "CeutIA-SourceFetch/0.1"})
    try:
        with urlopen(req, timeout=20) as resp:
            raw = resp.read()
            return resp.getcode(), raw, hashlib.sha256(raw).hexdigest()
    except HTTPError as e:
        return e.code, b"", ""
    except (URLError, Exception):
        return None, b"", ""


def main() -> None:
    out_dir = Path("monitor_records")
    out_dir.mkdir(exist_ok=True)
    for s in SOURCES:
        register_source(s["id"], s["url"], s["type"])
        status, raw, h = fetch(s["url"])
        excerpt = raw[:400].decode("utf-8", errors="replace") if raw else ""
        rec = update_fetch(s["id"], http_status=status, content_sha256=h or None, excerpt=excerpt)
        path = out_dir / f"{s['id']}_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
        path.write_text(json.dumps(rec.__dict__, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        print(s["id"], "status=", status, "->", path)


if __name__ == "__main__":
    main()