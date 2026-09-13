# CeutIA — Repository Gap Audit V2

Status: BOUNDED AUDIT CHECKPOINT — FAMILIES F–O
Base commit audited: f52b932685af6622786d2394a63c24ae0768635b

This document extends V1. It records implementation evidence for forecasting, decisions, adversarial/epistemic robustness, spatial/human systems, OMNI-NET clinical interface, simulation, learning, governance and validation.

## F. Forecasting and anticipation

F1 Probabilistic forecasts — **partially implemented**. `ForecastDistribution` exists, but it constructs a normal-style interval around a sample mean rather than a validated forecast distribution.

F2 Distributional forecasts — **scientifically insufficient**. The existing distribution object is not a general predictive distribution and its interval is a confidence interval for a mean, not a calibrated predictive interval.

F3 Multi-horizon forecasting — **absent** as a formal horizon-aware forecasting engine.

F4 Scenario generation — **scaffold** via scenario contracts/engine.

F5 Competing scenarios — **scaffold**; scenario structures exist but no evidence of probabilistically coherent competing scenario generation.

F6 Ensemble models — **scaffold / partial**. `MultimodelForecaster` aggregates model point predictions.

F7 Model disagreement — **partially implemented**. Mean absolute disagreement is preserved, but structural/distributional disagreement is not represented adequately.

F8 Calibration — **scaffold**. Calibration modules exist, but no proper probabilistic calibration framework is demonstrated.

F9 Calibration drift — **scaffold**. Current error minus baseline error is tracked; this is not a statistical calibration-drift detector.

F10 Distribution shift — **absent / scientifically insufficient**.

F11 Conformal/equivalent coverage — **absent**.

F12 Forecast validity windows — **scaffold**. Contracts can carry temporal validity but no demonstrated empirical validity-window estimator.

F13 Triggered reforecasting — **absent** as a complete event-driven mechanism.

F14 Rare-event forecasting — **absent**.

F15 Tail-risk estimation — **absent**.

F16 Forecasting under missing/manipulated observations — **absent**.

F17 Endogenous/exogenous driver decomposition — **absent**.

F18 Prospective temporally separated backtesting — **partially implemented** through prospective outcome recording, but not a full forecasting evaluation harness.

**Family F verdict: SCAFFOLD / SCIENTIFICALLY INSUFFICIENT.** The repository has forecast-shaped APIs, not a validated anticipation engine.

## G. Decision intelligence

G1 Formal decision context — **existing real at contract level**. `DecisionContext` captures identity, decision maker, horizon, objectives, constraints and assumptions.

G2 Action space — **existing real at contract level** through `DecisionOption`.

G3 Objectives/utility — **existing real** for supplied utilities.

G4 Constraints/resource budgets — **partially implemented**. Resource cost exists, but hard constraints are not generally solved as a constrained optimisation problem.

G5 Multi-objective/Pareto — **absent**.

G6 Risk-sensitive utility — **partially implemented** through harm/uncertainty modes.

G7 Regret minimisation — **existing real only for supplied regret values**; regret is not derived from a complete decision-theoretic reference set.

G8 Robust decision making — **partially implemented** using worst-case supplied utility.

G9 Value of information — **incorrect/incomplete in the current implementation**: `DecisionRecommendation.value_of_information` is always emitted as `0.0`; the system ranks `InformationRequest` by supplied net value but does not compute VoI from alternative information states.

G10 Active sensing — **absent**.

G11 Decision-specific causal identification — **scaffold** through causal governance, not an integrated estimator.

G12 Counterfactual policy comparison — **scaffold**.

G13 Policy simulation — **scaffold** via generic simulation, not policy-specific causal simulation.

G14 Decision abstention — **existing real at contract level**.

G15 Human review gates — **existing real at contract level**.

G16 Prohibited autonomous interventions — **partially implemented**; governance explicitly disables autonomous intervention by default.

G17 Re-evaluation triggers — **existing real as metadata**, not as a monitoring/execution engine.

G18 Action-conditional calibration — **absent**.

G19 Outcome feedback — **partially implemented** through `DecisionFeedback`.

