from __future__ import annotations

import pytest

from app.core.errors import (
    CeutIAError,
    ContractViolation,
    ProvenanceViolation,
    RuntimeBoundaryError,
    TemporalViolation,
    ValidationFailure,
)


@pytest.mark.parametrize(
    "error_type",
    [
        ContractViolation,
        TemporalViolation,
        ProvenanceViolation,
        ValidationFailure,
        RuntimeBoundaryError,
    ],
)
def test_foundational_errors_are_typed_and_fail_closed(error_type: type[CeutIAError]) -> None:
    error = error_type("deterministic failure")
    assert isinstance(error, CeutIAError)
    assert str(error) == "deterministic failure"


def test_temporal_and_provenance_failures_are_contract_violations() -> None:
    assert issubclass(TemporalViolation, ContractViolation)
    assert issubclass(ProvenanceViolation, ContractViolation)


def test_error_messages_are_not_silently_coerced() -> None:
    with pytest.raises(TemporalViolation, match="cutoff precedes availability"):
        raise TemporalViolation("cutoff precedes availability")
