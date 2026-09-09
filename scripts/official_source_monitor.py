#!/usr/bin/env python3
"""
Monitor mínimo de fuentes públicas.
- Descarga páginas/indicadores públicos cuando se ejecuta.
- Guarda registro auditable: [fuente] [fecha] [método] [extracto].
- NO calcula riesgo existencial.
- NO emite alertas de umbral.
- NO inventa datos ni probabilidades.
"""

from __future__ import annotations

import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# Fuentes públicas concretas (ampliable). Solo URLs verificables.
SOURCES = [
    {
        "id": "ohchr_ai_statement_context",
        "url": "https://www.ohchr.org/en/statements-and-speeches",
        "method": "HTTP GET + extract title/snippet if available",
        "note": "Listado de statements OHCHR; no es un feed de riesgo existencial.",
    },
    {
        "id": "un_ai_panel",
        "url": "https://www.un.org/independent-international-scientific-panel-ai/en/preliminary-report",
        "method": "HTTP GET",
        "note": "Página del panel científico independiente sobre IA (ONU).",
    },
    {
        "id": "eu_ai_act",
        "url": "https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai",
        "method": "HTTP GET",
        "note": "Marco regulatorio AI Act (Comisión Europea).",
    },
]

OUT_DIR = Path("monitor_records")
OUT_DIR.mkdir(exist_ok=True)


def fetch(url: str, timeout: int = 20) -> tuple[int | None, str, str]:
    """Devuelve (status_code, body_text_or_error, content_hash)."""
    req = Request(url, headers={"User-Agent": "CeutIA-SourceMonitor/0.1 (audit; non-operational)"})
    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            text = raw.decode("utf-8", errors="replace")
            status = getattr(resp, "status", None) or resp.getcode()
            h = hashlib.sha256(raw).hexdigest()
            return status, text, h
    except HTTPError as e:
        return e.code, f"HTTPError: {e}", ""
    except URLError as e:
        return None, f"URLError: {e}", ""
    except Exception as e:
        return None, f"Error: {type(e).__name__}: {e}", ""


def record_source(src: dict) -> dict:
    now = datetime.now(timezone.utc).isoformat()
    status, body, content_hash = fetch(src["url"])
    # Solo guardamos un extracto corto para auditoría, no el HTML completo
    excerpt = body[:500].replace("\n", " ").strip() if body else ""

    entry = {
        "id": src["id"],
        "fuente": src["url"],
        "fecha_consulta_utc": now,
        "metodo": src["method"],
        "http_status": status,
        "content_sha256": content_hash or None,
        "excerpt": excerpt,
        "nota": src.get("note", ""),
        "clasificacion": "OBSERVACION_DE_FUENTE_PUBLICA",
        "no_es": [
            "calculo de riesgo existencial",
            "probabilidad calibrada",
            "alerta operativa",
            "dato inventado",
        ],
    }
    return entry


def main() -> None:
    results = []
    for src in SOURCES:
        print(f"Consultando: {src['id']} ...")
        entry = record_source(src)
        results.append(entry)
        # Un archivo por fuente y corrida (auditable)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out = OUT_DIR / f"{src['id']}_{stamp}.json"
        out.write_text(json.dumps(entry, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  -> {out} (status={entry['http_status']})")

    summary = OUT_DIR / f"summary_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    summary.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Resumen: {summary}")


if __name__ == "__main__":
    main()