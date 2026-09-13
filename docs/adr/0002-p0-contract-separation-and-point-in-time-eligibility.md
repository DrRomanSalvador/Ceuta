# ADR 0002 — P0 contract separation and point-in-time eligibility

Date: 2026-09-13
Status: accepted for implementation on branch `codex/p0-rigorous-integration`
Decision ID: GPT-001

## Problem

CeutIA already contains an epistemic state machine, while repository documentation also describes validation-oriented states. Treating these as one vocabulary risks conflating epistemic status with implementation or review status. Temporal leakage is a separate risk: event time can legitimately precede publication, while information availability for an evaluation must never occur after the evaluation cutoff.

## Decision

Maintain three distinct dimensions:

1. Epistemic status: what is justified by the evidence.
2. Implementation status: whether a capability exists in the repository.
3. Validation/review status: whether an artifact has passed the required review gates.

Use point-in-time availability (`available_at`) rather than `event_time` as the default eligibility criterion for retrospective evaluation. Future observations may exist in the real world, but they are ineligible for an evaluation whose cutoff precedes their availability.

`CORROBORATED_FACT` requires at least two explicitly independent source groups and explicit corroborating evidence IDs. Dependent, copied, amplified, or unknown-source material does not count as independent corroboration.

## Alternatives rejected

- Replacing the existing epistemic state machine with a second state machine.
- Treating event time as the sole temporal eligibility criterion.
- Counting documents instead of independent source groups.
- Treating unknown source relationships as independent.
- Silently resolving contradictions.

## Consequences

The system becomes more conservative. Some observations remain `UNKNOWN`, `UNVERIFIED`, or `ATTRIBUTED_CLAIM` longer. This is intentional: uncertainty is preserved rather than converted into false certainty.

## Risks introduced

The current P0 state machine still permits some transitions that require stronger domain-specific evidence rules. Those rules must be progressively constrained without silently changing the existing contract. Human review remains mandatory for critical epistemic transitions and high-level alerts.

## Required follow-up

- Align documentation vocabulary with the three-dimensional model.
- Add runtime validation at CeutIA ingestion boundaries.
- Add schema validation to CI.
- Add CeutIA-Serpiente integration tests against the v1 contract.
- Add explicit review gates for alert level >= 3.
