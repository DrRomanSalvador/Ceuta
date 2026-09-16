# SCIENTIFIC FRONTIER CLOSURE 001

**Mission:** `SCIENTIFIC-AUDIT-CLOSURE`

**Active chain:** `CROSSREPO-PIT-BINDING-001` → `CROSSREPO-OUTCOME-ASCERTAINMENT-001` → `CROSSREPO-PROSPECTIVE-EVALUATION-001` → baseline/dependence/feedback/regime governance.

## 1. PIT semantic binding

**Invariant:** `X_t = φ(H_t, θ_t, c_t)` where `H_t` is the exact visible information set, `φ` is a versioned derivation, `θ_t` its configuration/version, and `c_t` the source/feature visibility constraints.

SERPIENTE `PointInTimeStore.history_at(as_of)` reconstructs visible revision-aware history and fingerprints it, but `LongitudinalForecaster.forecast(...)` still accepts `X` independently from the fingerprint. Therefore current v1.1 establishes **PIT_ATTESTATION**, not **PIT_SEMANTICALLY_VERIFIED**. The repair requires binding the actual model-input derivation to an explicit manifest and versioned derivation identity; the v1.1 contract must not be overloaded to imply this property.

**Status:** `SCIENTIFICALLY_CLOSED_WITH_LIMITATION` for the currently inspectable architecture; **scientific claim remains NOT_ESTABLISHED** and executable repair handoff remains required.

## 2. Outcome ascertainment

The outcome persistence layer has now been upgraded from basic identity/temporal eligibility to explicit ascertainment metadata. `SCHEMA_VERSION=5` persists source identity/version, observation/availability/ascertainment times, revision identity, measurement-process identity, outcome-definition version, transformation identity, censoring, missingness, selection and intervention exposure.

The endpoint request model now requires these ascertainment identities and timezone-aware timestamps. It enforces `observation_time <= availability_time <= ascertainment_time`, rejects outcomes whose availability follows the prediction evaluation eligibility point, and refuses missing/partial/censored/selected records from binary scoring rather than imputing them.

**Remaining defect:** the current `prediction_id` primary key means multiple revisions of the same prediction are not yet representable as a revision history; a changed revision collides rather than silently overwriting. This is fail-closed but does not yet satisfy the stronger requirement that a revision be stored as a distinct versioned record. Competing-source relations likewise remain outside the current record model.

**Status:** `PARTIALLY_CHARACTERIZED` → `IMPLEMENTATION_PENDING` for revision-history/source-conflict representation; basic ascertainment semantics are implemented and require runtime verification.

## 3. Prospective evaluation

`CEUTIA-SERPIENTE-PREDICTIVE-EVAL-1` is now protocol version `1.1`. It explicitly locks the evaluation window, outcome ascertainment fields and temporal order, baseline registration/leakage rules, dependence restrictions, intervention-feedback separation and regime/distribution-shift metadata. Prospective validity remains `NOT_ESTABLISHED` until real prospective forecasts and outcomes exist.

Required prospective artifact: immutable evaluation-window manifest linking forecast registry, PIT lineage, outcome ascertainment, baseline, model/code/configuration versions and evaluation-procedure hash.

**Status:** `BLOCKED_EXTERNAL` only for empirical prospective validation; protocol/instrumentation preparation continues independently.

## 4. Baseline integrity

SERPIENTE contains temporal prevalence and seasonal baselines in model validation, but the cross-repository evaluation endpoint does not transport a paired predeclared baseline output. Retrospective construction from realized outcomes remains forbidden.

**Status:** `HANDOFF_REQUIRED` for cross-repository paired baseline transport; comparative predictive utility remains `NOT_ESTABLISHED`.

## 5. Repeated-forecast dependence

Repeated forecasts remain explicitly non-independent by default. The aggregate evaluator emits descriptive metrics only and does not emit unsupported confidence intervals or hypothesis tests.

**Status:** `SCIENTIFICALLY_CLOSED` for the current descriptive scope; dependence-aware inference remains an explicit future requirement if inferential claims are introduced.

## 6. Intervention feedback and regime shift

Forecast → decision → action → outcome remains a distinct feedback path. Intervention-exposed outcomes are persisted as such when supplied, while causal effectiveness remains separate from predictive performance. SERPIENTE's state builder contains an explicit regime classifier; this supports engineering detection but does not establish prospective regime-transfer validity.

**Status:** `SCIENTIFICALLY_CLOSED` for governance/instrumentation scope; empirical intervention/regime validity remains `NOT_ESTABLISHED`.

## 7. Scientific claim governance

| Claim | Scientific state | Engineering state |
|---|---|---|
| Cross-repository transport | VERIFIED by repository tests | VALIDATED |
| Canonical contract integrity | VERIFIED | VALIDATED |
| PIT history fingerprint | EMPIRICALLY SUPPORTED | IMPLEMENTED |
| Actual X-to-H_t semantic PIT binding | NOT ESTABLISHED | HANDOFF_REQUIRED |
| Basic outcome temporal eligibility | VERIFIED | IMPLEMENTED |
| Outcome ascertainment metadata | PARTIALLY ESTABLISHED | IMPLEMENTED_PENDING_RUNTIME_VERIFICATION |
| Outcome revision history | NOT ESTABLISHED | REPAIR_REQUIRED |
| Retrospective/descriptive evaluation | VERIFIED / DESCRIPTIVE | IMPLEMENTED |
| Prospective predictive validity | NOT ESTABLISHED | PREPARATION_CONTINUES; EMPIRICAL STEP EXTERNAL |
| Prospective calibration validity | NOT ESTABLISHED | PREPARATION_CONTINUES |
| Comparative utility vs baseline | NOT ESTABLISHED | HANDOFF_REQUIRED |
| Dependence-aware inferential validity | NOT ESTABLISHED | NOT_IMPLEMENTED_BY_DESIGN |
| Causal effectiveness | NOT ESTABLISHED | OUTSIDE_PREDICTIVE_ESTIMAND |

## 8. Mission condition

The mission remains `IN_PROGRESS`. The absence of a real prospective outcome population blocks only empirical prospective validity. It does not block the engineering preparation, adversarial tests, protocol locking, provenance instrumentation, baseline safeguards, dependence governance, regime monitoring or PIT repair handoff.
