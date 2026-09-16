# CeutIA + SERPIENTE — Maximum Knowledge-to-Capability Audit 001

## Mission identity

This is a new mission of the **Ingeniero de CeutIA**. It follows the completed engineering audit, scientific-limitation resolution mission, and second-order scientific extraction. It does not reopen those missions.

Objective: systematically determine which scientifically justified capabilities can be constructed now from accumulated knowledge, existing architecture, existing data structures and validated engineering, while preserving the distinction between implementation and prospective scientific validation.

## State dimensions

- ENGINEERING_STATUS: AUDITED FOUNDATION COMPLETE
- SCIENTIFIC_STATUS: GOVERNED; PROSPECTIVE VALIDITY NOT ESTABLISHED
- DATA_STATUS: CORE TEMPORAL/PROVENANCE STRUCTURES AVAILABLE; COMPLETE LIVE PRODUCTION ACQUISITION NOT YET ESTABLISHED
- VALIDATION_STATUS: ENGINEERING AND METHODOLOGICAL TESTING ESTABLISHED; PROSPECTIVE TARGET-POPULATION VALIDATION PENDING
- OPERATIONAL_STATUS: CORE TRACEABILITY/decision infrastructure available; continuous real-world effectiveness not established
- EVIDENCE_STATUS: epistemic contracts and provenance implemented; external empirical evidence remains necessary for prospective claims

## Executive result

The accumulated audit supports a stronger immediate capability stack without adding speculative model families. The highest-value compositional capabilities are:

1. Information-set aware forecasting (`I_t`) as the conceptual scientific boundary.
2. Individual forecast forensic reconstruction and replay from bound PIT/provenance identities.
3. Temporal-semantic validation of longitudinal dynamics.
4. Multisystem state/trajectory composition with explicit uncertainty and evidence propagation.
5. Change detection and regime-awareness as separate from ordinary anomaly detection.
6. Interaction/coupling surveillance as a distinct scientific object from individual-variable drift.
7. Source-process intelligence to distinguish phenomenon change from measurement/reporting change.
8. Outcome-process surveillance separating outcome occurrence from ascertainment.
9. Dependence-aware evaluation and source-dependence awareness.
10. Evidence-aware early warning with context, uncertainty, provenance and suppression/hysteresis requirements.
11. Scientific self-monitoring that detects violated assumptions rather than claiming that a prediction is false.
12. Prospective research-ready cohort/intervention architecture.

The audit found no justification to add HMMs, Kalman filters, particle filters, VAR/VARX, Hawkes, ODE/SDE, graph dynamical systems, copulas, conformal prediction or other advanced model classes merely because they are available. They require a concrete target phenomenon, data-generating process, identifiable parameters/estimands, and validation design.

## 1. Knowledge-to-capability composition map

| Composition | Scientific purpose | Current state | Immediate action |
|---|---|---|---|
| observation + PIT + provenance | reconstruct legitimate historical information | ALREADY SUPPORTED | exploit in replay/forensics |
| longitudinal state + physical-time derivatives | trajectory | ALREADY SUPPORTED | retain explicit time semantics |
| trajectory + anomaly | transition candidate | PARTIALLY SUPPORTED | define change-vs-anomaly semantics before code |
| trajectory + interaction | dynamic coupling | PARTIALLY SUPPORTED | research capability; requires concrete variables |
| multiple domains + state | multisystem state | ALREADY SUPPORTED | use as composite descriptive state |
| multisystem state + anomaly | emergent configuration | PARTIALLY SUPPORTED | requires multivariate reference distribution/data |
| state + forecast + uncertainty | conditional risk representation | ALREADY SUPPORTED | preserve uncertainty semantics |
| risk + evidence + threshold | contextual warning | ALREADY SUPPORTED/PARTIALLY OPERATIONAL | no efficacy claim |
| warning + response lineage | prevention workflow | ALREADY SUPPORTED | evaluate response prospectively |
| multiple forecasts + disagreement | structural uncertainty signal | ALREADY SUPPORTED | monitor, do not equate with truth |
| source lineage + corroboration | false-corroboration detection | PARTIALLY SUPPORTED | declared source dependency can be analysed |
| revisions + latency + publication | documentary novelty analysis | ALREADY SUPPORTED primitives | distinguish source-process change |
| population denominator + incidence | denominator-aware signal | REQUIRES EXTERNAL DATA | no synthetic denominator |
| intervention + post-intervention trajectory | response/effect hypothesis | REQUIRES EXTERNAL DATA | prospective study |
| observation process + signal | measurement-process separation | PARTIALLY SUPPORTED | requires empirical observation-process data |

