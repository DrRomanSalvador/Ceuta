# ESTRATEGA EXECUTION CHECKPOINT 002

## Execution state

Canonical mission: `ESTRATEGA`
Repository: `DrRomanSalvador/Ceuta`
Working branch: `maximum-knowledge-to-capability`
State: `RUNNING`
Internal work exhausted: `FALSE`

## Re-audit performed

The previous checkpoint and engineering handoff were recovered. The existing decision subsystem was inspected rather than duplicated.

Verified existing capabilities include:

- `DecisionSystem`: robust, utility, regret and harm-minimization modes; constraints; abstention; human review policy; value-of-information ranking.
- `DecisionControlPlane`: evidence assessment, conflict handling, uncertainty, scenario representation, policy gating, decision manifests and hash-linked audit events.
- `DecisionFeedbackService`: persisted decision outcomes and retrospective utility/harm evaluation.
- `EpistemicEngine`: explicit epistemic states and a hard distinction between evidence confidence and calibrated event probability.

These components are reusable and remain authoritative for decision selection/control.

## What changed

A new semantic orchestration contract was implemented at:

`backend/app/core/actionability.py`

and exposed through:

`backend/app/core/__init__.py`

A focused contract suite was added at:

`backend/tests/test_actionability_contract.py`

The new capability does not rank decisions or authorize interventions. It provides the missing traceable boundary between governed evidence and downstream decision/outcome semantics.

## Implemented capability

`ActionabilityAssessment` now explicitly represents:

- PERSONA vs ESTADO client semantics;
- population scope and explicit denominator identity;
- evidence references and evidence level;
- applicability and reasons;
- risk state, calibrated-probability status and uncertainty;
- consequence, exposure and horizon;
- alternative explanations;
- candidate options and implementation constraints;
- resources, harms and reversibility;
- decision authority as an explicit field rather than implicit authority;
- activation/withdrawal/monitoring semantics;
- outcome and evaluation definitions;
- provenance;
- information cutoff and expiry;
- event/observation/publication/revision/ingestion timestamps;
- intervention/outcome windows;
- explicit actionability maturity state.

`ActionabilityTrace` now distinguishes actionability-only, recorded decision, recorded intervention, observed outcome and evaluated stages. Missing stages are never inferred.

## Important correction during implementation

The first draft attempted to impose a total chronological ordering on event, observation, publication, revision and ingestion timestamps. That was rejected and corrected. These timestamps have different semantics and must remain independently represented; a revision can follow ingestion, and ingestion order cannot substitute for event time.

## What was discovered

1. The repository already contains enough decision primitives that a second decision engine would be architectural duplication.
2. The missing layer was primarily semantic composition and maturity gating, not another optimizer.
3. Existing `EpistemicEngine` correctly prevents evidence confidence from being treated as calibrated probability.
4. The existing decision feedback layer observes utility/harm outcomes but does not by itself establish intervention effectiveness or causal effect.
5. The actionability contract therefore must terminate in explicit evaluation status rather than infer efficacy from execution or outcome observation.

## Newly identified scientific/engineering issue

`backend/app/core/epistemic.py` currently computes `risk_score` using both event probability and `evidence_confidence`, and attenuates it with `(1 - uncertainty)`. This couples epistemic support quality to the magnitude of risk itself. That can make a poorly observed but potentially high-consequence event appear low-risk merely because evidence is weak.

This is not corrected by ESTRATEGA through an arbitrary new formula. It is a scientific formalization issue requiring explicit treatment by FORJA/ESPÍA and reconciliation with the existing risk policy. The distinction required is at least:

`risk magnitude / consequence model`
separate from
`epistemic confidence / identifiability / uncertainty`.

A calibrated event probability, when available, must remain distinct from evidence confidence.

## New decision made possible

CEUTIA can now represent a governed actionability assessment without pretending that a decision has been authorized or an intervention has been validated. This permits downstream clients to distinguish:

`knowledge only`
→ `contextually actionable`
→ `decision support`
→ `intervention-relevant`
→ `prospectively evaluable`
→ `outcome validated`

without collapsing these states.

## New outcome that must be measured

For material actionability claims, the minimum downstream outcome chain is:

`DECISION → INTERVENTION EXPOSURE → OBSERVED OUTCOME → EVALUATION`

with causal status explicitly recorded. Alert generation alone remains insufficient evidence of utility.

## Rejected claims

The following claims remain explicitly rejected:

- actionability contract = scientific validation;
- candidate option = authorization;
- decision execution = intervention effectiveness;
- observed outcome = causal effect;
- engineering tests = prospective validation;
- evidence confidence = event probability;
- resident population = universally valid denominator;
- timestamp sequence = temporal semantics.

## Validation status

The new tests are persisted but have not been executed by a remote CI run in this session. The repository's CI workflow is manually dispatched, while push validation targets `main`; therefore this branch cannot be honestly marked CI-green from the available execution interface.

No scientific, prospective, operational or client validation is claimed.

## Required external work

### FORJA / ESPÍA

Formalize and test the separation between risk magnitude, event probability, evidence confidence, identifiability and epistemic uncertainty in the existing risk calculation. Determine whether the current formula is scientifically admissible for any intended use case and define replacement semantics if not.

### CRONOS

Reconcile actionability information-cutoff, forecast-horizon, expiry, intervention-window and outcome-window semantics with existing vintage/revision machinery and historical leakage tests.

### NOTARIO

Extend claim/evidence/provenance lineage so an actionability assessment can be reconstructed from source evidence through inference and decision-support output without conflating implementation state with evidence state.

### CENTINELA

Reconcile `ActionabilityTrace` with alert receipt, interpretation, decision, action and non-action reasons so alert utility is measurable at the decision boundary.

### INGENIERO

Integrate the actionability contract with existing canonical decision/control/outcome types where semantic identity is demonstrated. Do not create a parallel decision state machine.

## Second-order consequences discovered

1. Once actionability maturity is explicit, client-facing output can be gated by maturity rather than by the mere existence of a recommendation.
2. Explicit expiry creates a new operational obligation: stale actionability must be withdrawn or re-evaluated rather than silently reused.
3. Explicit denominator identity creates a dependency from actionability to exposure/population validity; an invalid denominator can downgrade otherwise strong evidence.
4. Explicit decision authority prevents the system from silently converting analytical output into institutional action.
5. Outcome definitions create a dependency on post-decision observation infrastructure; actionability cannot become outcome-validated merely through software state transitions.

## Third-order consequences discovered

1. If actionability is used to prioritize interventions, the prioritization itself becomes an intervention whose downstream effects must be evaluated.
2. If clients adapt behavior to repeated recommendations or alerts, the observation process can change; future measurements may therefore reflect both phenomenon and system-induced behavior.
3. If actionability maturity becomes a KPI, teams may optimize the number of "actionable" outputs rather than actual outcomes. The maturity state must therefore not be treated as a success metric.
4. If recommendations systematically change which cases enter observation, selection effects can contaminate later outcome evaluation; evaluation design must retain the exposure and comparison structure needed to interpret outcomes.

## Current next queue

1. Resolve the risk-score scientific semantics through FORJA/ESPÍA.
2. Reconcile temporal semantics with CRONOS.
3. Reconcile provenance with NOTARIO.
4. Reconcile alert-response trace with CENTINELA.
5. Integrate actionability with existing decision/control/outcome contracts through INGENIERO.
6. Re-audit second- and third-order consequences after those reconciliations.
7. Execute a final cross-mission fixed-point audit before any `INTERNAL_WORK_EXHAUSTED = TRUE` declaration.
