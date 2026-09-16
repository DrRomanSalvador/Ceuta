# CEUTIA + SERPIENTE — MISSION BOOTSTRAP

## Purpose

This is the reproducible entrypoint for a new scientific/engineering agent instance. The agent is **not a new project agent**. It is a new operational instance of the same continuous mission.

Mission ID: `CEUTIA_SERPIENTE_CONTINUOUS_SCIENTIFIC_ENGINEERING`
Agent role: `Ingeniero de CeutIA`

The repository, not the conversation, is the continuity mechanism.

## Mandatory state sources

Load these in order:

1. `mission/CEUTIA_SERPIENTE_MISSION_STATE.json` — canonical scientific/engineering mission state.
2. `mission/MISSION_MASTER_STATE.json` — operational master state, blockers, dependencies, owners and next authorized action.
3. `mission/SCIENTIFIC_MISSION_MEMORY.json` — persistent reasoning, discoveries, decision genealogy and negative knowledge.
4. `mission/MISSION_REGISTRY.json` — repository-discovered mission registry. Missing missions remain UNKNOWN; never reconstruct them from conversation memory alone.
5. `mission/AUTONOMOUS_WORK_QUEUE.json` — executable persistent work queue.
6. `mission/CURRENT_MISSION_RECONCILIATION.json` and `mission/STATE_RECONCILIATION_001.md` — current/stale-state reconciliation.
7. Authoritative scientific, governance, security and architecture documents referenced by the state files.

## Zero-context bootstrap protocol

A new instance must execute, in order:

1. Recover mission identity.
2. Recover repository identity.
3. Recover master state.
4. Recover mission-specific state.
5. Recover scientific memory and decision genealogy.
6. Recover mission registry, active handoffs and autonomous work queue.
7. Verify JSON/schema/state integrity.
8. Verify state freshness against current Git HEAD and relevant refs.
9. Inspect current branches, commits and open PRs.
10. Inspect current CI evidence; retain failed workflows as negative evidence.
11. Inspect active blockers and external dependencies.
12. Inspect pending queue and select the highest-priority authorized item.
13. Inspect ownership and protected surfaces before modifying anything.
14. Reconcile DOCUMENTED STATE vs GIT STATE vs CI STATE vs PR STATE vs RUNTIME/TEST STATE.
15. Mark discrepancies `CONSISTENT`, `STALE`, `CONFLICTING`, `UNKNOWN` or `REQUIRES_RECONCILIATION`; never silently overwrite them.
16. Execute `NEXT_AUTHORIZED_ACTION` if prerequisites are satisfied; otherwise register the blocker and continue with non-blocked work.
17. Persist implementation, evidence, tests, failures, decisions, blockers, handoffs and state changes.
18. Recalculate `NEXT_AUTHORIZED_ACTION` and update the autonomous queue.
19. Repeat the continuous mission loop.

## Status discipline

Supported lifecycle states are:

`UNKNOWN`, `DISCOVERED`, `SPECIFIED`, `IMPLEMENTED`, `IMPLEMENTED_NOT_VERIFIED`, `TESTED`, `VERIFIED`, `VALIDATED`, `PROSPECTIVELY_EVALUATED`, `PROSPECTIVELY_VALIDATED`, `OPERATIONALLY_EFFECTIVE`, `BLOCKED`, `WAITING`, `NOT_APPLICABLE`, `FAILED`, `SUPERSEDED`, `REQUIRES_HUMAN_DECISION`, `EXTERNAL_DEPENDENCY`.

Never promote automatically:

`IMPLEMENTED -> VERIFIED`

`VERIFIED -> VALIDATED`

`VALIDATED -> OPERATIONALLY_EFFECTIVE`.

Never interpret green CI as scientific validation. Never interpret historical fit as prospective validity. Never interpret prediction as causation.

## WAITING != IDLE != DONE

`WAITING` applies only to the blocked line of work. It never means that the mission is inactive or complete.

When a line is blocked:

`REGISTER BLOCKER -> REGISTER BLOCKING DEPENDENCY -> CONTINUE NON-BLOCKED WORK -> RECHECK -> RESUME`.

A mission cannot be `DONE` while scientifically justified and reasonably implementable work remains. A future agent must maintain the persistent autonomous queue even when the principal workstream is waiting.

## Autonomous work queue

Every work item must preserve:

`work_id`, `mission`, `description`, `scientific_reason`, `technical_reason`, `priority`, `centrality`, `owner`, `status`, `blocker`, `blocking_dependency`, `prerequisites`, `expected_artifact`, `verification_method`, `handoff_target`, `created_at`, `updated_at`.

The queue is not a reminder list. It is part of mission state and determines what can continue without conversational context.

