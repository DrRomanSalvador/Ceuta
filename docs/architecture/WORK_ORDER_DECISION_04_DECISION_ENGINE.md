# Decision-system work order 04 — Decision engine

## Objective
Convert the decision layer from a recommendation contract into a mathematically explicit decision engine that consumes calibrated state, causal and predictive uncertainty.

## Required implementation
- Explicit action space, objectives, utility/loss, constraints and time horizon.
- Expected utility and expected loss under predictive and structural uncertainty.
- Value of information integrated into action selection, using the existing VoI engine rather than a disconnected calculation.
- Robust decision-making under deep uncertainty and model disagreement.
- Regret analysis, minimax/robust alternatives where expected-value assumptions are inadequate.
- Risk-sensitive objectives and explicit tail-risk treatment.
- Multi-objective decisions with Pareto/frontier representation where appropriate.
- Decision thresholds must be derived from utilities/constraints or explicit policy, never arbitrary constants.
- Human-review and abstention gates must be executable.
- Decision provenance must expose which state, evidence, causal assessment, forecast and uncertainty components changed the recommendation.

## Acceptance criteria
The system must be able to compare feasible actions quantitatively, identify the information with highest net expected value, return a recommendation only when epistemically and operationally justified, and otherwise abstain or escalate to human review.
