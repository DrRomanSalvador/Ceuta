# APOYO — Architecture Integration

## Implemented repository boundaries

APOYO is registered in `docs/missions/MISSION_REGISTRY.json` and is discoverable by the canonical mission id `APOYO`.

Its machine-readable contract is `docs/missions/apoyo/APOYO_INVOCATION_CONTRACT.json`.

Its persistent meeting point is `APOYO-MEETING-POINT`, represented in `APOYO_MISSION_STATE.json` and discoverable through the mission registry.

Its repository runtime is `backend/app/missions/apoyo.py`.

Its zero-context bootstrap is `APOYO_BOOTSTRAP.md`.

Its account authorization boundary is `APOYO_ACCOUNT_AUTHORIZATION.json`.

## Authority

APOYO is subordinate to the requesting mission for each collaboration. A collaboration request cannot be accepted without a discoverable requesting mission and `CAN_INVOKE=true` authority context.

APOYO cannot redefine the requesting mission, assume its ownership, alter another mission's identity, or self-authorize.

## Collaboration lifecycle

`WAITING → INVOKED → ASSISTING → VALIDATING → PERSISTING → RETURNING_CONTROL → WAITING`

A duplicate active request returns `NO_ACTION` rather than creating parallel work.

Results and evidence are persisted before the requesting mission receives control back.

## Persistence and recovery

State is persisted atomically with POSIX file locking. The state contains identity, instance, meeting point, active/completed collaborations, handoffs, events and replication history. Recovery reconstructs the runtime from persisted state without conversation history.

## Replication boundary

The schema permits unbounded generations, but the repository runtime does not fabricate external sessions, accounts, processes or tokens. Replication requests therefore become explicit `REPLICATION_NOT_EXECUTABLE_IN_CURRENT_RUNTIME` records until a verified external provisioner exists.

The three-account policy is represented as a fail-closed external-root-of-trust configuration. The repository intentionally contains no guessed account identifiers.

## Constitutional integration

The universal execution constitution applies automatically through the existing mission registry inheritance mechanism. APOYO adds a mission-specific contract without weakening universal execution controls.

The protected `00_GOVERNANCE/` control plane was not modified. This is deliberate: `AGENTS.md` defines that control plane as protected against direct AI modification. The APOYO-specific constitutional/contractual layer is therefore implemented under `docs/missions/` and integrated through the existing registry rather than by bypassing the repository's protected-control invariant.

## Evidence status

- Designed: YES
- Repository implementation: YES
- External account identities: NOT CONFIGURED
- External session provisioning: NOT PROVIDED BY CURRENT RUNTIME
- Live multi-process orchestration: EXTERNAL BOUNDARY
- Platform-level operational proof: PENDING RUNTIME/CI VALIDATION