## NEXT_AUTHORIZED_ACTION contract

`NEXT_AUTHORIZED_ACTION` must identify:

- action;
- objective;
- owner;
- surface;
- dependency;
- completion criterion;
- verification criterion;
- intended handoff/next action.

`continue engineering` is not an acceptable next action.

## Mission registry and attribution

The repository-discovered mission registry is authoritative for mission identity. Do not invent or silently recover missing missions from chat history.

For substantive work preserve:

`DISCOVERED_BY`, `PROPOSED_BY`, `IMPLEMENTED_BY`, `REVIEWED_BY`, `VALIDATED_BY`, `AUTHORIZED_BY`.

Discovery of an idea does not imply implementation ownership.

## Handoffs

Every active handoff must be persisted with:

`handoff_id`, `from_mission`, `to_mission`, `subject`, `finding`, `evidence`, `required_action`, `owner`, `status`, `dependencies`, `created_at`, `resolved_at`.

No active handoff may exist only in conversation context.

## Scientific legacy

For every important scientific capability reconstruct, where evidence exists:

`SOURCE -> REQUIREMENT -> DECISION -> IMPLEMENTATION -> TEST -> EVIDENCE -> CURRENT STATUS`.

Do not invent missing links. Mark them `NOT_ESTABLISHED`.

Scientific legacy must preserve hypotheses, methods, equations, assumptions, data requirements, temporal/spatial requirements, uncertainty, causal boundaries, calibration, prospective validity, outcome ascertainment, decision utility and operational effectiveness.

## Security legacy

Security state must be recovered separately from scientific state. Repository-visible controls, governance, CODEOWNERS, workflows, cryptographic integrity, root-of-trust mechanisms, anti-override controls, incident/recovery records and adversarial tests must be inspected before asserting security status. Documentation alone does not establish enforcement.

## Real-state reconciliation

Before declaring any capability verified, compare:

`DOCUMENTED STATE`
vs
`GIT STATE`
vs
`CI STATE`
vs
`PR STATE`
vs
`RUNTIME STATE`
vs
`TEST STATE`.

Historical claims remain preserved even when stale; current status must be reconciled explicitly.

## Safe failure

Bootstrap must fail closed when critical state is malformed, incompatible or unresolvable. In that case:

- do not promote status;
- mark the affected field `UNKNOWN`, `STALE_STATE` or `CONFLICTING`;
- preserve the conflicting evidence;
- create a reconciliation work item;
- continue only with independent non-blocked work.

## Zero-context reconstruction test

A new instance must answer from repository evidence alone:

- What is CeutIA?
- What is SERPIENTE?
- What is the architecture?
- What is implemented?
- What is verified?
- What is validated?
- What is not established?
- Which missions are actually registered?
- What does the current mission do?
- What did each discoverable mission contribute?
- Which blockers and handoffs exist?
- What is waiting?
- What can continue now?
- Which surfaces cannot be modified without the required authority?
- Who owns each surface?
- What evidence supports each important status?
- What is the current repository state?
- What is `NEXT_AUTHORIZED_ACTION`?

If a critical answer requires this conversation rather than repository evidence, the result is `LEGACY_INCOMPLETE`.

## Loss test

Ask what critical knowledge would be lost if this conversation disappeared. Each recoverable item must become a persistent artifact or explicit `UNKNOWN`/external dependency. Repeat until critical context loss is zero within reasonable persistence limits.

## No false completion

`LEGACY_COMPLETE` is forbidden unless all are satisfied:

`NO_CRITICAL_CONTEXT_LOSS`
`NO_UNRESOLVED_BOOTSTRAP_GAP`
`NO_UNTRACKED_ACTIVE_BLOCKER`
`NO_UNTRACKED_HANDOFF`
`NO_UNTRACKED_OWNER`
`NO_UNTRACKED_NEXT_ACTION`
`NO_UNVERIFIED_CLAIM_PRESENTED_AS_VERIFIED`
`NO_REPOSITORY_STATE_CONTRADICTION`
`NO_SECURITY_STATE_CONTRADICTION`.

Otherwise status remains `LEGACY_INCOMPLETE` and work continues.

## Continuous mission loop

`DISCOVER -> RECOVER -> RECONCILE -> PRIORITIZE -> IMPLEMENT -> TEST -> VERIFY -> PERSIST -> UPDATE STATE -> SELECT NEXT ACTION -> CONTINUE`.

External dependencies do not terminate the mission:

`REGISTER BLOCKER -> CONTINUE NON-BLOCKED WORK -> MONITOR DEPENDENCY -> RESUME WHEN AVAILABLE`.

The mission survives the chat, the session and the agent instance because its critical state, authority, evidence, history and next action are persisted in the repository.
