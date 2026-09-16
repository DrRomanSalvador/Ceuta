# MASTER SCIENTIFIC DOSSIER EXECUTION 001

Mission: convert the supplied scientific dossier into real, bounded, verifiable CeutIA/SERPIENTE capability without reconstructing existing work or promoting engineering state into scientific validity.

Execution branch: `scientific-traceability-crossrepo`
Authoritative repositories: `DrRomanSalvador/Ceuta`, `DrRomanSalvador/SERPIENTE`

## 1. Central scientific model

The dossier is accepted as an architectural principle rather than as evidence that CeutIA/SERPIENTE already possess the claimed capabilities.

Canonical loop:

`REALITY → PHENOMENON → OBSERVATION → MEASUREMENT → OBSERVATION PROCESS → ACQUISITION → TEMPORALITY → PROVENANCE → EVIDENCE → EVENT → SIGNAL → STATE → TRAJECTORY → INTERACTION → DYNAMICS → PREDICTION → UNCERTAINTY → DECISION → INTERVENTION → OUTCOME → EVALUATION → LEARNING → MODEL REVISION → ONTOLOGY REVISION`

The key scientific invariant is that each arrow is a distinct transformation with its own assumptions, observables and validation requirement.

## 2. Finding classification

### F01 — Point-in-time and provenance

Status: `IMPLEMENTED_BUT_UNVERIFIED`

SERPIENTE documents point-in-time validation, revision-aware history and provenance. Its scientific integration contract requires information cutoff, observation vintage, feature availability, forecast origin and a point-in-time fingerprint. CeutIA validates prediction availability at decision time through its cross-repository consumer.

Remaining limitation: semantic PIT binding of the actual model-input derivation to the information set H_t is not yet established. A fingerprint or schema-compatible payload is insufficient to prove that the exact features used by a model were derivable from H_t.

Required external handoff: `CROSSREPO-PIT-BINDING-001`.

### F02 — Observation process

Status: `IMPLEMENTED_BUT_UNVERIFIED`

SERPIENTE exposes an `ObservationProcessDescriptor` containing variable definition, measurement process, denominator, coverage, bias, measurement error, temporal resolution and source. This is materially stronger than treating source values as direct observations of reality.

Remaining limitation: the descriptor does not itself establish that the declared process matches the deployed data-generating process. Empirical measurement validation remains external.

### F03 — Dynamic denominators and exposed population

Status: `PARTIAL`

The architecture already requires explicit denominator semantics in state-level actionability and recognizes that resident population is not universally valid as the exposure denominator. The exposed/present population problem has been formalized conceptually.

Remaining limitation: operational Ceuta exposure estimation still requires independent stocks/flows, mobility, occupancy, service-use or equivalent evidence. A single digital mobility provider cannot establish the denominator.

### F04 — Latent state with uncertainty

Status: `IMPLEMENTED_BUT_UNVERIFIED`

SERPIENTE implements longitudinal state construction, events, signals, patterns, trajectories and explicit uncertainty components. CeutIA preserves uncertainty in decision and epistemic contracts.

Remaining limitation: executable state estimation is not equivalent to empirical identification of the latent state. The target state, observation model, missingness assumptions and out-of-sample performance require validation against real data.

### F05 — Locked prospective validation

Status: `SCIENTIFICALLY_UNVALIDATED`

The repositories contain chronological holdout, calibration, out-of-sample scoring, baseline comparison, drift checks and prospective-validation infrastructure.

The empirical requirement remains open: a predeclared future prospective population and outcome window must be observed without using future information. Historical fit, replay and successful tests cannot close this frontier.

### F06 — Explicit decision loss / utility

Status: `IMPLEMENTED`

CeutIA already contains a decision subsystem with scenarios, utilities, harms, regret, constraints, value-of-information concepts and human review/abstention. ESTRATEGA's actionability layer was deliberately kept as a semantic boundary and did not create a second decision engine.

Remaining limitation: a decision utility implementation is not evidence that its loss function is empirically appropriate for a real operational client. That requires predeclared decision context and outcome evaluation.

### F07 — Intervention and outcome registry

Status: `PARTIAL → IMPLEMENTED_BOUNDARY`

SERPIENTE already records prospective forecast outcomes. CeutIA has an authorized action gateway and durable decision/outcome persistence. The newly implemented response lifecycle closes a major semantic gap by explicitly separating warning, decision, action, response eligibility, non-execution, intervention exposure, outcome ascertainment and causal status.

New artifacts:

