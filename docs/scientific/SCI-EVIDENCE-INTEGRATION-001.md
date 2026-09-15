# SCI-EVIDENCE-INTEGRATION-001 — High-Quality Scientific Evidence Integration

**Status:** IMPLEMENTED — EVIDENCE-INTEGRATED / LOCAL VALIDATION PENDING
**Priority:** P0
**Repository:** `DrRomanSalvador/Ceuta`
**Branch:** `scientific-reflexive-control-constraints`
**Parent checkpoint:** `5aaf3e501a656152b48f00ae2fac008973c478bb`

## 1. Objective

Integrate external scientific and official-data evidence into CeutIA without converting literature claims into stronger propositions than the evidence supports.

The integration rule is:

`SOURCE -> EVIDENCE -> CLAIM -> ASSUMPTIONS -> TEST -> SCIENTIFIC STATE`

A publication or official API is not itself a causal mechanism, observation, or validation of CeutIA. It is evidence about a proposition whose scope, population, method and limitations must remain explicit.

## 2. Evidence hierarchy used

### Tier A — official first-party operational/data documentation

1. **AEMET OpenData** — official service documentation. Current policy states that new API keys expire after 3 months and legacy keys without expiration cease to be accepted on 15 October 2026. This is direct evidence for acquisition-process volatility and therefore for the need to version acquisition credentials/process metadata operationally. It is not evidence that the underlying meteorological phenomenon changed.
2. **INE API JSON** — official INE documentation confirms programmatic access to INEbase via URL/JSON and automatic exploitation. This supports machine acquisition, but not by itself measurement validity or causal interpretation.
3. **Eurostat API/SDMX** — official documentation states that datasets are updated regularly, structural artefacts can be versioned, but historical versions of statistical observations are not retained: when an observation is updated, its previous value is no longer retrievable from the service. This directly supports CeutIA's requirement to archive raw responses and metadata when historical reconstruction is scientifically required.

### Tier B — peer-reviewed empirical evidence

4. **Bevan & Hood (2006), Public Administration, 84, 517–538. DOI 10.1111/j.1467-9299.2006.00600.x** — empirical evidence from English public health care on targets, measurement problems and gaming. Supports treating measurement reactivity and gaming as first-class risks; does not establish universal indicator collapse.
5. **Mannion & Braithwaite (2012), Internal Medicine Journal, 42, 569–574. DOI 10.1111/j.1445-5994.2012.02766.x** — narrative review identifying multiple dysfunctional consequences of national performance measurement systems, while also documenting cases of improvement. Supports a two-sided model: intervention can improve the target while simultaneously distorting the measurement process.

### Tier C — formal theoretical constraint

6. **Wolpert & Macready (1997), No Free Lunch theorems for optimization.** The theorem family establishes that no optimization algorithm dominates across all possible problem classes. For CeutIA this is a restriction on universal algorithm claims, not a claim that practical forecasting is random.

## 3. Scientific claims admitted into CeutIA

| Claim | Evidence status | Permitted interpretation | Forbidden overclaim |
|---|---|---|---|
| Performance targets can induce gaming/measurement distortion | Supported by empirical literature | First-class reactivity risk | Every indicator inevitably collapses |
| Performance measurement can improve outcomes and create unintended effects | Supported | Joint outcome + measurement-process monitoring | Intervention is necessarily harmful |
| Acquisition processes can change independently of phenomenon | Supported by official API lifecycle evidence | Version acquisition process and provenance | Acquisition change proves phenomenon change |
| Current statistical APIs may expose only latest observation version | Official Eurostat documentation | Archive raw artifacts for replay | Current API value is the historical value |
| Algorithm superiority is domain/problem-class dependent | Theoretical constraint | Store assumptions and evaluate prospective generalization | ML is universally/randomly equivalent |
| Predictive relation is not causal identification | Methodological invariant | Separate prediction from causal hypothesis | Forecast implies mechanism |

## 4. Reflexive measurement-control model

CeutIA shall treat high-impact indicators as potentially endogenous to the intervention regime:

`X_t -> M_t -> Y_t -> model_t -> decision_t -> intervention_t -> actor_adaptation_t -> {X_{t+1}, M_{t+1}} -> Y_{t+1}`

where `M_t` includes measurement, reporting, acquisition and revision processes.

The system therefore tracks two distinct objects:

- **phenomenon state** — what the world/system is doing;
- **observation-process state** — how that state is measured, reported, acquired and revised.

An indicator discontinuity is consequently not assigned a single mechanism by default.

## 5. Required scientific estimands

CeutIA must not collapse the following into one score:

- `PREDICTIVE_VALIDITY`
- `INTERVENTION_EFFECTIVENESS`
- `COUNTERFACTUAL_OUTCOME`
- `OPERATIONAL_UTILITY`
- `INDICATOR_INTEGRITY`

