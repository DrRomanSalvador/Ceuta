import pytest

from app.core.scientific.validation import (
    PreregistrationRegistry,
    ValidationPlan,
    ValidationWindow,
)


def plan_for(specification):
    return ValidationPlan(
        plan_id="plan-1",
        training=ValidationWindow("train", "2024-01-01", "2025-01-01"),
        validation=ValidationWindow("validate", "2025-01-01", "2026-01-01"),
        deployment=ValidationWindow("deploy", "2026-01-01", "2027-01-01"),
        specification_hash=ValidationPlan.specification_hash(specification),
    )


def test_registration_freezes_model_specification_hash() -> None:
    specification = {"features": ["a", "b"], "threshold": 0.7}
    registry = PreregistrationRegistry()
    registry.register("model-1", specification, plan_for(specification), "2026-09-15T00:00:00Z")
    assert registry.verify("model-1", specification)
    assert not registry.verify("model-1", {"features": ["a", "b"], "threshold": 0.8})


def test_registration_rejects_plan_hash_mismatch() -> None:
    registry = PreregistrationRegistry()
    specification = {"threshold": 0.7}
    plan = plan_for({"threshold": 0.6})
    with pytest.raises(ValueError, match="hash"):
        registry.register("model-1", specification, plan, "2026-09-15T00:00:00Z")


def test_validation_plan_rejects_temporal_leakage_order() -> None:
    with pytest.raises(ValueError, match="chronological"):
        ValidationPlan(
            plan_id="bad",
            training=ValidationWindow("train", "2025-01-01", "2026-01-01"),
            validation=ValidationWindow("validate", "2024-01-01", "2025-01-01"),
            deployment=ValidationWindow("deploy", "2026-01-01", "2027-01-01"),
            specification_hash="x",
        )


def test_validation_plan_orders_timezone_offsets_by_instant() -> None:
    with pytest.raises(ValueError, match="chronological"):
        ValidationPlan(
            plan_id="offset-order",
            training=ValidationWindow(
                "train", "2026-01-01T00:00:00+00:00", "2026-01-01T01:00:00+00:00"
            ),
            validation=ValidationWindow(
                "validate", "2026-01-01T02:00:00+02:00", "2026-01-01T03:00:00+02:00"
            ),
            deployment=ValidationWindow(
                "deploy", "2026-01-01T04:00:00+02:00", "2026-01-01T05:00:00+02:00"
            ),
            specification_hash="x",
        )


def test_validation_window_rejects_naive_datetime() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        ValidationWindow(
            "train", "2026-01-01T00:00:00", "2026-01-02T00:00:00"
        )
