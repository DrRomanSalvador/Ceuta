# CeutIA + SERPIENTE — Second-Order Scientific Extraction Audit 001

**Mission class:** second-order scientific extraction from the completed finite audit
**Date:** 2026-09-16
**Authoritative input state:**
- `GLOBAL_ENGINEERING_AUDIT = AUDIT_COMPLETE`
- `SCIENTIFIC_LIMITATION_RESOLUTION = COMPLETE`
- `PROSPECTIVE_PREDICTIVE_VALIDITY = NOT_ESTABLISHED`
- SERPIENTE `main`: `03cd2b3678a56e1b23480cf69113d0bdd97fc7f8`
- CeutIA scientific branch: `50cb91d39fe944bbaf91e45986941226c80d8fdf`
- SERPIENTE runtime validation `35071185835`: `SUCCESS`
- CeutIA scientific integration `35071683700`: `SUCCESS`
- PIT workflow `35070241485`: `FAILURE`; it is not positive evidence. PR #5 is merged, and the final `main` runtime validation is the applicable post-merge evidence.

This document is deliberately separate from `SCIENTIFIC_LIMITATION_RESOLUTION_MATRIX.md`. It does not reopen that mission and does not relabel its closed work. It extracts scientific consequences, capabilities, acquisition requirements, monitoring requirements and research opportunities exposed by that work.

## 1. Executive extraction

The completed audit produced a stronger scientific architecture than the individual repairs imply. The central consequence is that CeutIA + SERPIENTE can now preserve and reason about the provenance, temporal eligibility, epistemic status and downstream fate of an individual prediction rather than treating a prediction as an isolated numeric output.

The most important second-order consequences are:

1. A forecast is formally better understood as a function of a point-in-time information set, not merely a feature vector.
2. The system has the primitives required for individual-forecast forensic reconstruction and deterministic replay, subject to complete production lineage being supplied.
3. Time is now an explicit scientific dimension for derivative-like longitudinal quantities; observation order and physical elapsed time must not be conflated.
4. Probability semantics can be separated from raw scores and calibration status; a number in `[0,1]` is not thereby an empirically validated probability.
5. Observation and ascertainment processes are themselves potential sources of bias and must be represented separately from the phenomenon being measured.
6. Repeated forecasts define a longitudinal dependence structure and therefore an evaluation unit; forecast rows cannot automatically be treated as independent samples.
7. Baseline registration converts “improvement over baseline” into a predeclared comparative estimand rather than a retrospective choice.
8. Prediction, decision, intervention and causal effect form distinct epistemic layers and can support distinct research designs.
9. Propagation currently has descriptive/network-coverage semantics, not validated causal semantics; this is scientifically useful precisely because the distinction is preserved.
10. The architecture now has the primitives for scientific self-monitoring, but real monitoring of population, surveillance, intervention and regime validity requires live external data.

No additional mathematical model, microservice, arbitrary feature or speculative indicator is justified solely by this extraction.

## 2. Final-state verification

The requested final states were checked against repository data. SERPIENTE PR #5 is merged into `main`. Its dedicated PIT workflow failed on an intermediate PR commit and therefore is retained as a negative/diagnostic event, not as validation. The later `main` runtime validation succeeded on the requested final commit. CeutIA scientific integration also succeeded on the requested final commit.

The authoritative scientific matrix explicitly records completion of the limitation-resolution mission while retaining `PROSPECTIVE_PREDICTIVE_VALIDITY = NOT_ESTABLISHED`. The prospective protocol additionally requires point-in-time metadata, calibration metadata, OOD metadata, outcome ascertainment metadata, registered baselines and intervention separation before prospective eligibility.

## 3. Audit-of-the-audit: consequence extraction

