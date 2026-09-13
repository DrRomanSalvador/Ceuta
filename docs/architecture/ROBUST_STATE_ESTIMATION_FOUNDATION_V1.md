# CeutIA — Robust State Estimation Foundation V1

## Purpose

State estimation is a critical scientific boundary in CeutIA. The system must infer an evolving latent state from incomplete, noisy, delayed, heterogeneous and sometimes dependent observations without confusing the inferred state with the measurements that generated it.

The implementation is intentionally designed as a multidisciplinary foundation rather than a single Kalman-filter feature. Its requirements span:

- preventive and longitudinal health science: trajectory, reserve, recovery, heterogeneity and observation-process change;
- epidemiology: surveillance bias, reporting delays, under-ascertainment, changing case definitions, population denominators and time-varying observation processes;
- biostatistics: covariance, uncertainty propagation, dependence, missingness, measurement error, robustness and calibration;
- statistical signal processing / telecommunications: irregular sampling, correlated channels, sensor quality, filtering, smoothing, innovation diagnostics and non-stationary signals;
- data engineering: provenance, source identity, temporal ordering, schema/observation-process versions and missing-channel semantics;
- systems engineering: multivariate coupling, time-varying dynamics, nonlinear state transitions, feedback and model validity;
- scientific governance: explicit assumptions, diagnostics, abstention boundaries and separation of estimation from causality and decision.

## Implemented mathematical layers

`backend/app/core/state/advanced_estimation.py` provides:

1. Multivariate linear state-space specification with explicit transition matrix, process covariance and observation matrix.
2. Irregular-time propagation through a caller-supplied time-varying transition/process model.
3. Multichannel observations with arbitrary missing channels rather than silent imputation.
4. Full measurement covariance, including correlated observation errors.
5. Quality-weighted measurement uncertainty.
6. Mahalanobis innovation diagnostics.
7. Robust Huber innovation weighting as a sensitivity/contamination mechanism.
8. Joseph-form covariance update for improved numerical stability.
9. Rauch–Tung–Striebel fixed-interval smoothing, explicitly distinguished from real-time filtering.
10. Extended Kalman filtering for nonlinear differentiable transition/observation functions, with analytic or finite-difference Jacobians.
11. Bootstrap particle filtering for nonlinear and non-Gaussian state spaces, including effective-sample-size monitoring and systematic resampling.
12. Explicit diagnostics and assumption reporting.
13. Observation-process metadata and source identifiers retained at the observation boundary.

## Mathematical contracts

For the linear model:

`x_t = F_t x_{t-1} + w_t`, `w_t ~ (0, Q_t)`

`y_t = H_t x_t + v_t`, `v_t ~ (0, R_t)`

with prior propagation

`P^-_t = F_t P_{t-1} F_t^T + Q_t`

and innovation

`r_t = y_t - H_t x^-_t`

`S_t = H_t P^-_t H_t^T + R_t`.

The update is based on the supplied covariance structure. The implementation does not assume independent channels merely because they arrive in one packet.

For nonlinear models, the EKF uses local Jacobian linearisation. This is an approximation and is explicitly labelled as such. For strongly nonlinear or non-Gaussian systems, the particle filter provides a different inference regime and makes the transition and observation likelihood explicit.

## Missingness and epidemiological surveillance

A missing channel is not automatically a zero, a normal value, a carried-forward value or an imputed observation. The estimator skips the measurement update while propagating uncertainty through the state model.

This is necessary but not sufficient for MNAR inference. Missingness mechanism inference remains a separate statistical layer. In epidemiological applications, delayed reporting, changing case definitions, testing intensity, ascertainment and denominator changes must be represented in the observation model rather than absorbed into latent-state dynamics without evidence.

## Robustness

A large innovation is diagnostically important but is not automatically an erroneous observation. It can indicate:

- genuine state transition;
- structural model misspecification;
- sensor/reporting error;
- observation-process change;
- unmodelled intervention or exogenous shock;
- regime transition.

Therefore robust weighting is deliberately non-semantic: it changes measurement influence while retaining the innovation and its Mahalanobis diagnostic.

## Scientific boundaries

The following statements are prohibited:

- filtered state = observed reality;
- innovation = causal effect;
- smoothing = retrospective truth;
- high posterior probability = causal identification;
- robust downweighting = proof of bad data;
- epidemiological latent state = disease burden without an explicit observation/ascertainment model;
- sensor quality score = statistical validity without calibration evidence.

State estimation must feed the trajectory, dynamics, causal, forecasting and decision layers through provenance-preserving interfaces.

## Remaining frontier

This layer substantially strengthens estimation but does not claim universal identifiability. Further scientific work remains for:

- fully Bayesian hierarchical state-space models;
- parameter uncertainty and joint state/parameter inference;
- particle MCMC / sequential Monte Carlo parameter learning;
- switching and regime-state models with principled change-point inference;
- stochastic volatility and heavy-tailed observation/process models;
- explicit delay/nowcasting models for surveillance data;
- measurement-error and latent-variable identification;
- MNAR sensitivity analysis and selection models;
- spatial/spatiotemporal state-space models;
- network and interacting-particle state models;
- formal posterior/predictive calibration and prospective external validation;
- model comparison and model averaging under structural uncertainty.

These are implementation targets, not claims of completion.

## Validation policy

No final CI or scientific validation is performed during this implementation cycle. Numerical, statistical and scientific validation is reserved for the final validation phase, after the implementation frontier has been completed.
