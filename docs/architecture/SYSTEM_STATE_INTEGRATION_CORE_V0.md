# CeutIA — Integrated Dynamic System Core v0

Status: ARCHITECTURAL PRESERVATION CHECKPOINT

This document records a design decision that must not be lost during subsequent implementation. The recent trajectory, longitudinal estimation and dynamics work is useful only if these capabilities converge on a coherent representation of a complex system. CeutIA must therefore prioritize integration before accumulating further isolated analytical modules.

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

## 6. General-purpose dynamic primitives to preserve

The architecture should retain the following generic concepts because they are applicable across domains:

- functional/system reserve: available capacity relative to current load and perturbation;
- displacement after perturbation;
- recovery speed and recovery capacity;
- deviation from baseline;
- trajectory velocity and acceleration/deceleration;
- early-warning indicators based on changes in variance, autocorrelation, recovery behaviour or regime structure where scientifically justified;
- dynamic dependency strength and direction;
- feedback amplification and damping;
- cross-scale coupling;
- heterogeneity between entities or subsystems;
- perturbation → response → adaptation;
- system memory and path dependence;
- nonlinear interaction effects;
- state-conditioned counterfactual reasoning;
- intervention-as-experiment semantics;
- mechanism discrimination;
- prospective falsifiable predictions;
- failed-hypothesis and negative-result memory.

These are generic complex-systems primitives. They must not be converted into clinical-only abstractions or populated with OMNI-NET-specific health variables.

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
6. only then add further analytical capabilities where a demonstrated architectural gap remains.

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
