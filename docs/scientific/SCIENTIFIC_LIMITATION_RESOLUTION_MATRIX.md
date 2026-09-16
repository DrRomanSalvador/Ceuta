# Finite Scientific-Limitation Resolution Matrix

This document is the authoritative final state for the finite scientific-limitation resolution mission. It does not reopen the completed engineering audit.

## State model

`ENGINEERING_STATUS` and `SCIENTIFIC_STATUS` are independent. Engineering implementation or replay evidence does not establish prospective real-world validity.

## Resolution state

`SCIENTIFIC_LIMITATION_RESOLUTION = COMPLETE`

Completion means that every explicitly declared residual limitation has been decomposed, every resolvable engineering/methodological component has been implemented and adversarially tested, and every remaining unresolved claim has a specific external-evidence requirement. It does not mean prospective validity has been established.

| ID | Limitation | Final resolution status | Resolved now | Irreducible remainder |
|---|---|---|---|---|
| SL-01 | PIT semantic binding of actual X_t | PARTIALLY_RESOLVED | Producer-side feature-matrix fingerprinting is bound to the point-in-time manifest at runtime; multi-horizon matrices receive independent PIT fingerprints; CeutIA provides deterministic PIT manifests and replay verification. | Hidden upstream preprocessing not represented in the declared lineage cannot be disproved from repository code alone. |
| SL-02 | Future-derived feature detection | PARTIALLY_RESOLVED | Availability cutoffs, source versions, transformation lineage, outcome-derived flags and future-derived flags are fail-closed; adversarial contamination tests exist. | An undisclosed external transformation or backdated upstream metadata cannot be ruled out without evidence from the complete production data-generating process. |
| SL-03 | Prospective baseline integrity | PARTIALLY_RESOLVED | Temporal prevalence and seasonal baselines are evaluated under chronological holdout; immutable baseline identities with training/feature cutoffs are available. | Comparative superiority requires future held-out/prospective observations under the same information constraints. |
| SL-04 | Repeated-forecast dependence | PARTIALLY_RESOLVED | Dependence-aware cluster bootstrap and declared-unit aggregate evaluation are implemented; row-independence is no longer silently assumed. | The correct independent unit and stable sampling distribution remain properties of the real target-generating process. |
| SL-05 | Counterfactual/intervention evidence | PARTIALLY_RESOLVED | Prediction correctness is separated from intervention lanes; intervention observations require counterfactual information before ordinary scoring. | Real intervention assignment/exposure/outcome evidence is required for intervention-effect claims. |
| SL-06 | Real-world response effectiveness | PARTIALLY_RESOLVED | Warning, receipt, decision, action, execution, delay, capacity, exposure and outcome lineage are represented separately. | Real operational response and outcome observations are required. |
| SL-07 | Causal validity | PARTIALLY_RESOLVED | Estimands, assumptions, backdoor candidates, evidence gates, falsification diagnostics and transportability are explicitly separated; association cannot silently become causation. | Study-specific empirical evidence is required to support causal claims. |
| SL-08 | Calibrated predictive uncertainty | PARTIALLY_RESOLVED | Proper scoring, calibration diagnostics and dependence-aware validation are implemented; the final SERPIENTE ensemble probability itself is calibrated on a temporally separated calibration split. | Prospective calibration/uncertainty transport to future populations and regimes remains empirical. |
| SL-09 | Validated causal propagation | PARTIALLY_RESOLVED | Descriptive propagation is separated from causal status; unsupported causal promotion is blocked; causal graph identification remains acyclic and dynamic feedback must be time-unrolled. | Specific propagation mechanisms require empirical causal evidence in the relevant population/regime. |

## Closure evidence

### SL-01 / SL-02 — PIT and leakage

Required evidence was decomposed into forecast origin, information cutoff, feature-level provenance, source identity/version, availability, transformation lineage, feature fingerprint, manifest fingerprint and forecast binding.

Implemented controls: SERPIENTE `pit_binding.py`, runtime enforcement, multi-horizon binding, CeutIA `limitation_controls.py`, adversarial future-availability/tampering/outcome-derived/future-derived tests.

Closure boundary: repository controls establish the strongest declared PIT/leakage boundary; they cannot prove undisclosed external preprocessing.

### SL-03 — baselines

Implemented controls: chronological 60/20/20 model/calibration/test separation; temporal prevalence and seasonal day-of-week baselines; immutable baseline identities with training and feature cutoffs.

Closure boundary: baseline methodology is now predeclared and protected from silent retrospective mutation. Performance superiority remains an empirical comparison question.

### SL-04 — dependence

Implemented controls: declared dependence unit and cluster bootstrap for aggregate Brier uncertainty; regression test with repeated decision clusters.

Closure boundary: the appropriate independent unit must be determined from the actual study/data-generating process.

### SL-05 / SL-06 — intervention and response

Implemented controls: intervention-independent validation lanes, counterfactual-required state after intervention, durable provenance and separation of warning/decision/action/execution/outcome.

Closure boundary: no synthetic or replay intervention is counted as empirical effectiveness.

### SL-07 / SL-09 — causality

Implemented controls: explicit estimand/assumption contract, conservative backdoor candidate detection, internal-identification gate, separate falsification/negative-control diagnostics, separate transportability status, causal evidence gate, descriptive-vs-causal propagation separation, and acyclic graph semantics requiring time-unrolled representation for feedback.

Closure boundary: causal validity and specific propagation mechanisms remain empirical claims.

### SL-08 — uncertainty

Implemented controls: finite probability-domain enforcement, Brier score, log loss, calibration gap/ECE diagnostics, temporally separated isotonic calibration, and final-ensemble calibration rather than averaging calibrated and uncalibrated probabilities.

Second-order correction: longitudinal trend, acceleration and volatility are normalized by elapsed time rather than observation count, preventing irregular sampling from changing derivative semantics.

Closure boundary: prospective calibration and uncertainty transport remain empirical.

## Second-order review

The second-order review found and resolved two material implementation-level issues: derivative-like longitudinal features were previously sensitive to irregular observation spacing, and the final ensemble probability was previously formed by averaging a calibrated and an uncalibrated model output. Both are now regression-tested.

The remaining second-order boundaries are not hidden implementation gaps: PIT completeness, dependence-unit selection, calibration transport and causal empirical support each require evidence outside the repository or study-specific data-generating process.

No high-centrality, autonomous-resolvable scientific limitation remains.

## Verification state

`GLOBAL_ENGINEERING_AUDIT = AUDIT_COMPLETE` remains closed.

`SCIENTIFIC_LIMITATION_RESOLUTION = COMPLETE`.

`PROSPECTIVE_PREDICTIVE_VALIDITY = NOT_ESTABLISHED` remains unchanged.

The final scientific state is therefore: engineering and methodological resolution complete; prospective predictive validity not established; remaining scientific claims precisely bounded by future external evidence requirements.