A successful intervention can make the predicted adverse outcome unobserved. This changes the evaluation problem; it does not logically invalidate early-warning systems.

## 6. Acquisition-process evidence contract

For every high-impact external source, preserve at minimum:

- source identifier;
- endpoint/query;
- retrieval timestamp;
- availability timestamp when known;
- publication/update timestamp when available;
- raw artifact hash;
- metadata/schema hash;
- acquisition method/version;
- authentication/key lifecycle state where operationally relevant;
- source revision/version information;
- canonicalized observation hash;
- transformation code/model version;
- replay reference.

`DOWNLOAD != MEASUREMENT` and `SOURCE != OBSERVATION` remain mandatory distinctions.

## 7. Evidence-to-architecture mapping

### A. Goodhart/reactivity

Map empirical evidence to:

`MEASUREMENT_PROCESS_CHANGE`, `REPORTING_PROCESS_CHANGE`, `ACTOR_ADAPTATION`, `INDICATOR_GAMING_SIGNAL`, `INTERVENTION_EFFECT`.

No automatic causal upgrade is permitted.

### B. Acquisition drift

Map official API lifecycle/versioning changes to:

`ACQUISITION_PROCESS_CHANGE`, `REVISION_CHANGE`, `UNKNOWN_MECHANISM`.

A changed API key policy is an operational state transition, not a scientific observation about the target phenomenon.

### C. Historical reconstruction

Where the provider exposes only current values, CeutIA must rely on its own immutable raw archive for historical replay. If the archive is absent, historical knowledge reconstruction is degraded and must be marked accordingly.

### D. Generalization

Every prospective model evaluation must retain its training/reference class, domain restrictions and information set. Performance claims outside those restrictions require new evidence.

## 8. Falsification / stress tests

The following tests are required before promoting the reflexive theory from partially supported to scientifically validated:

1. **Intervention-pressure test:** an indicator remains stable against an independent outcome measure under sustained intervention pressure.
2. **Corruption test:** indicator behaviour changes after intervention while an independent outcome does not change correspondingly.
3. **Acquisition perturbation test:** acquisition/API changes alter the observed series without a corresponding independent phenomenon change.
4. **Revision replay test:** retrospective values differ from values available at the historical decision time, and point-in-time replay reproduces the information actually available then.
5. **Prospective regime test:** predictive performance is reported separately by intervention regime.
6. **Causal non-upgrade test:** prediction, dependency and temporal precedence never become causal status without an explicit identification assessment.

## 9. Scientific state transition

Current state:

- `SCI-REFLEXIVE-EWS-001`: **IMPLEMENTED — SCIENTIFICALLY PARTIALLY SUPPORTED**
- `SCI-DEP-GRAPH-001`: **IMPLEMENTED — NOT YET VALIDATED**
- Acquisition-process drift: **SUPPORTED AS A FIRST-CLASS RISK; CeutIA-SPECIFIC DEGRADATION RATE UNTESTED**
- Universal indicator collapse: **UNCERTAIN / NOT ESTABLISHED**
- Universal early-warning impossibility: **NOT ESTABLISHED**
- Causal identifiability: **CONSTRAINT ENFORCED; EMPIRICAL IDENTIFICATION REMAINS CASE-SPECIFIC**
- Historical knowledge reconstruction: **IMPLEMENTED; coverage depends on archived raw artifacts**

## 10. Reproducibility rule

External evidence can support a scientific claim only if the exact source, retrieval/version context and interpretation are recorded. For mutable APIs, the scientific artifact is the combination:

`raw artifact + metadata + acquisition context + hash + canonical transformation + replay state`.

This prevents a later source update from silently rewriting the evidentiary basis of a past decision.

## 11. References

- Bevan, G., & Hood, C. (2006). What's measured is what matters: Targets and gaming in the English public health care system. *Public Administration*, 84(3), 517–538. DOI: 10.1111/j.1467-9299.2006.00600.x
- Mannion, R., & Braithwaite, J. (2012). Unintended consequences of performance measurement in healthcare: 20 salutary lessons from the English National Health Service. *Internal Medicine Journal*, 42(5), 569–574. DOI: 10.1111/j.1445-5994.2012.02766.x
- Wolpert, D. H., & Macready, W. G. (1997). No Free Lunch Theorems for Optimization. *IEEE Transactions on Evolutionary Computation*.
- AEMET OpenData: official API documentation and current API-key lifecycle notices.
- INE: official API JSON documentation for INEbase.
- Eurostat: official Statistics API and SDMX documentation, including current observation-version/history limitations.

## 12. Integration checkpoint

This artifact does not promote literature into repository truth. It records the evidence boundary and converts supported propositions into explicit architectural safeguards and falsifiable validation tasks.
