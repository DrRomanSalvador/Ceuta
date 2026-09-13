"""Identification-first causal estimators for observational longitudinal data.

These estimators are deliberately narrow. They estimate explicit causal estimands
only after positivity, consistency and exchangeability assumptions are declared.
Failure of an identification check returns an abstention object rather than an
association mislabeled as a causal effect.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Sequence

import numpy as np
from scipy.special import expit
from scipy.stats import norm


@dataclass(frozen=True, slots=True)
class CausalEstimate:
    estimand: str
    estimate: float | None
    standard_error: float | None
    lower: float | None
    upper: float | None
    identified: bool
    positivity_ok: bool
    assumptions: tuple[str, ...]
    diagnostics: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class IdentificationCheck:
    identified: bool
    positivity_ok: bool
    consistency_declared: bool
    exchangeability_declared: bool
    diagnostics: tuple[str, ...]


class IdentificationGate:
    """Checks the minimum assumptions required by the estimators in this module."""

    @staticmethod
    def check(treatment: Sequence[float], propensity: Sequence[float], *,
              consistency: bool, exchangeability: bool,
              min_propensity: float = 0.01) -> IdentificationCheck:
        if len(treatment) != len(propensity) or not treatment:
            raise ValueError("treatment and propensity must have equal non-zero length")
        p = np.asarray(propensity, dtype=float)
        a = np.asarray(treatment, dtype=float)
        if np.any(~np.isfinite(p)) or np.any(~np.isfinite(a)):
            raise ValueError("treatment and propensity must be finite")
        binary = np.isin(a, [0.0, 1.0]).all()
        positivity = bool(binary and np.all((p >= min_propensity) & (p <= 1.0 - min_propensity)))
        diagnostics: list[str] = []
        if not binary:
            diagnostics.append("treatment must be binary for this estimator")
        if not positivity:
            diagnostics.append("positivity/common-support requirement failed")
        if not consistency:
            diagnostics.append("consistency has not been declared")
        if not exchangeability:
            diagnostics.append("conditional exchangeability has not been declared")
        return IdentificationCheck(bool(binary and positivity and consistency and exchangeability),
                                   positivity, consistency, exchangeability, tuple(diagnostics))


class AIPWBinaryATE:
    """Augmented inverse-probability weighted ATE with influence-function SE.

    Inputs are nuisance predictions evaluated out-of-sample (cross-fitting is
    therefore the caller's responsibility). This prevents the estimator from
    silently using the same observations to fit and evaluate nuisance models.
    """

    @staticmethod
    def estimate(treatment: Sequence[float], outcome: Sequence[float],
                 propensity: Sequence[float], mu1: Sequence[float], mu0: Sequence[float],
                 *, consistency: bool, exchangeability: bool,
                 min_propensity: float = 0.01, alpha: float = 0.05) -> CausalEstimate:
        arrays = [np.asarray(x, dtype=float) for x in (treatment, outcome, propensity, mu1, mu0)]
        if len({len(x) for x in arrays}) != 1 or not arrays[0].size:
            raise ValueError("all input vectors must have equal non-zero length")
        a, y, p, m1, m0 = arrays
        gate = IdentificationGate.check(a, p, consistency=consistency,
                                       exchangeability=exchangeability,
                                       min_propensity=min_propensity)
        if not gate.identified:
            return CausalEstimate("ATE", None, None, None, None, False, gate.positivity_ok,
                                  ("consistency", "conditional exchangeability", "positivity"), gate.diagnostics)
        score = m1 - m0 + a * (y - m1) / p - (1.0 - a) * (y - m0) / (1.0 - p)
        estimate = float(np.mean(score))
        influence = score - estimate
        se = float(np.std(influence, ddof=1) / np.sqrt(len(score)))
        z = float(norm.ppf(1.0 - alpha / 2.0))
        return CausalEstimate("ATE", estimate, se, estimate - z * se, estimate + z * se,
                              True, True, ("consistency", "conditional exchangeability", "positivity"),
                              ("nuisance predictions must be evaluated out-of-sample",))


class LongitudinalMarginalStructuralEffect:
    """Two-time-point IPW estimator for a binary treatment sequence.

    The caller supplies stabilized joint treatment weights. The implementation
    estimates the marginal contrast under the declared longitudinal exchangeability
    and positivity assumptions. It intentionally does not fit a treatment model,
    because doing so without the full time-varying covariate history would create a
    false impression of identification.
    """

    @staticmethod
    def estimate(outcome: Sequence[float], potential_regime: Sequence[int],
                 regime_probability: Sequence[float], *, positivity: bool,
                 sequential_exchangeability: bool, consistency: bool,
                 alpha: float = 0.05) -> CausalEstimate:
        y = np.asarray(outcome, dtype=float)
        regime = np.asarray(potential_regime, dtype=int)
        prob = np.asarray(regime_probability, dtype=float)
        if len(y) == 0 or len({len(y), len(regime), len(prob)}) != 1:
            raise ValueError("inputs must have equal non-zero length")
        if np.any(~np.isfinite(y)) or np.any(~np.isfinite(prob)):
            raise ValueError("outcomes and probabilities must be finite")
        identified = positivity and sequential_exchangeability and consistency
        if not identified:
            diagnostics = []
            if not positivity:
                diagnostics.append("longitudinal positivity not established")
            if not sequential_exchangeability:
                diagnostics.append("sequential exchangeability not established")
            if not consistency:
                diagnostics.append("consistency not established")
            return CausalEstimate("marginal regime contrast", None, None, None, None,
                                  False, positivity, ("positivity", "sequential exchangeability", "consistency"),
                                  tuple(diagnostics))
        if np.any((prob <= 0) | (prob > 1)) or not np.isin(regime, [0, 1]).all():
            raise ValueError("regime must be binary and probabilities in (0,1]")
        # Horvitz-Thompson mean within each regime; caller's probabilities are
        # stabilized joint probabilities for the complete treatment history.
        estimates = []
        variances = []
        for r in (0, 1):
            mask = regime == r
            if not mask.any():
                return CausalEstimate("marginal regime contrast", None, None, None, None,
                                      False, positivity, (), (f"regime {r} absent",))
            values = y[mask] / prob[mask]
            estimates.append(float(values.mean() / np.mean(1.0 / prob[mask])))
            variances.append(float(np.var(values, ddof=1) / len(values)))
        estimate = estimates[1] - estimates[0]
        se = float(np.sqrt(variances[0] + variances[1]))
        z = float(norm.ppf(1.0 - alpha / 2.0))
        return CausalEstimate("marginal regime contrast", estimate, se, estimate - z * se,
                              estimate + z * se, True, True,
                              ("positivity", "sequential exchangeability", "consistency"),
                              ("joint treatment probabilities must be correctly specified",))