| Completed component | Scientific assumption exposed | Failure mode removed | New information/capability | Classification |
|---|---|---|---|---|
| PIT feature binding | A forecast depends on what was knowable at origin | Detached/future feature set | Feature-level temporal/provenance identity and forecast binding | ALREADY SUPPORTED |
| PIT fingerprints | Feature values and lineage can change after creation | Silent feature mutation | Individual forecast integrity verification and replay anchor | ALREADY SUPPORTED |
| Point-in-time store | Historical truth and historical knowledge are different | Future information entering replay | Reconstructible historical visibility under declared timestamps | ALREADY SUPPORTED |
| Source/version/revision provenance | Measurements are versioned observations, not timeless facts | Silent replacement of revised data | Revision-aware forensic reconstruction | ALREADY SUPPORTED |
| Transformation lineage | Derived variables inherit temporal/provenance constraints | Hidden derivation leakage | Feature-level contamination analysis where lineage is declared | PARTIALLY SUPPORTED |
| Time-normalized trend/acceleration | Derivatives describe physical change, not observation count | Irregular sampling changes derivative magnitude | Physically interpretable longitudinal rates | IMPLEMENTED |
| Calibration correction | Probability semantics depend on calibration provenance | Mixing calibrated and uncalibrated outputs | Coherent final ensemble probability semantics | IMPLEMENTED |
| Uncertainty decomposition | Different uncertainty sources have different meanings | One undifferentiated uncertainty number | Measurement/parameter/structural/model-disagreement channels | ALREADY SUPPORTED |
| Dependence-aware evaluation | Repeated forecasts share information | False independent-sample inference | Declared-unit aggregate evaluation and clustered resampling | ALREADY SUPPORTED |
| Immutable baselines | Comparative utility must be defined before outcomes | Retrospective baseline selection | Auditable model-vs-baseline estimand | ALREADY SUPPORTED |
| Outcome ascertainment | Observed outcome is generated through a measurement process | Treating incomplete reporting as truth | Ascertainment-delay, censoring and selection metadata | ALREADY SUPPORTED |
| Intervention separation | Actions alter the data-generating process | Intervention outcomes interpreted as untreated validation | Separate prediction-effectiveness and intervention-effect estimands | ALREADY SUPPORTED |
| Causal identification gate | Association is not identification | Silent causal promotion | Explicit estimand/assumption/falsification/transportability layers | ALREADY SUPPORTED |
| Descriptive propagation separation | Co-occurrence is not mechanism | Network coverage interpreted as causal cascade | Explicit descriptive propagation semantics | ALREADY SUPPORTED |
| Temporal feedback rule | Instantaneous cyclic causality is not identifiable from an acyclic DAG | Invalid causal cycles | Requirement for time-unrolled feedback representation | ALREADY SUPPORTED |
| Regime/OOD metadata | Predictive validity is conditional on population/regime | Retrospective validity treated as universal | Regime-stratified prospective evaluation | PARTIALLY SUPPORTED |
| Scientific response lineage | Alert receipt/action is distinct from forecast correctness | Operational success attributed to prediction | Warning→receipt→decision→action→execution→outcome chain | ALREADY SUPPORTED |
| Cross-repository contract | Mathematical output and epistemic acceptance are distinct boundaries | Silent producer/consumer semantic drift | Versioned scientific interoperability | ALREADY SUPPORTED |
| Prospective protocol | Validity requires predeclared temporal/population rules | Retrospective methodological freedom | Locked future evaluation design | ALREADY SUPPORTED |

## 4. Information-set ontology: I_t

The audit justifies the following conceptual formulation:

`I_t = all information legitimately available to the forecasting process at forecast origin t`

`prediction_t = f(I_t, model_state_t)`

`X_t` is therefore a representation or projection of `I_t`, not necessarily the information set itself.

This distinction has direct consequences:

- **Training:** every training example must obey the information constraints corresponding to its historical origin.
- **Feature engineering:** derived features require temporal eligibility and lineage, not merely a timestamp on the final feature.
- **Replay:** replay must reconstruct the historical information set, not merely restore the current feature values.
- **Evaluation:** a forecast is eligible only if its information boundary is consistent with the declared protocol.
- **Baseline comparison:** model and baseline must operate on equivalent information sets.
- **Data acquisition:** latency and revision behaviour become scientific properties of the information process, not only engineering metrics.
- **Model comparison:** two models using nominally identical `X_t` can still differ scientifically if their hidden preprocessing or model state was formed from different information.

Current state: the repository already contains the principal PIT primitives. A complete external production feature-generation process is still required to prove that `I_t` has no undisclosed upstream component. This is a prospective evidence boundary, not a reason to add another speculative abstraction now.

## 5. Temporal ontology extracted from the audit

The architecture already distinguishes multiple temporal concepts for observations and outcomes. The second-order rule is now explicit:

`event_time != observation_time != acquisition_time != publication_time != availability_time != ascertainment_time != revision_time`

