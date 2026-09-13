# CeutIA — Integrated Dynamic System Core v0

Status: ARCHITECTURAL PRESERVATION CHECKPOINT

This document records design decisions and robustness primitives that must not be lost during subsequent implementation. The recent trajectory, longitudinal estimation and dynamics work is useful only if these capabilities converge on a coherent representation of a complex system. CeutIA must therefore prioritize integration before accumulating further isolated analytical modules.

## 1. Architectural decision

CeutIA must not evolve into a collection of independently sophisticated modules connected by data pipes.

The central computational abstraction must represent the evolving state of a system through time, together with its evidence, uncertainty, lineage, dynamics and explanatory hypotheses.

The existing `SystemStateContract` remains the canonical state contract. New layers must wrap, enrich or extend that contract deliberately rather than introduce competing canonical state objects.

## 2. Integrated scientific cycle

The core lifecycle is:

Observation → State → Trajectory → Dynamics → Hypothesis → Causality → Prediction → Intervention → Response → Learning → new State

Each transition must preserve an auditable relationship to the preceding representation. No stage may silently promote epistemic status.

In particular:

- observation is not inference;
- inference is not causal explanation;
- causal explanation is not prediction;
- prediction is not recommendation;
- recommendation is not intervention;
- intervention is not automatically evidence of causality;
- model output is not independent evidence;
- learning from an intervention outcome must preserve temporal and causal evaluation boundaries.

## 3. Required integrated context

The next architectural core should provide a system-level context/aggregate containing, directly or by stable references:

1. Canonical current system state.
2. Historical state trajectory.
3. State lineage and provenance.
4. Observation/evidence references and temporal windows.
5. Latent-state estimates with explicit uncertainty.
6. State transitions and dynamic descriptors.
7. Perturbation and recovery episodes where applicable.
8. Active dependencies, interactions and feedback references.
9. Competing hypotheses and their epistemic status.
10. References to causal models and their assumptions.
11. Forecasts/scenarios and their validity windows.
12. Candidate interventions and intervention status.
13. Response/outcome observations after intervention.
14. Learning/update records.
15. Contradictions, missing evidence and unresolved uncertainty.
16. Scale, regime and contextual metadata.
17. System capacity, load, reserve and bottleneck references.
18. Active shocks, perturbations and propagation paths.
19. Regime-transition and early-warning state.
20. Model disagreement and unresolved alternative scenarios.

The aggregate is a coordination and provenance boundary, not a requirement that every analytical model be implemented inside one class.

## 4. What the recent work contributes

The recent implementation should be retained because it supplies primitives required by the integrated core:

- trajectory representation provides longitudinal state continuity;
- lineage and uncertainty make state evolution auditable;
- longitudinal state estimation introduces an explicit latent-state layer rather than treating raw observations as the state itself;
- trajectory dynamics provide rates of change and recovery descriptors;
- the existing canonical pipeline contracts provide the system-state substrate.

These primitives should now be connected rather than multiplied.

## 5. Integration requirements

Before adding another isolated state/dynamics feature, implementation should establish explicit mappings among:

`ObservationRecord` → `SystemStateContract` → `StateSnapshot`/trajectory → `StateEstimate` → dynamic transition metrics → hypotheses/causal references → forecasts/decisions → intervention outcomes.

The mapping must preserve:

- identity of the underlying system and variables;
- event time and observation window;
- source/evidence provenance;
- uncertainty and confidence semantics;
- missingness and contradiction status;
- scale and regime context;
- transformation history;
- epistemic status;
- intervention status;
- lineage back to the original observations.

No duplicate representation should become canonical merely because a new module needs a convenient local structure.

## 6. Robustness primitives that must be preserved

The following blocks are not optional conceptual decoration. They are the mechanisms that prevent CeutIA from becoming a static prediction engine or a collection of brittle scores.

### 6.1 Reserve, capacity and load

The system should be able to distinguish current state from remaining functional capacity. Where scientifically meaningful, represent reserve as a relationship among capacity, current load, perturbation and recovery demand.

Reserve is contextual and dynamic. It must not become an arbitrary universal scalar.

### 6.2 Perturbation → response → recovery → adaptation

A perturbation should be represented separately from the response it produces. The system should retain displacement, recovery trajectory, recovery rate/capacity and the subsequent state rather than reducing the event to a binary success/failure label.

### 6.3 Baseline and deviation

