"""Decision-making under deep uncertainty and forecast aggregation primitives.

This module deliberately avoids an expected-value optimizer.  RDM evaluates
strategies over explicit plausible futures; DAPP represents adaptive pathways
and observable signposts; Bayesian model averaging aggregates probabilistic
forecasts using validation log predictive likelihood.  These are decision-
support mechanisms, not claims that uncertainty has been eliminated.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import itertools
import json
import math
import sqlite3
from typing import Callable, Sequence


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def _digest(value: object) -> str:
    return sha256(_canonical(value).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class PlausibleFuture:
    future_id: str
    assumptions: tuple[tuple[str, float], ...]

    def __post_init__(self) -> None:
        if not self.future_id or not self.assumptions:
            raise ValueError("future_id and assumptions are required")
        if len({key for key, _ in self.assumptions}) != len(self.assumptions):
            raise ValueError("future assumption keys must be unique")
        if any(not math.isfinite(value) for _, value in self.assumptions):
            raise ValueError("future assumptions must be finite")


@dataclass(frozen=True, slots=True)
class StrategyEvaluation:
    strategy_id: str
    future_id: str
    performance: float
    meets_threshold: bool
    regret: float = 0.0


@dataclass(frozen=True, slots=True)
class RobustnessProfile:
    strategy_id: str
    future_count: int
    satisficing_rate: float
    worst_case: float
    lower_quantile: float
    max_regret: float
    robustness_score: float


class ExploratoryModel:
    """Generate a reproducible Cartesian plausible-futures design."""

    def __init__(self, dimensions: dict[str, Sequence[float]]) -> None:
        if not dimensions:
            raise ValueError("at least one uncertainty dimension is required")
        normalized: dict[str, tuple[float, ...]] = {}
        for name, values in dimensions.items():
            if not name or not values:
                raise ValueError("uncertainty dimensions require names and values")
            vals = tuple(float(v) for v in values)
            if any(not math.isfinite(v) for v in vals):
                raise ValueError("uncertainty values must be finite")
            normalized[name] = vals
        self.dimensions = normalized

    def futures(self) -> tuple[PlausibleFuture, ...]:
        names = tuple(sorted(self.dimensions))
        result: list[PlausibleFuture] = []
        for values in itertools.product(*(self.dimensions[name] for name in names)):
            assumptions = tuple(zip(names, values))
            result.append(PlausibleFuture(_digest(assumptions)[:16], assumptions))
        return tuple(result)


class RobustDecisionMaker:
    """RDM evaluator using satisficing, worst-case and regret rather than EV."""

    def __init__(self, threshold: float = 0.0, lower_quantile: float = 0.1) -> None:
        if not math.isfinite(threshold):
            raise ValueError("threshold must be finite")
        if not 0 < lower_quantile <= 0.5:
            raise ValueError("lower_quantile must be in (0, 0.5]")
        self.threshold = threshold
        self.lower_quantile = lower_quantile

    def evaluate(
        self,
        strategies: dict[str, Callable[[PlausibleFuture], float]],
        futures: Sequence[PlausibleFuture],
    ) -> tuple[RobustnessProfile, ...]:
        if not strategies or not futures:
            raise ValueError("strategies and futures are required")
        raw: dict[str, list[float]] = {}
        for strategy_id, evaluator in strategies.items():
            if not strategy_id:
                raise ValueError("strategy_id is required")
            values = [float(evaluator(future)) for future in futures]
            if any(not math.isfinite(v) for v in values):
                raise ValueError("strategy performance must be finite")
            raw[strategy_id] = values
        per_future_best = [max(values[index] for values in raw.values()) for index in range(len(futures))]
        profiles: list[RobustnessProfile] = []
        for strategy_id, values in raw.items():
            ordered = sorted(values)
            index = max(0, min(len(ordered) - 1, math.ceil(self.lower_quantile * len(ordered)) - 1))
            regrets = [per_future_best[i] - value for i, value in enumerate(values)]
            satisficing = sum(value >= self.threshold for value in values) / len(values)
            worst = ordered[0]
            lower = ordered[index]
            max_regret = max(regrets)
            # A bounded multi-criteria robustness score; no probability over futures is assumed.
            scale = max(abs(worst), abs(lower), abs(max_regret), 1.0)
            score = 0.5 * satisficing + 0.25 * (worst / scale + 1.0) / 2 + 0.25 * (1.0 - max_regret / scale)
            profiles.append(RobustnessProfile(strategy_id, len(futures), satisficing, worst, lower, max_regret, max(0.0, min(1.0, score))))
        return tuple(sorted(profiles, key=lambda p: (-p.robustness_score, p.max_regret, p.strategy_id)))


@dataclass(frozen=True, slots=True)
class Signpost:
    signpost_id: str
    metric: str
    threshold: float
    direction: str
    next_pathway: str

    def __post_init__(self) -> None:
        if self.direction not in {"above", "below"}:
            raise ValueError("direction must be above or below")
        if not self.signpost_id or not self.metric or not self.next_pathway:
            raise ValueError("signpost fields are required")

    def triggered(self, value: float) -> bool:
        if not math.isfinite(value):
            raise ValueError("signpost value must be finite")
        return value >= self.threshold if self.direction == "above" else value <= self.threshold


@dataclass(frozen=True, slots=True)
class AdaptivePathway:
    pathway_id: str
    strategy_id: str
    signposts: tuple[Signpost, ...]
    trigger_window: int = 1

    def __post_init__(self) -> None:
        if not self.pathway_id or not self.strategy_id or not self.signposts:
            raise ValueError("adaptive pathway requires strategy and signposts")
        if self.trigger_window < 1:
            raise ValueError("trigger_window must be >= 1")

    def next_actions(self, observations: dict[str, Sequence[float]]) -> tuple[str, ...]:
        actions: list[str] = []
        for signpost in self.signposts:
            values = observations.get(signpost.metric, ())
            if len(values) >= self.trigger_window and all(signpost.triggered(v) for v in values[-self.trigger_window:]):
                actions.append(signpost.next_pathway)
        return tuple(actions)


@dataclass(frozen=True, slots=True)
class ModelForecast:
    model_id: str
    prior_weight: float
    validation_log_score: float
    probability: float

    def __post_init__(self) -> None:
        if self.prior_weight <= 0 or not math.isfinite(self.prior_weight):
            raise ValueError("prior_weight must be finite and > 0")
        if not math.isfinite(self.validation_log_score) or not 0 < self.probability < 1:
            raise ValueError("forecast values are invalid")


@dataclass(frozen=True, slots=True)
class EnsembleForecast:
    probability: float
    weights: tuple[tuple[str, float], ...]
    disagreement: float


class BayesianModelAverager:
    """Pseudo-posterior BMA from prior weights and validation log predictive scores."""

    def combine(self, forecasts: Sequence[ModelForecast]) -> EnsembleForecast:
        if not forecasts:
            raise ValueError("at least one model is required")
        scores = [math.log(item.prior_weight) + item.validation_log_score for item in forecasts]
        maximum = max(scores)
        unnormalized = [math.exp(score - maximum) for score in scores]
        total = sum(unnormalized)
        weights = [value / total for value in unnormalized]
        probability = sum(weight * item.probability for weight, item in zip(weights, forecasts))
        disagreement = math.sqrt(sum(weight * (item.probability - probability) ** 2 for weight, item in zip(weights, forecasts)))
        return EnsembleForecast(probability, tuple((item.model_id, weight) for item, weight in zip(forecasts, weights)), disagreement)

    @staticmethod
    def validation_log_score(probability: float, outcome: bool, epsilon: float = 1e-6) -> float:
        if not 0 < epsilon < 0.5 or not 0 < probability < 1:
            raise ValueError("invalid probability domain")
        p = min(1 - epsilon, max(epsilon, probability))
        return math.log(p if outcome else 1 - p)


@dataclass(frozen=True, slots=True)
class CausalIdentificationContract:
    estimand: str
    treatment: str
    outcome: str
    covariates: tuple[str, ...]
    assumptions: tuple[str, ...]
    positivity_required: bool = True
    unobserved_confounding_sensitivity: float | None = None

    def __post_init__(self) -> None:
        if not self.estimand or not self.treatment or not self.outcome:
            raise ValueError("estimand, treatment and outcome are required")
        if not self.assumptions:
            raise ValueError("causal assumptions must be explicit")
        if self.unobserved_confounding_sensitivity is not None and not 0 <= self.unobserved_confounding_sensitivity <= 1:
            raise ValueError("sensitivity must be in [0,1]")

    @property
    def identifiable(self) -> bool:
        required = {"consistency", "conditional_exchangeability", "positivity"}
        present = {item.strip().lower() for item in self.assumptions}
        return required.issubset(present)


class RobustDecisionLedger:
    """Durable audit record for RDM/BMA/causal decisions."""

    def __init__(self, storage_path: str) -> None:
        if not storage_path:
            raise ValueError("storage_path is required")
        self.storage_path = storage_path
        with sqlite3.connect(storage_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS robust_decision_records (
                record_id TEXT PRIMARY KEY, mechanism TEXT NOT NULL, payload TEXT NOT NULL,
                created_at TEXT NOT NULL, record_hash TEXT NOT NULL
            )""")

    def append(self, mechanism: str, payload: dict) -> str:
        if not mechanism:
            raise ValueError("mechanism is required")
        created = datetime.now(timezone.utc).isoformat()
        record_id = _digest((mechanism, payload, created))
        canonical = _canonical(payload)
        with sqlite3.connect(self.storage_path) as db:
            db.execute("INSERT INTO robust_decision_records VALUES(?,?,?,?,?)", (record_id, mechanism, canonical, created, _digest(canonical)))
        return record_id
