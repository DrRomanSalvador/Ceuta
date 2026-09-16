# SCIENTIFIC CAPABILITY GATES

## Purpose

This document defines the scientific gates that must precede advanced predictive, simulation, alerting, policy-recommendation, and closed-loop capabilities in CeutIA/SERPIENTE.

It is an engineering-facing specification of scientific prerequisites. Implementation is not validation. A passing software test proves execution of a control; it does not prove scientific validity, calibration, causal identification, external validity, or operational utility.

## 1. Foundational dependency chain

```text
PHENOMENON DEFINITION
        ↓
MEASUREMENT MODEL + PROVENANCE
        ↓
VINTAGES + DELAYS + REVISIONS
        ↓
QUALITY + MISSINGNESS + DYNAMIC DENOMINATORS
        ↓
LATENT-STATE ESTIMATION
        ↓
TEMPORAL DYNAMICS + REGIME
        ↓
INTERACTIONS + PROPAGATION
        ↓
CALIBRATED PROBABILISTIC FORECAST
        ↓
LOSS FUNCTION + DECISION RULE
        ↓
REGISTERED INTERVENTION
        ↓
PROSPECTIVE OUTCOME
        ↓
CAUSAL / UTILITY EVALUATION
        ↓
MODEL + ONTOLOGY REVISION
```

No downstream scientific capability may be treated as validated merely because an upstream software component exists.

## 2. Point-in-time / vintage integrity gate

Every time-varying datum must distinguish, where applicable:

- phenomenon/event time;
- observation/measurement time;
- publication/release time;
- revision time;
- first time the system could have known the value;
- vintage identifier or equivalent reconstruction key.

Historical evaluation must reconstruct the information set that was actually available at the prediction time. Retrospectively revised values must not silently enter earlier prediction windows.

Required tests:

- point-in-time reconstruction;
- revision replay;
- delayed-publication simulation;
- future-information leakage detection;
- historical-vintage reproducibility.

Exit criterion: a historical prediction can be reproduced from the information set available at that historical decision time.

## 3. Observation-process gate

The observation mechanism is a first-class object. The system must distinguish changes in the underlying phenomenon from changes in detection, reporting, coverage, sensitivity, administrative process, or revision behaviour.

Conceptual model:

```text
latent phenomenon/state → observation mechanism → recorded data
```

Where justified, a joint state/observation formulation may be used:

p(S₁:T, O₁:T | Y₁:T) ∝ p(S₁) ∏ₜ p(Sₜ₊₁ | Sₜ) p(Oₜ₊₁ | Oₜ, Sₜ) p(Yₜ | Sₜ, Oₜ)

This formulation is not itself evidence of identifiability. Identifiability limitations must be recorded explicitly.

Required tests:

- injected false-change tests;
- known administrative-change periods;
- source-to-source comparison;
- coverage/sensitivity perturbation tests;
- delayed-reporting tests;
- missingness mechanism analysis.

Failure mode to block: allowing a latent state to absorb arbitrary unexplained changes.

## 4. Dynamic denominator gate

Rates and burdens must use denominators that correspond to the relevant population and observation process.

The system must represent, where relevant:

- target population;
- exposed population;
- population covered by observation;
- temporal denominator changes;
- geographic denominator changes;
- subgroup denominators.

Static denominators must not be used silently when the denominator changes materially over time.

Exit criterion: every rate-like quantity has an explicit numerator, denominator, population definition, time window, coverage definition, and known limitations.

## 5. Latent-state gate

A latent state may be introduced only with an explicit definition of:

- the unobserved quantity being estimated;
- observations that inform it;
- model assumptions;
- identifiability conditions;
- uncertainty;
- alternative explanations;
- falsification tests.

The latent state must not become an unconstrained explanatory variable capable of accounting for any observed result.

## 6. Baseline-before-advanced-ML gate

Advanced machine learning, including deep learning, is blocked as a primary model when:

- the series are short;
- event counts are low;
- substantial drift exists;
- revisions are material;
- interpretability is necessary;
- a defensible baseline has not yet been defeated.

Required baseline family should be selected according to outcome and data-generating context and may include:

- persistence;
- climatology;
- moving averages;
- seasonal models;
- appropriate statistical models;
- null models.

Comparison must use temporally appropriate evaluation such as rolling-origin or blocked evaluation. Advanced ML requires demonstrated incremental value without unacceptable calibration degradation or traceability loss.

