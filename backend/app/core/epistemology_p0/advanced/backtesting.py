"""
P2 — Backtesting automatizado a escala.

Regla dura: solo datos con ingestion_time <= T de simulación.
Reporta cobertura, fugas detectadas y pesos efectivos.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Callable, Any, Dict
from datetime import datetime, timezone

from ..evidence.models import Evidence
from ..registry import ClaimRegistry
from ..temporal.multitemporal import TemporalFilter
from ..operational.bridge import ObservationBridge
from ..operational.uncertainty import weight_by_confidence


@dataclass
class BacktestConfig:
    simulation_times: List[datetime]
    variable: Optional[str] = None
    geography: Optional[str] = None
    require_no_future_leak: bool = True


@dataclass
class BacktestSlice:
    simulation_time: str
    n_available: int
    n_rejected_future: int
    mean_model_weight: Optional[float]
    observation_ids: List[str]
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "simulation_time": self.simulation_time,
            "n_available": self.n_available,
            "n_rejected_future": self.n_rejected_future,
            "mean_model_weight": self.mean_model_weight,
            "observation_ids": self.observation_ids,
            "notes": self.notes,
        }


@dataclass
class BacktestReport:
    config_variable: Optional[str]
    slices: List[BacktestSlice]
    total_future_leaks_blocked: int
    ok: bool
    summary: str

    def to_dict(self) -> dict:
        return {
            "config_variable": self.config_variable,
            "slices": [s.to_dict() for s in self.slices],
            "total_future_leaks_blocked": self.total_future_leaks_blocked,
            "ok": self.ok,
            "summary": self.summary,
        }


class BacktestRunner:
    def __init__(self, registry: ClaimRegistry, bridge: Optional[ObservationBridge] = None):
        self.registry = registry
        self.bridge = bridge or ObservationBridge()

    def run(self, config: BacktestConfig) -> BacktestReport:
        all_ev = list(self.registry.evidences.values())
        slices: List[BacktestSlice] = []
        total_blocked = 0

        for t in config.simulation_times:
            available = TemporalFilter.filter_by_ingestion_time(all_ev, t)
            rejected = len(all_ev) - len(available)
            total_blocked += rejected

            if config.require_no_future_leak:
                TemporalFilter.assert_no_future_leak(available, t)

            obs_ids: List[str] = []
            weights: List[float] = []
            for ev in available:
                var = config.variable or "unknown"
                obs = self.bridge.emit(ev, variable=var, geography=config.geography)
                payload = self.bridge.as_payload(obs)
                obs_ids.append(payload.get("observation_id", ev.evidence_id))
                weights.append(payload["model_weight"])

            mean_w = sum(weights) / len(weights) if weights else None
            slices.append(
                BacktestSlice(
                    simulation_time=t.isoformat(),
                    n_available=len(available),
                    n_rejected_future=rejected,
                    mean_model_weight=round(mean_w, 6) if mean_w is not None else None,
                    observation_ids=obs_ids,
                    notes="OK: no future leak in available set" if config.require_no_future_leak else "",
                )
            )

        ok = True
        summary = (
            f"Backtest sobre {len(config.simulation_times)} cortes temporales; "
            f"{total_blocked} observaciones futuras bloqueadas."
        )
        return BacktestReport(
            config_variable=config.variable,
            slices=slices,
            total_future_leaks_blocked=total_blocked,
            ok=ok,
            summary=summary,
        )
