import pytest

from app.core.governance.scientific_method_registry import (
    ScientificMethodRecord,
    ScientificMethodRegistry,
    ValidationStatus,
)


def record(status: ValidationStatus = ValidationStatus.NOT_VALIDATED) -> ScientificMethodRecord:
    return ScientificMethodRecord(
        "method-1",
        "test proposition",
        ("literature:verified",),
        ("assumption",),
        "y=f(x)",
        ("implementation:one",),
        ("validation:one",) if status is not ValidationStatus.NOT_VALIDATED else (),
        status,
        ("limitation",),
    )


def test_registry_requires_explicit_traceability() -> None:
    registry = ScientificMethodRegistry((record(),))
    assert registry.implementation_is_governed("method-1", "implementation:one") is True


def test_invalidated_method_cannot_govern_implementation() -> None:
    registry = ScientificMethodRegistry((record(ValidationStatus.INVALIDATED),))
    assert registry.implementation_is_governed("method-1", "implementation:one") is False


def test_duplicate_methods_are_rejected() -> None:
    registry = ScientificMethodRegistry((record(),))
    with pytest.raises(ValueError, match="duplicate"):
        registry.register(record())
