# CeutIA Statistical Validation Standard

## Scope

Predictive validation is an evidence claim, not a scalar score. Calibration, discrimination, probabilistic accuracy, transportability and prospective validity are distinct properties and must not be collapsed into a single pass/fail metric.

## Calibration

For binary outcomes, calibration is represented by the standard logistic recalibration model

`logit(P(Y=1 | p)) = alpha + beta * logit(p)`.

`alpha` is calibration-in-the-large and `beta` is the calibration slope. The implementation uses the unpenalized maximum-likelihood estimand. Regularization is not an acceptable numerical shortcut because it changes the estimand. Separation and non-identifiability are therefore reported as failures requiring a different evaluation design or method.

The reported uncertainty uses the inverse observed Fisher information. Confidence intervals are inferential summaries, not acceptance thresholds.

## Proper scoring

Brier score and logarithmic loss are both retained. Brier skill is referenced to the observed-prevalence climatology and is undefined when that baseline has zero variance. A model is never declared scientifically valid from Brier score alone.

## Discrimination

AUROC is computed as the Mann-Whitney concordance probability with half credit for ties. Discrimination does not imply calibration and must remain a separate property.

## Validation design

A strong external claim requires explicit separation of development and evaluation data, temporal holdout and a named external population. Prospective validation is distinct from retrospective external validation. Temporal dependence, clustering and repeated observations invalidate naive IID uncertainty calculations and require an appropriate resampling or hierarchical method before inferential claims are promoted.

## Missing data

Unknown missingness is not decision-ready. MNAR analyses require sensitivity analysis. Complete-case analysis is not treated as automatically unbiased.

## Observed/expected ratio

The observed/expected ratio is descriptive. Its current interval is explicitly labelled a log-scale Poisson approximation and must not be interpreted as exact under arbitrary longitudinal dependence, clustering or informative observation processes.

## Scientific governance

A favourable metric does not create calibration evidence. Calibration evidence must identify the evaluation population, prediction horizon, development/evaluation separation, temporal design, handling of missingness and uncertainty method. Any future claim of calibrated deployment must satisfy these provenance requirements.