## 2. Information-set capability

Scientific representation:

`I_t = legitimately available information at forecast origin t`

`X_t = declared computational representation of I_t`

`Yhat_t = f(I_t, M_t)`

where `M_t` is the model state/version applicable at t.

The immediate scientific benefit is not a new predictor. It is preventing a hidden distinction between “same features” and “same information”. Two forecasts with identical visible X can be scientifically non-equivalent if source revisions, preprocessing, model state or hidden upstream information differ.

Current implementation supports PIT binding, temporal eligibility, provenance, transformation lineage and fingerprints. Complete proof of the absence of undisclosed upstream information remains NOT IDENTIFIABLE from repository controls alone.

## 3. Temporal mathematics audit

All temporal quantities must declare whether they are based on:

- observation index;
- elapsed physical time;
- event time;
- acquisition/availability time.

Current trend/acceleration corrections are physical-time normalized. Current longitudinal `lags` are observation-order lags and must remain so until a concrete physical-time lag feature is specified.

Potential future methods are conditionally appropriate:

- state-space/Kalman/particle filtering: useful when a latent continuously evolving state is explicitly defined and noisy sequential observations exist;
- HMM/regime switching: useful when discrete latent regimes have identifiable transition structure and sufficient repeated observations;
- VAR/VARX/TVP-VAR: useful for multivariate stationary/locally varying time series with sufficient regular observations or explicitly modelled irregularity;
- point processes/Hawkes: useful for event-arrival self-/cross-excitation data, not generic periodic indicators;
- ODE/SDE/delay systems: useful when a mechanistic state equation is scientifically defensible and parameters are identifiable;
- change-point/regime methods: immediately relevant conceptually, but method choice depends on target signal and sampling distribution.

No universal replacement is justified.

## 4. Statistical consequence matrix

| Problem | Detectable now | Correctable/modelled now | Evidence/data dependency |
|---|---|---|---|
| temporal dependence | YES | YES for declared evaluation unit | process-specific unit |
| irregular sampling | YES | YES for implemented derivatives | timestamps |
| revisions/latency | YES where metadata supplied | PARTIAL | source metadata |
| calibration drift | PARTIAL | diagnostics/calibration machinery available | prospective outcomes |
| regime shift | PARTIAL | stratification/OOD framework | real population/regime data |
| source dependence | PARTIAL | declared lineage/dependency | upstream metadata |
| missingness | YES at data/runtime level | PARTIAL scientific correction | missingness mechanism |
| censoring | metadata-supported | study-specific | outcome data |
| selection bias | NOT generally identifiable from provenance alone | NO generic correction | design/data |
| measurement error | provenance supports tracking | NO universal correction | repeated/reference measurements |
| denominator instability | detectable if denominator supplied | correction requires valid denominator | population data |
| overdispersion/zero inflation | target-dependent | requires appropriate count target/data | empirical distribution |
| rare/extreme events | alerting/evaluation can represent them | specialized EVT/point-process model only when justified | sufficient tail observations |
| multiplicity | can be governed | study-specific adjustment | hypothesis family |
| correlated sources | declared dependency detectable | hidden common origin not generally identifiable | source lineage |

## 5. Multisystem dynamics

The architecture can represent a composite state without claiming a latent physical entity exists. A scientifically useful hierarchy is:

`variables → domain states → cross-domain state → trajectory → interaction → configuration → risk signal`

Interaction claims should carry an epistemic status:

`association → statistical dependence → predictive dependence → mechanistic hypothesis → causal hypothesis → causally supported → intervention-supported → operationally validated`.

This is an evidence ladder, not a ranking of model quality.

### Interaction change is a first-class monitoring target

A technically correct system can fail because coupling changes while every marginal remains stable. Therefore a future interaction monitor should compare the conditional/dependence structure across time or regimes, not only marginal distributions.

