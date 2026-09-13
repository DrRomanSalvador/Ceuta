# Decision-system work order 02 — Causal inference

## Objective
Replace the current causal boundary/scaffold with an identification-first causal engine that can support defensible intervention decisions.

## Required implementation
- Explicit estimands, target populations, treatment strategies, time zero and follow-up windows.
- Identification checks for consistency/SUTVA, positivity, exchangeability and interference.
- Time-varying confounding and marginal structural models where required.
- Longitudinal/clustered causal estimators, mediation, dose-response and heterogeneous treatment effects where identifiable.
- Quantitative sensitivity analysis for unmeasured confounding, selection and measurement error.
- Negative controls and falsification tests where appropriate.
- Explicit distinction between observational association, predictive attribution and causal effect.
- Transportability/generalizability and external-validity assessment.
- Uncertainty propagation from state estimation and observation processes into causal estimates.
- Automatic abstention when identification conditions fail.

## Acceptance criteria
No causal claim may reach the decision layer unless the estimand is explicit, identification status is machine-readable, assumptions are recorded, diagnostics/sensitivity are attached and the remaining uncertainty is propagated.
