# CeutIA — Task Control

This file is the persistent task register for multi-agent development.

## Status Values

Use only these status values:

- `PLANNED` — defined but not started.
- `READY` — sufficiently specified and ready to execute.
- `ACTIVE` — currently being executed by an agent.
- `BLOCKED` — cannot proceed without resolving a dependency or ambiguity.
- `REVIEW` — implementation exists and requires verification or review.
- `DONE` — completed and verified.
- `CANCELLED` — intentionally abandoned.

## Priority Values

- `P0` — blocking or critical.
- `P1` — high importance.
- `P2` — normal.
- `P3` — optional or deferred.

## Task Record

Each active task should use this structure:

```text
### TASK-XXXX — Short title
- Status: READY
- Priority: P1
- Agent: <agent>
- Scope: <files/components>
- Objective: <precise objective>
- Dependencies: <none or explicit dependencies>
- Verification: <required verification>
```

## Current Queue

No task is currently assigned by this file.

Agents must inspect the repository before creating or activating tasks and must preserve task history rather than silently replacing prior records.

## Rules

1. Do not mark a task `DONE` without verification.
2. Do not assign the same exclusive task to two agents simultaneously.
3. Do not expand a task's scope silently.
4. Split large tasks when that materially improves coordination or verification.
5. If a task becomes blocked, record the exact blocking condition.
6. If a task changes architectural assumptions, record the decision in `DECISIONS.md`.
7. If a defect is confirmed, record it in `ISSUES.md` when it requires tracking beyond the current task.
