# Scientific Fixed-Point Specification

## Meaning

`GLOBAL_SCIENTIFIC_FIXED_POINT` means that, for the current persisted scientific state, repository state, evidence and authorized infrastructure, no additional **executable, non-redundant, material and scientifically justified** work is presently available that would improve the declared objective enough to justify execution.

It does **not** mean scientific truth is complete, nor that future observations cannot reopen work.

## Required zero conditions

A fixed point requires:

- `EXECUTABLE_OPEN_WORK = 0`
- `UNPROCESSED_DERIVED_WORK = 0`
- `UNINTEGRATED_COMPLETED_WORK = 0`
- `UNRECONCILED_STATE = 0`
- `UNVERIFIED_INTERNAL_REPAIR = 0`
- `UNTESTED_EXECUTABLE_CHANGE = 0`
- `UNFOLLOWED_ACTIVE_HANDOFF = 0`
- no material contradiction is silently unresolved;
- no activation exists without a closure/continuation decision;
- no local task is deferred merely because ownership differs.

## Candidate-work test

Every discovered candidate is classified:

`MATERIAL_EXECUTABLE | NON_MATERIAL | REDUNDANT | EXTERNAL | HUMAN_AUTHORITY | NOT_JUSTIFIED`.

Only `MATERIAL_EXECUTABLE` can prevent the fixed point. `EXTERNAL` and `HUMAN_AUTHORITY` must include explicit evidence that the property cannot be executed under current authority/infrastructure.

## Reopening rule

The fixed point is event-sensitive. New evidence, new data, model degradation, contradiction, regime change, ontology change, provenance repair, or a newly available capability may reopen the work queue. Reopening must reference the event that invalidated the fixed-point snapshot.

## Anti-Goodhart rule

Fixed-point status is not optimized through a single score. It is a conjunction of closure invariants plus explicit evidence. A low task count is never sufficient evidence of scientific maturity.

## Validation boundary

Implementation and tests may be closed while prospective/operational/scientific validation remains `NOT_ESTABLISHED` when that validation genuinely requires future observations or unavailable infrastructure. The boundary must not be used to leave executable engineering work open.
