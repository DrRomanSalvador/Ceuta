# CeutIA Decision System

## Purpose

The decision layer must close the loop from evidence to action and back to observed consequences. A forecast alone is not a decision system.

The normative chain is:

`evidence -> state -> hypotheses -> scenarios -> forecasts -> options -> utility/trade-offs -> decision -> intervention -> observed response -> evaluation -> learning -> re-evaluation`

## Implemented contracts

`backend/app/core/decision/decision_system.py` provides explicit contracts for decision context, objectives, scenario outcomes, options, information requests, recommendations and feedback. It supports robust, expected-utility, regret-minimisation and harm-minimisation policies; probability-mass validation; uncertainty gates; explicit abstention; human-review escalation; information-value ranking; provenance references; and reevaluation triggers.

`backend/app/core/decision/governance.py` provides intervention specifications, provenance completeness checks, validity/reevaluation policy, outcome feedback and governance thresholds. Interventional claims require an explicit causal-model reference. The system does not infer causality merely from predictive association.

## Required decision principles

1. Utility must be explicit. A recommendation without an explicit objective function is not auditable.
2. Multiple policies must be comparable. Robustness, expected utility, harm minimisation and regret can produce different actions and that disagreement is information.
3. Deep uncertainty must be visible. Epistemic uncertainty must not be silently converted into probability.
4. Information has value. When the expected value of additional information exceeds its acquisition cost, the system should surface information acquisition before action.
5. Prediction and intervention are distinct. Counterfactual or interventional claims require explicit assumptions and causal-model provenance.
6. Every recommendation must be traceable to models, hypotheses, evidence, transformations, scenarios, utility and constraints.
7. Recommendations have validity windows and reevaluation triggers.
8. Real-world outcomes must return to the system as structured feedback. Forecast calibration alone is insufficient; decision error and regret must also be measured.
9. The system must be able to abstain. Abstention is a valid output, not an error state.
10. Autonomous intervention is governed separately from analytical recommendation and is disabled by default.

## Non-claims

These contracts do not by themselves establish causal identification, empirical calibration, policy optimality, or operational safety. Those properties require prospective validation against real observations, interventions, outcomes and failure cases.

## Exit criteria for this layer

- deterministic unit tests cover policy selection, abstention, human review, information value and invalid probability contracts;
- intervention claims cannot be represented without a causal-model reference;
- provenance completeness is machine-checkable;
- validity and reevaluation triggers are explicit;
- feedback exposes expected-versus-observed error;
- autonomous intervention remains disabled unless an explicit governance configuration enables it;
- the full CI suite passes before the layer is considered closed.
