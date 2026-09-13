# Longitudinal State Estimation

## Purpose

CeutIA must distinguish an observation from an estimate of the underlying system state. This increment introduces a narrow, auditable scalar state-space estimator for longitudinal data.

## Model

For one variable:

`x_t = x_(t-1) + w_t`

`y_t = x_t + v_t`

where `x` is the latent state, `y` is an observation, and process/measurement uncertainty are explicit. Process variance is scaled by elapsed time, allowing irregular observation intervals.

The implementation uses the exact one-dimensional Kalman predict/update equations. Observation variance is supplied explicitly; it is not inferred from the observed value itself.

## Scientific boundary

This module does not establish causality, detect regimes, identify anomalies, forecast outcomes, estimate intervention effects, or interpret a state as healthy/unhealthy. The innovation is an estimation residual, not a causal effect or anomaly claim.

The current implementation is intentionally scalar. Multivariate state-space models, cross-variable covariance, nonlinear filters, missingness mechanisms, time-varying parameters, smoothing, and model comparison remain future increments and must be benchmarked before being treated as validated capabilities.

## Reproducibility

Each posterior estimate records its time, prior, posterior variance, observation identifier, innovation, and innovation variance. Input observations remain linked to their canonical provenance/evidence fields.

Validation consists of deterministic unit tests plus `scripts/verify_state_estimation.py`.

## Next increment

Extend state estimation with an explicit observation-error model and benchmark the estimator on synthetic systems with known latent trajectories, measurement noise, irregular sampling, missing observations, and abrupt regime changes. Do not promote the implementation to scientific validation until those benchmarks pass predefined criteria.
