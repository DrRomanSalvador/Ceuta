# CeutIA runtime hardening cycle — 2026-09-14

## Scope

This cycle follows the repository-first rule: inspect the current implementation, identify a concrete defect, correct it, add a regression test where practical, push the correction, and only then continue inspection. No new architecture-gap universe is opened in this cycle.

## Defects resolved

1. P0 — `SystemIntelligenceGate` did not explicitly fail closed on `EpistemicIntegrityStatus.BROKEN`.
   - Root cause: missing terminal branch in the runtime gate.
   - Resolution: broken epistemic composition now returns `ABSTAIN` with zero confidence multiplier.
   - Regression: `backend/tests/test_final_epistemic_gate.py`.

2. P0 — prospective effectiveness could be marked established without a valid precommitted protocol/result linkage.
   - Root cause: effectiveness depended on result fields without enforcing protocol existence, precommitment and protocol identity linkage.
   - Resolution: effectiveness requires an active precommitted protocol, matching result protocol ID, valid deployment, prospectively validated status and positive finite observed benefit.
   - Regression: `backend/tests/test_final_epistemic_control.py`.

3. P1 — non-finite numeric values could pass runtime probability/uncertainty gates because comparisons with NaN are false.
   - Root cause: range checks omitted explicit finiteness checks.
   - Resolution: probability, uncertainty, evidence weights, provenance trust, decision scenario inputs and system-gate risk/confidence values are fail-closed on non-finite values.
   - Regression tests added under `backend/tests/test_runtime_numeric_finiteness.py`, `backend/tests/test_decision_numeric_finiteness.py`, and `backend/tests/test_system_gate_numeric_finiteness.py`.

4. P1 — final epistemic contract objects accepted invalid boundary values and could represent an established reality anchor without conditions/evidence.
   - Root cause: incomplete runtime validation in the contract dataclasses.
   - Resolution: finite/range validation, complete prospective-protocol identity/definition validation, prospective-result validation, ontology-signal validation, and reality-anchor establishment requirements.
   - Regression: `backend/tests/test_final_epistemic_contract_validation.py`.

5. P1 — registered official-source URLs followed arbitrary redirects.
   - Root cause: `httpx.Client(..., follow_redirects=True)` at the network boundary.
   - Resolution: redirects disabled; 3xx responses are not verified as current source data.
   - Regression: `backend/tests/test_source_client_security.py`.

6. P1 — decision evidence accepted malformed content hashes and assessment identity mismatches at the runtime integrity boundary.
   - Root cause: validation checked presence/length/provenance but not SHA-256 hexadecimal format or assessment identity correspondence.
   - Resolution: strict 64-character hexadecimal hash validation and identity consistency checks.
   - Regression: `backend/tests/test_evidence_integrity_contract.py`.

7. P1 — scientific and safety gates accepted truthy non-boolean state inputs; negative contradiction counts were also accepted as a non-zero/false ambiguity.
   - Root cause: Python truthiness was used as a semantic gate without input-type validation.
   - Resolution: strict boolean state flags and non-negative integer contradiction counts.
   - Regression: `backend/tests/test_scientific_guards_hardening.py` and `backend/tests/test_safety_gate_hardening.py`.

## Verification state

The repository's integration workflow is triggered on every push. Intermediate workflow runs were cancelled by later hardening commits, which is expected under the workflow's concurrency behavior. The latest run must reach a terminal successful state before this cycle can be considered engineering-verified.

Historical successful CI remains valid only for the commit on which it ran; it is not evidence for later commits.

## Scientific boundary

Passing compilation, unit tests, runtime-integrity tests and Compose validation establishes engineering correctness only. It does not establish predictive accuracy, causal validity, calibration quality, prospective effectiveness or real-world benefit.

## Remaining inspection target

Continue from the current repository state after the latest CI terminal result. Any newly discovered defect must be fixed and re-tested before broad-system analysis resumes.
