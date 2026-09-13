# CeutIA — Project Objectives and Exhaustive Gap Register v0

Status: CHECKPOINT / ARCHITECTURAL RECONCILIATION

This document is a loss-prevention checkpoint before further implementation. It records the current interpretation of the project, the distinction between CeutIA and OMNI-NET, principles extracted from the author's publicly indexed LinkedIn material, and the major capability families that must be audited before claiming completeness.

## 1. Scope boundary

### CeutIA
CeutIA is the general complex-systems inference, anticipation, causal reasoning, resilience and decision-intelligence platform. Its domain is not restricted to medicine. It must be capable of representing interactions among biological, psychological, behavioural, social, economic, environmental, technological, geopolitical, infrastructural and institutional systems.

Medicine is an important application domain and a source of methodological insight, but CeutIA must not collapse into a clinical-only system.

### OMNI-NET
OMNI-NET is the separate clinical project. It is exclusively preventive medicine: longitudinal human biological state modelling, precision prevention, continuous monitoring, causal clinical reasoning, biological trajectory estimation and intervention support. Its core thesis is that disease is often delayed observation of a trajectory rather than an isolated event.

The two projects may share scientific primitives, especially longitudinal state estimation, Bayesian updating, causal inference, temporal modelling and uncertainty management, but their scopes must remain architecturally distinguishable.

## 2. Intellectual thesis recovered from indexed public material

The recurring thesis is not simply "use AI in health". It is a systems doctrine:

1. A snapshot is an incomplete observation of a trajectory.
2. A value has meaning only in temporal and contextual state.
3. Disease, failure and crisis often emerge after a long period of accumulated system change.
4. The clinically or operationally visible event may be downstream of a much longer causal chain.
5. Disciplines create artificial boundaries that do not necessarily exist in the underlying system.
6. Interactions matter: the whole system can behave differently from the sum of individually correct components.
7. Thresholds, tipping points, loss of resilience and cascades are central.
8. The same perturbation can produce different outcomes depending on the state and regime of the system.
9. Early weak signals matter, but must not be confused with proof.
10. Prediction is not causation; causal reasoning must be explicitly governed.
11. Intervention changes the system and therefore must be represented separately from observation.
12. Prevention means changing a trajectory before the terminal state becomes obvious.
13. Human behaviour, institutions and environments are endogenous parts of many systems rather than external noise.
14. A system can compensate for perturbation, exhaust reserve, lose adaptive capacity and subsequently amplify perturbation through feedback.
15. The relevant question is often not "what is the current state?" but "how did the system arrive here and where is it moving?"

## 3. Concrete concepts evidenced in the indexed publications

The indexed material supplied by the user and the publicly indexed profile material reinforce the following concepts:

- longitudinal monitoring rather than isolated clinical measurements;
- Bayesian probabilistic updating of patient state;
- dynamic physiology and reconciliation of specialty-specific models;
- polypharmacy as an example of interaction effects between individually rational interventions;
- microbiome as an internal ecosystem interacting with host physiology;
- epigenetic and biological-age measures as longitudinal state markers;
- external determinants of health, including economic and geopolitical stress;
- allostatic load and chronic stress as a possible mediator between environment and biology;
- cross-domain chains such as threat -> stress -> sleep -> behaviour -> metabolism -> cardiovascular/immunological state;
- collective behaviour and shared environmental perturbations as possible synchronizers;
- health-system capacity, queues, bottlenecks and shock-response dynamics;
- migration and sudden population shocks as system perturbations that alter arrival-rate dynamics;
- resilience reserve, critical thresholds and cascade behaviour;
- misinformation, polarisation and perception as potentially interacting system variables;
- feedback where an attempted stabilising action can itself modify perception or behaviour;
- etiological treatment rather than merely treating downstream symptoms;
- the need to preserve evidence quality while permitting interdisciplinary hypothesis generation;
- prospective pilots and measurable evidence rather than unsupported technological claims.

These observations are methodological requirements for the architecture, not assertions that every mechanism is already scientifically established.

## 4. Core scientific doctrine required by the project

CeutIA must separate at least the following epistemic states:

observed -> measured -> temporally associated -> statistically associated -> mechanistically plausible -> causally hypothesised -> causally identified under explicit assumptions -> interventionally estimable -> prospectively tested -> prospectively validated.

No lower state may silently promote itself to a higher state.

Every inference should preserve:

- source provenance;
- timestamp and observation window;
- data-generating process where known;
- transformation history;
- uncertainty;
- assumptions;
- alternative explanations;
- competing models;
- contradictions;
- missing evidence;
- falsification status;
- validity window;
- applicable population/context/regime;
- intervention status.

## 5. Exhaustive capability families to audit

### A. System ontology and representation

A1. Multi-domain entities, agents, populations, institutions, environments and infrastructures.
A2. State variables, latent states and observable proxies.
A3. Hierarchies and nested systems.
A4. Time scales from milliseconds to decades.
A5. Spatial scales from individual to network, territory and global system.
A6. Dynamic regimes and regime transitions.
A7. Feedback loops and circular causality.
A8. Delays, memory, hysteresis and path dependence.
A9. Thresholds, tipping points and critical transitions.
A10. Resource constraints, capacity and bottlenecks.
A11. Endogenous versus exogenous shocks.
A12. Intervention versus observation semantics.

### B. Data and observation architecture

B1. Streaming and batch observations.
B2. Event-time versus ingestion-time semantics.
B3. Longitudinal identity and entity resolution.
B4. Source reliability and source dependency.
B5. Schema drift.
B6. Missingness mechanisms: MCAR/MAR/MNAR where applicable.
B7. Measurement error and sensor uncertainty.
B8. Sampling bias and selection mechanisms.
B9. Survivorship and collider risks.
B10. Temporal leakage prevention.
B11. Dataset/version lineage.
B12. Historical reconstruction.
B13. Replayability.
B14. Observation conflict reconciliation.
B15. Provenance down to raw source and transformation.
B16. Data quality scoring that cannot masquerade as truth probability.

### C. State estimation and longitudinal modelling

C1. Dynamic latent-state estimation.
C2. Bayesian filtering and smoothing.
C3. State-space models.
C4. Time-varying parameter models.
C5. Change-point detection.
C6. Regime-switching models.
C7. Individual versus population trajectories.
C8. Personal baselines and deviation-from-baseline.
C9. Context-dependent reference ranges.
C10. Trajectory derivatives and acceleration/deceleration.
C11. Early-warning indicators.
C12. Uncertainty propagation through state estimation.

### D. Causal intelligence

D1. Explicit DAG/SCM representation.
D2. Potential outcomes representation where appropriate.
D3. Temporal causal graphs.
D4. Time-varying confounding.
D5. Marginal structural reasoning.
D6. Backdoor/frontdoor identification where assumptions permit.
D7. Collider and mediator protection.
D8. Unmeasured-confounding sensitivity analysis.
D9. Negative controls.
D10. Falsification tests.
D11. Causal discovery as hypothesis generation, never automatic proof.
D12. Competing causal graphs.
D13. Mechanistic constraints on causal graphs.
D14. Interventional semantics using do-operators.
D15. Counterfactuals and potential outcomes.
D16. Mediation.
D17. Moderation/effect modification.
D18. Heterogeneous treatment/effect estimation.
D19. Dose-response and nonlinear effects.
D20. Delayed causal effects.
D21. Feedback and simultaneous causality.
D22. Cross-domain causal chains.
D23. Regime-dependent causal effects.
D24. Causal transportability/generalisation.
D25. External validity.
D26. Positivity/overlap.
D27. Consistency/SUTVA-like assumptions where applicable.
D28. Sensitivity to model misspecification.
D29. Causal model ensembles.
D30. Causal disagreement preservation.
D31. Active causal learning.
D32. Intervention design and feasibility constraints.
D33. Causal attribution after interventions.
D34. Prospective causal validation.

### E. Complex-systems dynamics

E1. Network topology and dynamic graphs.
E2. Node/edge state evolution.
E3. Centrality and changing influence.
E4. Community formation and fragmentation.
E5. Contagion and propagation.
E6. Cascades.
E7. Percolation-style thresholds where scientifically justified.
E8. Feedback amplification and damping.
E9. Adaptive capacity.
E10. Resilience reserve.
E11. Critical slowing down.
E12. Variance/autocorrelation early-warning signals.
E13. Hysteresis.
E14. Nonlinear response.
E15. Multi-stability and alternative attractors.
E16. Path dependence.
E17. Emergence.
E18. Synchronisation.
E19. Cross-scale coupling.
E20. Shock absorption versus shock amplification.
E21. Bottleneck detection.
E22. Capacity queues and flow constraints.
E23. Failure propagation through coupled networks.

