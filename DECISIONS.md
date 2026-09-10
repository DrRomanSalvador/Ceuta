# CeutIA — Decision Register

This file records durable decisions that materially affect CeutIA.

## Decision Format

```text
## DEC-XXXX — Short title

- Date: YYYY-MM-DD
- Status: PROPOSED | ACCEPTED | SUPERSEDED | REJECTED
- Decision owner: <agent or human owner>

### Context
<why the decision was required>

### Evidence
<repository evidence, requirements, tests, or external evidence>

### Decision
<precise decision>

### Consequences
<known consequences>

### Supersedes
<previous decision, if applicable>
```

## Current Decisions

No new architectural decision is registered by this file.

## Rules

- Record decisions that future agents need to preserve.
- Do not record temporary implementation preferences as architectural decisions.
- Never convert an agent's suggestion into an accepted decision without an explicit basis.
- When a decision is superseded, preserve the old entry and mark it `SUPERSEDED`.
- When evidence is incomplete, say so explicitly.
