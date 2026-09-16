# Universal Execution Control — Validation Matrix

| Property | Repository evidence | External verification | Current state |
|---|---|---|---|
| PRE_WRITE gate | executable tests | none for schema-level enforcement | VERIFIED BY EXECUTED TESTS |
| POST_WRITE gate | executable tests | none for schema-level enforcement | VERIFIED BY EXECUTED TESTS |
| incremental persistence | atomic fsync + tests | deployment storage semantics | REPOSITORY-VERIFIED |
| checkpoint idempotence | collision/retry tests | distributed storage semantics | REPOSITORY-VERIFIED |
| checkpoint-to-task linkage | persisted `checkpoint_ref` + zero-context recovery tests | external process restart | REPOSITORY-VERIFIED |
| CAS stale-writer rejection | stale version test | multi-host lease backend | REPOSITORY-VERIFIED LOCALLY |
| task queue | state machine tests | external scheduler | REPOSITORY-VERIFIED LOCALLY |
| liveness | ACTIVE/STALLED/BLOCKED/FAILED/LOST/RECOVERABLE/UNKNOWN tests | real process telemetry | REPOSITORY-VERIFIED CLASSIFIER; LIVE TELEMETRY EXTERNAL |
| zero-context recovery | persisted state reconstruction + checkpoint replay | external session host | REPOSITORY-VERIFIED |
| mission inheritance | registry composition test | external host routing | REPOSITORY-VERIFIED AT REGISTRY BOUNDARY |
| CI | explicit universal test step | live PR run | PENDING CURRENT RERUN |
| deletion/downgrade protection | non-weakening contract | CODEOWNERS/ruleset | EXTERNAL_BOUNDARY |
| INGENIERO live status | repository records | live orchestrator/process telemetry | UNKNOWN_UNRESOLVED_BY_AVAILABLE_EVIDENCE |
| crash recovery | restart/checkpoint simulation | real process termination/restart | REPOSITORY-SIMULATION VERIFIED; REAL PROCESS BOUNDARY EXTERNAL |
| internal fixed point | executable continuation/fixed-point tests | external protection | INTERNAL CLOSURE DOES NOT REQUIRE EXTERNAL PROTECTION |

## Closure rule

The internal fixed point is reached when no executable internal task, repair, required local validation, regression, contradiction, integration or persistence inconsistency remains. External boundaries are recorded separately and do not keep ROMÁN open when the internal closure conditions are satisfied.

No stronger claim is permitted until the corresponding evidence exists.
