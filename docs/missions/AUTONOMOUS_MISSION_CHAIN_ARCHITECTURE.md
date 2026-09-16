# Autonomous Mission Chain Architecture

**Status:** DESIGN-READY / ENGINEERING HANDOFF
**Owner:** NOTARIO (epistemic guarantees)
**Operational integrator:** INGENIERO
**Parent architecture:** `docs/missions/SCIENTIFIC_MISSION_ARCHITECTURE.md`

## 1. Purpose

Convert the existing persistent multi-mission control plane from a primarily invocation-oriented architecture into an **event-driven scientific work loop** without creating a second registry, provenance system, evidence graph, or mission lifecycle.

Canonical loop:

`GLOBAL SCIENTIFIC STATE → DISCOVER OPEN WORK → PRIORITIZE → SELECT CAPABILITY → ACTIVATE → EXECUTE → VALIDATE → INTEGRATE → GLOBAL REGRESSION → UPDATE STATE → DISCOVER NEXT WORK`

The loop is allowed to stop only at a fixed point or a demonstrated external/human-authority boundary.

## 2. Existing primitives reused

- Mission identity/discovery: `docs/missions/MISSION_REGISTRY.json`.
- Invocation envelope and authority separation: `docs/missions/MISSION_INVOCATION_CONTRACT.md`.
- Admission/creation gates: `backend/app/missions/evolution.py` and `evolution_runtime.py`.
- Mission lifecycle review/retirement: `backend/app/missions/lifecycle.py`.
- Persistent mission state and append-only transition requirements: `docs/missions/contracts/MISSION_STATE_MACHINE.yaml`.
- Existing provenance/dependence/conflict/claim/hypothesis/VoI mechanisms remain authoritative; this layer emits references to them rather than replacing them.
- Existing second-order contracts for discovery candidates, disagreement, impact/revalidation, capability regression and scientific/epistemic debt are consumed as downstream contracts.

## 3. New control-plane concept: Scientific Work Event

A scientifically meaningful state change produces a durable event envelope:

`event_id, event_type, source_refs, scientific_reason, affected_refs, capability_implications, validation_status, provenance_refs, state_version, emitted_at`.

Events are **signals for work discovery**, not evidence of the scientific claim itself. Generated model output never becomes evidence merely because it triggered a mission.

## 4. Chain of custody

Every activation forms a reconstructible chain:

`REAL_WORLD_EVENT → OBSERVATION/EVIDENCE → SCIENTIFIC_CONSEQUENCE → OPEN_TASK → CAPABILITY_MATCH → SELECTION → ACTIVATION → RESULT → VALIDATION → INTEGRATION → DOWNSTREAM_TASKS → GLOBAL_REGRESSION → STATE_UPDATE`.

The chain is append-only. Every edge references the source artifact/event and validation level.

## 5. Mission selection

Selection is deterministic and policy-governed:

1. Reject missions lacking authority, required inputs, scientific compatibility or declared capability.
2. Prefer an existing materially sufficient capability.
3. Prefer an extension of an existing mission before collaboration/task-force/new mission.
4. Prefer the mission with the highest evidence-backed capability fit.
5. Resolve ties by lower activation cost, lower duplication/overlap, fewer unresolved dependencies, then stable mission ID.
6. If no existing capability passes, invoke Mission Evolution Engine precedence rather than inventing a mission locally.

A numeric score may be used for ordering only when its dimensions and evidence are explicit. No opaque model score can authorize activation.

## 6. Automatic chaining

A validated result is converted into one or more **scientific consequences**. Consequences may:

- close an open task;
- invalidate or downgrade a claim;
- create a revalidation obligation;
- create a discriminative test;
- expose a dependency;
- create a new scientifically justified task;
- publish an event to subscribed capabilities.

Task creation requires `WHY_THIS_TASK`, `WHY_NOW`, `EXPECTED_VALUE`, `ACCEPTANCE_CRITERIA`, and `STOP_CONDITION`.

## 7. Asynchronous continuity and live work

A running process is active work, not passive waiting. Each asynchronous activity is represented by a `ProcessObservation` containing process identity/type, start and last-observed timestamps, current status, expected result, dependencies, dependent tasks, independent work available, and the next observation condition.

The explicit work queue has the disjoint buckets:

`executable_now | running | blocked | delegated | external | completed | cancelled`.

`RUNNING` therefore keeps the mission active and obliges independent work discovery/execution and subsequent re-observation. `WAITING` is valid only when no executable, running, blocked or delegated internal work remains. A CI workflow, handoff, replay, subprocess, validation or migration must never by itself terminate a mission execution iteration.

## 8. Coherence gate

Before integration, NOTARIO evaluates whether the result is compatible with the global scientific specification and classifies it as:

`COMPATIBLE | EXTENDS | MODIFIES | CONTRADICTS | REFUTES | INCONCLUSIVE`.

The gate additionally records uncertainty/debt, dependency changes, capability delta and regression obligations. A local success cannot bypass this gate. Material modification, contradiction or refutation requires an explicit revalidation path before it can change the global state.

## 9. Global regression

Integration is not complete until impacted prior capabilities and scientific invariants are rechecked. The impact graph/revalidation obligations determine scope; a full system-wide rerun is not required when a smaller evidence-backed regression set is sufficient.

A regression may be:

- engineering;
- scientific/epistemic;
- provenance/traceability;
- authorization/security;
- reproducibility;
- performance/complexity;
- cross-mission coherence.

## 10. Circuit breakers

The chain must fail closed on provenance loss, state corruption, authority conflict, critical contradiction, unsafe recursion, task explosion, repeated circular activation, integrity failure or global degradation. The breaker persists the reason and resumable recovery state.

## 11. Fixed point

The executable fixed-point predicate requires all of the following to be zero: executable open work, unprocessed derived work, unintegrated completed work, unreconciled state, unverified internal repairs, untested executable changes, unfollowed active handoffs, active internal processes, unresolved critical contradictions, unprocessed high-value discoveries, required integration, repairable regression, and material capability gaps.

Only after this predicate and the global regression audit pass may the system enter `FIXED_POINT`/`QUIESCENT_READY`. An external property may remain explicitly recorded without preventing closure of locally exhausted work. This is a property of the current state of knowledge and infrastructure, not a claim that science is complete.

## 12. Human authority

Humans retain authority for constitutional changes, privileged access, irreversible actions, protected mission changes, and explicitly designated critical scientific decisions. Ordinary routing, validation scheduling, persistence and continuation are autonomous once authorized.

## 13. Anti-sprawl rule

A mission is not activated because it exists. A task is not created because a capability exists. A new mission is not admitted while existing capability, extension, collaboration or temporary task force can satisfy the requirement. Retirement uses the existing lifecycle governance rather than a new lifecycle.