They answer different scientific questions:

- `event_time`: when the phenomenon occurred.
- `observation_time`: when a measurement describes the phenomenon.
- `acquisition_time`: when the system acquired it.
- `publication_time`: when the source made it publicly available.
- `availability_time`: when it became eligible for a given computational process.
- `ascertainment_time`: when the outcome was sufficiently established for its protocol state.
- `revision_time`/revision identity: which version of the observation is being evaluated.

A separate distinction is mandatory for temporal mathematics:

- observation lag = previous `k` observations;
- physical lag = elapsed time between observations.

SERPIENTE's current `StateSnapshot.lags` is an observation-order lag representation. It must not be interpreted as a physical-time lag. Trend and acceleration are already normalized by elapsed physical time. No further code change is justified until a model actually requires physical-time lag features; at that point those should be introduced as explicitly time-based quantities rather than silently changing the existing observation-order semantics.

Audited quantities:

- velocity/trend: physical-time normalized where currently implemented — IMPLEMENTED.
- acceleration: physical-time normalized where currently implemented — IMPLEMENTED.
- volatility of rate: derived from time-normalized rates — ALREADY SUPPORTED.
- observation-order lags: explicit by implementation semantics — ALREADY SUPPORTED, with semantic boundary documented here.
- moving averages: window semantics remain feature-dependent; no universal error was found because a window can legitimately be observation-count based. Any physical-time moving window must be explicitly time-based when introduced.
- hazards, temporal kernels and state-transition rates: no central current implementation was identified that justifies a speculative rewrite. REQUIREMENTS are protocol-specific.

## 6. Probability semantics

The audit establishes a useful hierarchy:

`raw score` → model output before probabilistic interpretation

`probability estimate` → output interpreted on a probability scale

`calibrated probability` → probability estimate with calibration procedure explicitly identified

`empirically validated probability` → calibrated probability whose calibration/performance has been demonstrated on appropriate held-out/prospective target data

`decision probability` → probability used inside a predeclared decision rule; it is not a new scientific probability type merely because a threshold is applied.

Current repository state:

- finite probability-domain enforcement — IMPLEMENTED;
- final SERPIENTE ensemble calibration — IMPLEMENTED;
- calibration diagnostics — ALREADY SUPPORTED;
- uncertainty decomposition — ALREADY SUPPORTED;
- prospective calibration/transport — REQUIRES PROSPECTIVE EVIDENCE;
- universal probability validity across future regimes — NOT ESTABLISHED.

No further probability-producing pathway should be created without declaring which level it represents.

## 7. Observation-process science

The audit reveals that the observation process can itself become scientifically informative. Changes in reporting frequency, healthcare utilisation, surveillance intensity or publication behaviour may reflect:

- a change in the underlying phenomenon;
- a change in surveillance effort;
- a change in access/utilisation;
- a source-process intervention;
- a reporting artefact;
- a missingness mechanism.

Therefore observation intensity should not automatically become a predictive feature. It should first be classified as one of:

1. nuisance/measurement process;
2. informative observation process;
3. surveillance indicator;
4. legitimate covariate;
5. separate signal requiring independent interpretation.

Current state: the temporal/provenance model can retain the relevant timestamps and source identity. A validated observation-process model is REQUIRES EXTERNAL DATA / REQUIRES PROSPECTIVE EVIDENCE. No automatic feature promotion is scientifically justified.

## 8. Outcome ascertainment as a data-generating process

Outcome time and ascertainment time are distinct in the current prospective protocol. This permits future analysis of:

- ascertainment delay distributions;
- source-specific reporting latency;
- censoring;
- missingness;
- competing outcomes;
- selection into ascertainment;
- revision dynamics;
- measurement-process changes.

The correct conceptual structure is:

`real-world outcome process → observation/reporting process → ascertainment process → scored outcome`

rather than treating the scored outcome as a direct transparent copy of reality.

Current state: metadata architecture is ALREADY SUPPORTED. Estimation of ascertainment-process bias requires real longitudinal outcome data and therefore REQUIRES EXTERNAL DATA / PROSPECTIVE EVIDENCE.

## 9. Repeated-forecast dependence

Repeated predictions are observations in the operational ledger but not automatically independent statistical units. The completed work therefore enables:

