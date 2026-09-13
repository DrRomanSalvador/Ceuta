"""Canonical fail-closed error taxonomy for CeutIA core boundaries."""

from __future__ import annotations


class CeutIAError(Exception):
    """Base class for expected CeutIA domain failures."""


class ContractViolation(CeutIAError):
    """A typed contract contains an invalid or inconsistent value."""


class TemporalViolation(ContractViolation):
    """A temporal invariant would be violated, including information leakage."""


class ProvenanceViolation(ContractViolation):
    """Required provenance is absent, malformed, or internally inconsistent."""


class ValidationFailure(CeutIAError):
    """A validation gate rejected an otherwise well-formed operation."""


class RuntimeBoundaryError(CeutIAError):
    """An execution boundary rejected an operation rather than degrading silently."""