G20 Regret/opportunity-cost audit — **absent** as a longitudinal audit system.

G21 Simulation-to-reality monitoring — **absent**.

**Family G verdict: PARTIALLY IMPLEMENTED, with good safety-oriented contracts but insufficient decision science for high-stakes autonomous use.**

## H. Adversarial, information and epistemic robustness

H1 Source manipulation detection — **scaffold**.

H2 Coordinated information-operation detection — **scaffold / scientifically insufficient**. `InformationOperationDetector` simply averages supplied amplification/coordination/targeting scores.

H3 Bot/coordinated behaviour — **absent** as a validated detector.

H4 Narrative propagation modelling — **absent**.

H5 Polarisation dynamics — **absent** as a dynamic model.

H6 Perception-versus-event separation — **partially implemented conceptually**, but no general paired state model was found.

H7 Adversarial source dependency — **scaffold** through source-dependency graph/provenance.

H8 Data poisoning detection — **absent / scientifically insufficient**.

H9 Prompt/data boundary — **existing real at contract level**. `LLMGuard` requires evidence identifiers and explicitly forbids state mutation by LLM output.

H10 LLM confinement — **partially implemented**. The guard is strong as a contract, but full runtime enforcement requires integration with all model/application paths.

H11 Hallucination/unsupported-claim barriers — **partially implemented** via evidence/epistemic requirements; no comprehensive claim-verification engine.

H12 Red-team alternative explanations — **scaffold**. Red-team/stress-test modules exist but do not constitute a broad adversarial scientific testing system.

H13 Adversarial causal hypotheses — **scaffold**.

H14 Strategic deception/selection effects — **absent** as a rigorous inference framework.

H15 Evidence laundering detection — **absent**.

H16 Provenance contamination tracking — **partially implemented** in architecture, not fully enforced through all transformations.

**Family H verdict: PARTIALLY IMPLEMENTED AS GOVERNANCE SCAFFOLDING; SCIENTIFICALLY INSUFFICIENT FOR OPERATIONAL INFORMATION-OPERATIONS DETECTION.**

## I. Spatial, mobility and environmental intelligence

I1 GIS representation — **absent** as a real GIS/geospatial engine. `SpatialNode` uses latitude/longitude fields but no coordinate reference systems or GIS primitives.

I2 Dynamic spatial graphs — **scaffold** only.

I3 Mobility/flow modelling — **scaffold**. `flow_model.py` exists, but no demonstrated mobility model with real trajectories or OD matrices.

I4 Spatial spillovers — **scaffold / scientifically insufficient**. The current propagation logic transfers the maximum nearby risk within a radius.

I5 Spatial causal effects — **absent**.

I6 Geographic bottlenecks — **scaffold** through spatial/resource concepts, not measured network bottlenecks.

I7 Infrastructure dependencies — **absent** as a formal dependency graph integrated with spatial state.

I8 Environmental exposure trajectories — **absent**.

I9 Climate/weather perturbations — **absent** as a data-driven environmental model.

I10 Cross-border effects — **absent** as a formal spatial-causal capability.

I11 Spatially heterogeneous intervention effects — **absent**.

Important technical defect: the current spatial distance is Euclidean distance over latitude/longitude degrees (`hypot(lat_delta, lon_delta)`), which is not a physically correct geographic distance and cannot support rigorous spatial inference.

**Family I verdict: SCAFFOLD / SCIENTIFICALLY INSUFFICIENT; the current spatial engine is not a GIS-grade spatial intelligence layer.**

## J. Human and population systems

J1 Individual behaviour — **absent** as a general behavioural-state model.

J2 Group behaviour — **absent**.

J3 Institutional behaviour — **absent**.

J4 Behavioural adaptation to interventions — **absent**.

J5 Social contagion — **absent**.

J6 Trust/legitimacy — **absent** as measurable dynamic state variables.

J7 Polarisation — **scaffold at governance/narrative concept level; absent as a dynamical model**.

J8 Collective action — **absent**.

J9 Resource competition — **partially represented by generic resource optimisation contracts, not population dynamics**.

J10 Vulnerability/unequal exposure — **absent** as a formal population model.

