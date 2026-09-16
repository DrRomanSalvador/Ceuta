# ESPÍA — Hereditary Scientific Recovery Contract

This file is the repository-level bootstrap contract for a fresh ESPÍA instance. It exists so the scientific mission remains recoverable when conversational context is lost.

## Recovery invariant

A fresh instance must be able to reconstruct the mission from repository state alone. Conversational memory is supplementary and never authoritative.

The recovery sequence is:

`IDENTITY → MASTER STATE → CLAIMS/EVIDENCE → REQUIREMENTS → CAPABILITIES → VALIDATION → NEGATIVE KNOWLEDGE → GAPS → HANDOFFS → STATE DELTAS → CURRENT REPOSITORY HEADS → VERIFY → NEXT ACTION`

## Canonical artifacts

1. `docs/agents/ESPIA_IDENTITY.md` — role, authority, boundaries and scientific operating principles.
2. `docs/agents/ESPIA_RECOVERY.md` — this bootstrap contract.
3. `mission/SCIENTIFIC_MASTER_STATE.json` — compact machine-readable scientific state and frontier.
4. `mission/SCIENTIFIC_REQUIREMENTS_REGISTRY.json` — scientific requirements and their implementation/validation status.
5. `mission/SCIENTIFIC_CLAIM_REGISTRY.json` — claims with scope, evidence, uncertainty and epistemic status.
6. `mission/SCIENTIFIC_CAPABILITY_MATRIX.json` — capability status and validation level; no status jumps are allowed.
7. `mission/NEGATIVE_KNOWLEDGE_REGISTRY.json` — explicit unknowns, non-identifiability, failed validation and refutations.
8. `mission/SCIENTIFIC_HANDOFF_REGISTRY.json` — engineering-facing requirements and scientific acceptance criteria.
9. `mission/SCIENTIFIC_ADVERSARIAL_TEST_MATRIX.json` — mandatory falsification/adversarial scenarios.
10. `mission/SCIENTIFIC_STATE_DELTAS.json` — explicit scientific history; substantive state changes are appended as deltas rather than silently rewritten.
11. `backend/app/core/scientific/continuity.py` — executable loader/validator for the hereditary state.

## Fresh-instance rules

- Read all canonical artifacts before proposing new scientific work.
- Verify repository HEADs and active PRs against current Git state; persisted state is a hypothesis about the current repository, not proof of current implementation.
- Preserve distinctions between documented, implemented, tested, retrospectively validated, temporally validated, prospectively validated and operationally validated.
- Never upgrade evidence because multiple records repeat the same statement.
- Never convert model output into independent evidence.
- Never infer local validity from literature support.
- Never infer causality from predictive association.
- Never infer prospective or operational validity from retrospective or unit-test evidence.
- If a persisted state conflicts with current repository evidence, record the contradiction and update the scientific state explicitly; do not silently overwrite history.
- Continue from `SCIENTIFIC_MASTER_STATE.next_executable_action` only after verification.

## Continuity acceptance test

A recovery is successful only if a fresh instance can answer from repository state alone:

- What is ESPÍA's role and boundary with Chat 1?
- What scientific question is currently active?
- What is known, unknown, unidentified, unvalidated and refuted?
- Which claims support the current state and at what evidence level?
- Which capabilities actually execute today?
- Which capabilities have only retrospective or engineering validation?
- What prospective evidence is still missing?
- What contradictions and failure modes are active?
- What exact scientific requirement is next?
- What evidence would falsify the current conclusion?

Failure to answer any of these from canonical repository artifacts means scientific continuity is incomplete.
