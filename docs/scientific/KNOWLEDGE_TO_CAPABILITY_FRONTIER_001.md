# Knowledge-to-Capability Frontier 001

This file is a working frontier for the open **Ingeniero de CeutIA — Maximum Knowledge-to-Capability** mission. It is intentionally not a closure document.

## Current implementation frontier

The completed audits show that the immediate opportunity is primarily **composition and governance of existing primitives**, not indiscriminate addition of advanced statistical models.

### Priority 1 — scientific information-set contract
Status: IMPLEMENTABLE IMMEDIATELY.

Required invariant: every forecast evaluation/replay must be interpreted relative to the information legitimately available at origin time. `X_t` is a computational representation; `I_t` is the scientific information boundary.

Acceptance tests should include identical visible features with different source/revision availability histories and demonstrate that they are not treated as equivalent historical information sets.

### Priority 2 — forecast forensic reconstruction
Status: IMPLEMENTABLE IMMEDIATELY from existing PIT/provenance/fingerprint primitives.

A forecast-forensics record should answer: which model version, which feature identity, which observation IDs, which source versions, which transformations, which availability constraints, which fingerprint and which outcome/evaluation lineage were used.

This is a diagnostic/reporting capability, not a new predictive model.

### Priority 3 — source-process intelligence
Status: TARGET-SPECIFIC IMPLEMENTATION.

Source changes must be represented independently from world-state changes. The minimum scientifically useful event taxonomy is: schema, definition, denominator, cadence, latency, revision burst, coverage, classification, population, acquisition failure.

No source-process event may automatically become a world phenomenon.

### Priority 4 — interaction drift
Status: TARGET-SPECIFIC IMPLEMENTATION.

A multisystem monitor should be able to detect a change in the relationship between two or more signals even if their marginal distributions remain stable. Candidate diagnostics include lagged association, conditional dependence, dynamic partial correlation, predictive incremental value and network-edge changes.

No causal interpretation is implied.

### Priority 5 — emergent joint anomaly
Status: TARGET-SPECIFIC IMPLEMENTATION.

A joint configuration can become unusual while all marginals remain within univariate limits. A multivariate state-distance method is scientifically justified only after a reference state distribution/covariance structure is registered.

### Priority 6 — change point / regime transition
Status: TARGET-SPECIFIC IMPLEMENTATION.

Anomaly, change point and regime are separate event types. The implementation should be selected by phenomenon, sampling and loss function rather than by algorithm prestige.

### Priority 7 — incremental predictive value
Status: TARGET-SPECIFIC IMPLEMENTATION.

For candidate A→B relationships, compare a locked baseline information set against an augmented set under temporal validation, dependence-aware scoring and registered outcome definitions.

### Priority 8 — value of information
Status: REQUIRES DECISION TARGET.

VOI is only scientifically meaningful when a decision, loss/utility function, candidate acquisition and uncertainty model are specified. It must not be reduced to feature importance.

## Advanced-method gate

No advanced family is admitted to production merely because it is mathematically available. Admission requires:

`phenomenon → data-generating process → estimand → identifiable parameters → assumptions → validation design → operational use → failure handling`.

This frontier remains open until target-specific capabilities are either implemented and verified or formally classified as externally dependent.