- cluster-level bootstrap;
- dependence-aware aggregate Brier uncertainty;
- temporal blocking;
- subject/event-level clustering where appropriate;
- effective-sample-size analysis when justified;
- dependence-aware calibration and model comparison.

Current state: the machinery is ALREADY SUPPORTED. The independent unit remains a property of the target-generating process and study design. Selecting it is REQUIRES EXTERNAL DATA / STUDY-SPECIFIC EVIDENCE.

Adversarial consequence: 10,000 hourly forecasts of one evolving process cannot be treated as equivalent evidence to 10,000 independent events merely because the row count is 10,000.

## 10. Baseline hierarchy

The audit justifies a hierarchy, but not universal inclusion of every baseline.

Potential comparator classes:

`MODEL → NAIVE → PERSISTENCE → SEASONAL → STATISTICAL → OPERATIONAL/EXPERT`

The required comparator depends on the target:

- persistent state targets require a persistence comparator where scientifically meaningful;
- periodic phenomena require a seasonal comparator;
- binary event targets require a prevalence/temporal-prevalence comparator where appropriate;
- operational systems should retain the pre-existing operational rule when it constitutes the real decision comparator;
- expert judgement is a comparator only when its construction and information set can be registered reproducibly.

The scientific estimand is not “model score minus arbitrary baseline”. It is comparative performance on the same eligible population, horizon, information set and outcome definition.

Current state: immutable registration and temporal protection are ALREADY SUPPORTED. The final comparator set is PROBLEM-SPECIFIC and REQUIRES PROSPECTIVE EVIDENCE before superiority claims.

## 11. Epistemic layer architecture

The repository already has a normative epistemic separation between observation, evidence, assertion, inference, hypothesis, signal, prediction and risk. The completed audit adds a useful operational interpretation:

`DESCRIPTIVE → PREDICTIVE → DECISIONAL → INTERVENTIONAL → CAUSAL`

These are not a quality ranking. They are different estimands and evidence requirements.

Current state:

- descriptive evidence/provenance separation — ALREADY SUPPORTED;
- prediction/decision separation — ALREADY SUPPORTED;
- intervention lane and counterfactual requirement — ALREADY SUPPORTED;
- causal identification and evidence gates — ALREADY SUPPORTED;
- empirical causal effect — REQUIRES EXTERNAL DATA / PROSPECTIVE EVIDENCE.

No additional generic layer object is justified merely for naming purposes; the existing contracts and governance already encode the material distinction.

## 12. Propagation taxonomy

Current trajectory propagation is descriptive/network coverage: it measures cross-domain co-occurrence/coverage within the supplied signal set. It is not evidence of physical, mechanistic or causal transmission.

The scientifically valid future taxonomy is:

- statistical propagation — dependence/association;
- temporal propagation — ordered lead/lag behaviour;
- spatial propagation — movement across geography;
- network propagation — spread through an explicitly represented network;
- mechanistic propagation — propagation supported by a mechanism model;
- causal propagation — propagation supported by causal identification and empirical evidence.

Different types require different evidence. They must not collapse into one undifferentiated “cascade” claim.

Current state: descriptive propagation is ALREADY SUPPORTED; temporal/spatial/network extensions are POSSIBLE only when corresponding data are available; mechanistic and causal propagation REQUIRE EXTERNAL DATA and PROSPECTIVE/EMPIRICAL EVIDENCE. No automatic implementation is justified now.

## 13. Evidence → capability map

The repository's currently identifiable scientific evidence is primarily encoded in normative specifications, epistemic contracts, prospective protocol documents and the completed audit rather than a dedicated machine-readable literature corpus. The `docs/external/{gemini,grok,perplexity}` directories contain no evidence files at the audited revision. Therefore no claim is made that an exhaustive external bibliography has been mined from repository storage.

