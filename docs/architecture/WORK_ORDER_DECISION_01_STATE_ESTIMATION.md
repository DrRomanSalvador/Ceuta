# Decision-system work order 01 — Full state estimation

## Objective
Turn the existing estimation primitives into an executable, domain-neutral latent-state engine used by the unified system kernel.

## Required implementation
- Integrate multivariate state-space estimation into `SystemContext` and the closed loop; do not leave estimators as standalone APIs.
- Support linear/nonlinear and Gaussian/non-Gaussian regimes through explicit model selection.
- Add smoothing, irregular sampling, delayed observations, correlated measurement error, missing channels and observation-process changes.
- Add switching/regime models, time-varying parameters and explicit delay/nowcasting models.
- Add hierarchical and spatial/spatiotemporal state estimation where the problem specification requires them.
- Separate measurement, process, parameter and structural uncertainty and propagate them downstream.
- Add diagnostics for identifiability, observability, covariance conditioning, innovation behaviour, residual dependence and model misspecification.
- Permit explicit abstention when the observation model, covariance structure or identifiability is inadequate.
- Preserve complete temporal/provenance lineage for every state estimate.

## Acceptance criteria
The kernel must be able to consume observations and produce a timestamped latent state with covariance/uncertainty, diagnostics, method identity, assumptions and provenance, and downstream stages must consume that state rather than merely storing references to an estimator.

No clinical or domain-specific assumptions may be introduced.
