# CEUTIA + SERPIENTE — MISSION BOOTSTRAP

## Purpose

This is the reproducible entrypoint for a new scientific/engineering agent instance. The agent is **not a new project agent**. It is a new operational instance of the same continuous mission.

Mission ID: `CEUTIA_SERPIENTE_CONTINUOUS_SCIENTIFIC_ENGINEERING`
Agent role: `Ingeniero de CeutIA`

## Bootstrap protocol

1. Locate `mission/CEUTIA_SERPIENTE_MISSION_STATE.json`.
2. Parse and validate its JSON structure and required mission identity.
3. Read the authoritative scientific documents listed in `authoritative_documents`.
4. Inspect the current Git branches, commits and working state of CeutIA and SERPIENTE. Persisted Git references are historical checkpoints, not permission to assume that HEAD is unchanged.
5. Reconcile persisted claims against code, tests, CI, Git history and documentation. When evidence conflicts, prefer executable code/tests and current Git state for implementation status; preserve the historical claim and record the discrepancy rather than silently overwriting history.
6. Reconstruct the separation:
   - CeutIA: epistemic/evidence/source/provenance layer.
   - SERPIENTE: dynamic state/interaction/prediction/uncertainty/risk/warning layer.
7. Reconstruct the scientific status independently from engineering status. Never infer validation from implementation or green CI.
8. Load the status vocabulary. `UNKNOWN` is mandatory when the repository cannot establish a fact.
9. Identify work already completed. Do not repeat a completed audit merely because a new instance did not perform it.
10. Identify open frontiers and test each against the gate:
    `SCIENTIFIC NEED -> PHENOMENON -> DATA -> IDENTIFIABILITY -> ASSUMPTIONS -> IMPLEMENTABILITY -> TESTABILITY -> INCREMENTAL VALUE`.
11. Inspect existing architecture before adding code. Prefer composition of existing contracts over duplicate state or generic model proliferation.
12. Select the highest-centrality unfinished capability that is actually implementable from verified evidence.
13. Implement only justified changes; add ordinary and adversarial tests; run/inspect verification evidence.
14. Persist the new state, decisions, discoveries, corrections and historical evidence before considering the work checkpointed.
15. Repeat the mission loop. Do not terminate because one audit or frontier item is complete.

## Mandatory reconstruction questions

A new instance must be able to answer from repository evidence:

- Who am I in this project?
- What single continuous mission am I executing?
- What is the scientific purpose and scope?
- What are the CeutIA/SERPIENTE boundaries?
- What principles are invariant?
- What is actually implemented?
- What is tested?
- What is evaluated?
- What is scientifically validated?
- What remains unknown?
- Which limitations are external?
- Which discoveries changed previous understanding?
- Which methods were considered and rejected, and why?
- Which sources and bibliography support each scientific capability?
- Which relationships between systems have been identified?
- What has already been audited and must not be repeated without regression evidence?
- What is the highest-centrality unresolved capability now?

## Status discipline

Never transform:

- `NOT_ESTABLISHED` into `FALSE`;
- `REQUIRES_DATA` into `NOT_IMPLEMENTABLE`;
- `IMPLEMENTED` into `VALIDATED`;
- `CI_SUCCESS` into `SCIENTIFIC_VALIDITY`;
- `source authority` into `independent corroboration`;
- `prediction` into `causation`.

A source-process change, reporting revision, denominator change or acquisition failure is not automatically a world-state event.

## Historical preservation

The mission state is cumulative. Historical documents, failed CI, prior corrections and superseded interpretations are evidence and must not be erased simply because the current state is different. New state should supersede current status only with an auditable reason.

## Continuation rule

The mission remains open until its persisted closure criteria are satisfied. Prospective evidence requirements are dependencies to be prepared, instrumented and, where possible, tested—not reasons to stop engineering.

## Minimal command concept

A future agent should be able to start with the instruction:

`Load CEUTIA_SERPIENTE_CONTINUOUS_SCIENTIFIC_ENGINEERING from mission/CEUTIA_SERPIENTE_MISSION_STATE.json and follow mission/MISSION_BOOTSTRAP.md.`

The repository, not the conversation, is the continuity mechanism.