Candidate diagnostics, to be selected per phenomenon:

- lagged association change;
- conditional dependence change;
- dynamic partial correlation;
- predictive incremental value;
- sign reversal;
- coefficient drift in an explicitly specified model;
- network edge appearance/disappearance;
- regime-specific interaction strength.

These are diagnostics, not automatic causal estimators.

## 6. Incremental predictive value

The scientifically correct question is:

`Does A improve prediction of B beyond history(B) + already admitted covariates?`

The corresponding evaluation must preserve time order, information-set eligibility, outcome definition and dependence structure. A correlation matrix is insufficient.

For candidate interactions the estimand should compare:

`baseline information set → baseline forecast`

against

`baseline information set + A → augmented forecast`.

Improvement must be evaluated using proper scoring rules and predeclared temporal splits. This capability is REQUIRES IMPLEMENTATION when a concrete target and candidate variable set are registered; the generic engine should not guess targets.

## 7. Emergent multisystem anomalies

The audit supports the scientific concept of a joint configuration becoming unusual even when no single variable crosses its univariate threshold.

Potential methods:

- Mahalanobis/reference-state distance where covariance is estimable;
- robust multivariate distance where heavy tails/outliers matter;
- latent-state deviation where a validated latent-state model exists;
- joint tail/dependence diagnostics where sufficient data exist;
- network-configuration deviation where network structure is explicit.

This is REQUIRES IMPLEMENTATION for a concrete multisystem state definition and reference distribution. It is not justified to add a generic anomaly score without those definitions.

## 8. Change detection and regime detection

Anomaly and change point answer different questions:

- anomaly: an observation/configuration is unusual relative to a reference;
- change point: the data-generating distribution or process appears to have changed;
- regime: a persistent state/process condition with distinct behaviour.

This distinction should be preserved in future warning logic. A one-off extreme should not automatically become a regime change, and a persistent regime change may occur without a single extreme observation.

Appropriate families include sequential likelihood methods, CUSUM/Page-type procedures, Bayesian change-point models and distributional two-sample/energy-distance methods, selected by data structure. No universal algorithm is inserted at this stage.

## 9. Source intelligence

The acquisition process is scientifically observable. Source metadata should permit detection of:

`schema change; definition change; denominator change; cadence change; latency change; revision burst; coverage loss; API change; classification change; population change`.

A source-process event must not automatically be classified as a world event.

Current state: provenance/version/availability primitives are available. A complete automated source-intelligence layer is PARTIALLY SUPPORTED and requires concrete source adapters and historical source-process data.

## 10. Outcome-process science

The outcome pipeline is best represented as:

`phenomenon → observation → report → ascertainment → scored outcome`.

This supports future estimation of reporting-delay distributions, censoring, competing ascertainment pathways and ascertainment bias. Such estimation requires actual outcome data; no repository-only correction can establish unbiasedness.

## 11. Evidence engineering

Each scientific object should preserve, where available:

`evidence_level; source_authority; source_identity; source_dependency; corroboration; contradiction; temporal_validity; provenance; uncertainty; revision_state; confidence; causal_status`.

The key second-order principle is that corroboration is not a count of documents. If multiple documents inherit the same upstream source, they do not provide independent corroboration.

Current epistemic/provenance architecture supports the fields conceptually and in relevant components. Full automatic source-independence inference requires explicit lineage and remains PARTIALLY SUPPORTED.

## 12. Uncertainty propagation

The architecture supports multiple uncertainty concepts but should preserve their origin rather than collapsing them:

`measurement → state → interaction/model → forecast → risk → warning`.

Potential components:

- measurement uncertainty;
- data/source uncertainty;
- parameter uncertainty;
- model disagreement/structural uncertainty;
- aleatoric uncertainty;
- epistemic uncertainty.

The audit does not justify pretending all are numerically estimable today. Where only bounded heuristics exist, the output must retain that status. Prospective calibration remains required for empirical probability claims.

## 13. Early-warning composition

A scientifically meaningful warning object should combine:

`signal + anomaly/change status + temporal context + evidence + provenance + uncertainty + horizon + severity rule + persistence/suppression state + timestamp`.

The warning is an operational statement that a predeclared criterion has been met; it is not itself proof of future harm.

