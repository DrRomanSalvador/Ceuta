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
   - The runtime gate degrades unresolved composition and abstains on broken composition when the final assessment is supplied.

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
   - The controller cannot mark method effectiveness as established without a precommitted prospective result with deployment validity and explicit prospective validation status.

## Runtime integration

`backend/app/core/runtime/system_gate.py` accepts the final epistemic assessment. Global validity doubt or epistemic suspension forces `ABSTAIN`; weakened or unresolved composition forces `DEGRADED`.

## Focused tests added

- `backend/tests/test_final_epistemic_control.py`
- `backend/tests/test_final_epistemic_gate.py`

The tests target broken epistemic composition, explicit intervention counterfactual status, ontology-review escalation, absence of unsupported whole-system effectiveness claims, global model doubt, and runtime abstention.

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