## 7. Interaction and complexity gate

Interactions must not be accepted merely because a flexible model can represent them.

Required controls include, where appropriate:

- preregistered/pre-specified interactions;
- permutation tests;
- ablation;
- null models;
- regime-stratified analysis;
- complexity limits;
- replication out of sample.

Exit criterion: an interaction is reproducible and materially useful outside the fitting sample under the declared evaluation protocol.

## 8. Multisystem integration gate

Health, mobility, climate, economic, service, border, and social systems may be integrated only with explicit handling of incompatible temporal/spatial scales and uncertainty.

Required representation:

- subsystem boundaries;
- temporal scales;
- spatial scales;
- reconciliation rules;
- exposed population;
- coupling mechanisms;
- uncertainty interfaces;
- incompatibilities and unresolved assumptions.

Exit criterion: integration does not materially degrade calibration, provenance, or traceability relative to the constituent models under the declared evaluation protocol.

## 9. Forecasting gate

Forecasts intended for scientific or operational use must be probabilistic where the outcome permits, not only point estimates.

Required evaluation may include:

- rolling-origin evaluation;
- blocked temporal test sets;
- calibration assessment;
- Brier score for suitable binary/probability outcomes;
- log score for suitable probabilistic forecasts;
- CRPS for suitable continuous probabilistic forecasts;
- interval/coverage assessment;
- subgroup performance and calibration;
- drift monitoring.

Metrics must be matched to the outcome and decision context. A single aggregate score is insufficient evidence of a valid forecasting system.

## 10. Alert gate

Automated alerts must not be deployed publicly before the alerting problem itself is validated.

Required controls:

- explicit loss function;
- false-positive cost;
- false-negative cost;
- persistence/minimum duration where appropriate;
- escalation policy;
- expiry;
- source/sensor change detection;
- acceptable false-alert burden;
- operational response capacity;
- governance and ownership;
- appeal/correction mechanism;
- anti-stigmatisation safeguards;
- simulation/drill evidence.

Alert thresholds are decision parameters, not merely statistical significance thresholds.

## 11. Decision and policy gate

The system must not autonomously recommend irreversible or coercive interventions solely from correlations, scores, or unvalidated predictive signals.

Any decision coupling must expose:

- signal identity;
- decision identity;
- responsible authority/actor;
- action identity;
- cost;
- constraints;
- reversible alternatives;
- option of no action;
- value-of-information considerations where relevant;
- human decision record.

The software may record an explicitly identified decision/action; it must not invent a decision producer or infer that an intervention occurred merely because a recommendation was generated.

## 12. Digital-twin gate

A territorial digital twin is blocked until the system has:

- a measurement model;
- identifiable states;
- calibrated parameters;
- plausible scenario definitions;
- validation against relevant outcomes;
- sensitivity analysis.

A simulation that produces plausible-looking trajectories is not, by itself, evidence of a valid digital twin.

## 13. Outcome and prospective-evaluation gate

Outcomes must be specified before the relevant intervention/evaluation window whenever the design requires prospective protection against hindsight bias.

The specification must include:

- outcome definition;
- population;
- time horizon;
- measurement method;
- comparison strategy;
- missing/outcome censoring rules;
- prospective lock where appropriate.

Prediction correctness must remain distinct from intervention utility. A correct forecast does not demonstrate that an intervention improved an outcome.

## 14. Causal / utility gate

Causal effectiveness and operational utility are separate claims from predictive accuracy.

Required evidence should distinguish, as applicable:

- association;
- prediction;
- causal effect;
- intervention effect;
- operational utility;
- harm.

No causal-effectiveness claim may be promoted solely because a predictive association is strong.

## 15. Closed-loop gate

A closed loop is defined as:

```text
INTERVENTION → OUTCOME → EVALUATION → UPDATE
```

The loop must preserve:

- intervention identity;
- responsible authority;
- timing;
- affected population;
- outcome definition;
- comparison information;
- audit of benefit and harm;
- model drift review;
- ontology review;
- model retirement capability;
- change governance;
- use restrictions.

The system must not attribute an observed outcome to its intervention without an identification strategy adequate to the claim being made.

## 16. Scientific debt register

The following are explicit debt classes:

