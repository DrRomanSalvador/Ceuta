# CeutIA — Current Status

Last updated: 2026-09-13
Branch: `codex/p0-rigorous-integration`
Latest implementation commit: `04d4ee37087370071f8b5ef85833e276e04383c1`
Status: `IMPLEMENTED_VERIFIED` for Layers 1–2; production approval remains human-controlled.

## Repository state

- PR #15 remains open and not merged.
- Layer 1 was blocked until the protected Security Control Plane and full CI produced observable PASS results.
- The original reference commit `578f10c11b24be95cb6a8b1a6f82ba8245d9c6e1` was directly inspected before remediation.
- No independent external red-team review has been received; internal ROLE-REDTEAM checks are not treated as independent audit.

## Layer 1 — Observation Boundary

Implemented and verified controls:

1. `available_at` is the sole analytical availability boundary with precedence `revision_time -> publication_time -> ingestion_time`; `event_time` is never substituted.
2. Temporal filtering and backtesting use `available_at` and reject future information.
3. Revised versions cannot be used historically at their pre-revision availability.
4. Canonical `EvidenceContract` validation gates ingestion.
5. Direct legacy registry admission now passes through canonical P0 contract validation.
6. `src/data_fetcher.py` no longer exposes a parallel `VerifiedData` representation; fetched content is returned as canonical, explicitly unverified evidence.
7. `UNKNOWN`, `CONTRADICTED`, uncertainty, provenance and source independence are preserved.
8. Corroboration requires distinct explicitly independent source groups; dependent/copy/amplifier relationships do not count.
9. Malformed temporal input fails closed.
10. The API surface was inspected. The legacy operational API uses the controlled fetcher; the public CeutIA API explicitly remains non-operational and does not claim connected evidence retrieval.
11. The canonical application reports cache/monitoring/analytical dependencies as not connected; therefore no active cache/index/RAG path was found that could silently bypass the boundary.

## Layer 1 verification evidence

Latest verified commit before Layer 2 implementation: `f271c2b1b0f22bc460fba053974e870e07befc22`.

- `CeutIA CI`: completed / success.
- `CeutIA Security Control Plane`: completed / success.
- Security runtime regression suite: passed.
- P0 observation/temporal suites: passed.
- v1 JSON schemas: validated by the protected workflow.
- Security static checks: passed.
- Full CI test suite: passed.

## Layer 2 — Semantic Graph and Rival Hypotheses

Implemented and verified on `04d4ee37087370071f8b5ef85833e276e04383c1`:

1. Graph relations explicitly distinguish `ASSOCIATION`, `TEMPORAL_PRECEDENCE`, `SUPPORTS`, `CONTRADICTS`, `SOURCE_DEPENDENCY`, `CAUSAL_HYPOTHESIS` and `CAUSALITY_SUPPORTED`.
2. No `CAUSALITY_CONFIRMED` state exists.
3. Temporal precedence requires explicit ordered timestamps and cannot itself establish causality.
4. Causal edges require an explicit hypothesis, mechanism, evidence, alternative explanations, predictions and falsification criterion.
5. `CAUSALITY_SUPPORTED` additionally requires a validation method.
6. The graph admits observations only through `ObservationBoundary` and `EvidenceContract`; future evidence is rejected before node creation.
7. Canonical epistemic states remain separate from graph relationships.
8. Rival hypothesis records implement H1–H5 with predictions, favorable/contrary evidence, confounders, missing data, falsification criteria, verification cost and action/inaction consequences.
9. Graph and hypothesis tests cover causal overclaiming, temporal leakage, dependency relations, rival completeness and UNKNOWN/CONTRADICTED preservation.

## Latest CI evidence

For `04d4ee37087370071f8b5ef85833e276e04383c1`:

- `CeutIA CI`: completed / success; compile, full test suite and Compose validation passed.
- `CeutIA Security Control Plane`: completed / success; protected-control integrity, runtime security regression, v1 schema validation, P0 observation/temporal suites and static security checks passed.

## Current blockers

No Layer 1 or Layer 2 verification blocker is currently open.

Still prohibited until a separate validation gate is established:

- mathematical prediction;
- operational automated alerts based on unvalidated causal inference;
- claims of external scientific validation;
- production certification;
- human-approval bypass.

## Next authorized step

Layer 3 may be designed only after a new explicit layer definition and verification gate. Prediction remains separately gated until the required temporal out-of-sample, calibration, robustness and adversarial validation infrastructure exists.

Human approval remains final.
