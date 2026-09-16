# BLOCKER 03–06 — Scientific Execution Specification

**Status:** SPECIFIED / HANDOFF-READY
**Owner:** ESPÍA (scientific semantics and acceptance criteria)
**Technical realization:** FORJA / CRONOS / CENTINELA / NOTARIO / ORÁCULO / ESTRATEGA / GROK according to mission boundary; INGENIERO for cross-repository implementation
**Scope:** CeutIA + SERPIENTE + NOTARIO
**Date:** 2026-09-16

This document converts BLOCKER-03 through BLOCKER-06 into executable scientific contracts. It does not claim implementation, empirical validity, prospective validity, causal validity, or operational effectiveness.

## 1. BLOCKER-03 — Explicit latent-state theory

### Scientific claim
Observed indicators are measurements of a partially observed system, not the system state itself. SERPIENTE therefore requires an explicit state-estimation contract before any heterogeneous composite state is treated as scientifically meaningful.

### Minimum formal object

A state-space family SHALL be represented conceptually as:

`x[t+1] = f_theta(x[t], u[t], w[t])`

`y[t] ~ h_phi(x[t], o[t], v[t])`

where `x` is latent state, `u` exogenous input/action context as applicable, `y` observations, `o` observation-process state, and `w/v` process and measurement uncertainty.

The architecture MUST preserve the distinction between:

- latent phenomenon/state;
- observation process;
- observed measurement;
- exogenous input/intervention;
- uncertainty;
- inferred state.

### Candidate model ladder

1. Parsimonious linear state-space / Kalman baseline where assumptions are defensible.
2. Irregular or mixed-frequency state-space models when observation timing requires them.
3. Nonlinear filtering / particle methods only where nonlinear structure is evidenced.
4. HMM/regime-switching models where discrete regimes have independently defensible interpretation.
5. Hierarchical/dynamic-factor models where pooling or common latent structure is scientifically justified.
6. Mechanistic state models only when mechanism and parameter identifiability are defensible.

No opaque composite index SHALL be accepted as a latent-state model merely because it aggregates indicators.

### Minimum validation contract

Every candidate latent-state implementation MUST define:

- retained-observation forecasting/reconstruction task;
- simple baseline comparator;
- source-change stability test;
- prior/sensitivity analysis where Bayesian assumptions exist;
- alternative-state falsification test;
- uncertainty intervals/distributions;
- overfit diagnostic;
- identifiability status;
- observation-process assumptions;
- explicit conditions under which the inferred state becomes non-identifiable or uninterpretable.

A state estimate MUST NOT be promoted to a validated latent state merely because it fits observed data.

### Required acceptance tests

- Same phenomenon with altered observation intensity MUST not automatically produce a substantive state change.
- Source replacement with semantically equivalent measurement MUST expose whether the inferred state is invariant within declared tolerance.
- Missingness and asynchronous observations MUST be represented rather than silently interpolated as truth.
- A simpler benchmark MUST remain a required comparator.
- Competing latent-state specifications MUST support rejection/revision/abstention, not only confirmation.

## 2. BLOCKER-04 — Observation-process versus phenomenon change

### Scientific claim
A detected change in observed data is not sufficient evidence of a change in the underlying phenomenon.

At minimum, the system SHALL represent competing explanations:

`H_obs: phenomenon stable, observation process changed`

`H_state: phenomenon changed, observation process sufficiently stable`

with additional hypotheses where warranted, including denominator/population composition change, exogenous shock, intervention, coding/definition change, and joint change.

### Required change-event decomposition

Each material change signal SHALL expose, separately:

1. evidence for change in the measured phenomenon;
2. evidence concerning observation-process stability;
3. denominator/population stability evidence where a denominator exists;
4. source/version/definition/reporting changes;
5. unresolved attribution.

If attribution is not identified, canonical output SHALL be:

> Change observed; attribution to the underlying phenomenon not identified.

### Observation-process dimensions

The contract SHALL cover, when applicable:

- source substitution;
- source availability;
- coverage;
- coding and definition;
- reporting intensity;
- diagnostic/ascertainment intensity;
- reporting delay;
- revision behaviour;
- denominator change;
- sensor/instrument change;
- personnel/capacity change;
- institutional interruption;
- sampling/frame change;
- missingness and selection.

### Required adversarial tests

A change detector MUST be challenged with synthetic or replayable scenarios in which:

- only reporting intensity changes;
- only coverage changes;
- only coding/definition changes;
- only reporting delay changes;
- only denominator changes;
- only source/sensor changes;
- only institutional capacity changes;
- phenomenon and observation process change jointly.

The detector MUST NOT label an observation-process-only perturbation as a confirmed phenomenon change without independent evidence.

## 3. BLOCKER-05 — Intervention-contaminated evaluation

### Scientific claim
Once an alert changes behaviour, the observed outcome is potentially affected by the system itself. Predictive performance and intervention effect therefore become distinct estimands.

The architecture SHALL distinguish, conceptually:

`Y(h | A=0)` from `Y(h | A=1)`

and SHALL never imply that both are observed for the same unit without an explicit valid design.

### Immutable intervention lineage

For every operationally exposed prediction/alert, the auditable lineage SHALL preserve, where applicable:

