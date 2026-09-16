# CROSSREPO-ENDPOINT-001 — Evidence Matrix

Status: OPEN / SCIENTIFIC AUDIT CONTINUES

This matrix separates software evidence from scientific validity. Passing implementation tests does not establish prospective predictive validity.

| Criterion | Current evidence | Status | Scientific interpretation |
|---|---|---|---|
| Canonical contract | CeutIA v1.1 contract; SERPIENTE producer boundary; pinned hash `672dfa6b60d2e8c0854a024e83acf6b23eed44f2cd3293708aee533d7a9dc1f0` | VALIDATED | Schema identity and required scientific metadata are versioned and receiver-checked. |
| Forecast construction | SERPIENTE `Forecast` and `forecast_to_scientific_prediction` | TESTED | A SERPIENTE forecast can be transformed into the canonical scientific prediction. |
| Authentication | HMAC transport, timestamp window, nonce replay protection | TESTED | Transport authenticity is distinct from scientific validity. |
| Runtime configuration | `/ready` requires transport secret, DB and code revision | TESTED | Missing production-critical configuration prevents readiness. |
| Reception | CeutIA consumer receives authenticated SERPIENTE payload | TESTED | Cross-repository reception is demonstrated in CI. |
| Scientific gate | OOD/calibration/source-independence/temporal/integrity controls | TESTED | Ineligible forecasts abstain rather than silently entering decisions. |
| Rejected-prediction persistence | Acceptance is checked before `record_prediction`; regression test verifies no rejected row | TESTED | Rejected forecasts do not contaminate prediction persistence. |
| Persistence identity | Prediction ID + canonical payload fingerprint + decision identity | TESTED | Duplicate identical delivery is idempotent; conflicting identity is rejected. |
| Persistence integrity | Stored fingerprint checked during replay | TESTED | Direct persisted payload mutation is detected. |
| Decision linkage | `prediction_id -> decision_id -> prediction lineage` | TESTED | Forecast identity survives decision execution. |
| Lineage | Explicit prediction lineage plus scientific/runtime/governance references | TESTED | Scientific origin remains traceable in the decision graph. |
| Point-in-time replay | Authenticated replay endpoint and availability/origin checks | TESTED | Replay prevents a persisted forecast from being reconstructed before its stored availability/origin. This does **not** independently verify that the producer fingerprint is semantically bound to the exact information set used by the model. |
| Point-in-time information-set binding | SERPIENTE carries `point_in_time_fingerprint`; CeutIA treats it as required opaque metadata | PARTIALLY_IMPLEMENTED | Presence, persistence and cryptographic payload integrity are enforced, but CeutIA cannot currently recompute the fingerprint from the producer's underlying observations/features. A producer-supplied fingerprint is an attestation, not independent proof of information-set membership. |
| Outcome eligibility | Outcome must be after availability and forecast target time; future outcomes rejected | TESTED | Basic temporal alignment avoids direct outcome-time leakage. |
| Outcome ascertainment semantics | Outcome has ID, binary value, time and provenance | PARTIALLY_IMPLEMENTED | Provenance is required, but the contract does not yet encode ascertainment source/version, measurement process, revision status or ascertainment time separately from outcome time. |
| Outcome identity | Unique outcome ID and prediction/outcome collision checks | TESTED | Duplicate/conflicting outcome linkage is detected. |
| Prediction-level evaluation | Brier and log-loss | TESTED | Mathematical scoring is implemented for eligible observed outcomes. |
| Aggregate evaluation | Predeclared protocol; target/model/horizon slices; calibration gap | TESTED / DESCRIPTIVE | Aggregate evaluation exists and explicitly avoids claiming prospective validity. |
| Missing outcomes | Not imputed; ineligible outcomes excluded | DOCUMENTED LIMITATION | Selection/ascertainment missingness is not yet modeled; observed-outcome aggregates may be selected samples. |
| Repeated forecasts | Stored and evaluable, but no inferential dependence correction | DOCUMENTED LIMITATION | No inferential uncertainty claims are permitted. |
| Baseline comparison | SERPIENTE computes temporal prevalence and seasonal baselines internally; canonical cross-repo payload does not carry a matched baseline forecast | OPEN P1 | Comparative predictive utility cannot be reconstructed without a predeclared, point-in-time baseline output or reproducible baseline method. |
| Distribution/regime shift | SERPIENTE declares regime and has temporal validation; CeutIA endpoint does not yet perform prospective post-shift evaluation | PARTIALLY_IMPLEMENTED | Regime metadata and temporal holdout exist, but endpoint-level forecast degradation monitoring is not established. |
| Feedback contamination | Decision/action linkage exists; outcome records action identity | PARTIALLY_IMPLEMENTED | Intervention identity is preserved, but outcome evaluation does not yet estimate or stratify intervention-induced changes in the outcome/measurement process. |
| Real prospective outcomes | None established in this engineering environment | BLOCKER FOR SCIENTIFIC VALIDITY | `PROSPECTIVE_PREDICTIVE_VALIDITY = NOT_ESTABLISHED`. |
| Causal effectiveness | No causal identification/intervention effect design in this capability | NOT ESTABLISHED | Prediction error metrics do not identify intervention effects. |
| Final E2E | Deterministic actual `SERPIENTE Forecast -> canonical prediction -> HMAC -> /decision/evaluate` test; replay/outcome/evaluation path separately tested | TESTED / FUNCTIONAL | CI run `35066018857` on current PR head passed 38 targeted tests. Functional closure is distinct from scientific validation. |

## Scientific audit conclusions

1. The deterministic cross-repository endpoint lifecycle is now **functionally demonstrated** by the latest CI run.
2. The most important remaining information-integrity gap is **semantic point-in-time binding**: the system proves that a declared fingerprint is present and protected, but not that the fingerprint corresponds exactly to the information actually used to generate the forecast.
3. Outcome alignment is temporally constrained, but **outcome ascertainment remains underspecified** for measurement/revision/source effects.
4. Baseline comparison is not safely implementable from the current canonical payload without adding a predeclared baseline output/method to the scientific contract or evaluation input; deriving a baseline retrospectively from evaluation outcomes would create leakage.
5. Missing-outcome selection and intervention-induced distribution change remain explicit limitations.

## Closure rule

`FUNCTIONALLY_CLOSED` requires the latest code to pass the integrated cross-repository suite and demonstrate the deterministic lifecycle through decision, persistence, lineage, replay, outcome and evaluation, including failure-path and integrity tests.

`SCIENTIFICALLY_VALIDATED` additionally requires real prospectively generated predictions and prospectively ascertained outcomes under the predeclared evaluation protocol. This requirement is currently **not met**.
