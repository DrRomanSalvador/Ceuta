# Response Coupling Audit 001

## Scope

This audit inspects the current warning/decision/action path before introducing response-coupling persistence. It is intentionally limited to the existing implementation and does not infer operational effectiveness.

## Existing producer/consumer path

`src/monitor.py` obtains verified data, computes a `RiskResult`, passes it to `AlertSystem.check_and_alert`, and writes an in-memory/log-oriented audit representation. The monitor retains only `last_risk_result` and the alert system retains an in-memory `alert_history`.

`src/risk_calculator.py` produces a `RiskResult` containing risk score, confidence interval, component scores, alert level, calculation timestamp, data-source identifiers and an audit hash. This is a prediction/risk-output record, not a response record.

`src/alert_system.py` converts non-GREEN risk results into an in-memory `Alert`. The alert contains level, risk score, message, timestamp, recommended action strings, data sources and the inherited audit hash. Notification channels are email/webhook/SMS logging paths; there is no persisted decision identity or action-execution record.

## Required response fields: current coverage

| Required field | Current state | Evidence |
|---|---|---|
| warning_or_prediction_identity | Partial | `RiskResult.audit_hash` and calculation timestamp exist, but no canonical prediction identity is defined |
| decision_identity/time | Absent | no decision object or decision timestamp |
| action_identity/execution_time | Absent | recommended action strings exist; execution is not recorded |
| response_eligibility | Absent | no eligibility contract/window |
| intended_mechanism | Absent | recommendation text is not a mechanism specification |
| response_delay | Absent | warning and response timestamps are not linked |
| intervention_exposure/intensity | Absent | no exposure record |
| implementation_failure | Absent | notification failure is logged but not represented as response-state data |
| resource_capacity_constraints | Absent | no response-capacity fields |
| outcome_ascertainment_identity | Absent | no linked outcome record |
| response_horizon | Absent | no predeclared response window |
| counterfactual_causal_status | Absent | no causal-identification state |

## Duplicate-state decision

No existing response ledger or response contract was found in the inspected warning/monitor path. The existing `RiskResult` and `Alert` contracts should remain prediction/notification contracts. A separate response-coupling ledger is therefore justified rather than overloading either object.

## Required semantic separation

The new ledger must preserve four distinct estimands:

1. predictive validity;
2. response execution;
3. response effectiveness;
4. operational utility.

Temporal linkage alone must never promote a warning→response→outcome sequence to a causal effectiveness claim.

## Minimum adversarial cases

The ledger contract must represent and distinguish warning/no response, response without warning, non-execution, delayed response outside the eligible window, outcome improvement without a counterfactual, deterioration after response, external intervention/confounding, actor adaptation, repeated-warning fatigue/threshold changes, and response selection using unobserved information.

## Engineering decision

**IMPLEMENTATION_JUSTIFIED:** yes.

The existing path lacks the fields required to establish response execution or effectiveness and has no separate response persistence contract. Implement a dependency-light response ledger with fail-closed causal-status validation; do not change the predictive model or imply empirical response effectiveness.
