# CeutIA — Frontier Longitudinal Statistical Validation Standard

## 1. Statistical unit before statistical test

Repeated observations are not independent merely because they occupy different rows. Every validation record must declare the entity, cluster and time structure. The resampling unit must correspond to the scientific source of independent variation.

Supported dependence-preserving methods are entity/cluster bootstrap and moving time-block bootstrap. IID bootstrap is not an accepted fallback for longitudinal claims.

## 2. Temporal validation

Prediction must be evaluated forward in time. Rolling-origin evaluation creates an expanding or sliding training window, a purge gap for delayed labels/information leakage, and a future test horizon. No test observation may be available to model fitting.

The gap must be chosen from the data-generating process: label latency, publication latency, revision latency and feature availability are all potential leakage paths.

## 3. Temporal calibration

Calibration is evaluated separately at each temporal fold. The calibration intercept measures systematic temporal prevalence/level drift; the slope measures shrinkage or over-dispersion drift. A pooled calibration estimate cannot replace fold-specific calibration because it can conceal temporal non-stationarity.

## 4. Proper scoring under dependence

Brier score and logarithmic loss remain proper scoring rules. Their point estimates are row-weighted descriptive quantities; inferential uncertainty must respect the independent unit. Effective sample size is reported as a diagnostic and never substituted for a principled cluster/block variance estimator.

## 5. Optimism correction

Apparent performance is distinguished from bootstrap test performance. Optimism is estimated within the same dependence-preserving resampling design and subtracted from apparent performance. Any model selection performed before bootstrap correction is a source of residual optimism.

## 6. Nested cross-validation

Hyperparameter/model selection occurs exclusively inside the inner validation loop. The outer loop estimates generalization. No target-fold observation may influence parameter selection. For temporal data both inner and outer designs must respect chronology.

## 7. Transportability

External transport is evaluated without refitting on the target population. Target discrimination/proper scores, target calibration intercept and target calibration slope are reported separately. A change in target performance is not automatically attributed to model failure: covariate shift, prevalence shift, measurement-process change and outcome-definition drift require separate provenance.

## 8. Missingness and observation processes

Longitudinal missingness is a data-generating mechanism, not a preprocessing nuisance. MCAR/MAR/MNAR assumptions must be explicit. Informative visit processes and intermittent observation can induce selection bias even when individual missing values appear innocuous.

## 9. Dependence-aware uncertainty

For serially correlated observations, subject-cluster bootstrap, cluster bootstrap, or time-block bootstrap must be selected according to the causal/statistical dependence structure. Standard errors based on the number of rows are not scientifically acceptable when rows share an entity or temporal shock.

## 10. Validation contract

A decision-ready longitudinal validation requires:

1. dependence structure declared;
2. independent unit declared;
3. temporal holdout;
4. leakage test;
5. dependence-preserving uncertainty method;
6. missingness/observation-process assessment;
7. optimism assessment;
8. nested model-selection validation;
9. external transport assessment;
10. explicit prediction horizon.

Failure of any required element blocks a claim of frontier statistical validation.

## 11. Claims CeutIA must not make

A high AUROC does not prove calibration.

A good Brier score does not prove transportability.

A temporally held-out score does not prove absence of dataset shift.

A bootstrap confidence interval is not valid if the bootstrap unit is wrong.

A pooled longitudinal confidence interval is not valid merely because the sample size is large.

External validation is not prospective validation.

Calibration in one period does not imply calibration in another.

An optimism-corrected score is not unbiased if model selection occurred outside the resampling loop.

## 12. Frontier extensions required for the highest tier

The current substrate is designed to support, without architectural replacement: block-length selection from autocorrelation/mixing diagnostics; stationary and circular block bootstrap; cluster-robust sandwich estimators; hierarchical Bayesian calibration; recurrent-event/survival validation; competing risks; dynamic discrimination; time-dependent Brier/integrated Brier score; conformal risk control under temporal dependence; covariate-shift weighting; density-ratio diagnostics; measurement-error sensitivity; informative observation-process models; and sequential prospective monitoring.

These extensions must be implemented only with explicit estimands, assumptions, diagnostics and validation evidence. They must not be approximated by adding labels to IID statistics.