### F. Forecasting and anticipation

F1. Probabilistic forecasts.
F2. Distributional forecasts, not only point predictions.
F3. Multi-horizon forecasting.
F4. Scenario generation.
F5. Competing scenarios.
F6. Ensemble models.
F7. Model disagreement.
F8. Calibration.
F9. Calibration drift.
F10. Distribution shift.
F11. Conformal or equivalent uncertainty coverage where applicable.
F12. Forecast validity windows.
F13. Triggered reforecasting.
F14. Rare-event forecasting.
F15. Tail-risk estimation.
F16. Forecasting under missing/manipulated observations.
F17. Forecast decomposition into endogenous/exogenous drivers.
F18. Prospective backtesting with temporal separation.

### G. Decision intelligence

G1. Formal decision context.
G2. Action space.
G3. Objectives and utility.
G4. Constraints and resource budgets.
G5. Multi-objective/Pareto decisions.
G6. Risk-sensitive utility.
G7. Regret minimisation.
G8. Robust decision making under deep uncertainty.
G9. Value of information.
G10. Active sensing.
G11. Decision-specific causal identification.
G12. Counterfactual policy comparison.
G13. Policy simulation.
G14. Decision abstention.
G15. Human review gates.
G16. Prohibited autonomous interventions.
G17. Re-evaluation triggers.
G18. Action-conditional calibration.
G19. Outcome feedback.
G20. Decision regret and opportunity-cost audit.
G21. Simulation-to-reality monitoring.

### H. Adversarial, information and epistemic robustness

H1. Source manipulation detection.
H2. Coordinated information-operation detection.
H3. Bot/coordinated behaviour indicators where justified.
H4. Narrative propagation modelling.
H5. Polarisation dynamics.
H6. Perception-versus-event separation.
H7. Adversarial source dependency.
H8. Data poisoning detection.
H9. Prompt/data boundary enforcement.
H10. LLM confinement.
H11. Hallucination and unsupported-claim barriers.
H12. Red-team generation of alternative explanations.
H13. Adversarial causal hypotheses.
H14. Strategic deception and selection effects.
H15. Evidence laundering detection.
H16. Provenance contamination tracking.

### I. Spatial, mobility and environmental intelligence

I1. GIS representation.
I2. Dynamic spatial graphs.
I3. Mobility/flow modelling.
I4. Spatial spillovers.
I5. Spatial causal effects.
I6. Geographic bottlenecks.
I7. Infrastructure dependencies.
I8. Environmental exposure trajectories.
I9. Climate and weather perturbations.
I10. Cross-border effects.
I11. Spatially heterogeneous intervention effects.

### J. Human and population systems

J1. Individual behaviour.
J2. Group behaviour.
J3. Institutional behaviour.
J4. Behavioural adaptation to interventions.
J5. Social contagion.
J6. Trust and legitimacy.
J7. Polarisation.
J8. Collective action.
J9. Resource competition.
J10. Vulnerability and unequal exposure.
J11. Human rights and system sustainability as simultaneous constraints.
J12. Feedback between system policy and public perception.

### K. Clinical preventive medicine interface for OMNI-NET

K1. Longitudinal clinical record.
K2. Continuous biosignals.
K3. Wearables.
K4. Laboratory trajectories.
K5. Imaging trajectories.
K6. Genetics/epigenetics.
K7. Microbiome.
K8. Sleep/autonomic physiology.
K9. Lifestyle and behavioural trajectories.
K10. Medication exposure and polypharmacy interactions.
K11. Biological-age models.
K12. Risk trajectories rather than static risk scores.
K13. Personal baseline deviation.
K14. Preventive intervention optimisation.
K15. Clinical causal inference.
K16. Clinical uncertainty and abstention.
K17. Patient-specific competing hypotheses.
K18. Prospective preventive validation.
K19. Safety monitoring.
K20. Human clinician oversight.

### L. Simulation and digital twins

L1. Digital twin state synchronisation.
L2. Model parameter calibration.
L3. Agent-based simulation.
L4. Intervention simulation.
L5. Counterfactual policy simulation.
L6. Scenario stress testing.
L7. Monte Carlo uncertainty propagation.
L8. Model discrepancy.
L9. Simulation-to-real transfer monitoring.
L10. Safe sandboxing of interventions.

