# CeutIA Phase 2 — Foundational Contracts and Error Semantics

Status: IN PROGRESS

## Purpose

Phase 2 establishes the typed, deterministic contract layer required before implementing higher-order CeutIA subsystems. It must not duplicate existing pipeline contracts. Existing contracts remain canonical unless a compatibility-preserving extension is required.

## Scope

1. Inventory and reconcile canonical domain contracts already present in `backend/app/core/pipeline/contracts.py`.
2. Define a single explicit error taxonomy for contract, temporal, provenance, validation, and runtime-boundary failures.
3. Enforce deterministic serialization and stable identifiers for new foundational contract types.
4. Preserve temporal anti-leakage semantics: future availability cannot enter a knowledge state whose cutoff precedes that availability.
5. Make invalid states fail closed rather than being silently coerced.
6. Add executable tests for invariants and failure semantics.

## Non-goals

This phase does not implement ingestion orchestration, source dependency graphs, entity resolution, dynamic graphs, forecasting, decision engines, spatial engines, or digital twins. Those remain subsequent phases.

## Exit criteria

The phase can only be CLOSED when all are true:

- foundational contracts are present exactly once and their ownership is explicit;
- invalid contract states have deterministic typed failures;
- tests exercise valid and invalid boundary cases;
- the verifier for this phase is reproducible from a clean checkout;
- the CI workflow executes the verifier and the complete test suite;
- the exact validating commit has a successful GitHub Actions run;
- the evidence is traceable to the commit SHA and verifier output.

Absence of a CI result is not success.