- original prediction identity and value;
- information cutoff and forecast origin;
- publication/availability timestamp;
- recipient/authority class;
- alert state and threshold;
- action or non-action;
- action timestamp;
- population/unit exposed;
- intervention version;
- outcome definition/version;
- outcome observation time;
- outcome ascertainment/availability time;
- revision history;
- censoring/missingness/selection;
- intervention-related co-interventions;
- adverse or unintended outcomes.

Prediction records MUST be immutable after publication; corrections SHALL create explicit revisions rather than rewriting historical prediction identity.

### Separate evaluation layers

The system SHALL keep separate:

1. predictive discrimination/accuracy;
2. probabilistic calibration and scoring;
3. decision utility;
4. intervention effect;
5. cost and harm;
6. response robustness;
7. distributional/equity effects.

Predictive accuracy SHALL NOT be presented as evidence of intervention effectiveness.

### Minimum contamination tests

- alert causes intervention before outcome;
- no intervention despite eligible alert;
- intervention delayed after alert;
- intervention applied selectively;
- intervention changes future measurements/reporting;
- intervention prevents the target event;
- intervention creates an adverse outcome;
- repeated/overlapping alerts;
- outcome definition changes after intervention;
- post-intervention information enters later forecast features.

Successful prevention MUST remain compatible with a non-event outcome and MUST NOT be automatically classified as a false alarm.

## 4. BLOCKER-06 — Decision loss and alert utility

### Scientific claim
An alert threshold is a decision rule, not merely a model statistic. Its evaluation requires an explicit loss/utility specification appropriate to the decision context.

A generic loss family MAY be represented as:

`L(a,theta) = c_FP I(a=1,theta=0) + c_FN I(a=0,theta=1) + c_action(a) + c_harm(a,theta)`

but costs MUST be treated as declared decision-context inputs, not universal constants.

### Required alert contract

Every operational alert definition SHALL specify:

- decision/problem statement;
- target/event definition and version;
- forecast horizon;
- decision origin/cutoff;
- probability or evidence quantity used;
- threshold/rule;
- false-positive consequences;
- false-negative consequences;
- action cost;
- potential harm;
- authority/recipient;
- reversible versus irreversible action class;
- escalation rule;
- withdrawal/de-escalation rule;
- expiry time;
- abstention/no-alert state;
- uncertainty and identifiability status;
- provenance of cost/utility assumptions.

### Threshold rule

A cost-derived threshold MAY be used only when the decision model and cost assumptions are explicitly specified. The system MUST NOT hard-code the commonly quoted threshold formula as a universal scientific rule.

When costs are unknown, disputed, context-dependent, or non-comparable, the system SHALL preserve that uncertainty and may return an abstention/decision-not-identified state rather than inventing a utility optimum.

### Required alert evaluation

Alert evaluation SHALL report, where estimable:

- proper probabilistic scores;
- calibration;
- decision-curve/net-benefit or another justified utility analysis;
- false-alert burden;
- missed-event burden;
- intervention burden;
- harm/adverse-event burden;
- lead time;
- alert frequency;
- stability under observation-process and denominator drift;
- subgroup/distributional effects where relevant.

AUC, accuracy, F1 or similar discrimination metrics MUST NOT be used as sole evidence that an alert is scientifically useful.

## 5. Cross-blocker dependency graph

`Observation process integrity -> latent-state identifiability -> change attribution -> prediction validity -> decision utility -> intervention evaluation -> learning`

Dynamic denominator/population integrity is an upstream dependency of all rates and any decision quantity derived from them.

PIT provenance is an upstream dependency of latent-state evaluation, forecasting and intervention-effect attribution.

Outcome ascertainment integrity is an upstream dependency of predictive scoring and intervention evaluation.

Decision-loss specification is downstream of prediction semantics and MUST NOT be used to justify a model whose target/outcome is not scientifically identified.

## 6. Capability-state discipline

The following states MUST remain distinct:

`SPECIFIED -> HANDOFF_READY -> IMPLEMENTED -> TESTED -> VERIFIED -> VALIDATED -> PROSPECTIVELY_VALIDATED -> OPERATIONALLY_EFFECTIVE`

This specification establishes only `SPECIFIED/HANDOFF_READY` for the requirements in this document unless implementation evidence exists elsewhere and is independently verified.

## 7. Cross-mission handoff acceptance criteria

FORJA/INGENIERO: implement executable contracts and regression tests without collapsing latent state, observation process, intervention or utility into one score.

CRONOS: implement temporal identity, origin-based replay and dynamic/state estimation semantics without retrospective leakage.

CENTINELA: implement change attribution with explicit observation-process alternatives and fail-closed attribution when separation is not identifiable.

ORÁCULO/ESTRATEGA: implement decision/utility semantics only after target, outcome, PIT and intervention lineage are established.

NOTARIO: persist scientific consequences, competing explanations, falsification results and candidate work without optimizing task count or closure count.

GROK: adversarially challenge the full chain, especially prevention-as-false-alarm, sensor drift, denominator drift, intervention contamination, utility assumptions and post-intervention leakage.

## 8. Fixed-point condition for BLOCKER-03–06

These blockers are not closed when classes, schemas or tests merely exist. Closure requires executable implementation where authorized, adversarial regression coverage, empirical/retrospective validation where appropriate, prospective validation where claimed, and explicit evidence for each promoted capability state.

No blocker may be marked ESTABLISHED solely because its mathematical formulation or documentation exists.