1. documented capability without independent validation → overclaim risk;
2. official sources treated as unbiased measurements → false-trend risk;
3. incomplete vintages → leakage risk;
4. static denominators → rate-interpretation risk;
5. undefined latent states → narrative mathematics;
6. unidentified interactions → spurious complexity;
7. causal separation by naming only → indefensible recommendations;
8. non-prospectively locked outcomes → contaminated evaluation;
9. no alert loss function → arbitrary thresholds;
10. no human decision record → unassessable utility;
11. no geographic validation → territorial overfit;
12. no subgroup evaluation → unequal error/harm;
13. no model-retirement protocol → persistence of failed models;
14. no use limits → institutional misuse;
15. model evidence confused with system evidence → technological overclaim.

## 17. Scientific roadmap and exit gates

### Phase A — Foundations

Deliverables:

- assertion-level ontology;
- source catalogue;
- provenance;
- multiple timestamps;
- revision policy;
- missingness taxonomy;
- denominators;
- baselines;
- assumption registry;
- claim/evidence matrix.

Exit: every datum has origin, knowledge time, definition, coverage, and limitations.

### Phase B — Dynamic system

Deliverables:

- observation model;
- latent state;
- filters/estimators where justified;
- delays;
- regime changes;
- propagated uncertainty.

Exit: improvement over baselines without unacceptable loss of calibration or traceability.

### Phase C — Interaction

Deliverables:

- prespecified interactions;
- permutation tests;
- ablation;
- null models;
- regime analysis;
- complexity limits.

Exit: interaction replicated and useful out of sample.

### Phase D — Multisystem

Deliverables:

- explicit subsystem scales;
- temporal/spatial reconciliation;
- uncertainty interfaces;
- exposed population;
- coupling mechanisms.

Exit: integration does not degrade calibration or traceability under the declared protocol.

### Phase E — Prediction

Deliverables:

- rolling-origin evaluation;
- blocked tests;
- calibration;
- appropriate proper scoring rules;
- transparent ensembles;
- subgroup coverage/calibration.

Exit: predictive performance is prospectively defensible and calibrated under the locked evaluation design.

### Phase F — Alert

Deliverables:

- loss function;
- decision-dependent thresholds;
- persistence;
- escalation;
- expiry;
- source/sensor change detection;
- false-alert burden assessment.

Exit: alert performance and operational burden are acceptable for the declared use case and governance exists.

### Phase G — Decision

Deliverables:

- action menu;
- authority;
- costs;
- constraints;
- no-action option;
- value of information;
- utility evaluation.

Exit: decisions are explicit, attributable, bounded, and evaluated rather than inferred from scores.

### Phase H — Closed loop

Deliverables:

- intervention registry;
- outcomes;
- comparison strategy;
- harm audit;
- model review;
- ontology review;
- drift control;
- change governance;
- retirement protocol;
- use limits.

Exit: the system can learn from prospective outcomes without claiming unidentifiable causal success.

## 18. High-value discovery: observation as a first-class scientific object

Core question:

> Does an observed change belong to the phenomenon, or to the observation system?

This is a foundational blocker for CeutIA/SERPIENTE because surveillance and administrative data are conditioned by detection, reporting, coverage, revisions, and denominators.

The implementation priority is therefore not “add a more powerful model”, but “make the information-generating process explicit enough to test whether the observed signal is real”.

## 19. Engineering translation

The following capabilities should be represented as executable requirements when implemented:

- point-in-time/vintage integrity;
- observation-process representation;
- dynamic denominators;
- latent-state definitions and identifiability metadata;
- baseline registry and baseline-vs-advanced-model comparisons;
- interaction test registry;
- probabilistic forecast evaluation;
- alert loss and operational burden registry;
- explicit signal→decision→intervention lineage;
- prospective outcome registry;
- causal/utility evidence separation;
- closed-loop update and retirement controls;
- scientific debt tracking;
- use-limit and governance metadata.

## 20. Non-equivalence rules

The following equivalences are prohibited:

```text
implemented ≠ scientifically validated
passing tests ≠ calibrated
prediction accuracy ≠ causal effect
forecast correctness ≠ intervention utility
official source ≠ unbiased measurement
correlation ≠ mechanism
plausible simulation ≠ validated digital twin
model evidence ≠ system evidence
alert generation ≠ operational usefulness
recommendation generated ≠ decision made
```

These rules are part of the scientific boundary and must remain visible in engineering, validation, and audit artifacts.
