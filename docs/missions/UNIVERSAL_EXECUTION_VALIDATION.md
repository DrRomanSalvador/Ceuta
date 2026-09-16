# Universal Execution Control — Validation Matrix

| Property | Repository evidence | External verification | Current state |
|---|---|---|---|
| PRE_WRITE gate | executable tests | none for schema-level enforcement | ENFORCED_AND_VERIFIED pending full CI |
| POST_WRITE gate | executable tests | none for schema-level enforcement | ENFORCED_AND_VERIFIED pending full CI |
| incremental persistence | atomic fsync + tests | deployment storage semantics | repository-verified |
| checkpoint idempotence | collision/retry tests | distributed storage semantics | repository-verified |
| CAS stale-writer rejection | stale version test | multi-host lease backend | repository-verified locally |
| task queue | state machine tests | external scheduler | repository-verified locally |
| liveness | classification tests | real process telemetry | EXTERNAL_BOUNDARY |
| zero-context recovery | persisted state reconstruction | external session host | repository-verified |
| mission inheritance | registry composition test | external host routing | repository-verified at registry boundary |
| CI | explicit universal test step | live run | pending/repair cycle |
| deletion/downgrade protection | non-weakening contract | CODEOWNERS/ruleset | EXTERNAL_BOUNDARY |
| INGENIERO live status | repository records | live orchestrator/process telemetry | UNKNOWN |
| crash recovery | restart/checkpoint simulation | real process termination/restart | EXTERNAL_BOUNDARY |

No stronger claim is permitted until the corresponding evidence exists.
