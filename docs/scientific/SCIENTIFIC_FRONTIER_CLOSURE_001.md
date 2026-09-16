# SCIENTIFIC FRONTIER CLOSURE 001

**Mission:** `SCIENTIFIC-AUDIT-CLOSURE`

**Active chain:** `CROSSREPO-PIT-BINDING-001` → `CROSSREPO-OUTCOME-ASCERTAINMENT-001` → `CROSSREPO-PROSPECTIVE-EVALUATION-001` → baseline/dependence/feedback/regime governance → `F14_RESPONSE_COUPLING`.

## 1. PIT semantic binding

**Invariant:** `X_t = φ(H_t, θ_t, c_t)` where `H_t` is the exact visible information set, `φ` is a versioned derivation, `θ_t` its configuration/version, and `c_t` the source/feature visibility constraints.

SERPIENTE `PointInTimeStore.history_at(as_of)` reconstructs visible revision-aware history and fingerprints it, but `LongitudinalForecaster.forecast(...)` still accepts `X` independently from the fingerprint. Therefore current v1.1 establishes **PIT_ATTESTATION**, not **PIT_SEMANTICALLY_VERIFIED**. The repair requires binding the actual model-input derivation to an explicit manifest and versioned derivation identity; the v1.1 contract must not be overloaded to imply this property.

**Status:** scientific claim `NOT_ESTABLISHED`; executable repair handoff required.

## 2. Outcome ascertainment

The outcome persistence layer has been upgraded to explicit ascertainment metadata. `SCHEMA_VERSION=5` persists source identity/version, observation/availability/ascertainment times, revision identity, measurement-process identity, outcome-definition version, transformation identity, censoring, missingness, selection and intervention exposure.

The endpoint request model requires these ascertainment identities and timezone-aware timestamps. It enforces `observation_time <= availability_time <= ascertainment_time`, rejects outcomes whose availability follows the prediction evaluation eligibility point, and refuses missing/partial/censored/selected records from binary scoring rather than imputing them.

**Remaining defect:** the current `prediction_id` primary key means multiple revisions of the same prediction are not yet representable as a revision history; a changed revision collides rather than silently overwriting. This is fail-closed but does not satisfy the stronger requirement that a revision be stored as a distinct versioned record. Competing-source relations likewise remain outside the current record model.

**Status:** `PARTIALLY_CHARACTERIZED` → `IMPLEMENTATION_PENDING` for revision-history/source-conflict representation; basic ascertainment semantics require runtime verification.

## 3. Prospective evaluation

`CEUTIA-SERPIENTE-PREDICTIVE-EVAL-1` is protocol version `1.1`. It locks the evaluation window, outcome ascertainment fields and temporal order, baseline registration/leakage rules, dependence restrictions, intervention-feedback separation and regime/distribution-shift metadata. Prospective validity remains `NOT_ESTABLISHED` until real prospective forecasts and outcomes exist.

Required prospective artifact: immutable evaluation-window manifest linking forecast registry, PIT lineage, outcome ascertainment, baseline, model/code/configuration versions and evaluation-procedure hash.

**Status:** `BLOCKED_EXTERNAL` only for empirical prospective validation; protocol/instrumentation preparation continues independently.

## 4. Baseline integrity

SERPIENTE contains temporal prevalence and seasonal baselines in model validation, but the cross-repository evaluation endpoint does not transport a paired predeclared baseline output. Retrospective construction from realized outcomes remains forbidden.

**Status:** `HANDOFF_REQUIRED` for cross-repository paired baseline transport; comparative predictive utility remains `NOT_ESTABLISHED`.

## 5. Repeated-forecast dependence

Repeated forecasts remain explicitly non-independent by default. The aggregate evaluator emits descriptive metrics only and does not emit unsupported confidence intervals or hypothesis tests.

**Status:** `SCIENTIFICALLY_CLOSED` for the current descriptive scope; dependence-aware inference remains an explicit requirement if inferential claims are introduced.

## 6. Intervention feedback and regime shift

