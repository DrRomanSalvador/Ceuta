# CeutIA — Multi-Agent Collaboration Protocol

This document defines how independent AI agents coordinate work through the shared repository.

## Purpose

The repository is the persistent coordination layer between agents. Important project state must not depend exclusively on a conversation between an agent and the human owner.

## Shared State

The following files form the coordination system:

- `AGENTS.md` — mandatory operating contract.
- `COLLABORATION.md` — collaboration protocol.
- `TASKS.md` — active work queue and task state.
- `DECISIONS.md` — durable architectural and operational decisions.
- `ISSUES.md` — confirmed problems and unresolved technical issues.
- `HANDOFF.md` — current handoff state between agents.
- `CHANGELOG.md` — significant repository changes.

## Agent Identity

Every agent must identify itself in coordination records using its actual model or platform name when known.

Do not impersonate another agent.

## Before Starting Work

1. Read `AGENTS.md`.
2. Read `COLLABORATION.md`.
3. Read `TASKS.md`.
4. Read `HANDOFF.md`.
5. Read relevant entries in `DECISIONS.md` and `ISSUES.md`.
6. Inspect the actual repository and Git state.

## Task Ownership

A task should have one active owner at a time unless explicitly marked as parallel work.

Before starting a task, record:

- task identifier;
- objective;
- agent;
- status;
- scope;
- dependencies, if any.

Do not silently take ownership of a task already marked active by another agent.

## Parallel Work

Parallel work is allowed only when scopes are sufficiently isolated.

Agents must avoid simultaneously editing the same file unless the coordination record explicitly permits it.

If two agents need the same file, coordinate through the repository state before modifying it.

## Handoffs

When stopping work that another agent may continue:

1. update `HANDOFF.md`;
2. update `TASKS.md`;
3. record relevant decisions in `DECISIONS.md`;
4. record confirmed unresolved problems in `ISSUES.md`;
5. record significant completed changes in `CHANGELOG.md`.

A handoff must describe the actual repository state, not merely intentions.

## Conflicts

If agents reach contradictory conclusions:

1. preserve both positions temporarily;
2. identify the evidence supporting each position;
3. do not silently overwrite the other position;
4. record the conflict in `DECISIONS.md` or `ISSUES.md`;
5. escalate to the human owner when the conflict cannot be resolved from evidence.

## Communication Quality

Coordination records must be factual and concise.

Separate:

- confirmed facts;
- observations;
- inferences;
- hypotheses;
- unresolved questions.

Never record speculation as an established project fact.

## Completion

An agent may mark a task complete only after verification required by the task has been performed.

The completion record must state what was changed and what was verified.

## Human Authority

The human owner remains the final authority for project-level decisions that cannot be resolved from repository evidence or explicit requirements.

Agents must not manufacture consensus between agents.
