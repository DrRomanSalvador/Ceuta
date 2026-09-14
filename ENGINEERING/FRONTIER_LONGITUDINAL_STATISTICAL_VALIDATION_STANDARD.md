# CeutIA Frontier Longitudinal Statistical Validation Standard

## 1. Purpose

CeutIA must not treat repeated observations as independent merely because they are stored as separate rows. Every performance, uncertainty, calibration, transport and learning claim must declare the stochastic dependence structure that generated the observations.

This standard is the statistical gate for longitudinal, clustered and temporally dependent evidence.

## 2. Independent statistical unit

Before estimation, the system declares one of:

- entity/subject;
- cluster/site/household/organization;
- time block for a time-series process.

The row is never assumed to be the independent unit by default.

The validation record must preserve entity, cluster, observation time, prediction horizon, outcome and observation identity.

Effective sample size is diagnostic only. It is never accepted as a substitute for a valid variance estimator.

## 3. Dependence-aware uncertainty

Primary methods:

1. cluster/entity bootstrap for repeated-measure data;
2. moving-block bootstrap for locally dependent time series;
3. circular block bootstrap where boundary wrapping is scientifically defensible;
4. stationary bootstrap for stochastic processes with random block lengths;
5. cluster-robust sandwich intervals for estimands with unit-level score contributions.

The method, block length, resampling unit, seed, replicate count and interval construction are persisted with the result.

Row-level IID bootstrap is prohibited for longitudinal performance claims unless independence has been demonstrated and recorded.

## 4. Block-length discipline

Block length is a scientific hyperparameter. It must not be silently chosen.

The production layer must eventually support data-driven block-length diagnostics based on dependence diagnostics, with sensitivity analysis across plausible lengths. A single arbitrary block width is not evidence that serial dependence has been handled.

## 5. Rolling-origin validation

Temporal validation is forward-only. Training data precede test data, and an explicit purge gap can be inserted to prevent delayed-label or information leakage.

The temporal fold definition records:

- training interval;
- test interval;
- purge gap;
- expanding versus rolling training window;
- horizon;
- entity overlap policy.

The predictor is executed once per fold and the resulting predictions are persisted. Re-running a stochastic predictor merely to compute a pooled score is prohibited.

## 6. Temporal calibration

Calibration must be evaluated over time rather than inferred from one pooled estimate.

The minimum production analysis contains:

- calibration intercept by temporal fold;
- calibration slope by temporal fold;
- dependence-aware confidence intervals;
- drift detection with an explicitly declared threshold or statistical decision rule;
- recalibration policy separated from performance assessment.

Calibration failure is not silently repaired before reporting model performance.

## 7. Proper scoring under dependence

For probabilistic predictions the minimum score set is:

- Brier score;
- logarithmic score/log loss;
- horizon-specific Brier score when prediction horizons exist;
- integrated Brier score where the horizon domain is meaningful.

Scores are point estimates. Their uncertainty must be obtained at the independent statistical unit or by a scientifically justified time-series bootstrap.

An effective-N adjustment alone is not a confidence interval.

## 8. Optimism correction

Apparent performance after fitting or selecting a model on the same observations is optimistic.

The correction must be performed inside the resampling process. The implementation must record metric direction explicitly because some losses are lower-is-better and some utility/discrimination metrics are higher-is-better.

Optimism correction is not interchangeable with ordinary bootstrap confidence intervals.

## 9. Nested temporal cross-validation

Hyperparameter/model selection must occur inside the training portion of every outer temporal fold.

The outer test set is inaccessible to:

- parameter selection;
- threshold selection;
- feature selection;
- calibration selection;
- model ranking;
- early stopping decisions.

A model chosen using future outer-test observations is considered temporally contaminated even if the final score is computed correctly.

## 10. Transport validation

External validity is a separate question from internal performance.

Transport validation must distinguish:

- source performance;
- target performance without target refitting;
- target calibration drift;
- performance difference;
- target population size and independent-unit count;
- whether any target adaptation occurred.

Target refitting is never mislabeled as external validation.

## 11. Missingness and observation process

The system must distinguish missing values from unequal observation frequency.

It must report the observation count per independent unit and identify patterns compatible with an informative observation process. No automatic MCAR, MAR or MNAR assumption is permitted.

Where observation intensity itself can depend on latent state or outcome risk, sensitivity analysis or an explicit observation-process model becomes mandatory for causal or longitudinal claims.

## 12. Repeated outcomes and horizons

A prediction at horizon h for entity e is not interchangeable with a prediction at horizon h+1 for the same entity.

Horizon must therefore be explicit. Scores may be stratified by horizon and integrated only over a declared horizon measure.

If censoring, survival, recurrent events or competing risks are introduced, ordinary binary Brier scoring is insufficient. The production layer must then use the appropriate time-to-event estimand and censoring treatment.

## 13. Scientific extensions required before the corresponding claims

The following are frontier extensions, not permitted to be silently approximated by the current binary layer:

- survival and recurrent-event validation;
- competing-risk prediction;
- time-dependent discrimination;
- IPCW and integrated Brier score for censored outcomes;
- conformal prediction under temporal dependence;
- covariate-shift/density-ratio transport weighting;
- measurement-error sensitivity analysis;
- informative observation-process models;
- hierarchical calibration;
- sequential prospective monitoring;
- block-length selection and sensitivity curves;
- model disagreement as an epistemic signal.

When these data-generating structures appear, CeutIA must fail closed or downgrade the claim rather than substitute an IID approximation.

## 14. Reproducibility contract

Every validation result must persist:

- data snapshot/version identifier;
- feature/configuration hash and retrievable configuration content;
- estimator/model identifier;
- validation design identifier;
- independent unit;
- temporal boundaries and purge gap;
- horizon;
- missingness assumptions;
- resampling method;
- block length;
- replicate count;
- random seed;
- metric and direction;
- calibration method;
- selected parameters;
- target/source population identifiers;
- code version/commit.

## 15. Decision gate

A validation result is decision-ready only when:

1. the independent unit is explicit;
2. temporal leakage has been checked;
3. uncertainty respects dependence;
4. proper scoring is reported where probabilistic predictions are made;
5. optimism is assessed where selection/fitting creates optimism;
6. nested validation protects the outer test set;
7. transport is separated from refitting;
8. missingness/observation processes have been assessed;
9. all assumptions and provenance are reproducible.

Otherwise the system reports a validation limitation and does not elevate the result to a calibrated decision claim.
