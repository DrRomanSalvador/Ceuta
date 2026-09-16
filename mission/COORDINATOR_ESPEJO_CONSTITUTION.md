# COORDINATOR / ESPEJO constitutional runtime

## Operational hierarchy

`H0 HUMAN AUTHORITY → H1 COORDINATOR → H2 MISSION / AGENT → H3 ESPEJO`

This is an operational-authority hierarchy, not a scientific-quality hierarchy. Constitution, security and human authority remain superior to delegated coordination authority.

## COORDINATOR

COORDINATOR is a convocable operational mission. It observes collective agents, missions and tasks; distinguishes progress from stall; allocates or reprioritizes work within authority; emits attributable commands; requests ESPEJO assistance; coordinates checkpoint, standby, resume, recovery and handoff; and escalates conflicts to superior authority.

A healthy progressing agent receives no intervention merely because the coordinator can intervene. `ACTIVE + PROGRESSING + COHERENT` is an explicit no-intervention state.

Supported commands are exactly: `CONTINUE`, `CHECKPOINT`, `SPLIT`, `REQUEST_MIRROR`, `PAUSE`, `STANDBY`, `RESUME`, `REDIRECT`, `DELEGATE`, `HANDOFF`, `RECOVER`, `ABANDON`, `REPRIORITIZE`.

Every command persists identity, issuer, target, mission, reason, authority basis, timestamp, state, expected effect, acknowledgement and execution result. Repository runtime additionally records command type, expected state version and reversibility.

`PAUSE` is safe-pause semantics: checkpoint and persistence precede the pause command. Failure to checkpoint must remain an explicit risk state rather than silently discarding context. `STANDBY` is reversible and preserves mission identity and recovery state.

COORDINATOR is not a scientific arbiter, mission owner, constitution editor, permanent scheduler or substitute for specialist missions.

## ESPEJO

ESPEJO is a convocable adaptive assistant. Its identity remains `ESPEJO`; it may adopt a temporary `functional_role` such as tester, researcher, auditor, programmer or verifier. Functional role does not change identity or mission ownership.

The runtime separates `MISSION_OWNER` from `SUBTASK_OWNER`. A mirror may own a subtask while the assisted mission remains the owner of the mission. Mirror provenance contains `MIRROR_OF`, and mirror handoff records preserve both owners.

The intended cycle is:

`OBSERVE → UNDERSTAND → IDENTIFY_NEED → CHECK_AUTHORITY → CHECK_NON_INTERFERENCE → ADOPT_FUNCTIONAL_ROLE → ASSIST → VALIDATE → PERSIST → HANDOFF → RETURN_CONTROL`

Supported assistance actions are: `ASSIST`, `REVIEW`, `VERIFY`, `RESEARCH`, `TEST`, `RED_TEAM`, `CHECKPOINT`, `RECOVERY`, `PREPARE`.

ESPEJO cannot independently pause, standby, reprioritize, redirect, abandon, fail or complete the assisted mission. It can detect and recommend; operational control remains with COORDINATOR or higher authority.

## Persistence and recovery

`mission/COORDINATION_STATE.json` is the canonical coordination projection. It contains agents, missions, tasks, priorities, checkpoints, commands, interventions, mirrors, standby, recovery, conflicts, handoffs, pending reviews and deferred hypotheses.

State mutations use a monotonically increasing `state_version`, exclusive file locking and atomic replacement. Mutations may require an expected version; stale writers fail closed with `StaleStateError`.

Every material coordination mutation also emits an event through the existing hash-chained `mission/event_log.py`. This is an extension of the existing event lineage, not a second event system.

A new coordinator or mirror instance reconstructs state from the persistent projection and event lineage. Conversation memory is not authoritative.

## Concurrency and security

Work ownership is protected by the shared coordination state. Two mirrors cannot acquire the same subtask without an ownership conflict. Stale coordinator state is rejected. Conflicting commands are preserved rather than silently overwritten.

The runtime explicitly treats forged authority, stale state, duplicate execution, mission spoofing, ownership hijacking and provenance manipulation as control-plane threats. It does not grant a mirror coordinator authority by virtue of functional role.

## Deferred hypotheses

Operational obedience does not erase scientific reasoning. An agent can persist `DEFERRED_HYPOTHESIS` with author, timestamp, context, reasoning, alternative and suspension reason while executing a valid operational command.

## Evaluation

The runtime must not optimize for command count, intervention count or mirror count. The relevant property is preservation of correct mission execution, continuity, coherence, traceability and recovery while minimizing interference, duplication and loss.

## Evidence boundary

Runtime unit, adversarial and concurrency fixtures establish repository-level behavior. They do not by themselves establish live distributed-host behavior, external platform enforcement, or operational effectiveness. Those remain explicit validation boundaries until independently evidenced.
