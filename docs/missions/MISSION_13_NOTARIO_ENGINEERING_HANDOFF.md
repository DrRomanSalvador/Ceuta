# MISSION 13 — NOTARIO → INGENIERO

## Purpose
Implement the runtime enforcement required by the constitutional mission-control-plane projection without creating a second governance mechanism.

## Authority boundary
NOTARIO defines the normative requirements, contracts, invariants, evidence requirements and validation criteria. INGENIERO owns runtime/code/CI implementation.

## Canonical sources
- Normative constitution: `00_GOVERNANCE/AI_MANDATORY_SYSTEM_CONSTITUTION.md`
- Machine projection: `docs/missions/CONSTITUTION_MANIFEST.yaml`
- Mission contract: `docs/missions/contracts/MISSION_CONTRACT.schema.json`
- State machine: `docs/missions/contracts/MISSION_STATE_MACHINE.yaml`
- Existing evolution contract: `docs/missions/EVOLUTION_ENGINE_CONTRACT.json`
- Existing governance protocol: `docs/missions/MISSION_GOVERNANCE_PROTOCOLS.md`
- Existing runtime: `backend/app/missions/evolution.py`, `backend/app/missions/evolution_runtime.py`, `backend/app/missions/lifecycle.py`

## Required runtime changes
1. Load and expose the active constitution version to mission admission and lifecycle decisions.
2. Validate every permanent mission contract against the canonical mission contract schema.
3. Enforce the mission state-machine invariants, including productive WAITING, blocker-scoped BLOCKED, contractual DONE, successor-required SUPERSEDED, destination-required MERGED, reason-required RETIRED/ABORTED.
4. Ensure admission remains exclusively delegated to `MISSION_EVOLUTION_ENGINE`; no second admission path.
5. Enforce constitutional admission gates in addition to the engine's existing gates.
6. Persist constitution version, authority context, provenance, next action, blockers, validation status and repository revision in mission state.
7. Make zero-context discovery validate identity, authority, state, evidence, blockers, handoffs and next action—not merely file existence.
8. Reject stale or constitution-incompatible writers fail-closed.
9. Preserve immutable lifecycle history and attribution through merge, supersede and retirement.
10. Expose explicit PASS / FAIL / NOT_EXECUTED results for constitutional tests; never coerce NOT_EXECUTED to PASS.
11. Add CI validation for YAML/JSON schemas, state-machine invariants, admission-gate references and zero-context recovery.

## Required tests
Implement and execute `docs/missions/tests/CONSTITUTIONAL_TEST_MATRIX.yaml` as runtime/CI tests where technically applicable.

## Validation criteria
- Existing admission behaviour remains compatible unless the new invariant is deliberately stricter and documented.
- Existing missions remain discoverable and invocable.
- No duplicate registry, lineage or admission subsystem is introduced.
- A context-free agent can reconstruct mission identity, purpose, authority, state, evidence, blockers, handoffs, next action and success criteria from persistent artifacts alone.
- Every constitutional violation fails closed and leaves an auditable record.

## Status
HANDOFF_REQUIRED / IMPLEMENTATION_PENDING

This handoff does not transfer NOTARIO's normative authority or INGENIERO's implementation authority. It is a bounded dependency; NOTARIO continues with all non-blocked constitutional work.