Useful control mechanisms include persistence criteria, hysteresis, duplicate suppression, multi-signal confirmation and evidence thresholds. These are implementable only when a concrete warning target and operational loss function are registered.

## 14. Prevention architecture

The completed architecture permits a clean chain:

`prediction → warning → decision support → feasible response → action/no action → outcome → effectiveness`.

This permits prevention workflows to be built before prospective effectiveness is known. The system must preserve whether a warning was received, whether action was feasible, whether action occurred, and what happened afterward. It must not convert operational success into causal evidence automatically.

## 15. Scientific self-monitoring

The system should be able to state a conditional validity warning of the form:

`CURRENT CONDITIONS MAY BE OUTSIDE THE CONDITIONS UNDER WHICH THIS BEHAVIOUR WAS EVALUATED.`

This is scientifically different from claiming:

`THE PREDICTION IS FALSE.`

Candidate monitors:

- source availability and definition drift;
- population/denominator drift;
- surveillance intensity;
- feature missingness/disappearance;
- latency/revision changes;
- OOD/regime change;
- calibration degradation;
- residual degradation;
- model disagreement;
- interaction/coupling drift;
- outcome ascertainment drift.

Several primitives already exist; integrated production operation requires external data and predeclared thresholds.

## 16. Acquisition architecture

For each important scientific variable, a production registry should eventually contain:

`source; acquisition_method; cadence; latency; event_time; publication_time; acquisition_time; availability_rule; revision_policy; raw_preservation; validation; normalization; semantic_mapping; provenance; failure_detection; expected_missingness; scientific_consequence_of_delay`.

Acquisition classes must remain explicit:

`REAL-TIME / NEAR-REAL-TIME / PERIODIC / RETROSPECTIVE / STATIC`.

The repository currently provides infrastructure for temporal/provenance-aware processing but does not establish continuous acquisition of every identified Ceuta source. No source is labelled real-time without evidence of actual acquisition behaviour.

## 17. Research-method selection matrix

| Method family | Immediate scientific value | Implement now? | Reason |
|---|---|---|---|
| state-space/Kalman | latent noisy longitudinal state | NO generic implementation | target/observation model not registered |
| HMM/regime switching | discrete latent regimes | NO generic implementation | regime definition/data required |
| VAR/VARX/TVP-VAR | multivariate temporal dependence | CONDITIONAL | requires concrete regularly/appropriately sampled target system |
| Hawkes/point process | event excitation | CONDITIONAL | only event-arrival phenomena |
| survival/hazard | time-to-event/censoring | CONDITIONAL | outcome/event target required |
| mixed-effects/hierarchical | clustered population heterogeneity | CONDITIONAL | hierarchy/cohort required |
| graph dynamical systems | explicit network state evolution | CONDITIONAL | network + sufficient longitudinal observations |
| nonlinear ODE/SDE/delay | mechanistic dynamics | NO generic implementation | mechanism/identifiability absent |
| change-point detection | process transition detection | HIGH VALUE, target-dependent | concrete signal/reference needed |
| conformal prediction | finite-sample predictive sets under assumptions | CONDITIONAL | target, exchangeability/dependence handling and calibration protocol required |
| information theory | nonlinear/dependency diagnostics | CONDITIONAL | sample size/bias controls needed |
| Granger-type tests | predictive lead/lag diagnostics | CONDITIONAL | temporal design and stationarity/regime handling needed |
| copulas/tail dependence | joint extremes | CONDITIONAL | sufficient multivariate tail data required |
| EVT | extreme-event tails | CONDITIONAL | sufficient extreme observations required |
| VOI/optimal design | acquisition/measurement prioritisation | HIGH VALUE conceptually | requires decision loss, candidate measurements and uncertainty model |
| sequential decision theory | warning/action optimisation | CONDITIONAL | operational utility function required |

## 18. What is immediately constructible

The audit identifies a small set of central capabilities that can be developed without inventing data or model classes:

1. A formal scientific `I_t` / information-set contract in methodology and validation.
2. A reusable forecast-forensics report generated from existing PIT/provenance/fingerprint metadata.
3. A source-process event taxonomy using existing version/availability/revision metadata.
4. An explicit warning-context schema/contract if a concrete warning target is defined.
5. A capability matrix linking each production phenomenon to acquisition class and evidence/validation state.
6. A scientific self-monitoring registry that separates world/data/model/scientific-validity monitors.

