#!/usr/bin/env python3
"""Ceuta Ciudadano legacy compatibility module.

The historical standalone script was syntactically corrupted by an appended
configuration snippet.  This repaired module preserves its public analytical
helpers without pretending that the legacy risk model is scientifically
validated.  Production control-plane functionality lives under ``mission``
and ``src``.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

try:
    import numpy as np
except ImportError:  # pragma: no cover
    np = None

CONFIG = {
    "version": "2.0.0-legacy-repaired",
    "timestamp": "2026-09-09T12:48:00Z",
    "api_keys": {
        "telegram": os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "reuters": os.getenv("REUTERS_API_KEY", ""),
    },
    "weights": {
        "capability_growth": 0.25,
        "incident_count": 0.20,
        "governance_gap": 0.20,
        "awareness_level": -0.15,
        "international_cooperation": -0.20,
    },
    "thresholds": {"green": 0.4, "yellow": 0.6, "orange": 0.75},
    "update_interval_hours": 6,
}

FUENTES = {
    "UN": {"nombre": "Naciones Unidas (OHCHR)", "veracidad": "OFICIAL", "url": "https://www.ohchr.org/en/press-releases"},
    "Reuters": {"nombre": "Reuters AI", "veracidad": "MEDIO_PROFESIONAL", "url": "https://www.reuters.com/technology/artificial-intelligence/"},
    "ScienceDirect": {"nombre": "ScienceDirect", "veracidad": "CIENTIFICA_REVISADA", "url": "https://www.sciencedirect.com/"},
    "arXiv": {"nombre": "arXiv", "veracidad": "PREPRINT", "url": "https://arxiv.org/"},
    "GitHub": {"nombre": "GitHub (proyectos IA)", "veracidad": "SOCIAL_NO_VERIFICADA", "url": "https://github.com/topics/artificial-intelligence"},
}


def sigmoid(x: float) -> float:
    if x >= 0:
        z = pow(2.718281828459045, -x)
        return 1.0 / (1.0 + z)
    z = pow(2.718281828459045, x)
    return z / (1.0 + z)


def fetch_with_fallback(url: str, timeout: int = 10, auth: bool = False) -> Optional[Dict]:
    """Fetch JSON when requests is available; otherwise return no observation."""
    try:
        import requests
        headers = {}
        if auth and CONFIG["api_keys"].get("reuters"):
            headers["Authorization"] = f"Bearer {CONFIG['api_keys']['reuters']}"
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except Exception:
        return None


def extract_indicators_from_data(un_data, reuters_data, arxiv_data, github_data) -> Dict[str, float]:
    github_activity = min(github_data.get("top_stars", 0) / 10000, 1.0)
    arxiv_activity = min(arxiv_data.get("count", 0) / 100, 1.0)
    un_incidents = min(un_data.get("count", 0) / 50, 1.0)
    reuters_incidents = min(reuters_data.get("count", 0) / 100, 1.0)
    return {
        "capability_growth": round((github_activity + arxiv_activity) / 2, 4),
        "incident_count": round((un_incidents + reuters_incidents) / 2, 4),
        "governance_gap": round(1.0 - min((un_data.get("count", 0) + reuters_data.get("count", 0)) / 200, 1.0), 4),
        "awareness_level": round(min((un_data.get("count", 0) + reuters_data.get("count", 0) + arxiv_data.get("count", 0)) / 300, 1.0), 4),
        "international_cooperation": round((github_activity + arxiv_activity + un_incidents) / 3, 4),
    }


def calculate_risk(indicators: Dict[str, float]) -> Dict:
    """Legacy heuristic calculation; not a validated predictive model."""
    raw_score = sum(CONFIG["weights"][key] * indicators.get(key, 0.5) for key in CONFIG["weights"])
    risk_score = sigmoid(raw_score)
    n = len(indicators)
    if np is not None and n >= 2:
        se = float(np.sqrt(risk_score * (1 - risk_score) / n))
    else:
        se = 0.5
    ci_low = max(0.0, risk_score - 1.96 * se)
    ci_high = min(1.0, risk_score + 1.96 * se)
    if risk_score < CONFIG["thresholds"]["green"]:
        level = "GREEN"
    elif risk_score < CONFIG["thresholds"]["yellow"]:
        level = "YELLOW"
    elif risk_score < CONFIG["thresholds"]["orange"]:
        level = "ORANGE"
    else:
        level = "RED"
    audit_content = f"{risk_score}{ci_low}{ci_high}{json.dumps(indicators, sort_keys=True)}"
    return {
        "risk_score": round(risk_score, 4),
        "confidence_interval": [round(ci_low, 4), round(ci_high, 4)],
        "standard_error": round(se, 4),
        "alert_level": level,
        "component_scores": indicators,
        "audit_hash": hashlib.sha256(audit_content.encode()).hexdigest()[:16],
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "config_version": CONFIG["version"],
        "scientific_status": "LEGACY_HEURISTIC_NOT_VALIDATED",
    }


def estratificar_fuentes() -> List[Dict]:
    niveles = {"OFICIAL": 0.95, "CIENTIFICA_REVISADA": 0.90, "MEDIO_PROFESIONAL": 0.75, "PREPRINT": 0.50, "SOCIAL_NO_VERIFICADA": 0.20}
    return [
        {"nombre": info["nombre"], "nivel_veracidad": info["veracidad"], "score": niveles[info["veracidad"]], "url": info["url"]}
        for info in FUENTES.values()
    ]


def generar_informe_ciudadano(risk_result: Dict, fuentes_strat: List[Dict]) -> str:
    return "\n".join([
        "CEUTA CIUDADANO — INFORME LEGACY",
        f"Risk score (heuristic, not validated): {risk_result['risk_score']:.4f}",
        f"Alert level: {risk_result['alert_level']}",
        f"Scientific status: {risk_result['scientific_status']}",
        f"Audit hash: {risk_result['audit_hash']}",
    ])


def backtest() -> Dict[str, float | bool]:
    """Legacy smoke backtest only; simulated data are not prospective validation."""
    historical = [(0.45, 0.48), (0.52, 0.50), (0.58, 0.55), (0.62, 0.60), (0.65, 0.63), (0.67, 0.66)]
    errors = [abs(a - p) for a, p in historical]
    mae = sum(errors) / len(errors)
    rmse = (sum(e * e for e in errors) / len(errors)) ** 0.5
    return {"mae": mae, "rmse": rmse, "calibrated": False}


def run_monitor() -> None:
    raise RuntimeError("Legacy monitor is not an authoritative CeutIA runtime; use the control-plane runtime.")


def run_web() -> None:
    raise RuntimeError("Legacy web entrypoint is not an authoritative CeutIA runtime.")


def run_bot() -> None:
    raise RuntimeError("Legacy bot entrypoint is not an authoritative CeutIA runtime.")


if __name__ == "__main__":
    print(generar_informe_ciudadano(calculate_risk({}), estratificar_fuentes()))