Absolute values are insufficient in heterogeneous systems. CeutIA should support reference states that are conditional on entity, context, regime, scale and time, allowing meaningful deviation-from-baseline reasoning without assuming that a population average is a universal normal state.

### 6.4 Early warning and distance to transition

Potential loss of resilience can manifest through altered variance, autocorrelation, recovery time, distributional structure or other regime-sensitive indicators. These should be treated as evidence about changing dynamics, not proof that a transition will occur.

False positives, confounding perturbations and changes in observation processes must remain explicit.

### 6.5 Regimes, thresholds and transitions

The same perturbation may produce different outcomes in different regimes. CeutIA should therefore represent regime membership or uncertainty about regime, transition candidates, thresholds and hysteresis where justified.

A threshold must retain its empirical/model basis, uncertainty and validity domain. It must never become a hard-coded truth merely because a number exists.

### 6.6 Hysteresis, memory and path dependence

Current state can depend on the route by which the system arrived there. The architecture should preserve historical exposure, prior interventions, prior perturbations and memory effects where they materially influence future response.

### 6.7 Multistability and alternative attractors

A system may have multiple stable or metastable configurations. CeutIA must be able to represent competing plausible regimes rather than forcing every trajectory toward a single expected equilibrium.

### 6.8 Nonlinearity and interaction effects

Effects may depend on combinations of variables rather than isolated marginal effects. Interaction terms, thresholds, saturation, amplification and damping should be representable without assuming that every observed interaction is causal.

### 6.9 Dynamic networks and feedback

Dependencies should be represented as changing relationships, including direction, strength, delays and feedback loops. Static graphs are insufficient for systems whose topology or interaction strength changes over time.

### 6.10 Cross-scale coupling

Micro-, meso- and macro-scale processes can interact. The architecture should retain scale metadata and allow propagation across scales without assuming that a relationship observed at one scale transfers automatically to another.

### 6.11 Heterogeneity and effect modification

Different entities, populations, locations or regimes can respond differently to the same perturbation or intervention. Aggregate effects must not erase relevant heterogeneity.

### 6.12 Bottlenecks, queues and constrained flows

Capacity constraints can produce nonlinear system behaviour even when individual components remain functional. Queues, arrival rates, service capacity, bottlenecks and flow dependencies should therefore be representable where relevant.

### 6.13 Cascades and propagation

A local perturbation may propagate through coupled dependencies and produce system-level consequences. CeutIA should preserve propagation paths and intermediate states rather than attributing the final outcome directly to the initial perturbation.

### 6.14 Exogenous versus endogenous shocks

A change can originate outside the system or emerge from the system's own feedback. This distinction matters for attribution, intervention and forecasting and must remain explicit.

### 6.15 Mechanism discrimination

When multiple mechanisms can explain the same observed trajectory, the system should identify observations or interventions capable of discriminating among them. It should not collapse competing hypotheses simply because one currently has the highest score.

### 6.16 Counterfactuals conditioned on state

Counterfactual reasoning should be conditioned on the state, context, regime and assumptions under which the counterfactual is meaningful. Counterfactual outputs must retain their assumptions and uncertainty.

### 6.17 Intervention as an experiment

An intervention changes the system. It therefore needs its own representation: target, timing, dose/intensity where relevant, scope, implementation fidelity, concurrent interventions and post-intervention response.

### 6.18 Prospective falsification

Important hypotheses should generate predictions that could prove them wrong. CeutIA should preserve those predictions, expected observations, time horizon and falsification status.

### 6.19 Negative-result and failed-hypothesis memory

The system must remember hypotheses that failed, predictions that were wrong and interventions that did not produce the expected response. Otherwise learning can repeatedly rediscover the same false explanation.

### 6.20 Contradiction preservation

Contradictory observations or sources must not be silently averaged away. Contradiction itself can be an informative state of the evidence system and may indicate measurement problems, regime differences, source dependence or adversarial manipulation.

### 6.21 Missingness as information

Missing data should retain its mechanism where knowable: MCAR, MAR, MNAR or unknown. Missingness caused by system failure, selection, censorship or behavioural adaptation can itself carry information.

### 6.22 Measurement and selection processes

Observed data are generated by measurement and selection mechanisms. Sensor error, sampling bias, survivorship, collider structures, reporting changes and temporal leakage must remain distinguishable from changes in the underlying system.

### 6.23 Source dependency and evidence contamination

