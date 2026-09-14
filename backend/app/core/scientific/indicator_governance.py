"""Governance primitives for anti-Goodhart indicator publication.

These primitives deliberately separate three concerns:
- immutable pre-registration of the indicator configuration;
- controlled rotation/retirement of indicators and adversarial findings;
- bounded privacy release with explicit per-actor query accounting.

They do not claim that secrecy or differential privacy guarantees truthful
behaviour. They constrain observable interfaces so gaming and reconstruction
become harder while preserving an auditable configuration and release policy.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import math
from typing import Iterable


@dataclass(frozen=True, slots=True)
class IndicatorDefinition:
    indicator_id: str
    epoch: str
    weight: float
    threshold: float
    active: bool = True

    def __post_init__(self) -> None:
        if not self.indicator_id or not self.epoch:
            raise ValueError("indicator_id and epoch are required")
        if not math.isfinite(self.weight) or self.weight < 0:
            raise ValueError("weight must be finite and non-negative")
        if not math.isfinite(self.threshold):
            raise ValueError("threshold must be finite")


@dataclass(frozen=True, slots=True)
class PreRegistration:
    registration_id: str
    epoch: str
    configuration_hash: str
    registered_at: str


@dataclass(frozen=True, slots=True)
class RedTeamFinding:
    indicator_id: str
    severity: str
    exploitable: bool
    finding_id: str
    mitigation: str = ""


class IndicatorGovernance:
    """Immutable-by-epoch indicator configuration with explicit rotation."""

    def __init__(self) -> None:
        self._definitions: dict[str, tuple[IndicatorDefinition, ...]] = {}
        self._registrations: dict[str, PreRegistration] = {}
        self._findings: dict[str, tuple[RedTeamFinding, ...]] = {}

    @staticmethod
    def configuration_hash(definitions: Iterable[IndicatorDefinition]) -> str:
        canonical = [
            {
                "indicator_id": item.indicator_id,
                "epoch": item.epoch,
                "weight": item.weight,
                "threshold": item.threshold,
                "active": item.active,
            }
            for item in sorted(definitions, key=lambda item: item.indicator_id)
        ]
        payload = json.dumps(canonical, sort_keys=True, separators=(",", ":"))
        return sha256(payload.encode("utf-8")).hexdigest()

    def preregister(
        self,
        registration_id: str,
        epoch: str,
        definitions: Iterable[IndicatorDefinition],
        registered_at: str,
    ) -> PreRegistration:
        if registration_id in self._registrations:
            raise ValueError(f"duplicate registration_id: {registration_id}")
        items = tuple(definitions)
        if not items or any(item.epoch != epoch for item in items):
            raise ValueError("a registration requires non-empty, single-epoch definitions")
        if epoch in self._registrations:
            raise ValueError(f"epoch already preregistered: {epoch}")
        if epoch in self._definitions:
            raise ValueError(f"epoch already registered: {epoch}")
        digest = self.configuration_hash(items)
        registration = PreRegistration(registration_id, epoch, digest, registered_at)
        self._definitions[epoch] = items
        self._registrations[epoch] = registration
        return registration

    def definitions(self, epoch: str) -> tuple[IndicatorDefinition, ...]:
        return self._definitions[epoch]

    def preregistration(self, epoch: str) -> PreRegistration:
        return self._registrations[epoch]

    def verify_configuration(self, epoch: str, definitions: Iterable[IndicatorDefinition]) -> bool:
        return self.configuration_hash(definitions) == self._registrations[epoch].configuration_hash

    def rotate(self, epoch: str, next_epoch: str, definitions: Iterable[IndicatorDefinition], registered_at: str) -> PreRegistration:
        if next_epoch == epoch:
            raise ValueError("rotation requires a new epoch")
        if any(item.active for item in self._definitions[epoch]):
            retired = tuple(
                IndicatorDefinition(item.indicator_id, item.epoch, item.weight, item.threshold, active=False)
                for item in self._definitions[epoch]
            )
            self._definitions[epoch] = retired
        return self.preregister(f"rotation:{next_epoch}", next_epoch, definitions, registered_at)

    def record_red_team_findings(self, epoch: str, findings: Iterable[RedTeamFinding]) -> None:
        items = tuple(findings)
        known = {item.indicator_id for item in self._definitions[epoch]}
        if any(item.indicator_id not in known for item in items):
            raise ValueError("red-team finding references unknown indicator")
        self._findings[epoch] = items

    def deployable(self, epoch: str) -> bool:
        return not any(item.exploitable for item in self._findings.get(epoch, ()))

    def findings(self, epoch: str) -> tuple[RedTeamFinding, ...]:
        return self._findings.get(epoch, ())


@dataclass(frozen=True, slots=True)
class PrivacyBudget:
    epsilon: float
    delta: float = 0.0

    def __post_init__(self) -> None:
        if not math.isfinite(self.epsilon) or self.epsilon <= 0:
            raise ValueError("epsilon must be finite and positive")
        if not math.isfinite(self.delta) or not 0 <= self.delta < 1:
            raise ValueError("delta must be finite and in [0, 1)")


class PrivacyBudgetLedger:
    """Basic pure-DP accounting using additive epsilon composition."""

    def __init__(self, budget: PrivacyBudget, max_queries_per_actor: int) -> None:
        if max_queries_per_actor <= 0:
            raise ValueError("max_queries_per_actor must be positive")
        self.budget = budget
        self.max_queries_per_actor = max_queries_per_actor
        self._spent = 0.0
        self._queries: dict[str, int] = {}

    @property
    def remaining_epsilon(self) -> float:
        return max(0.0, self.budget.epsilon - self._spent)

    def consume(self, actor_id: str, epsilon: float) -> None:
        if not actor_id:
            raise ValueError("actor_id is required")
        if not math.isfinite(epsilon) or epsilon <= 0:
            raise ValueError("query epsilon must be finite and positive")
        if self._queries.get(actor_id, 0) >= self.max_queries_per_actor:
            raise ValueError("actor query limit exceeded")
        if self._spent + epsilon > self.budget.epsilon + 1e-12:
            raise ValueError("privacy budget exhausted")
        self._queries[actor_id] = self._queries.get(actor_id, 0) + 1
        self._spent += epsilon

    def noisy_sum(self, actor_id: str, values: Iterable[float], sensitivity: float, epsilon: float, noise: float) -> float:
        if not math.isfinite(sensitivity) or sensitivity <= 0:
            raise ValueError("sensitivity must be finite and positive")
        if not math.isfinite(noise):
            raise ValueError("noise must be finite")
        self.consume(actor_id, epsilon)
        expected_scale = sensitivity / epsilon
        if abs(noise) > 50 * expected_scale:
            raise ValueError("noise is outside the bounded release envelope")
        return sum(values) + noise


__all__ = [
    "IndicatorDefinition",
    "IndicatorGovernance",
    "PreRegistration",
    "PrivacyBudget",
    "PrivacyBudgetLedger",
    "RedTeamFinding",
]
