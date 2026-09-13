# CeutIA Causal Inference Governance

## Purpose

CeutIA must never convert an association into a causal claim merely because variables co-vary, correlate, or occur in temporal sequence. Causal claims require an explicit hypothesis, graph semantics, identification assumptions, falsification tests, and causal evidence.

## Epistemic ladder

`observed -> associational -> temporally compatible -> causally plausible -> causally identified -> intervenable -> prospectively validated`

Advancing between levels is gated. No automatic promotion from correlation to causality is permitted.

## Required causal representation

A causal hypothesis explicitly declares exposure, outcome, estimand, candidate confounders, mediators, moderators, negative controls, and assumptions. The graph is directed and acyclic within a time slice; feedback is represented through explicit temporal lags rather than instantaneous cycles.

## Identification gate

A causal claim is blocked when candidate backdoor paths remain unaddressed, assumptions are absent, negative controls are absent, or no directed exposure-to-outcome path exists. The system records the blocker rather than silently resolving it.

## Intervention semantics

`P(Y | X)` is observational. `P(Y | do(X))` is interventional. Decision logic may not substitute the former for the latter. Counterfactual decision queries therefore require an explicit `do` intervention and a causal model reference.

## Falsification

Negative controls and adversarial tests are first-class evidence. Missing tests remain unresolved; failed tests remain visible and prevent silent causal promotion.

## Interactions

CeutIA must preserve candidate interaction terms rather than reducing the system to independent pairwise effects. Interaction, mediation, moderation, nonlinear thresholds, temporal lags and feedback require explicit hypotheses and validation.

## Decision consequence

Only causal assessments satisfying their identification and evidence gates may authorize a causal intervention claim. Otherwise the result remains associational or uncertain and must be governed accordingly.

## Scientific limitation

These contracts establish epistemic and software guardrails; they do not by themselves prove that an observational dataset identifies a causal effect. Empirical identification remains dependent on the data-generating process, measurement quality, design, assumptions and prospective validation.
