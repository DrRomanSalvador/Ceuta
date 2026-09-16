# Finite Scientific-Limitation Resolution Matrix

This document is the authoritative working state for the finite scientific-limitation resolution mission. It does not reopen the completed engineering audit.

## State model

`ENGINEERING_STATUS` and `SCIENTIFIC_STATUS` are independent. Engineering implementation or replay evidence does not establish prospective real-world validity.

## Initial residual limitations

| ID | Limitation | Current resolution status | What can be established now | Irreducible external evidence |
|---|---|---|---|---|
| SL-01 | PIT semantic binding of actual X_t | PARTIALLY_RESOLVED | Point-in-time temporal constraints, provenance/integrity primitives, deterministic replay requirements and cryptographic binding can be engineered/tested. The remaining requirement is binding the actual feature vector consumed by the model to a complete reconstructible information set. | Prospective/retrospective source-process evidence proving that every production feature is generated only from the declared PIT information set. |
| SL-02 | Future-derived feature detection | PARTIALLY_RESOLVED | Temporal eligibility, provenance and adversarial contamination boundaries can be enforced where feature lineage metadata are supplied. No timestamp-only mechanism can prove absence of arbitrary hidden future computation. | Evidence from the complete production feature-generation process and all upstream transformations. |
| SL-03 | Prospective baseline integrity | PARTIALLY_RESOLVED | Baseline methodology, versioning and temporal separation can be formalized and evaluated. Superiority cannot be claimed without frozen baseline definitions and a valid held-out/prospective comparison. | Future held-out/prospective baseline performance under the same information constraints. |
| SL-04 | Repeated-forecast dependence | PARTIALLY_RESOLVED | Cluster/block bootstrap, dependence diagnostics, temporal folds and dependence-aware intervals are implemented. The correct independent unit remains design-dependent for each target and sampling process. | Empirical confirmation of the target-generating dependence structure and sufficient observations for stable inference. |
| SL-05 | Counterfactual/intervention evidence | PARTIALLY_RESOLVED | Prediction, decision, warning/action and outcome lineage can be represented and the causal estimand can be predeclared. Synthetic/replay interventions are methodological tests only. | Real intervention assignment/exposure/outcome data or a justified experimental/quasi-experimental design. |
| SL-06 | Real-world response effectiveness | PARTIALLY_RESOLVED | Response provenance can be specified: warning, receipt, decision, action, delay, execution, capacity constraint and outcome. | Real operational response and outcome observations. |
| SL-07 | Causal validity | PARTIALLY_RESOLVED | Explicit estimand/assumption/evidence contracts and identification gates can prevent association from being silently promoted to causation. | Identifiable design plus empirical data satisfying consistency, positivity, confounding/interference and transport assumptions as applicable. |
| SL-08 | Calibrated predictive uncertainty | PARTIALLY_RESOLVED | Probability-domain checks, Brier/log-loss, calibration-in-the-large, calibration slope/intercepts, intervals, discrimination and dependence-aware validation primitives are available. | Calibration and uncertainty performance on appropriately held-out/prospective data from the target population/regimes. |
| SL-09 | Validated causal propagation | PARTIALLY_RESOLVED | Causal status can be separated from descriptive cross-domain propagation; unsupported causal claims can be blocked. | Empirical causal evidence validating specific propagation mechanisms in the relevant population and regime. |

## Concrete closure criteria

### SL-01 / SL-02 — PIT and leakage

Question: Can the exact feature vector consumed by a forecast be reconstructed from a declared point-in-time information set?

Required evidence: feature-level source identity/version, publication/acquisition/availability semantics, derivation graph, transformation parameters, aggregation/lookback windows, cutoff, feature fingerprint, manifest fingerprint and forecast binding.

Closure test: inject a future value or revision into any declared upstream input; the resulting feature and fingerprint must change or the feature must be rejected. Identical PIT inputs must reproduce identical feature fingerprints. A future-ineligible dependency must fail closed.

Scientific remainder: hidden external preprocessing not represented in the lineage contract cannot be disproved by repository code alone.

### SL-03 — baselines

Question: Is the comparison model frozen before evaluation and subject to the same information constraints?

