# CROSSREPO-ENDPOINT-001 — Evidence Matrix

Status: OPEN / TESTING

This matrix separates software evidence from scientific validity. A passing implementation test does not establish prospective predictive validity.

| Criterion | Current evidence | Status | Scientific interpretation |
|---|---|---|---|
| Canonical contract | CeutIA v1.1 contract; SERPIENTE producer boundary; pinned hash `672dfa6b60d2e8c0854a024e83acf6b23eed44f2cd3293708aee533d7a9dc1f0` | VALIDATED | Schema identity and semantic metadata are versioned and receiver-checked. |
| Forecast construction | SERPIENTE `Forecast` and `forecast_to_scientific_prediction` | TESTED | A SERPIENTE forecast can be transformed into the canonical scientific prediction. |
| Authentication | HMAC transport, timestamp window, nonce replay protection | TESTED | Transport authenticity is distinct from scientific validity. |
| Runtime configuration | `/ready` requires transport secret, DB and code revision | TESTED | Missing production-critical configuration prevents readiness. |
| Reception | CeutIA consumer receives authenticated SERPIENTE payload | TESTED | Cross-repository reception is demonstrated in CI. |
| Scientific gate | OOD/calibration/source-independence/temporal/integrity controls | TESTED | Ineligible forecasts abstain rather than silently entering decisions. |
| Rejected-prediction persistence | Acceptance is checked before `record_prediction`; regression test verifies no rejected row | TESTING | Prevents scientific and audit contamination by rejected forecasts. |
| Persistence identity | Prediction ID + canonical payload fingerprint + decision identity | TESTED | Duplicate identical delivery is idempotent; conflicting identity is rejected. |
| Persistence integrity | Stored fingerprint checked during replay | TESTED | Direct persisted payload mutation is detected. |
| Decision linkage | `prediction_id -> decision_id -> prediction lineage` | TESTED | Forecast identity survives decision execution. |
| Lineage | Explicit prediction lineage plus scientific/runtime/governance references | TESTED | Scientific origin remains traceable in the decision graph. |
| Point-in-time replay | Authenticated replay endpoint and availability/origin checks | TESTED | Future information cannot be reconstructed as historically available. |
| Outcome eligibility | Outcome must be after availability and forecast target time; future outcomes rejected | TESTED | Outcome alignment avoids temporal leakage. |
| Outcome identity | Unique outcome ID and prediction/outcome collision checks | TESTED | Duplicate/conflicting outcome linkage is detected. |
| Prediction-level evaluation | Brier and log-loss | TESTED | Mathematical scoring is implemented for eligible outcomes. |
| Aggregate evaluation | Predeclared protocol; target/model/horizon slices; calibration gap | TESTING | Descriptive evaluation exists; it is not by itself prospective validation. |
| Missing outcomes | Not imputed; ineligible outcomes excluded | DOCUMENTED LIMITATION | Selection/missingness bias is not yet modeled. |
| Repeated forecasts | Stored and evaluable, but no inferential dependence correction | DOCUMENTED LIMITATION | No inferential uncertainty claims are permitted. |
| Baseline comparison | SERPIENTE has historical temporal baselines internally; crossrepo evaluator does not yet compare them | OPEN P1 | Comparative predictive utility is not established by the endpoint evaluator. |
| Real prospective outcomes | None established in this engineering environment | BLOCKER FOR SCIENTIFIC VALIDITY | `PROSPECTIVE_PREDICTIVE_VALIDITY = NOT_ESTABLISHED`. |
| Causal effectiveness | No causal identification/intervention effect design in this capability | NOT APPLICABLE / UNESTABLISHED | Prediction is not causation. |
| Final E2E | Deterministic actual `SERPIENTE Forecast -> canonical prediction -> HMAC -> /decision/evaluate` test added; replay/outcome/evaluation path separately tested | TESTING | Latest CI must pass before functional closure is considered. |

## Closure rule

`FUNCTIONALLY_CLOSED` requires the latest code to pass the integrated cross-repository suite and demonstrate the complete deterministic lifecycle through decision, persistence, lineage, replay, outcome and evaluation, including failure-path and integrity tests.

`SCIENTIFICALLY_VALIDATED` additionally requires real prospectively generated predictions and prospectively ascertained outcomes under the predeclared evaluation protocol. This requirement is currently **not met**.
