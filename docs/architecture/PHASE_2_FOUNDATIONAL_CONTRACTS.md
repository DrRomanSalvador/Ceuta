# CeutIA Phase 2 — Foundational Contracts and Error Semantics

Status: IN PROGRESS

## Purpose

Phase 2 establishes typed, deterministic failure semantics at the existing pipeline contract boundary without creating a second contract model.

## Implemented scope

1. The existing `backend/app/core/pipeline/contracts.py` remains the canonical pipeline contract module.
2. `backend/app/core/errors.py` owns the foundational error taxonomy: contract, temporal, provenance, validation, and runtime-boundary failures.
3. Existing contract validation now raises typed failures. `ContractViolation` remains a `ValueError` subclass for compatibility with existing callers while exposing an explicit domain type.
4. Temporal invariants use `TemporalViolation`, including timezone requirements, observation availability ordering, and state cutoff ordering.
5. The phase verifier checks error ownership, required tests, and audit criteria from a clean checkout.
6. CI executes the Phase 2 verifier after the complete test suite.

## Non-goals

This phase does not implement ingestion orchestration, source dependency graphs, entity resolution, dynamic graphs, forecasting, decision engines, spatial engines, or digital twins. Those remain subsequent phases.

## Invalid contract states

The exact audit phrase is: invalid contract states.

Invalid contract states fail closed through the typed foundational error taxonomy. They are not silently coerced into valid state and are not treated as successful execution.

## Exit criteria

The phase can only be CLOSED when all are true:

- foundational errors are present exactly once and their ownership is explicit;
- existing canonical contracts emit deterministic typed failures;
- tests exercise the error hierarchy and fail-closed semantics;
- the verifier is reproducible from a clean checkout;
- the CI workflow executes the verifier and the complete test suite;
- the exact validating commit has a successful GitHub Actions run;
- the evidence is traceable to the commit SHA and verifier output.

Absence of a CI result is not success.

Current state: implementation is committed. Final CI validation of the latest commit is still required; therefore this phase is not yet closed.