Closure test: baseline version and training cutoff are immutable for an evaluation; retrospective changes create a new baseline identity and cannot modify historical results.

Scientific remainder: comparative performance still requires held-out/prospective observations.

### SL-04 — dependence

Question: Are uncertainty estimates based on the actual independent sampling unit and temporal dependence structure?

Closure test: row-level resampling must not be used when repeated units are declared dependent; cluster/block procedures preserve the declared dependence unit; temporal folds prevent future training information.

Scientific remainder: the data-generating dependence structure must be known or empirically defensible.

### SL-05 / SL-06 — intervention and response

Question: Can prediction correctness be separated from intervention effectiveness and operational execution?

Closure test: prediction, decision, warning, receipt, action, execution, exposure, delay and outcome retain separate timestamps/identities and cannot be collapsed into a single success label.

Scientific remainder: effectiveness requires real-world intervention/outcome observations.

### SL-07 / SL-09 — causality

Question: Is a causal claim identifiable under a declared causal design rather than inferred from association or graph connectivity?

Closure test: unaddressed ancestral backdoor candidates or missing core identification assumptions block causal identification. Negative controls are explicit falsification/diagnostic tests when declared, but their absence is not by itself a universal logical blocker to internal identification. A claim of transportability is separately gated from internal identification. Descriptive propagation is not emitted as causal propagation without causal evidence.

Scientific remainder: identification assumptions, falsification diagnostics and empirical support remain study-specific.

### SL-08 — uncertainty

Question: Does uncertainty have a defined statistical interpretation and valid empirical calibration procedure?

Closure test: invalid probabilities fail; calibration uses proper scoring and calibration parameters; dependence-aware uncertainty is used for repeated/clustered observations; degenerate calibration is handled explicitly rather than silently treated as calibrated.

Scientific remainder: prospective calibration and uncertainty transport are empirical claims.

## Traceability amendments

- `SL-01/SL-02`: `limitation_controls.py` adds deterministic PIT manifests, dependency eligibility, feature fingerprints and fail-closed rejection of outcome/future-derived dependencies.
- `SL-03`: the same module adds immutable baseline identities with training/feature cutoffs; retrospective mutation of a baseline identity is rejected.
- `SL-04`: `cluster_bootstrap_mean` and aggregate prediction evaluation now report uncertainty at a declared dependence unit rather than assuming row independence.
- `SL-08`: `binary_calibration` reports Brier score, log loss, calibration gap and ECE while explicitly retaining `PROSPECTIVE_VALIDITY_STATUS=NOT_ESTABLISHED`.
- `SL-07`: causal identification logic now explicitly separates internal identification from falsification diagnostics and transportability. Negative controls are not treated as universal identification prerequisites.
- Corresponding adversarial tests cover future dependencies, revision identity, immutable baselines, clustered resampling, calibration status, missing negative controls and unaddressed backdoor candidates.
- Engineering closure remains independent from the scientific claim of prospective predictive or causal validity.

## Second-order review state

The resolution work has surfaced four material second-order boundaries that remain explicitly controlled rather than silently assumed resolved:

1. PIT controls can prove eligibility and reproducible fingerprints for declared lineage, but cannot prove absence of undisclosed upstream preprocessing outside the manifest.
2. Dependence-aware inference can enforce the declared unit, but selecting the correct independent unit remains a property of the target-generating process and study design.
3. Calibration diagnostics can be computed correctly on held-out/replay data, but calibration transport to future regimes and populations remains empirical.
4. Causal identification gates can prevent unsupported causal promotion, but identification assumptions and empirical causal support remain study-specific.

No second-order finding currently reopens a closed engineering surface.

## Current engineering-scientific boundary

`GLOBAL_ENGINEERING_AUDIT = AUDIT_COMPLETE` remains closed.

`SCIENTIFIC_LIMITATION_RESOLUTION` is not yet complete.

`PROSPECTIVE_PREDICTIVE_VALIDITY = NOT_ESTABLISHED` remains unchanged.

This matrix is a working control document; every subsequent implementation must reference a limitation ID, closure criterion, adversarial test and remaining scientific claim.