| Evidence / methodological principle | Phenomenon | Measurement / variable consequence | Acquisition consequence | Model consequence | Validation consequence | Current classification |
|---|---|---|---|---|---|---|
| PIT temporal eligibility | historical information availability | availability/source/revision timestamps | retain source latency/revision | restrict features to `I_t` | point-in-time replay | ALREADY SUPPORTED |
| Feature provenance | measurement lineage | observation IDs/source versions/transforms | preserve lineage | bind feature identity | contamination audit | ALREADY SUPPORTED |
| Irregular-sampling mathematics | longitudinal change | elapsed-time deltas | retain event times | rates/acceleration use physical time | irregular-sampling regression tests | IMPLEMENTED |
| Probability calibration | binary risk | probability + calibration metadata | preserve calibration-set identity | calibrate final ensemble | Brier/log loss/calibration diagnostics | ALREADY SUPPORTED |
| Repeated-forecast dependence | longitudinal predictions | dependence unit | retain cluster identity | no automatic iid assumption | clustered/time-aware evaluation | ALREADY SUPPORTED |
| Outcome ascertainment | observed outcome | ascertainment/censoring/missingness | retain reporting process | exclude ineligible outcomes from scoring | ascertainment-bias analysis | ALREADY SUPPORTED / EXTERNAL DATA |
| Distribution/regime shift | changing population/process | OOD/regime labels | detect population/source changes | stratify/condition evaluation | regime-specific performance | PARTIALLY SUPPORTED |
| Causal identification | interventions/mechanisms | estimand/confounder/negative-control metadata | intervention exposure capture | causal model only under gates | falsification/identification | ALREADY SUPPORTED / EXTERNAL DATA |
| Operational response | warnings/actions | receipt/action/delay/capacity | event-level response logging | decision-response analysis | effectiveness study | ALREADY SUPPORTED / EXTERNAL DATA |
| Source dependence | evidence corroboration | source lineage/dependency | upstream-source identity | avoid pseudo-replication | dependence-aware evidence synthesis | PARTIALLY SUPPORTED |

## 14. Continuous acquisition classification

No variable should be called real-time merely because the system polls periodically. The scientific acquisition classes are:

- **REAL-TIME:** acquisition latency is sufficiently small relative to the phenomenon and is continuously available by design.
- **NEAR-REAL-TIME:** periodic/streaming acquisition with a non-negligible but operationally bounded latency.
- **PERIODIC:** scheduled publication/acquisition at a defined cadence.
- **RETROSPECTIVE:** available only after the relevant phenomenon or reporting window.
- **STATIC:** slowly changing reference information without a continuous acquisition requirement.

For each production variable the minimum future registry should capture: source, cadence, latency, availability rule, revision policy, provenance, failure detection, expected missingness, and scientific consequence of delay.

Current repository state: the data model can represent core temporal/provenance properties, and the runtime daemon can poll source adapters. A complete Ceuta production acquisition catalogue with validated cadence/latency for every scientific variable is REQUIRES EXTERNAL DATA. It must not be invented from code alone.

## 15. Four-system monitoring architecture

Continuous monitoring should remain four-dimensional rather than collapsing into a single health score.

| System | Signals | Criterion | Failure mode | Required response | Evidence needed |
|---|---|---|---|---|---|
| WORLD | target phenomenon, regime, interventions, environment | predeclared regime/phenomenon criteria | real-world regime change or intervention | downgrade/stratify/reevaluate | external observations |
| DATA | freshness, latency, missingness, revisions, source-process change | source-specific thresholds/rules | stale, missing, revised or biased data | quarantine/downgrade source | acquisition/provenance logs |
| MODEL | error, calibration, disagreement, residuals, OOD | locked validation criteria | drift, calibration loss, model disagreement | recalibrate/quarantine/escalate | prospectively observed outcomes |
| SCIENTIFIC VALIDITY | population, denominator, outcome definition, causal assumptions, surveillance process | predeclared invariants | assumption invalidation | block scientific promotion | study/process evidence |

Current state: individual elements exist across runtime, provenance, calibration, OOD and epistemic controls. A fully integrated four-system scientific-validity dashboard/decision gate is PARTIALLY SUPPORTED and would require live external data to become operationally meaningful. No aggregate “system score” is justified.

## 16. Scientific self-monitoring

The extraction identifies concrete assumption monitors that can be specified without inventing new predictive models:

1. source-definition/version change;
2. denominator/population-definition change;
3. population-composition shift;
4. surveillance/reporting-intensity shift;
5. intervention exposure/regime change;
6. disease/event regime change;
7. migration/flow regime change where relevant data exist;
8. climate/environment regime change where relevant data exist;
9. residual/calibration degradation;
10. model-disagreement increase;
11. feature disappearance or persistent missingness;
12. source acquisition failure;
13. outcome ascertainment-delay change;
14. outcome-definition/revision change;
15. relationship inversion between a modelled signal and its target.