### M. Learning architecture

M1. Prospective learning loops.
M2. Outcome-linked updates.
M3. Model versioning.
M4. Model governance.
M5. Champion/challenger models.
M6. Rollback.
M7. Drift detection.
M8. Calibration monitoring.
M9. Causal hypothesis lifecycle.
M10. Evidence accumulation.
M11. Failed-hypothesis memory.
M12. Negative-result preservation.
M13. Avoidance of self-reinforcing feedback from model outputs into training data without causal controls.

### N. Governance, safety and auditability

N1. Full audit trail.
N2. Immutable provenance.
N3. Public/OWNER separation.
N4. Data access boundaries.
N5. Privacy-preserving aggregation.
N6. Differential privacy where applicable.
N7. Security controls.
N8. Incident ledger.
N9. Emergency degradation.
N10. Checkpointing.
N11. Failover.
N12. Reproducible builds/tests.
N13. Scientific validity gates.
N14. Model cards/assumption cards.
N15. Decision records.
N16. Intervention records.
N17. Explicit prohibited inference classes.
N18. Human accountability.

### O. Validation and scientific evidence

O1. Unit tests.
O2. Contract tests.
O3. Integration tests.
O4. End-to-end deterministic tests.
O5. Temporal leakage tests.
O6. Synthetic causal benchmarks.
O7. Known-DAG recovery benchmarks.
O8. Confounding benchmarks.
O9. Intervention-effect benchmarks.
O10. Counterfactual benchmarks.
O11. Distribution-shift benchmarks.
O12. Adversarial benchmarks.
O13. Rare-event benchmarks.
O14. Calibration benchmarks.
O15. Prospective validation harness.
O16. External validation.
O17. Reproducibility across seeds/runs.
O18. Sensitivity analysis.
O19. Ablation studies.
O20. Error taxonomy.
O21. Failure-mode catalogue.
O22. Scientific claims registry.
O23. Evidence threshold registry.
O24. No-evidence / insufficient-evidence outputs.

## 6. Architectural principle that is currently missing at the highest level

The system must not be a collection of sophisticated modules connected by data pipes. The central object must be a time-indexed, provenance-aware, uncertainty-aware system state and its evolving causal/dynamic model.

Every major subsystem should be able to answer:

- What was observed?
- When was it observed?
- Where and at what scale?
- What state did the observation inform?
- What alternative explanations exist?
- Which relationships are merely associative?
- Which causal assumptions are being made?
- What evidence could falsify the current explanation?
- What is changing now?
- Which feedback loops are active?
- Is the system approaching a threshold?
- What is the forecast distribution?
- What action is being considered?
- What would change under intervention?
- What information would most reduce uncertainty?
- What happened after the decision?
- Did the model learn from the outcome without contaminating the causal evaluation?

## 7. Critical anti-failure rules

- Never equate correlation with causation.
- Never equate temporal precedence with causation.
- Never treat model output as evidence independent of its training/evidence lineage.
- Never collapse competing hypotheses prematurely.
- Never discard contradictory evidence merely because it lowers confidence.
- Never hide missing evidence behind a confidence score.
- Never use a static threshold when the relevant baseline is dynamic without explicit justification.
- Never treat an intervention as an observation.
- Never let a forecast silently become a causal explanation.
- Never let a causal explanation silently become a recommendation.
- Never let a recommendation silently become an autonomous intervention.
- Never allow public outputs to expose OWNER-only intelligence.
- Never close a scientific phase on code presence alone; require reproducible validation and explicit exit criteria.

## 8. Checkpoint protocol for subsequent implementation

Implementation must proceed in bounded increments. After each increment:

1. write/update the affected code;
2. add deterministic tests;
3. update the relevant verifier;
4. update architecture documentation;
5. commit to Git;
6. record the commit SHA;
7. run or trigger CI;
8. record the CI result;
9. only then begin the next increment.

No large uncommitted batch is acceptable. If execution stops, the last successful commit is the recovery point.

## 9. Current interpretation

The project is substantially broader than the causal layer implemented so far. The causal layer is necessary but not sufficient. The principal remaining work is not simply adding more algorithms; it is making the entire architecture longitudinal, state-based, causal, dynamic, cross-domain, uncertainty-aware, adversarially robust and prospectively validated.

The next engineering step must therefore be a repository-wide gap audit against this register before additional feature implementation is selected.
