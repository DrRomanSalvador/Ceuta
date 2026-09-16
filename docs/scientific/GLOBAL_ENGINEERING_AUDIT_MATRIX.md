# Global Engineering Audit Matrix

Audit mission: complete the remaining finite deep engineering audit of CeutIA + SERPIENTE.

Current audit checkpoint: 2026-09-16T07:07Z
CeutIA branch: `scientific-traceability-crossrepo`
CeutIA HEAD: `19f6fd4667be0510fc728c987483c3dd4b507dd2`
SERPIENTE branch: `main`
SERPIENTE HEAD: `0f4a100f3d9cb6d43218bb129b12a15025a468d1`

This matrix records audit evidence, not predictive validity. `AUDIT_CLOSED` is assigned only after inspection, finding classification, repair where required, regression, consumer verification and integration evidence.

| Surface | Inspected | Defects/findings | Repairs | Regression evidence | Consumer verification | Status |
|---|---|---|---|---|---|---|
| Persistence / historical integrity | SQLite decision store, scientific prediction persistence, outcome evaluation | SQLite migration scripts previously used `executescript`, which can break the intended outer transaction; outcome evaluation did not verify persisted prediction fingerprint | Atomic statement-by-statement migration execution; prediction fingerprint verification before scoring | `test_sqlite_migration_rolls_back_partial_ddl`; `test_mutated_prediction_cannot_enter_outcome_evaluation` | Cross-repository `/decision/evaluate` path plus persistence tests | IN_PROGRESS pending final CI |
| Concurrency / transactions / migrations | SQLite transaction boundaries, prediction identity path; SERPIENTE PostgreSQL runtime workflow | Prediction identity persistence had SELECT/INSERT race; migration atomicity gap | `BEGIN IMMEDIATE` serialization and collision handling; atomic migration helper | 32 concurrent identical deliveries + conflict test; migration rollback test | Scientific CI pending final run | IN_PROGRESS pending final CI |
| Provenance / traceability / hashes | Cross-repo contract, prediction persistence, outcome evaluator, runtime lineage | Upstream persisted payload could be modified without being detected by outcome consumer | Fingerprint re-verification at evaluation boundary | Mutation regression test | `/decision/evaluate` uses authenticated contract and persistence path | IN_PROGRESS pending final CI |
| Temporal semantics / leakage | Contract timestamps, replay, outcome horizon checks, SERPIENTE temporal split and leakage checks | No newly actionable defect identified in inspected boundary; arbitrary future-derived feature leakage remains a declared data-contract limitation | No architectural change; preserve explicit limitation | Existing point-in-time/replay and horizon tests | Cross-repo consumer and replay path inspected | PARTIALLY_AUDITED |
| Mathematical / numerical | Cross-repo probability/interval/uncertainty domains; SERPIENTE binary forecaster, Brier/log-loss, uncertainty construction, nonstationarity | Cross-repo contract did not constrain interval/uncertainty domains; SERPIENTE training target was not explicitly restricted to binary | Domain enforcement in contract; binary target validation in SERPIENTE | Contract boundary tests; SERPIENTE binary-target regression | SERPIENTE forecast contract consumes constrained values | IN_PROGRESS pending CI |
| Registry / epistemology / consumers | Scientific method registry, runtime scientific assessment, final epistemic gate, cross-repo consumer | No new runtime bypass identified in inspected paths | None required at checkpoint | Existing registry/runtime/adversarial suites | Decision endpoint and consumer inspected | PARTIALLY_AUDITED |
| SERPIENTE / dynamics / separation | Canonical contract, transport, producer boundary, longitudinal state builder, multi-horizon, forecaster | No boundary bypass identified; heuristic uncertainty/regime measures remain scientific limitations rather than established validity claims | Binary target guard; contract domain guards | Existing producer/consumer/transport suites plus new producer test | CeutIA consumer validates canonical contract and transport | IN_PROGRESS pending CI |
| Runtime / integration / failure modes | `/decision/evaluate`, readiness/configuration, authenticated transport, rejected prediction paths | Previously found pre-persistence test defect; fixed. Partial decision attempts intentionally preserve accepted prediction intake rather than silently deleting history | Test correction; persistence hardening | Cross-repo endpoint adversarial suite | Actual FastAPI endpoint exercised by existing tests | IN_PROGRESS pending CI |
| Adversarial / regression | Existing adversarial suites plus newly added persistence, integrity and numerical-boundary tests | Findings above converted into regressions | Added targeted tests | Current scientific CI run | Pending final CI result | IN_PROGRESS |
| Final CI / closure documentation | Workflow definitions and historical workflow evidence | Final stabilized state not yet green at this checkpoint | Workflow expanded to include global persistence audit tests | Runs 35066824608 and subsequent run(s) | Pending latest stabilized run | NOT_STARTED |

## Checkpoint evidence

- CeutIA historical run `34939453793`: 36 passed, 1 failed. Failure was in a pre-persistence rejection test that queried `scientific_predictions` when the table did not exist. The test was corrected.
- CeutIA run `35066018857`: scientific workflow executed successfully through compilation and the scientific test step after the correction; it was superseded by later audit changes.
- CeutIA run `35066725492`: workflow reached the scientific test step successfully after persistence audit additions; later commits superseded it.
- Current CeutIA run `35066824608`: triggered by contract-boundary repair and remains the stabilized validation run for this checkpoint.
- SERPIENTE historical run `34938571671`: runtime, PostgreSQL persistence integration, security, dependency audit, Compose validation and image build all completed successfully; test result was 43 passed, 2 skipped in the general suite and 2 passed in the PostgreSQL integration suite.
- SERPIENTE current run `35066900233`: triggered by binary-target validation repair and is the current producer-side regression run.

## Scientific status

`GLOBAL_ENGINEERING_AUDIT = IN_PROGRESS`

`FUNCTIONAL_SCIENTIFIC_GOVERNANCE = IMPLEMENTED / UNDER AUDIT`

`PROSPECTIVE_PREDICTIVE_VALIDITY = NOT_ESTABLISHED`

The audit does not treat software tests, calibration code, or historical CI success as evidence of prospective real-world predictive validity.

## Current frontier

1. Verify the stabilized CeutIA and SERPIENTE CI runs after the latest repairs.
2. Complete consumer-level audit of temporal, registry and failure-path surfaces.
3. Reconcile cross-repository drift against the canonical contract and current producer HEAD.
4. Produce the final closure matrix and only then assign `AUDIT_COMPLETE`.
