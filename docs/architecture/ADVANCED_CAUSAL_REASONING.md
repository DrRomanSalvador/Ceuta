# Advanced causal reasoning in CeutIA

CeutIA treats causal reasoning as a gated inference layer between observation and decision. Association, temporal precedence, causal plausibility, identification, intervention and prospective validation are distinct epistemic states.

## Implemented capabilities

- longitudinal temporal precedence and lag representation;
- explicit confounding and adjustment status;
- collider warnings;
- interaction and effect-modification candidates;
- heterogeneous effects by subgroup and regime;
- preservation of competing causal models and structural disagreement;
- explicit counterfactual identification gate;
- cross-domain causal links;
- regime-dependent effects;
- lagged feedback, tipping thresholds and hysteresis representation;
- assumption stress-testing and falsification challenges;
- active causal learning ranked by expected information gain, feasibility and cost;
- prospective intervention/outcome validation.

## Epistemic rule

No component in this layer is allowed to infer causality from association alone. Temporal precedence is necessary for many causal claims but is not sufficient. Identification requires a defensible causal structure and explicit assumptions. Counterfactual and intervention claims require identification. Prospective validation is a separate terminal state and cannot be inferred from retrospective fit.

## Scientific boundary

The implementation supplies auditable contracts and conservative gates. It does not pretend that a deterministic software function can establish causal identification without data, design, domain assumptions and appropriate statistical estimation. Numerical causal estimators, when introduced, must declare their estimand, identification strategy, assumptions, uncertainty, missing-data handling, positivity/consistency requirements, sensitivity analysis and prospective validation protocol.

## Closed loop

Observation -> temporal structure -> candidate mechanisms -> confounding/collider analysis -> competing causal models -> identification -> falsification -> effect estimation -> heterogeneous/regime analysis -> counterfactual/intervention -> decision -> observed outcome -> prospective validation -> model update.

Any unresolved gate remains visible and propagates uncertainty instead of being silently converted into a stronger claim.