J11 Human rights/system sustainability constraints — **partially implemented in governance documentation and safety contracts; not represented as a computable multi-objective state layer**.

J12 Policy/perception feedback — **absent** as an executable model.

**Family J verdict: LARGELY ABSENT.** This is a major gap because the user's Ceuta work treats perception, behaviour, institutions and capacity as endogenous components of the system, not merely contextual metadata.

## K. Clinical preventive medicine interface — OMNI-NET

K1 Longitudinal clinical record — **absent**.

K2 Continuous biosignals — **absent**.

K3 Wearables — **absent**.

K4 Laboratory trajectories — **absent**.

K5 Imaging trajectories — **absent**.

K6 Genetics/epigenetics — **absent**.

K7 Microbiome — **absent**.

K8 Sleep/autonomic physiology — **absent**.

K9 Lifestyle/behavioural trajectories — **absent**.

K10 Medication exposure/polypharmacy interactions — **absent** as a clinical implementation.

K11 Biological-age models — **absent**.

K12 Risk trajectories rather than static scores — **absent**.

K13 Personal baseline deviation — **absent**.

K14 Preventive intervention optimisation — **absent**.

K15 Clinical causal inference — **generic causal scaffolding only; clinically insufficient**.

K16 Clinical uncertainty/abstention — **generic abstention exists; clinical safety layer absent**.

K17 Patient-specific competing hypotheses — **generic causal model disagreement exists; no clinical hypothesis engine**.

K18 Prospective preventive validation — **absent**.

K19 Safety monitoring — **generic system safety exists; OMNI-specific clinical safety absent**.

K20 Clinician oversight — **generic human-review contract exists; no clinical workflow implementation**.

### OMNI-NET vFINAL-specific requirements

The repository contains none of the following as operational clinical science: RFR_i(t), five-domain RFR calculation, IVO argmin rule, empirically estimated CRS, Cox weighting pipeline, Bayesian 5D state-space model, explicit seven-layer clinical DAG, clinical variable-tier governance (Core/Extended/Research/Moderator), pre-analytic protocol enforcement, or Studies 0–4 validation registry.

The explicit OMNI-NET rule that the CRS is only a mathematical framework until weights are learned from own data is exactly the type of scientific validity gate CeutIA should support generically. It must not be replaced by theoretical weights or invented performance.

**Family K verdict: ABSENT FROM CEUTIA, AS IT SHOULD BE AS A SEPARATE PRODUCT DOMAIN; however, the generic state/causal infrastructure needed to support a future OMNI-NET integration is also not yet mature.**

## L. Simulation and digital twins

L1 Digital-twin state synchronisation — **scaffold**. `DigitalTwinCore` can iterate a supplied transition function but has no live synchronization with observed system state.

L2 Parameter calibration — **absent**.

L3 Agent-based simulation — **scaffold**. `agent_stress.py` exists but no validated ABM framework.

L4 Intervention simulation — **scaffold** through generic transitions.

L5 Counterfactual policy simulation — **absent / scaffold**.

L6 Scenario stress testing — **scaffold**.

L7 Monte Carlo uncertainty propagation — **absent**.

L8 Model discrepancy — **absent**.

L9 Simulation-to-real transfer monitoring — **absent**.

L10 Safe sandboxing of interventions — **partially implemented** at governance/pipeline boundary, but no complete simulation sandbox lifecycle.

**Family L verdict: SCAFFOLD.** It is a transition-loop primitive, not yet a digital twin in the scientific sense.

## M. Learning architecture

M1 Prospective learning loops — **scaffold**. Forecast/outcome recording and MAE exist.

M2 Outcome-linked updates — **absent** as actual model updating.

M3 Model versioning — **partially implemented** through model release metadata and knowledge versioning.

M4 Model governance — **partially implemented**. Approval/rollback contracts exist, but validation evidence is represented by a scalar score without a complete evidence registry.

M5 Champion/challenger — **absent**.

M6 Rollback — **existing real as a state transition contract**, not deployment rollback orchestration.

M7 Drift detection — **scaffold**.

