# Final Invisible-Layer Engineering

Authoritative engineering state for the final invisible-layer mission. This record does not reopen previous audits or define another gap universe.

## Five requirements and current architectural state

1. **External reality anchoring / global falsifiability — ENGINEERINGALLY_INTEGRATED**
   - `backend/app/core/final_epistemic_control.py`
   - `FalsificationCondition`, `RealityAnchorAssessment`, `FalsifiabilityStatus`.
   - Explicit independent evidence, common-mode dependencies, divergence and global-model-doubt state.

2. **Compositional epistemic integrity — ENGINEERINGALLY_INTEGRATED**
   - `EpistemicContract`, `EpistemicTransformation`, `EpistemicIntegrityEngine`.
   - Transformations explicitly preserve, weaken, break or leave epistemic properties unknown.
   - The runtime gate degrades unresolved composition, but abstains on broken composition when the final assessment is supplied.

3. **Closed-loop causal evaluability — ENGINEERINGALLY_INTEGRATED**
   - `ClosedLoopEvaluation`, `CounterfactualStatus`.
   - Intervention-conditioned outcomes cannot be represented as ordinary outcomes without an explicit counterfactual status.
   - Unidentifiable counterfactuals remain explicitly unidentifiable.

4. **Epistemic self-model / controlled ontological self-critique — ENGINEERINGALLY_INTEGRATED**
   - `EpistemicSelfModel`, `OntologySignal`, `EpistemicSelfCritique`, `OntologyStatus`.
   - Persistent unexplained structure can escalate to ontology review.
   - Candidate ontology revision requires independent review; anomalies do not silently mutate the active ontology.

5. **Prospective whole-system incremental validity — ARCHITECTURALLY_SUPPORTED / EMPIRICALLY_UNVALIDATED**
   - `ProspectiveEvaluationProtocol`, `ProspectiveEvaluationResult`.
   - Protocol captures target, population, context, horizon, decision rule, comparator and version identities.
   - The controller cannot mark method effectiveness as established without a precommitted prospective protocol and a result linked to that exact protocol, with deployment validity and explicit prospective validation status.

## Runtime integration

`backend/app/core/runtime/system_gate.py` accepts the final epistemic assessment. Global validity doubt or epistemic suspension forces `ABSTAIN`; broken epistemic composition forces `ABSTAIN`; weakened or unresolved composition forces `DEGRADED`.

## Engineering hardening cycle — 2026-09-14

### P0 — resolved: broken epistemic composition could pass the runtime gate

- Defect: `SystemIntelligenceGate` handled `weakened` and `unknown` composition as degraded, but did not explicitly handle `broken` composition. A final assessment could therefore reach `ALLOW` when the final validity remained `SUPPORTED`.
- Root cause: the gate encoded only the degradation branch and relied on `SystemValidity` for global doubt, while `EpistemicIntegrityStatus.BROKEN` is an independent safety invariant.
- Correction: `backend/app/core/runtime/system_gate.py` now gives `BROKEN` composition an unconditional `ABSTAIN` disposition with zero confidence multiplier.
- Regression protection: `backend/tests/test_final_epistemic_gate.py` now asserts abstention and the corresponding reason.

### P0 — resolved: prospective effectiveness could be established without a valid precommitted protocol linkage

- Defect: `FinalEpistemicController` could set `method_effectiveness_established=True` from a prospective result even when no prospective protocol existed, when the protocol was not precommitted, or when the result referenced a different protocol ID.
- Root cause: the effectiveness predicate checked result fields but did not require protocol existence, precommitment, or protocol/result identity linkage.
- Correction: `backend/app/core/final_epistemic_control.py` now requires an active precommitted protocol, exact protocol-ID match, deployment validity, prospective-validation status and a non-null positive observed benefit before establishing effectiveness. Mismatched results are explicitly recorded as unlinked.
- Regression protection: `backend/tests/test_final_epistemic_control.py` covers non-precommitted protocols and mismatched protocol IDs in addition to the existing absence-of-evidence case.

## Focused tests added

- `backend/tests/test_final_epistemic_control.py`
- `backend/tests/test_final_epistemic_gate.py`

The tests target broken epistemic composition, explicit intervention counterfactual status, ontology-review escalation, absence of unsupported whole-system effectiveness claims, prospective protocol linkage, global model doubt, and runtime abstention.

## Verification state

Changes were persisted directly to `main`. GitHub Actions `CeutIA Integration Validation` was triggered by the resulting push and is the authoritative execution check for the current hardening cycle. The latest run must be allowed to complete before treating the corrections as execution-verified.

## Completion states

- ARCHITECTURALLY_SUPPORTED
- ENGINEERINGALLY_INTEGRATED
- EMPIRICALLY_UNVALIDATED
- PROSPECTIVELY_VALIDATED

Current overall state: **ENGINEERINGALLY_INTEGRATED; EMPIRICALLY_UNVALIDATED**.

## Required focused failure tests

- coherent wrong world
- successful self-contamination
- false independence
- ontological novelty
- valid prediction without real-world benefit
- model self-validation loop
- epistemic invariant loss
- global validity doubt

## Scientific boundary

Passing implementation tests does not establish prospective real-world effectiveness. That requires precommitted prospective comparison against a credible alternative.

## Recovery rule

A future engineering agent must inspect this record and the authoritative implementation before making changes. No new gap universe is to be opened by this record.