- `DrRomanSalvador/SERPIENTE: backend/app/response_ledger.py`
- `DrRomanSalvador/SERPIENTE: backend/tests/test_response_ledger.py`
- `DrRomanSalvador/Ceuta: backend/app/core/scientific/response_consumer.py`
- `DrRomanSalvador/Ceuta: backend/tests/test_response_consumer.py`

The new contract explicitly supports `NO_RESPONSE`; therefore failure to act is observable rather than silently disappearing.

### F08 — Regime and measurement change

Status: `PARTIAL`

SERPIENTE contains data-process-change detection, explicit regime/change screening and distribution-drift testing. The system therefore does not assume that every observed shift is a phenomenon shift.

Remaining limitation: prospective operational performance across actual regime changes and measurement-system changes is not established.

### F09 — Benchmark against simple models

Status: `IMPLEMENTED_BUT_UNVERIFIED`

SERPIENTE contains prevalence/seasonal baselines and benchmark-family semantics. The scientific contract distinguishes benchmark families and excludes benchmarks only with an explicit reason.

Remaining limitation: paired predeclared baseline transport using only origin-time information remains an explicit frontier. A complex model cannot claim incremental value merely because it beats an internally reconstructed or retrospectively selected comparator.

### F10 — Alert governance, damage and withdrawal

Status: `IMPLEMENTED_BUT_OPERATIONALLY_UNVALIDATED`

CeutIA contains alert/decision controls, expiry-aware actionability, human review, abstention and downstream action authorization. The architecture explicitly separates warning quality from response execution and effectiveness.

Remaining limitation: operational alert utility requires real measurement of warning receipt, interpretation, decision, action/non-action, delay, capacity, outcomes and alert burden/fatigue. No operational effectiveness claim is made.

## 3. Scientific claims that remain prohibited

The implementation must not claim that CeutIA/SERPIENTE currently:

- detects crises in the validated empirical sense;
- predicts general deterioration in deployment;
- identifies causes;
- recommends effective interventions;
- measures resilience as an empirically validated construct;
- detects tipping points as a validated operational capability;
- learns causally from outcomes;
- prevents harm.

Each statement requires a separately defined estimand, population, information set, outcome, validation protocol and evidence boundary.

## 4. Highest-centrality engineering result from this execution

The most material executable gap found after auditing the current architecture was F14: the warning-response boundary.

Predictive validity, response execution, response effectiveness and operational utility are four distinct estimands. The system therefore now has an explicit response lifecycle contract rather than relying on temporal association between warning, action and outcome.

Required chain:

`WARNING → DECISION → RESPONSE ELIGIBILITY → ACTION / NO ACTION → EXECUTION STATUS → INTERVENTION EXPOSURE → OUTCOME ASCERTAINMENT → COUNTERFACTUAL / CAUSAL STATUS`

The implementation deliberately does not infer any missing stage.

## 5. Adversarial invariants added

The response boundary rejects or explicitly represents:

- warning without response;
- response without decision;
- action without decision;
- action before decision;
- eligible non-response without a non-execution reason;
- outcome without intervention exposure;
- outcome timestamp without outcome identity;
- outcome before action;
- causal identification without counterfactual reference;
- causal identification without outcome ascertainment provenance;
- naive timestamps;
- executed response outside its declared eligible window.

## 6. Validation state

The new focused test suites have been persisted but were not executed in the current environment. No CI-green claim is therefore made.

The scientific state remains bounded:

`ENGINEERING CONTRACT IMPLEMENTED`
`≠`
`PROSPECTIVE VALIDITY`
`≠`
`RESPONSE EFFECTIVENESS`
`≠`
`CAUSAL EFFECT`
`≠`
`OPERATIONAL UTILITY`.

## 7. Remaining high-centrality work

1. F01: producer-side semantic PIT binding in SERPIENTE.
2. F02: immutable revision/competing-source outcome ascertainment in CeutIA.
3. F03: real prospective evaluation population/outcomes.
4. F04: paired predeclared baseline transport.
5. F07/F12: real intervention-response-outcome feedback data.
6. F08: prospective regime/measurement-change validation.
7. F10/F14: operational response utility and causal effectiveness under an explicit counterfactual design.
8. Risk decomposition formalization remains delegated to scientific validation rather than invented by the orchestration layer.

## 8. Fixed-point criterion for this dossier execution

The dossier is not declared scientifically complete. The current execution reaches a bounded engineering/scientific-governance fixed point only when every implementable, non-redundant capability that does not require external empirical evidence has been either implemented or explicitly handed off.

The remaining empirical claims are intentionally blocked rather than converted into software assertions.
