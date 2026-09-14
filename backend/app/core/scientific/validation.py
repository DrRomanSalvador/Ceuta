"""Pre-registration and strict temporal validation planning primitives."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Iterable


@dataclass(frozen=True, slots=True)
class ValidationWindow:
    name: str
    start: str
    end: str

    def __post_init__(self) -> None:
        if not self.name or not self.start or not self.end:
            raise ValueError("validation window requires name, start and end")
        if self.start >= self.end:
            raise ValueError("validation window start must precede end")


@dataclass(frozen=True, slots=True)
class ValidationPlan:
    plan_id: str
    training: ValidationWindow
    validation: ValidationWindow
    deployment: ValidationWindow
    specification_hash: str

    def __post_init__(self) -> None:
        if not self.plan_id or not self.specification_hash:
            raise ValueError("plan_id and specification_hash are required")
        if not (self.training.end <= self.validation.start <= self.validation.end <= self.deployment.start):
            raise ValueError("training, validation and deployment windows must be chronological")

    @staticmethod
    def specification_hash(specification: object) -> str:
        payload = json.dumps(specification, sort_keys=True, separators=(",", ":"), default=str)
        return sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class PreregisteredModel:
    model_id: str
    specification_hash: str
    plan: ValidationPlan
    registered_at: str


class PreregistrationRegistry:
    """Immutable model-registration ledger for out-of-sample evaluation."""

    def __init__(self) -> None:
        self._models: dict[str, PreregisteredModel] = {}

    def register(
        self,
        model_id: str,
        specification: object,
        plan: ValidationPlan,
        registered_at: str,
    ) -> PreregisteredModel:
        if model_id in self._models:
            raise ValueError(f"model already registered: {model_id}")
        digest = ValidationPlan.specification_hash(specification)
        if digest != plan.specification_hash:
            raise ValueError("plan hash does not match model specification")
        model = PreregisteredModel(model_id, digest, plan, registered_at)
        self._models[model_id] = model
        return model

    def get(self, model_id: str) -> PreregisteredModel:
        return self._models[model_id]

    def verify(self, model_id: str, specification: object) -> bool:
        return ValidationPlan.specification_hash(specification) == self._models[model_id].specification_hash

    def all(self) -> tuple[PreregisteredModel, ...]:
        return tuple(self._models.values())


__all__ = [
    "PreregisteredModel",
    "PreregistrationRegistry",
    "ValidationPlan",
    "ValidationWindow",
]