Current classification:

- source acquisition failure: ALREADY SUPPORTED at runtime health level;
- feature/source temporal integrity: ALREADY SUPPORTED;
- calibration/model diagnostics: ALREADY SUPPORTED in validation components;
- population/surveillance/intervention/relationship-change monitoring: REQUIRES EXTERNAL DATA and PROSPECTIVE EVIDENCE for meaningful thresholds.

## 17. New high-value research capabilities

| Capability | Status | Reason |
|---|---|---|
| Individual prediction provenance | ALREADY SUPPORTED | Forecast identity, provenance and PIT fingerprint are persisted/bound. |
| Exact historical replay | PARTIALLY SUPPORTED | Historical visibility and fingerprints exist; complete undisclosed upstream preprocessing cannot be reconstructed from repository code alone. |
| Temporal forensic reconstruction | ALREADY SUPPORTED | Revision/availability/provenance metadata permit event-level reconstruction within declared lineage. |
| Feature-level contamination analysis | PARTIALLY SUPPORTED | Declared lineage is auditable; hidden external preprocessing is not observable. |
| Model-version comparability | ALREADY SUPPORTED | Model/baseline identity and immutable evaluation principles exist. |
| Regime-aware validation | PARTIALLY SUPPORTED | OOD/regime metadata and protocol exist; target-population evidence is external. |
| Model disagreement monitoring | ALREADY SUPPORTED | Model-disagreement is represented in the forecast contract; prospective meaning remains empirical. |
| Evidence-weighted model selection | REQUIRES IMPLEMENTATION | Would require a predeclared scientific weighting rule and validation showing that evidence quality improves model selection; not justified as an automatic feature yet. |
| Uncertainty-aware alerts | ALREADY SUPPORTED | Alert uncertainty and forecast uncertainty are represented; operational calibration remains empirical. |
| Dynamic evidence levels | ALREADY SUPPORTED | Epistemic state vocabulary and evidence gates exist. |
| Longitudinal risk trajectories | ALREADY SUPPORTED | Longitudinal state, trends, acceleration, volatility and forecast lineage exist. |
| Multidomain signal convergence | ALREADY SUPPORTED | Pattern/trajectory engines preserve domain structure and provenance; causal interpretation is not implied. |
| Prospective cohort construction | REQUIRES EXTERNAL DATA | Protocol exists, but a real prospectively observed cohort does not yet exist in the repository. |
| Intervention-effect evaluation | REQUIRES EXTERNAL DATA | Intervention lanes and metadata exist; real assignment/exposure/outcome data are required. |
| Adaptive scientific governance | PARTIALLY SUPPORTED | Fail-closed epistemic and validation gates exist; continuous assumption-monitoring requires production data. |
| Measurement-process modelling | REQUIRES EXTERNAL DATA | Temporal/provenance primitives exist, but empirical observation-process estimation requires data. |

`Evidence-weighted model selection` is deliberately not implemented in this mission because the scientific benefit, weighting rule and validation target are not yet sufficiently defined. It remains a research possibility rather than a material missing capability.

## 18. Adversarial second-order audit

| Technically correct but scientifically wrong scenario | Current detection | Classification |
|---|---|---|
| PIT-perfect data from a biased measurement process | Not necessarily detected by PIT itself | REQUIRES EXTERNAL DATA / PROSPECTIVE EVIDENCE |
| Perfect calibration after population shift | OOD/regime metadata can flag when available; calibration transport is not proven | PARTIALLY SUPPORTED / PROSPECTIVE EVIDENCE |
| Accurate prediction of an administrative reporting artefact | Temporal/provenance model can expose reporting process, but cannot infer truth without an external target | REQUIRES EXTERNAL DATA |
| Correct association during intervention-induced regime change | Intervention lineage separates the regime; causal meaning is not inferred | ALREADY SUPPORTED as an epistemic boundary |
| Multiple sources sharing one upstream source | Provenance/dependency controls can represent declared lineage; undisclosed common upstream origin is not identifiable | PARTIALLY SUPPORTED |
| Correct model uncertainty under an incorrect model class | Internal uncertainty cannot certify model-class adequacy | REQUIRES PROSPECTIVE EVIDENCE |
| Correct outcome time with incomplete ascertainment | Ascertainment/missingness/censoring metadata explicitly preserve non-eligibility | ALREADY SUPPORTED as a protection; bias estimation requires external data |
| Valid retrospective evaluation under a non-representative prospective regime | Prospective protocol explicitly retains regime/OOD metadata | PARTIALLY SUPPORTED; prospective evidence required |
| 10,000 repeated forecasts mistaken for 10,000 independent events | Dependence-aware evaluation prevents automatic iid inference | ALREADY SUPPORTED |
| Calibrated component averaged with an uncalibrated component | Final-ensemble calibration correction prevents this specific failure | IMPLEMENTED |
| Derivative changes solely because observation cadence changes | Time-normalized trend/acceleration regression protects against this | IMPLEMENTED |

