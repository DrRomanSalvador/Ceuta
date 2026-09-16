# Universal Execution Control — Validation Matrix

This matrix records what can be verified inside the repository and what remains an external boundary.

| Property | Repository test | External verification required | Completion claim |
|---|---|---|---|
| PRE_WRITE gate | yes | no | repository-enforced |
| POST_WRITE gate | yes | no | repository-enforced |
| atomic persistence | yes | deployment filesystem semantics | repository-enforced locally |
| checkpoint idempotence | yes | multi-host storage semantics | repository-enforced locally |
| CAS stale-writer rejection | yes | distributed lease backend | repository-enforced locally |
| task state machine | yes | external scheduler integration | repository-enforced locally |
| liveness classification | yes | real process telemetry | not established live |
| zero-context reconstruction | yes | external session host | repository contract verified |
| cross-mission inheritance | registry boundary | external host routing | repository-enforced at contract boundary |
| CI gate | workflow configured | actual CI run | pending run evidence |
| deletion/downgrade protection | contract + tests | CODEOWNERS/ruleset verification | external boundary until verified |
| live INGENIERO state | repository evidence only | process/orchestrator telemetry | UNKNOWN |
| crash recovery of real agent | simulated/repository | live host termination/restart | external boundary |

A stronger state must not be claimed until the corresponding external evidence exists.
