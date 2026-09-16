# Universal Mission Discovery and Invocation Contract

**Status:** ACTIVE
**Registry:** `docs/missions/MISSION_REGISTRY.json`
**Universal execution constitution:** `docs/missions/UNIVERSAL_EXECUTION_CONSTITUTION.md`
**Universal execution contract:** `docs/missions/UNIVERSAL_EXECUTION_CONTRACT.json`

## Canonical flow

`BOOTSTRAP → LOAD REGISTRY → DISCOVER MISSION → LOAD CONTRACT → INHERIT UNIVERSAL EXECUTION CONTROLS → CHECK AUTHORITY → CHECK INPUTS → INVOKE → MICRO-TASK EXECUTION → PRE_WRITE → WRITE → POST_WRITE → VERIFY → PERSIST → CHECKPOINT → REASSESS → HANDOFF/CONTINUE`

The registry is the discovery source. A mission must never depend on conversational memory for existence, identity, scope or next action.

## Universal inheritance

Every mission admitted to the registry automatically inherits the universal execution contract. Mission-local instructions may add stricter controls but may not weaken, disable or bypass the universal contract.

## Invocation envelope

Every invocation MUST contain:

- `mission_id`
- `operation`
- `request_id`
- `session_id`
- `requested_at`
- `authority_context`
- `input_refs`
- `expected_output_type`
- `base_state_version`

The invoked mission MUST return:

- `mission_id`
- `request_id`
- `operation`
- `status`
- `result_refs`
- `source_refs`
- `evidence_level`
- `state_version_read`
- `state_delta_ref` or an explicit `NO_PERSISTENCE_DELTA`
- `handoff_refs`
- `conflict_status`
- `next_authorized_action`

## Coherence gates

Material writes MUST pass `PRE_WRITE_COHERENCE_GATE` before mutation and `POST_WRITE_COHERENCE_GATE` after mutation. A failed post-write gate prevents task completion.

The gates evaluate contradiction, duplication, complexity, degradation, regression, integration, maintainability, security and persistence. Runtime enforcement validates the gate schema and evidence presence; semantic correctness remains subject to the applicable tests and independent evidence.

## Authority

`CAN_DISCOVER`, `CAN_INVOKE`, `CAN_READ`, `CAN_PROPOSE`, `CAN_MODIFY`, `CAN_VALIDATE`, and `CAN_AUTHORIZE` are separate capabilities. Invocation never implies master-state modification.

## Concurrency and recovery

State writes must use compare-and-swap semantics over `base_state_version`, or an equivalent transactional lease/claim mechanism supplied by the deployment orchestrator. A stale writer MUST fail closed and produce a conflict record rather than overwrite newer state.

Checkpoints are idempotent. A fresh session must recover from persisted state rather than conversation memory.

The repository runtime cannot by itself prove live external process state, multi-process leases or infrastructure-level recovery; those capabilities remain explicitly `EXTERNAL_BOUNDARY` until exercised and verified.

## Identity isolation

Mission contracts are scoped. ROMÁN authorial rules activate only for a ROMÁN invocation. No registry entry may set a global voice or alter another mission's identity.

## Fresh-chat acceptance test

A fresh session must be able to:

1. load the registry;
2. find the mission;
3. load its mission contract plus the mandatory universal execution contract;
4. verify authority and required inputs;
5. construct an invocation envelope;
6. execute through a host that routes material work through the universal execution runtime;
7. persist a versioned delta/checkpoint;
8. continue or hand off without this conversation.

If the host cannot execute step 6 or transactional persistence in step 7, the missing external capability must remain `NOT_ESTABLISHED` rather than being claimed as implemented.
