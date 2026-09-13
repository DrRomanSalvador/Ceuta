# Decision-system work order 06 — Real-time integrity and fail-closed operation

## Objective
Make the unified kernel genuinely event-driven and safe to operate continuously under changing data, model and system conditions.

## Required implementation
- Consume `RealtimeEvent` payloads directly into observation/state/inference rather than accepting an unrelated pre-built cycle.
- Maintain deterministic event ordering, event-time semantics, watermarks, late-arrival handling and explicit replay/reconciliation.
- Preserve append-only provenance and reproducibility of every decision state.
- Detect stale observations, duplicated events, source corruption and observation-process changes.
- Integrate self-observation into every cycle, including model drift, assumption violations, observability/identifiability degradation and uncertainty explosions.
- Execute epistemic integrity gates before prediction, causal claims and decisions.
- Fail closed on insufficient evidence, incompatible models, invalid state, broken assumptions or exceeded uncertainty limits.
- Support idempotent recovery, checkpointing and deterministic replay.
- Expose decision latency and computational-budget diagnostics without silently degrading scientific validity.

## Acceptance criteria
A real-time event must traverse the canonical inference chain from observation to decision using the event's information set, with complete lineage and explicit fail-closed behaviour. Replaying the same ordered event stream must reproduce the same decision state within declared numerical tolerances.
