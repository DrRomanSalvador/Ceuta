# ESTRATEGA ENGINEERING HANDOFF 001

## Purpose

Determine and, where locally executable, implement the minimum shared capability that converts governed evidence/model outputs into an auditable actionability assessment for two distinct clients: PERSONA and ESTADO.

Do not build a parallel decision engine if existing decision/alert/response/outcome primitives can satisfy the contract.

## Problem

CEUTIA already contains executable scientific and decision primitives, but the verified repository evidence does not yet establish a single end-to-end client-facing actionability contract linking applicability, risk, options, decision-support, intervention exposure, outcome and evaluation.

## Scientific basis

The ESTRATEGA mission requires explicit separation of:

- observation vs evidence;
- evidence strength vs event probability;
- association vs causal effect;
- prediction vs certainty;
- decision-support vs decision authority;
- intervention execution vs intervention effectiveness;
- output vs outcome;
- engineering test status vs scientific validation.

## Client need

PERSONA requires contextualized, safe, uncertainty-explicit next-action support.

ESTADO requires territorial decision-support covering prevention, surveillance, preparedness, resources, response and evaluation.

The two products must share governed evidence/provenance but must not silently share client semantics or authority.

## Affected objects to reconcile before implementation

1. Existing decision layer, especially `backend/app/core/decision/decision_system.py`.
2. Existing alert governance and response coupling.
3. Existing evidence/epistemic contracts.
4. Existing temporal/vintage contracts.
5. Existing outcome/decision persistence.
6. Existing mission/control-plane provenance and lifecycle state.

## Required canonical actionability object

The implementation must preserve, at minimum:

```text
assessment_id
client_type
subject_or_territory
problem_definition
population_scope
denominator_id
evidence_refs
evidence_level
applicability_status
applicability_reasons
risk_state
risk_probability
risk_uncertainty
consequence
exposure
time_horizon
alternative_explanations
options
resource_requirements
potential_harms
reversibility
recommended_next_step
decision_authority
activation_triggers
withdrawal_triggers
monitoring_indicators
outcome_definition
evaluation_plan
provenance
created_at
information_cutoff
expiry
status
```

This is a minimum semantic contract, not permission to duplicate existing models. Reuse existing canonical types when they are semantically equivalent.

## Option semantics

Each option must preserve:

```text
option_id
description
target
mechanism
expected_effect
required_resources
time_to_effect
risks
reversibility
implementation_constraints
monitoring_requirements
withdrawal_conditions
```

No option may be promoted solely because it is computationally available.

## Mathematical requirements

Risk-supporting probabilities must be traceable to a calibrated model or explicitly represented as unavailable/uncalibrated. Do not synthesize probabilities from evidence confidence.

If utility/loss is used, preserve the decision-maker, horizon, objective, constraints and assumptions. Reuse existing `DecisionContext`, `DecisionOption`, `ScenarioOutcome` and risk-policy machinery where appropriate.

For deep uncertainty, represent scenario distributions or bounded alternatives rather than a forced point estimate.

For prioritization, preserve explicit criteria and provenance; do not introduce an opaque composite score without a documented decision rationale and sensitivity/robustness treatment.

## Temporal semantics

The actionability contract must distinguish, when applicable:

```text
event_time
knowledge_time
observation_time
publication_time
revision_time
ingestion_time
information_cutoff
forecast_horizon
intervention_window
outcome_window
expiry
```

Historical decisions must not consume future revisions unavailable at the decision time.

## Failure modes to block

- evidence transported across materially different populations without an uncertainty state;
- resident denominator substituted for exposed/present denominator without justification;
- prediction presented as certainty;
- evidence confidence presented as event probability;
- correlation presented as causal effect;
- recommendation presented as authorized decision;
- executed intervention presented as successful intervention;
- alert generation counted as alert utility;
- complex model accepted without baseline incremental value;
- simulation presented as validated digital twin;
- CI success presented as scientific validation;
- missing denominator hidden by numerator-only rates;
- changed reporting process interpreted as changed phenomenon;
- expired recommendation remaining active;
- unresolved contradiction silently averaged;
- non-identifiable state forced into a unique estimate.

## Test requirements

### Contract tests

- required identity and client fields;
- PERSONA/ESTADO semantic separation;
- provenance completeness;
- information-cutoff enforcement;
- expiry and withdrawal semantics;
- authority boundary;
- uncertainty preservation.

### Statistical tests

- no conversion of confidence/evidence score into probability;
- denominator changes alter rates only through explicit denominator inputs;
- calibrated probabilities remain within model contract;
- scenario probabilities preserve valid normalization;
- sensitivity to alternative assumptions is observable;
- baseline comparison is explicit where model complexity is introduced.

### Adversarial tests

- stale source revision;
- denominator mismatch;
- changed ascertainment/reporting;
- missing data;
- contradictory sources;
- non-identifiable latent state;
- uncalibrated prediction;
- impossible resource requirement;
- expired alert;
- unauthorized decision actor;
- intervention executed but outcome unchanged;
- outcome changed for an alternative reason;
- false positive / false negative asymmetry;
- alert received but not acted upon.

### Integration tests

Trace at least:

```text
EVIDENCE
 -> APPLICABILITY
 -> RISK
 -> OPTION
 -> DECISION SUPPORT
 -> INTERVENTION EXPOSURE
 -> OUTCOME
 -> EVALUATION
```

and verify that each transition preserves identity and provenance.

## Acceptance criteria

1. Existing canonical decision/alert/response/outcome contracts are reused where possible.
2. PERSONA and ESTADO outputs are semantically distinguishable at runtime.
3. Every actionable assessment carries evidence, applicability, uncertainty, provenance and expiry.
4. No recommendation path grants decision authority.
5. No probability is emitted without a valid probabilistic source/calibration state.
6. Dynamic denominators cannot be silently replaced by resident population.
7. Alert utility cannot be claimed without response-chain evidence.
8. Outcome evaluation records alternative explanations and causal status.
9. The implementation remains fail-closed where mandatory evidence or authority is absent.
10. Tests demonstrate the above invariants.
11. CI execution is required before promotion to `INTEGRATION_TESTED`.
12. Scientific/prospective/operational/client validation remain separate states and are not promoted by software tests alone.

## Capability boundary

Until the acceptance criteria are demonstrated, the capability state is `FORMALIZED` or `IMPLEMENTED_PENDING_VERIFICATION`, not `SCIENTIFICALLY_VALIDATED`, `OPERATIONALLY_VALIDATED`, `CLIENT_VALIDATED` or `ESTABLISHED`.

## Expected client utility

PERSONA: a traceable path from a person's stated situation to evidence-applicable options, uncertainty, resources and next action without artificial authority.

ESTADO: a traceable path from a territorial signal/state to scenarios, intervention options, resource implications, activation/withdrawal criteria and measurable outcomes.

## Required downstream handoffs

If existing implementation is insufficient:

- FORJA: formal utility/loss/reversibility and uncertainty requirements;
- CRONOS: complete temporal/vintage implementation and leakage tests;
- NOTARIO: claim/evidence/provenance/decision/outcome lineage;
- ESPÍA: empirical evidence gaps and identification questions;
- CENTINELA: alert-to-response contract and decision-effectiveness measurement.

A handoff is not completion. ESTRATEGA remains responsible for assessing resulting client utility after implementation.
