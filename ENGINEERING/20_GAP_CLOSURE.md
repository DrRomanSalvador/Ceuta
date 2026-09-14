# CeutIA — 20-gap engineering closure contract

This document consolidates the previously identified runtime gaps into one executable engineering contract. It is an implementation contract, not a claim of scientific validation.

1. Canonical runtime orchestration — source, evidence, state, analysis, scenario, control, decision, audit and persistence must participate in one runtime path.
2. Official-source ingestion — registered authoritative sources must be retrievable with bounded network behavior, freshness and integrity metadata; retrieval must never itself become evidence.
3. Evidence identity and lineage — evidence requires source, claim, content hash, provenance and immutable identity; hash collisions are rejected.
4. Bitemporal semantics — valid time and knowledge/recorded time must be represented and queried explicitly.
5. Epistemic stage separation — observation/evidence/signal/state/inference/hypothesis/prediction/scenario/decision/outcome are distinct contracts.
6. State evolution — decisions must reference an explicit state and preserve the state-to-decision lineage.
7. Signal/change detection — change points, anomalies and escalation signals must remain analytically distinct from observations and predictions.
8. Source reliability and dependence — source authority, evidential weight, independence, contradiction and adversarial risk remain separate variables.
9. Conflict resolution — supporting and contradicting evidence must be represented and unresolved material conflict must prevent silent recommendation.
10. Uncertainty propagation — uncertainty is carried through evidence and decision control; indeterminate uncertainty causes abstention/degradation.
11. Scenario integrity — scenario probabilities are bounded and must form a complete probability distribution before decision optimization.
12. Model governance — model releases require reproducible code/data identity and validation, calibration and approval provenance; calibrated releases outside validity are rejected.
13. Deterministic/statistical/LLM separation — model provenance identifies the computational class and does not permit an ungoverned model to masquerade as validated evidence.
14. Decision policy and utility — risk class, policy, constraints, assumptions and utility are included in the decision manifest and control decision.
15. Human review and override — review requires explicit actor identity, authority, risk scope and reason and is audit-linked.
16. Information boundary — restricted information cannot be emitted through the public decision path without an authorized boundary.
17. Adversarial/manipulation controls — adversarial risk, corroboration requirements and contradiction are first-class decision controls.
18. Degraded-mode behavior — missing evidence, unavailable state, invalid model releases and persistence failures must fail closed or produce explicit degraded output.
19. Action and feedback lifecycle — recommendations must be separated from downstream action; outcomes must be recorded retrospectively and linked to model/decision review.
20. End-to-end traceability and observability — every emitted decision must expose an auditable lineage from inputs and assumptions to decision and provide enough runtime diagnostics to identify failure state.

## Current implementation boundary

The canonical FastAPI decision path now performs provenance-complete evidence admission, append-only evidence identity enforcement, bitemporal evidence validation, scenario-distribution validation, model-governance gating, decision-control authorization, audit persistence and lineage emission. Existing source, review, action and feedback services remain separate enforcement boundaries and must be invoked by their corresponding operational workflows; they are not implicitly executed by a decision recommendation.

## Non-claim

Engineering completion is not equivalent to scientific validation. Temporal backtesting, calibration assessment, out-of-sample performance, causal validation, red-team evaluation and production source validation remain empirical validation activities and must not be represented as complete merely because the software contracts exist.