Forecast → decision → action → outcome remains a distinct feedback path. Intervention-exposed outcomes are persisted as such when supplied, while causal effectiveness remains separate from predictive performance. SERPIENTE's state builder contains an explicit regime classifier; this supports engineering detection but does not establish prospective regime-transfer validity.

**Status:** governance/instrumentation scope closed; empirical intervention/regime validity remains `NOT_ESTABLISHED`.

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
| Warning-response coupling | NOT ESTABLISHED | IMPLEMENTATION_PENDING |

## 8. New material frontier: warning-response gap

A material frontier has now been registered as `F14_RESPONSE_COUPLING` and persisted in `docs/scientific/SCIENTIFIC_RESPONSE_GAP_001.md`.

The scientific distinction is explicit: predictive validity, response execution, response effectiveness and operational utility are different estimands. A warning that predicts an outcome does not establish that a response was executed, that it was effective, or that the outcome improved because of the response.

The architecture therefore requires a bounded response ledger/contract capable of linking warning/prediction identity, decision identity/time, action/intervention identity/time, eligibility and response window, implementation/non-execution, intervention exposure, resource/capacity constraints, outcome ascertainment and causal/counterfactual status. This is an instrumentation requirement, not a claim of causal effectiveness.

The frontier is supported by external literature documenting a warning-response gap in early-warning systems, while leaving CeutIA-specific response effectiveness as an empirical question. It is not a license to redesign the complete architecture.

**F14 status:** `FORMALIZED`; empirical response effectiveness `NOT_ESTABLISHED`; engineering state `IMPLEMENTATION_PENDING`; queue `ACTIVE`.

## 9. Bounded audit of the newly supplied advanced methods

The newly supplied architecture does contain material methodological candidates, but they do **not** justify the statement that the scientific optimization problem is already solved or that no material evidence can remain. They are mapped to existing frontiers rather than blindly implemented:

- **Causal forests / Double ML / sensitivity analysis:** relevant to `F10`/`F11`; useful only for explicit causal estimands with treatment, outcome, confounder and counterfactual definitions. They mitigate modeling/estimation problems but do not solve non-identifiability.
- **Critical slowing down:** relevant to `F08`; variance and lag-1 autocorrelation can be monitored, but literature documents false positives, false negatives and dependence on detrending/window/noise/regime assumptions. It must remain a signal class, not a universal tipping-point detector.
- **Prediction markets:** relevant to `F13` validation; useful as an external benchmark where an appropriate market exists. The reported 79% meta-analytic figure is task/context-specific and cannot be promoted to a universal accuracy advantage.
- **Cry-wolf / asymmetric loss / credibility:** relevant to `F06` and operational governance. Thresholds should be tied to explicit costs, response capacity and predeclared alert semantics rather than a generic preference for fewer false positives.
- **FORIN-aligned vulnerability mapping:** relevant to substantive risk representation; it should preserve distinction between vulnerability description, prediction and causal explanation.
- **Mechanism design / TVA-style incentives:** potentially material to Goodhart resistance and provider reporting, but the published result is conditional on stated assumptions. It does not imply that CeutIA can guarantee truthful reporting in its deployment environment.
- **Indicator rotation / obfuscation:** adversarially useful but introduces reproducibility, governance and auditability trade-offs. Secret weights cannot be allowed to undermine scientific reproducibility or retrospective audit trails.
- **Differential privacy:** potentially useful for release-layer protection against reverse engineering, but privacy noise can alter calibration/threshold semantics and must be treated as a separate release mechanism rather than as proof against gaming.
- **Pre-registration / out-of-sample validation:** already aligned with `F03`; these strengthen evaluation integrity but do not create prospective evidence where none exists.

## 10. Mission condition

The mission remains `IN_PROGRESS`. The newly identified warning-response frontier is material and therefore joins the bounded closure sequence. External evidence blocks only empirical claims that require future observations; it does not block engineering preparation, adversarial testing, protocol locking, provenance instrumentation, baseline safeguards, response instrumentation or scientific falsification work that can be executed now.