M8 Calibration monitoring — **scaffold**.

M9 Causal hypothesis lifecycle — **absent**.

M10 Evidence accumulation — **partially implemented** through epistemic/evidence structures, not a longitudinal scientific evidence ledger.

M11 Failed-hypothesis memory — **absent**.

M12 Negative-result preservation — **absent** as a dedicated scientific knowledge mechanism.

M13 Protection against self-reinforcing model-output contamination — **absent** as a full data lineage/control mechanism.

**Family M verdict: SCAFFOLD / PARTIALLY IMPLEMENTED.** The repository can record outcomes but cannot yet learn scientifically safely from them.

## N. Governance, safety and auditability

N1 Full audit trail — **partially implemented**. Audit/traceability/incident modules exist, but complete end-to-end coverage must still be demonstrated.

N2 Immutable provenance — **partially implemented**. Provenance hashes/lineage exist, but not all derived artefacts are demonstrably immutable.

N3 Public/OWNER separation — **existing real at contract level**. `information_boundary.py` explicitly separates PUBLIC, INTERNAL, OWNER and RESTRICTED domains.

N4 Data access boundaries — **partially implemented**. Information classification/access contracts are real; application authentication/authorization integration remains external.

N5 Privacy-preserving aggregation — **scientifically insufficient**. The aggregation layer calculates and reports a `noise_scale` but does not actually add calibrated differential-privacy noise.

N6 Differential privacy — **incorrect if interpreted as implemented DP**. An epsilon parameter alone is not differential privacy; the current method returns the mean unchanged.

N7 Security controls — **partially implemented / substantial documentation**. There is a large security control plane and runtime-boundary architecture; executable coverage still needs independent verification.

N8 Incident ledger — **scaffold / partial**.

N9 Emergency degradation — **scaffold**.

N10 Checkpointing — **existing real for project-development checkpoints and a resilience module**, but application-state checkpointing is not equivalent to repository checkpointing.

N11 Failover — **scaffold**.

N12 Reproducible builds/tests — **partially implemented**. CI compiles, installs, runs tests, phase verifiers and Compose validation.

N13 Scientific validity gates — **partially implemented**. Epistemic and causal gates exist, but domain-specific claim registries and empirical validation thresholds are incomplete.

N14 Model/assumption cards — **absent** as a standardized executable registry.

N15 Decision records — **partially implemented**.

N16 Intervention records — **scaffold**.

N17 Prohibited inference classes — **partially implemented** through causal governance, LLM guard and safety documents.

N18 Human accountability — **partially implemented** via human review/OWNER controls; complete operational accountability chain is not demonstrated.

**Family N verdict: PARTIALLY IMPLEMENTED, with strong policy/contract architecture but important executable and scientific gaps.** The differential-privacy claim is the clearest concrete technical defect found in this audit.

## O. Validation and scientific evidence

O1 Unit tests — **existing real**. The repository has a substantial pytest suite.

O2 Contract tests — **existing real**. Foundational, temporal, epistemic and causal contract tests exist.

O3 Integration tests — **existing real / partial**. Multiple integration tests exist.

O4 End-to-end deterministic tests — **existing real for selected workflows**, including heat-risk and complex-system completion tests; not comprehensive for the entire scientific architecture.

O5 Temporal leakage tests — **existing real** in dedicated test areas and Phase 3 validation.

O6 Synthetic causal benchmarks — **absent**.

O7 Known-DAG recovery benchmarks — **absent**.

O8 Confounding benchmarks — **absent**.

O9 Intervention-effect benchmarks — **absent**.

O10 Counterfactual benchmarks — **absent**.

O11 Distribution-shift benchmarks — **absent**.

O12 Adversarial benchmarks — **partial/scaffold**; security/red-team tests exist, but not a systematic scientific adversarial benchmark suite.

O13 Rare-event benchmarks — **absent**.

O14 Calibration benchmarks — **absent** as rigorous probabilistic calibration benchmarks.

O15 Prospective validation harness — **scaffold / partial**. Prospective workflows exist, but current validators are mostly error-recording/threshold contracts, not full prospective study designs.

O16 External validation — **absent**.