These are architecture-level capabilities. They should be implemented only when their concrete schemas can be connected to existing contracts without duplicating existing state.

## 19. Immediate implementation gate

A candidate extension passes only if:

`SCIENTIFIC NEED → PHENOMENON → DATA → IDENTIFIABILITY → ASSUMPTIONS → IMPLEMENTABILITY → TESTABILITY → INCREMENTAL VALUE`.

Failure of any element means documentation/research classification rather than code.

## 20. Adversarial second-order scenarios

| Scenario | Current protection | Residual consequence |
|---|---|---|
| authentic PIT + biased measurement | PIT valid | measurement-process data required |
| correct marginals + changed coupling | marginal monitors may pass | interaction monitor needed for concrete system |
| independent calibration + wrong joint calibration | individual calibration insufficient | joint target data needed |
| dependent sources appear corroborative | declared lineage helps | hidden common source not identifiable |
| source latency creates false decline | availability metadata helps | source-process monitor needed |
| denominator change creates incidence spike | denominator metadata can expose | valid denominator data required |
| warning changes intervention regime | response lineage separates | effectiveness/causal analysis remains prospective |
| source disappears and phenomenon appears to decline | acquisition health can detect | world-state cannot be inferred without alternative measurement |
| multiple forecasts share one model | forecast provenance can expose identity | dependence-aware evaluation required |
| uncertainty low because structural uncertainty omitted | disagreement can reveal some risk | model-class adequacy remains empirical |
| A highly correlated but non-incremental | temporal incremental evaluation rejects | concrete target/evaluation required |
| true signal disappears under regime change | OOD/regime metadata may warn | prospective adaptation/validation required |

## 21. Final classification

### A — Already implemented and correctly exploited
PIT binding primitives; provenance/fingerprints; temporal eligibility; time-normalized longitudinal derivatives; calibrated final ensemble; uncertainty metadata; dependence-aware evaluation; immutable baselines; outcome ascertainment metadata; intervention/causal separation; descriptive propagation; prospective protocol; scientific contracts; runtime integrity.

### B — Implemented but still underexploited
Individual prediction forensic reconstruction; source-process interpretation; multisystem state composition; explicit warning context; model disagreement as a monitoring signal; scientific-validity monitoring as a unified conceptual registry; information-set methodology.

### C — Implementable immediately, but target-specific
Concrete change-point detection; multivariate/emergent anomaly detection; interaction/coupling drift detection; incremental predictive-value evaluation; source-intelligence automation; VOI calculation; richer warning hysteresis/suppression; physical-time lag features.

### D — Requires internal dependency
A generic capability requires a registered target phenomenon, explicit data contract, reference distribution or loss function, and corresponding test fixture before implementation. This applies to most advanced model families.

### E — Requires external data
Continuous source acquisition catalogue; population denominators; observation-process estimation; ascertainment-bias estimation; spatial propagation; intervention exposure; real-world response/outcome data.

### F — Requires prospective evidence
Predictive validity; calibration transport; superiority to baselines; operational effectiveness; intervention effects; causal validity; causal propagation.

### G — Plausible but not identifiable from current data
Hidden common upstream sources; absence of undisclosed preprocessing; unmeasured confounding; model-class adequacy from internal uncertainty alone.

### H — Not scientifically justified now
Generic advanced-model proliferation; automatic observation-frequency features; universal causal propagation; arbitrary composite risk scores; aggregate “health” scores; new microservices without a concrete scientific contract.

### I — Must remain outside architecture
Claims that CI proves scientific validity; claims that calibrated retrospective probabilities are prospectively valid; claims that descriptive propagation is causal; claims that operational response success proves prediction causality.

## 22. Completion rule for this mission

This document records the maximum current knowledge-to-capability extraction that can be justified from the audited architecture without manufacturing data, claims or complexity. It is not a claim that every future scientific method has been exhausted. It establishes the next implementation frontier and prevents prospective-evidence requirements from being mistaken for engineering blockers.

The mission remains open for implementation of any target-specific capability that subsequently satisfies the immediate implementation gate. No generic advanced method is added solely to enlarge the technology stack.
