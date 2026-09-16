# ESTRATEGA EXTERNAL HANDOFF 002

## Handoff A — FORJA / ESPÍA: risk semantics

MISSION: `FORJA` + `ESPÍA`

DISCOVERY:
The existing `calculate_risk` implementation combines evidence confidence, event probability and uncertainty into the risk magnitude. The current semantics are not yet demonstrated to preserve the distinction between how dangerous an event is and how well it is observed/identified.

SCIENTIFIC_BASIS:
Risk assessment under uncertainty requires separation of the target quantity from uncertainty about that quantity. Evidence quality/confidence is not itself event probability. Absence or weakness of evidence cannot safely be treated as evidence of low consequence.

DECISIONAL_RELEVANCE:
Risk feeds actionability and therefore can alter prioritization, escalation and abstention. An incorrect attenuation can suppress action for poorly observed high-consequence states.

AFFECTED_OBJECTS:
`backend/app/core/epistemic.py`; downstream risk/actionability consumers.

CURRENT_CAPABILITY:
The code distinguishes calibrated event probability from evidence confidence at the type level, but the risk-score calculation combines them.

MISSING_CAPABILITY:
A formally justified risk representation separating magnitude/consequence, event probability where identifiable, epistemic uncertainty, exposure and confidence/identifiability.

MATHEMATICAL_REQUIREMENT:
Define the target estimand(s), uncertainty semantics and admissible aggregation. Demonstrate behavior for calibrated probability, unknown probability, weak observation and high-consequence/low-observability cases.

DATA_REQUIREMENT:
Representative validation cases with known or adjudicated event rates, observation quality and consequence scales where possible.

TEMPORAL_REQUIREMENT:
Evaluate by information cutoff and horizon; do not use future evidence to assess past risk.

UNCERTAINTY_REQUIREMENT:
Keep epistemic uncertainty and aleatory/event uncertainty distinguishable where the data support it.

FAILURE_MODES:
Risk suppressed by low evidence confidence; confidence interpreted as probability; unknown state forced into low risk; high consequence hidden by observation weakness; denominator/exposure omitted.

SECURITY_IMPLICATIONS:
A manipulated or degraded observation process could artificially reduce apparent risk if evidence quality is embedded in magnitude.

PERSISTENCE_REQUIREMENT:
Record formula/version, target quantity, probability status, uncertainty components and assumptions.

VALIDATION_REQUIREMENT:
Unit tests are insufficient. Require scientific specification plus adversarial and prospective evaluation before any stronger capability state.

ACCEPTANCE_CRITERIA:
No risk output can silently treat evidence confidence as event probability; behavior is documented for identifiable and non-identifiable states; high-consequence/low-observability cases do not collapse by construction.

DEPENDENCIES:
CRONOS for cutoff/horizon; NOTARIO for formula/provenance; CEUTIA denominator/exposure contracts.

PROVENANCE:
Discovery derived from direct inspection of `backend/app/core/epistemic.py` during ESTRATEGA execution.

PRIORITY: HIGH

REASON_FOR_HANDOFF:
The scientific design of risk semantics is outside ESTRATEGA's authority to invent ad hoc.

---

## Handoff B — CRONOS: actionability temporal semantics

MISSION: `CRONOS`

DISCOVERY:
Actionability now records event, observation, publication, revision and ingestion timestamps plus information cutoff, forecast horizon, intervention window, outcome window and expiry.

SCIENTIFIC_BASIS:
These timestamps have distinct meanings and cannot be collapsed into ingestion order or an artificial total ordering.

DECISIONAL_RELEVANCE:
Historical decision reconstruction and prospective evaluation depend on using only information available at the decision cutoff and respecting expiry.

AFFECTED_OBJECTS:
`backend/app/core/actionability.py` and existing temporal/vintage contracts.

CURRENT_CAPABILITY:
The actionability contract preserves the fields independently and validates timezone-aware timestamps.

MISSING_CAPABILITY:
Formal integration with existing vintage selection, revision handling and leakage controls.

