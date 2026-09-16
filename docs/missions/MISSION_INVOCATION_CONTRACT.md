# Universal Mission Discovery and Invocation Contract

**Status:** ACTIVE
**Registry:** `docs/missions/MISSION_REGISTRY.json`
**Architecture:** `docs/missions/SCIENTIFIC_MISSION_ARCHITECTURE.md`

## Canonical flow

`BOOTSTRAP → LOAD REGISTRY → DISCOVER MISSION → LOAD CONTRACT → CHECK AUTHORITY → CHECK INPUTS → INVOKE → EXECUTE → PRODUCE TRACEABLE RESULT → PERSIST DELTA → HANDOFF/CONTINUE`

The registry is the discovery source. A mission must never depend on conversational memory for existence, identity, scope or next action.

## Discovery

A new session discovers missions by loading `MISSION_REGISTRY.json` and selecting by `mission_id` or `canonical_name`. Discovery is read-only and does not grant mutation authority.

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

## Authority

`CAN_DISCOVER`, `CAN_INVOKE`, `CAN_READ`, `CAN_PROPOSE`, `CAN_MODIFY`, `CAN_VALIDATE`, and `CAN_AUTHORIZE` are separate capabilities. Invocation never implies master-state modification.

The common control plane coordinates these capabilities; it does not perform ROMÁN's intellectual work.

## Concurrency

State writes must use compare-and-swap semantics over `base_state_version`, or an equivalent transactional lease/claim mechanism supplied by the deployment orchestrator. A stale writer MUST fail closed and produce a conflict record rather than overwrite newer state.

Parallel findings are retained with provenance. Reconciliation is explicit.

The repository is the durable contract source; an external runtime/orchestrator is required for true multi-process leases and transactional live-state writes. This limitation is intentionally explicit rather than simulated by documentation.

## Identity isolation

Mission contracts are scoped. ROMÁN authorial rules activate only for a ROMÁN invocation. No registry entry may set a global voice or alter another mission's identity.

## Fresh-chat acceptance test

A fresh session must be able to:

1. load the registry;
2. find `ROMAN`;
3. load its contract and state;
4. verify authority and required inputs;
5. construct an invocation envelope;
6. execute a valid operation through the host/orchestrator;
7. persist or propose a versioned delta;
8. continue or hand off without this conversation.

If the host cannot execute step 6 or transactional persistence in step 7, the missing external capability must remain `NOT_ESTABLISHED` rather than being claimed as implemented.