## 19. Material implementation decision

The extraction does **not** justify a new production code feature at the current repository state.

Reason: the independently resolvable high-value consequences identified by this mission are already represented by existing contracts, provenance, PIT binding, validation, epistemic governance and runtime structures. The remaining high-value consequences are predominantly empirical: they require live external observations, real outcome ascertainment, population/regime data, intervention exposure or a production acquisition process.

One semantic boundary was explicitly extracted rather than changed in code: current SERPIENTE `lags` are observation-order lags, while derivative-like quantities are physical-time normalized. Introducing physical-time lags should be a separate, explicitly specified feature when a concrete model requires them. Silent reinterpretation would be scientifically worse than the current explicit distinction.

Therefore no arbitrary equations, ML components, data sources, microservices or ontology objects are added by this mission.

## 20. Classification ledger

Final classifications for material consequences identified by this extraction:

- **IMPLEMENTED:** elapsed-time derivative correction; final-ensemble calibration correction; associated adversarial regressions.
- **ALREADY SUPPORTED:** individual prediction provenance; PIT fingerprints; temporal/revision provenance; outcome ascertainment metadata; dependence-aware aggregate evaluation; immutable baselines; causal/intervention separation; epistemic states; descriptive propagation separation; model disagreement; uncertainty-aware alert metadata; longitudinal state/trajectory representation; prospective protocol.
- **PARTIALLY SUPPORTED:** complete PIT information-set reconstruction; hidden transformation detection; regime-aware validation; source-dependence detection; four-system integrated scientific-validity monitoring; exact replay where upstream processing is external.
- **REQUIRES IMPLEMENTATION:** evidence-weighted model selection only if a scientifically predeclared estimand and validation design is subsequently justified. It is not implemented now because those prerequisites are absent.
- **REQUIRES EXTERNAL DATA:** complete acquisition catalogue, observation-process modelling, ascertainment-process estimation, intervention exposure, population composition/regime monitoring and causal propagation evidence.
- **REQUIRES PROSPECTIVE EVIDENCE:** predictive validity, calibration transport, baseline superiority, real-world response effectiveness, intervention effects, causal validity and transportability.
- **NOT IDENTIFIABLE:** absence of undisclosed upstream preprocessing; undisclosed common-source dependence; causal mechanisms without identifying information.
- **NOT SCIENTIFICALLY JUSTIFIED:** adding generic probability layers, arbitrary propagation equations, automatic observation-intensity features, universal physical-time lag semantics, aggregate health scores or new services without a concrete phenomenon/data/validation target.

## 21. Completion condition

This mission is complete when the completed finite audit has been systematically mined for material second-order consequences, the consequences are classified, independently resolvable extensions have either been implemented or explicitly documented, acquisition and monitoring requirements are explicit, and external-evidence boundaries are separated from repository capabilities.

This document does **not** claim that all possible scientific discoveries have been exhausted. It records that the completed audit has been systematically mined for material second-order consequences without introducing unsupported complexity.

## 22. Final scientific state

`GLOBAL_ENGINEERING_AUDIT = AUDIT_COMPLETE`

`SCIENTIFIC_LIMITATION_RESOLUTION = COMPLETE`

`SECOND_ORDER_SCIENTIFIC_EXTRACTION = COMPLETE`

`PROSPECTIVE_PREDICTIVE_VALIDITY = NOT_ESTABLISHED`

The principal newly extracted scientific value is therefore not a new predictor. It is a stronger architecture for preserving the conditions under which a prediction can legitimately be interpreted, replayed, challenged, compared, monitored and eventually validated against the real world.