O17 Reproducibility across seeds/runs — **partial**; deterministic contracts are tested, but stochastic scientific reproducibility is not comprehensively established.

O18 Sensitivity analysis — **absent** as a broad scientific framework.

O19 Ablation studies — **absent**.

O20 Error taxonomy — **partial** through validation/error modules, but no unified scientific error ontology.

O21 Failure-mode catalogue — **partial** in governance/security documentation, not unified with model validation.

O22 Scientific claims registry — **absent**.

O23 Evidence threshold registry — **partial** conceptually, not a comprehensive machine-enforced registry.

O24 No-evidence/insufficient-evidence outputs — **existing real at epistemic contract level**. The epistemic layer can return `UNCERTAIN` and explicitly distinguishes evidence confidence from calibrated event probability.

The current CI workflow is real and enforces compile/test/phase verifiers/Compose validation, but CI passing is not equivalent to scientific validation. The workflow currently verifies implementation invariants rather than causal, forecasting, spatial, resilience or clinical validity benchmarks.

**Family O verdict: STRONG SOFTWARE VALIDATION FOUNDATION, SCIENTIFIC VALIDATION LARGELY ABSENT.**

## Cross-family conclusion after V2

The repository has three materially different maturity zones:

1. **Software-contract/governance zone:** relatively mature. Temporal availability semantics, epistemic separation, information boundaries, LLM non-mutation, phase verifiers, tests and CI are real.

2. **Analytical scaffold zone:** broad but shallow. Causal reasoning, forecasting, decisions, graphs, spatial propagation, simulation, learning and resilience have named modules and executable contracts, but most are deterministic primitives rather than scientifically validated engines.

3. **Core scientific state/dynamics zone:** largely absent. There is no mature latent-state estimator, state-space/Bayesian filter, longitudinal trajectory engine, quantified reserve/capacity model, regime-switching inference, critical-transition detector, multiscale dynamics engine, or unified observation -> state -> trajectory -> causal/dynamic model -> intervention -> outcome loop.

## Consequence for OMNI-NET

OMNI-NET vFINAL clarifies what the missing state layer must eventually be capable of without making CeutIA clinical. Its RFR/IVO construction is a domain-specific example of a more general CeutIA capability:

- define a latent/derived functional state;
- normalize it against an appropriate context-dependent reference;
- preserve measurement uncertainty;
- track it longitudinally;
- derive trajectory and recovery dynamics;
- identify the lowest-reserve component;
- test the hypothesis prospectively;
- refuse clinical deployment until empirical validation gates are met.

The five OMNI-NET RFR domains are therefore not candidates for arbitrary insertion into CeutIA. They are a concrete test case for whether CeutIA's generic architecture can represent reserve, heterogeneity, cross-domain stress, trajectory and failure without collapsing the evidence hierarchy.

## Current highest-priority gaps

P0 — Canonical dynamic-state ontology and state-estimation substrate.

P0 — Longitudinal trajectory, baseline-deviation, uncertainty and multiscale temporal model.

P0 — Scientific causal inference beyond contracts: identification, sensitivity, time-varying confounding, negative controls, transportability, intervention estimation and prospective validation.

P0 — Complex-dynamics engine: reserve/capacity, feedback, nonlinearities, hysteresis, early-warning signals, tipping points and regime transitions.

P1 — Forecasting calibration/distribution shift/tail risk/multihorizon evaluation.

P1 — Decision VoI/active sensing/Pareto/action-conditional calibration.

P1 — Human/population behavioural and institutional dynamics.

P1 — Spatial causal/GIS/flow infrastructure.

P1 — Scientific benchmark suite and claims/evidence registry.

P1 — Learning architecture that preserves failed hypotheses, negative results and causal independence from model-generated data.

P2 — Hardening of privacy/security/external authorization and complete audit propagation.

## Stop condition for implementation

No new specialist feature should be treated as priority merely because it is absent. Before further feature construction, the architecture must resolve the P0 substrate gaps and explicitly map every existing module onto the canonical state/trajectory lifecycle. Otherwise additional modules will increase surface area without solving the central problem.
