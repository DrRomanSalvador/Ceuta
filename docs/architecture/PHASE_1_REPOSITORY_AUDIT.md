# CeutIA — Phase 1 Repository Audit

## Scope

This document freezes the architectural findings from Phase 1 before implementation of the missing Dynamic Decision Support System (DSS) layers.

The audit is intentionally descriptive. It does not claim that a capability is production-ready merely because a related implementation exists elsewhere in the repository.

## Repository and packaging facts

- Repository: `drsalvadorroman-beep/Ceuta`
- Target branch: `main`
- Python requirement: `>=3.12,<3.14`
- Source root: `backend`
- Python package root: `backend/app`
- Pytest test root: `tests`
- Package discovery: `app` and `app.*`
- Mypy mode: strict
- Ruff target: Python 3.12

The repository configuration therefore establishes `tests/` as the canonical test tree. The proposed `backend/tests/` path is not adopted because it would contradict the current packaging and pytest configuration.

## Existing architectural foundation

The repository already contains a substantial epistemic and event-driven foundation, including:

- typed pipeline contracts;
- EventBus infrastructure;
- pipeline orchestration and state storage;
- temporal/provenance-aware observation contracts;
- advanced epistemology components;
- dynamic-system functionality;
- hypothesis and anticipation functionality;
- forecasting/backtesting-related functionality;
- Shadow Mode and shadow metrics;
- source-envelope and observation infrastructure;
- evidence deduplication;
- causality gating;
- validation and safety pipeline components.

These components are existing foundations and must be reused where their contracts satisfy the new subsystem requirements.

## Architectural gaps confirmed in Phase 1

The following proposed DSS package layers are not currently present as complete packages at the requested locations:

- `backend/app/core/ingestion/`
- `backend/app/core/provenance/`
- `backend/app/core/knowledge/`
- `backend/app/core/serpiente/`
- `backend/app/core/forecasting/`
- `backend/app/core/calibration/`
- `backend/app/core/learning/`
- `backend/app/core/governance/`
- `backend/app/core/privacy/`
- `backend/app/core/decision/`
- `backend/app/core/spatial/`
- `backend/app/core/simulation/`
- `backend/app/core/resilience/`

This is a structural finding, not a statement that equivalent functionality does not exist elsewhere.

## Reconciliation rule

New DSS layers must not introduce parallel definitions of foundational epistemic objects when an existing contract can be extended or adapted safely.

The following concepts require one authoritative contract across the system:

1. observation temporal semantics;
2. provenance and source identity;
3. evidence identity and independence;
4. version and supersession semantics;
5. historical-state reconstruction;
6. forecast identity and cutoff/target semantics;
7. uncertainty representation;
8. epistemic status;
9. causal authorization;
10. lineage and audit identity.

## P0 construction order

The implementation sequence is frozen as follows:

### P0-A — temporal/provenance foundation

Establish the shared contracts required to answer exactly what information was available at any historical cutoff.

Required properties:

- `event_time` and `available_at` remain distinct;
- future information is rejected fail-closed;
- provenance is immutable;
- version and supersession are explicit;
- historical reconstruction is deterministic.

### P0-B — source independence

Implement source dependency and effective-evidence resolution before evidence-weighted inference is promoted.

Required properties:

- source lineage is explicit;
- republication and aggregation do not count as independent evidence;
- independent evidence remains distinguishable;
- uncertainty is preserved when dependency cannot be resolved.

### P0-C — historical knowledge state

Implement versioning, supersession, state reconstruction, lineage and retrospective audit.

The required invariant is:

`State(T) = F(observations with available_at <= T, valid versions, provenance, temporal rules)`

A historical forecast must never be recomputed from a later knowledge state merely because the later state is easier to query.

### P0-D — DSS epistemic boundary

Only after the preceding foundations exist should the system expose higher-level hypothesis, scenario, forecasting, decision and counterfactual layers.

## Explicit non-goals of Phase 1

Phase 1 does not:

- declare the DSS operational;
- certify forecasting performance;
- certify causal inference;
- implement the missing DSS engines;
- create duplicate model, observation or forecast contracts;
- move tests to `backend/tests/`;
- treat the existing related components as equivalent to the missing architectural layers without contract verification.

## Reproducibility and audit protocol

Phase 1 is not considered scientifically closed merely because its conclusions are documented. The repository must contain a deterministic verifier that can independently re-evaluate the structural claims.

The canonical verifier is:

`python scripts/verify_phase1.py`

The verifier checks, fail-closed:

- required repository roots and files exist;
- `pyproject.toml` still establishes `backend` as the source root and `tests` as the canonical test root;
- strict typing configuration remains present;
- every Phase 1 declared missing DSS package remains absent;
- every declared missing package is explicitly represented in the audit document;
- the audit document contains its required architectural sections and historical-state invariant;
- the CI workflow still contains compilation, dependency installation, full pytest and Compose validation;
- a canonical SHA-256 digest is generated from the audit manifest.

This verifier is structural by design. It does not claim that absence of a package proves absence of equivalent functionality elsewhere; that distinction remains explicit in the audit. It also does not substitute for the full CI suite.

The verifier itself must pass in CI before Phase 1 can be considered reproducibly closed.

## CI validation standard

The repository CI is authoritative for executable validation. The Phase 1 closure requires a successful workflow run on the final Phase 1 commit, with all required checks completed successfully.

The required CI sequence is:

1. compile all Python sources;
2. install the project and development dependencies;
3. execute the complete pytest suite;
4. validate Docker Compose configuration;
5. execute the Phase 1 structural verifier.

A missing CI result is not interpreted as success. A failed or absent check prevents the phase from being certified.

## Exit criteria

Phase 1 is complete only when all of the following are true:

- the existing foundation has been inventoried;
- the missing package boundaries have been identified;
- the canonical test location has been confirmed from repository configuration;
- existing and future responsibilities have been separated;
- the P0 dependency order is explicit;
- no implementation has been silently represented as complete merely because a similarly named component exists elsewhere;
- the structural verifier passes;
- the complete CI workflow passes on the final Phase 1 commit;
- the exact commit SHA and CI result are recorded as the closure evidence.

Until the last two conditions are satisfied, Phase 1 remains `IMPLEMENTED — NOT YET VALIDATED` rather than `CLOSED`.

## Next phase

Phase 2 begins with the shared temporal, provenance, versioning and fail-closed error contracts. Existing P0 contracts must be inspected and reused before new abstractions are introduced.
