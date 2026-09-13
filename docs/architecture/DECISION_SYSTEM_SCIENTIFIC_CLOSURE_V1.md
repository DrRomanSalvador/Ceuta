# CeutIA Decision System — Scientific Closure Criteria V1

## Purpose

This document defines the minimum conditions under which CeutIA may emit an operational recommendation rather than merely an analytical result.

## Decision chain

`observation -> state estimation -> uncertainty -> dynamics -> causal identification -> probabilistic prediction -> scenarios/counterfactuals -> utility/harm -> constrained optimization -> decision -> intervention -> outcome -> attribution -> learning -> reassessment`

A component existing in the repository is not evidence that the chain is scientifically executable. Each link must be integrated, tested and validated at the appropriate maturity level.

## Fail-closed epistemic conditions

A recommendation requires, at minimum:

1. adequate observability for the decision;
2. an identified estimand or explicitly non-causal predictive target;
3. valid and calibrated model outputs for the intended use;
4. explicit scenario probabilities or a formally stated robust uncertainty set;
5. common scenario support across alternatives being compared;
6. explicit utility, harm and resource-cost semantics;
7. hard constraints evaluated before selection;
8. uncertainty propagated to the decision criterion;
9. provenance and assumptions attached to the decision;
10. predefined reassessment triggers.

Failure of a required condition must result in abstention or human review, never silent substitution with a weaker epistemic claim.

## Decision mathematics

For a finite scenario set `s`, option `a`, utility `U(a,s)`, harm `H(a,s)` and probability `p(s)`:

`EU(a) = sum_s p(s) U(a,s) - cost(a)`

`EH(a) = sum_s p(s) H(a,s)`

`WC(a) = min_s U(a,s) - cost(a)`

Tail-risk criteria use lower-tail utility CVaR. Regret is defined against the best available alternative within each common scenario, not as the utility range of a single option.

## Information as an action

If the net expected value of information is positive and materially changes the decision, information acquisition may be selected as the optimal action. This must not be confused with simply reporting a VoI number.

## Validation boundary

The decision layer cannot establish the scientific validity of upstream state, causal or predictive models. It consumes explicit validity declarations and preserves their provenance. Prospective, external and distribution-shift validation therefore remain separate requirements for claims of operational effectiveness.

## Current implementation

`backend/app/core/decision/rigorous_engine.py` provides a fail-closed finite-scenario decision analysis engine with common-scenario validation, hard feasibility constraints, expected utility, worst-case utility, lower-tail CVaR and cross-alternative maximum regret. Its output is conditional on the supplied probabilities and scenario model.

This is a substantive decision layer, not evidence that CeutIA has completed prospective scientific validation as a whole.