Multiple apparently independent observations may derive from the same underlying source. Provenance should permit dependency detection and prevent duplicated evidence from being mistaken for independent confirmation.

### 6.24 Distribution shift and model validity

Every forecast or model-dependent inference should have a validity context. Changes in population, regime, data-generating process or intervention environment can invalidate historical performance.

### 6.25 Calibration and uncertainty coverage

A probabilistic output is useful only if its uncertainty has empirical meaning. Forecast calibration, coverage, drift and failure under distribution shift must be treated as first-class properties.

### 6.26 Rare events and tail risk

Mean behaviour is often insufficient for complex systems. Where justified, CeutIA should represent tail probabilities, extreme outcomes and asymmetric loss without turning speculative tail estimates into facts.

### 6.27 Model disagreement

Disagreement among models can be more informative than an artificial consensus. Competing models, assumptions and forecasts should remain distinguishable and their disagreement should be available to downstream decision logic.

### 6.28 Active sensing and value of information

The system should be able to identify observations or measurements that would materially reduce decision-relevant uncertainty. Information acquisition should be treated separately from intervention and its value should be decision-context dependent.

### 6.29 Robust decisions under deep uncertainty

When probabilities are poorly identified, decisions should not depend exclusively on a single best model. Robustness, regret, worst-case consequences, opportunity cost and sensitivity to alternative models should be representable.

### 6.30 Abstention and human review

The system must have a principled ability to say that evidence is insufficient, models disagree materially or assumptions are violated. Abstention is a valid output, not a failure of the system.

### 6.31 Adversarial and information robustness

The evidence layer should be able to represent suspected manipulation, coordinated information effects, source contamination, perception-versus-event discrepancies and adversarial hypotheses without automatically declaring an operation or actor responsible.

### 6.32 Intervention-response feedback without self-contamination

When model recommendations influence the system, subsequent observations are partly consequences of the model itself. Learning loops must therefore distinguish observational outcomes from model-induced outcomes and prevent uncontrolled self-reinforcement.

### 6.33 Reversibility and degradation

The architecture should represent whether an intervention or transition is reversible, partially reversible or associated with hysteresis/path dependence. This is essential for prioritising early action when recovery capacity may decline after a threshold.

## 7. Scientific safeguards for the integration layer

The integrated representation must preserve uncertainty instead of collapsing it prematurely.

Competing explanations must remain representable simultaneously.

A dynamic association must not be promoted to a causal relationship merely because it occurs in the same trajectory.

A forecast must retain its model, horizon, calibration status and validity window.

An intervention outcome must retain the intervention context and cannot be treated as an ordinary observational data point without qualification.

Weak signals may contribute to an early-warning state but cannot by themselves establish a transition, causal mechanism or threat.

Thresholds, reserve estimates and recovery metrics must expose their assumptions and measurement basis.

## 8. Implementation priority

The next implementation phase should therefore be:

1. inspect and reuse the existing state/pipeline architecture;
2. define the smallest coherent integration context around the canonical `SystemStateContract`;
3. connect trajectory, estimation and dynamics to that context;
4. expose provenance, uncertainty, contradictions and epistemic status through the same boundary;
5. provide stable hand-off points to causal, forecasting and decision layers;
6. incorporate the robustness primitives above as explicit state/evidence semantics rather than disconnected scores;
7. only then add further analytical capabilities where a demonstrated architectural gap remains.

The objective is not to make one large class. The objective is to create one coherent state-and-evidence spine through which the existing and future analytical modules operate.

## 9. Explicit non-goals

This checkpoint does not authorize:

- importing OMNI-NET's clinical node taxonomy into CeutIA;
- treating the current scalar Kalman filter as a general solution to latent-state estimation;
- treating current recovery metrics as causal or predictive models;
- declaring the causal layer scientifically complete;
- declaring forecasting calibrated merely because a distribution-shaped object exists;
- declaring a digital twin complete merely because a transition function can be iterated;
- running final CI or scientific validation before the implementation cycle is complete.

## 10. Definition of architectural success

The integration is successful when CeutIA can represent a changing complex system as a coherent, time-indexed object of evidence and inference rather than as disconnected outputs from separate modules.

A subsystem should be able to consume the current state and its trajectory, understand the uncertainty and provenance attached to that state, contribute an inference without overwriting competing explanations, and return its result with sufficient lineage for downstream causal, predictive and decision reasoning.

This is the required bridge between the existing modules and the intended CeutIA architecture.
