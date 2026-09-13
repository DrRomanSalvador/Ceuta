# ADR-0002 — Proxy-gate epistemic boundary

- Date: 2026-09-13
- Status: ACCEPTED (reflects already-implemented Cycle 1 behaviour)
- Decision owner: sole human owner via authorised agent action

### Context

Cycle 1 implemented an auditable spatial proxy screening gate. The epistemic limits of that gate must be explicit and non-negotiable.

### Decision

A proxy-gate result:

- may classify PROXY_RISK or return fail-closed states;
- must never be interpreted as establishing causality;
- must never be interpreted as proving absence of bias;
- must never alone authorise operational promotion.

These constraints are already encoded in the implementation and are now recorded as an architectural decision.

### Consequences

Any future change that weakens these constraints is a breaking change to the epistemic contract and requires explicit owner-level decision.
