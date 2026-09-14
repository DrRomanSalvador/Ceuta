"""Pre-registration and strict temporal validation planning primitives."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime
from hashlib import sha256
import json


def _parse_window_time(value: str) -> datetime:
    """Parse an ISO-8601 window boundary without relying on string ordering."""
    if not isinstance(value, str) or not value:
        raise ValueError("validation window boundaries must be non-empty strings")
    try:
        parsed_date = date.fromisoformat(value)
    except ValueError:
        parsed_date = None
    if parsed_date is not None and "T" not in value and "t" not in value:
        return datetime.combine(parsed_date, datetime.min.time(), tzinfo=UTC)
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("validation window boundaries must be ISO-8601 dates or datetimes") from exc
    if parsed.tzinfo is None:
        raise ValueError("validation window datetime boundaries must be timezone-aware")
    return parsed.astimezone(UTC)


@dataclass(frozen=True)
class ValidationWindow:
    name: str
    start: str
    end: str

    def __post_init__(self) -> None:
        if not self.name or not self.start or not self.end:
            raise ValueError("validation window requires name, start and end")
        start = _parse_window_time(self.start)
        end = _parse_window_time(self.end)
        if start >= end:
            raise ValueError("validation window start must precede end")


@dataclass(frozen=True)
class ValidationPlan:
    plan_id: str
    training: ValidationWindow
    validation: ValidationWindow
    deployment: ValidationWindow
    specification_hash: str

    def __post_init__(self) -> None:
        if not self.plan_id or not self.specification_hash:
            raise ValueError("plan_id and specification_hash are required")
        training_end = _parse_window_time(self.training.end)
        validation_start = _parse_window_time(self.validation.start)
        validation_end = _parse_window_time(self.validation.end)
        deployment_start = _parse_window_time(self.deployment.start)
        if not (training_end <= validation_start <= validation_end <= deployment_start):
            raise ValueError("training, validation and deployment windows must be chronological")

    @staticmethod
    def _compute_specification_hash(specification: object) -> str:
        try:
            payload = json.dumps(specification, sort_keys=True, separators=(",", ":"), allow_nan=False)
        except (TypeError, ValueError) as exc:
            raise ValueError("model specification must be strict JSON-serializable") from exc
        return sha256(payload.encode("utf-8")).hexdigest()


class _SpecificationHashDescriptor:
    """Expose the historical class-call API while retaining the stored field."""

    def __get__(self, instance, owner):
        if instance is None:
            return owner._compute_specification_hash
        return instance.__dict__["_specification_hash_value"]

    def __set__(self, instance, value) -> None:
        object.__setattr__(instance, "_specification_hash_value", value)


ValidationPlan.specification_hash = _SpecificationHashDescriptor()


@dataclass(frozen=True)
class PreregisteredModel:
    model_id: str
    specification_hash: str
    plan: ValidationPlan
    registered_at: str


class PreregistrationRegistry:
    """Immutable model-registration ledger for out-of-sample evaluation."""

    def __init__(self) -> None:
        self._models: dict[str, PreregisteredModel] = {}

    def register(self, model_id: str, specification: object, plan: ValidationPlan, registered_at: str) -> PreregisteredModel:
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


__all__ = ["PreregisteredModel", "PreregistrationRegistry", "ValidationPlan", "ValidationWindow"]
