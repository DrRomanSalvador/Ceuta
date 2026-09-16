# CeutIA — Universal Autonomous Execution Constitution

**Status:** MANDATORY / VERSIONED
**Scope:** ALL missions, agents, providers, models and execution sessions admitted to the CeutIA mission control plane.
**Purpose:** prevent material work loss, silent stalls, incoherent writes and non-recoverable mission execution without turning micro-tasking into bureaucracy.

## 1. Constitutional invariant

`MISSION > TASK > SUBTASK > ACTION`

and:

`ACTION → PERSISTENCE → CHECKPOINT → NEXT ACTION`

A task is not the mission. Task completion is not mission completion.

## 2. Universal execution sequence

Before a material write:

`INSPECT → PRE_WRITE_COHERENCE_GATE → WRITE`

After a material write:

`POST_WRITE_COHERENCE_GATE → TEST/VERIFY → PERSIST → CHECKPOINT`

After a completed task:

`REASSESS → NEXT TASK`

If execution disappears:

`RECOVER → VERIFY → RESUME`

If no executable work exists and a real dependency remains:

`WAIT`

Otherwise:

`CONTINUE`

## 3. Coherence gates

The gates MUST evaluate, at the level that can actually be verified:

- contradiction;
- unnecessary duplication;
- unnecessary complexity;
- degradation;
- regression;
- integration compatibility;
- maintainability;
- security;
- persistence correctness.

A model assertion is not evidence that a gate passed. Runtime enforcement validates the gate schema and required evidence; semantic truth remains subject to the relevant tests and reviewers.

A failed post-write gate prevents task completion.

## 4. Incremental persistence

Material progress MUST be persisted before loss of the current process can become catastrophic. A checkpoint MUST contain, at minimum:

- mission id and mission version;
- agent identity;
- execution id;
- task id/subtask;
- state and state version;
- last material result;
- last verified revision/test evidence;
- next authorized action;
- dependencies and blockers;
- delegated work;
- process/liveness evidence when available.

Checkpoint writes MUST be idempotent and compare-and-swap protected where concurrent writers are possible.

## 5. Work queue semantics

Canonical task states are:

`EXECUTABLE_NOW | RUNNING | BLOCKED_INTERNAL | BLOCKED_EXTERNAL | DELEGATED | COMPLETED | FAILED | CANCELLED`

`WAITING` is not a synonym for `RUNNING`. A task may enter WAITING only when no independent executable work exists for that task and a real dependency is recorded.

## 6. Liveness semantics

The runtime MUST distinguish:

`ACTIVE | STALLED | BLOCKED | FAILED | LOST | RECOVERABLE | UNKNOWN`

The absence of user-facing messages is not evidence of inactivity. Liveness is based on persisted progress/process evidence. No universal timeout value is assumed; deployment policy supplies the observation interval.

## 7. Zero-context recovery

A fresh session MUST be able to reconstruct the mission from persisted state and the repository:

`BOOTSTRAP → READ STATE → VERIFY REALITY → RECONSTRUCT → RESUME`

Conversational memory is never the sole source of mission identity, state, next action or completion.

## 8. Mission continuity

Agents MUST continue while authorized executable work exists. They MUST NOT use user communication as a scheduler. User-facing communication is reserved for material results, mission completion, real external blocking, material risk, constitutional events or actions requiring authority.

## 9. CI continuity

CI is evidence, not a scheduler. Independent work MAY continue while CI runs. A failing CI run requires diagnosis and repair before the affected completion claim can pass. CI status MUST be reported from actual run evidence.

## 10. Mission completion / fixed point

`MISSION_COMPLETE` requires, at minimum:

- no executable authorized task remains;
- required handoffs are emitted;
- material state is persisted;
- latest applicable verification is recorded;
- no unresolved coherence-gate failure remains;
- recovery state is sufficient;
- the mission contract's completion criteria are satisfied.

A locally empty queue is never sufficient proof of mission completion.

## 11. Constitutional protection

This policy MUST NOT be silently deleted, downgraded from MUST to SHOULD, bypassed by an alternative execution path, or disabled by mission-local configuration.

Constitutional changes are distinct from operational changes and require a versioned `POLICY_CHANGE_EVENT` containing:

- previous version;
- new version;
- reason;
- author/proposer;
- evidence;
- impact;
- compatibility result;
- validation result;
- timestamp.

Repository-side protection is not claimed to be cryptographic immutability unless independently enforced and verified.

## 12. Inheritance

The mission registry's universal execution contract applies automatically to every admitted mission, including missions created by the Mission Evolution Engine. A mission-specific contract may add stricter requirements but may not weaken these invariants.

## 13. Authority boundary

This constitution grants no authority by itself. Mission authority remains bounded by the existing control plane, security controls, owner authority, mission contract and tool permissions.

## 14. Evidence discipline

Use only these operational states for claims about this policy:

`ENFORCED_AND_VERIFIED | ENFORCED_NOT_YET_VERIFIED | DOCUMENTED_ONLY | NOT_IMPLEMENTED | EXTERNAL_BOUNDARY`

Never report a stronger state than the evidence demonstrates.

## 15. Supreme anti-loss principle

Any process may disappear at any time. Therefore the system MUST prefer small verifiable work units, frequent material persistence, observable state, recovery and automatic continuation over reliance on process memory or conversational continuity.