MATHEMATICAL_REQUIREMENT:
None beyond temporal indexing and cutoff-consistent dataset construction; exact semantics should be inherited from existing temporal contracts.

DATA_REQUIREMENT:
Versioned observations and revisions sufficient to reconstruct information sets.

TEMPORAL_REQUIREMENT:
Explicit information-set reconstruction at decision time.

UNCERTAINTY_REQUIREMENT:
Revision uncertainty and observation delay must remain distinguishable from phenomenon uncertainty.

FAILURE_MODES:
Future revision leakage; stale actionability reused after expiry; publication time substituted for event time; ingestion order treated as phenomenon chronology.

SECURITY_IMPLICATIONS:
Temporal leakage can create false retrospective performance and conceal operational failure.

PERSISTENCE_REQUIREMENT:
Persist information cutoff, source version/vintage and expiry with every actionability assessment.

VALIDATION_REQUIREMENT:
Historical leakage tests plus prospective temporal validation.

ACCEPTANCE_CRITERIA:
An assessment reconstructed for a past cutoff cannot consume evidence unavailable at that cutoff; expiry is enforceable.

DEPENDENCIES:
Existing temporal/vintage layer; NOTARIO provenance.

PROVENANCE:
Derived from ESTRATEGA actionability implementation and temporal audit.

PRIORITY: HIGH

REASON_FOR_HANDOFF:
Temporal infrastructure is CRONOS's domain; ESTRATEGA must consume it rather than recreate it.

---

## Handoff C — NOTARIO + CENTINELA: trace integration

MISSION: `NOTARIO` + `CENTINELA`

DISCOVERY:
`ActionabilityTrace` establishes decision → intervention → outcome → evaluation stage separation, but existing audit/alert response infrastructure must be reconciled so the same identifiers and provenance are preserved end to end.

SCIENTIFIC_BASIS:
Alert generation, decision, intervention and outcome are different observables. Their causal/utility status cannot be inferred from one another.

DECISIONAL_RELEVANCE:
The utility of an alert depends on whether it changes an informed decision and produces an observable downstream effect, including non-action.

AFFECTED_OBJECTS:
`ActionabilityTrace`; existing decision audit chain; alert governance; response coupling; outcome persistence.

CURRENT_CAPABILITY:
Decision audit events and decision outcomes already exist. Actionability now adds an explicit semantic chain.

MISSING_CAPABILITY:
A shared cross-layer identifier/provenance contract linking alert receipt, interpretation, decision, action/non-action, outcome and evaluation.

MATHEMATICAL_REQUIREMENT:
Decision-effectiveness metrics must be defined separately from predictive metrics; causal status must remain explicit.

DATA_REQUIREMENT:
Receipt time, interpretation/decision record, action exposure, non-action reason, outcome and evaluation data.

TEMPORAL_REQUIREMENT:
Preserve event times and information cutoffs at each transition.

UNCERTAINTY_REQUIREMENT:
Outcome uncertainty and alternative explanations must be recorded.

FAILURE_MODES:
Alert generated = alert useful; action executed = intervention effective; outcome changed = causal effect; missing non-action interpreted as success.

SECURITY_IMPLICATIONS:
Missing provenance or actor identity can prevent reconstruction of consequential decisions.

PERSISTENCE_REQUIREMENT:
Stable IDs across alert, decision, intervention and outcome records.

VALIDATION_REQUIREMENT:
Integration and prospective operational validation.

ACCEPTANCE_CRITERIA:
A single case can be traced from evidence/alert through decision and intervention exposure to outcome and evaluation without identity or provenance breaks.

DEPENDENCIES:
Existing control plane, alert governance, response coupling, outcome store.

PROVENANCE:
Derived from ESTRATEGA actionability execution and prior Discovery 4.

PRIORITY: HIGH

REASON_FOR_HANDOFF:
Cross-layer audit and alert-response infrastructure belongs to NOTARIO/CENTINELA; ESTRATEGA remains responsible for assessing client utility.
