"""Calibrated probabilistic forecasting primitives.

The module separates point prediction, interval calibration and distributional
scoring. It never reports an interval as a confidence statement about a causal
parameter: intervals are predictive unless explicitly identified otherwise.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import erf, exp, isfinite, log, pi, sqrt
from statistics import mean, median
from typing import Callable, Sequence


@dataclass(frozen=True, slots=True)
class Forecast:
    origin: float
    target: float
    mean: float
    lower: float
    upper: float
    scale: float
    coverage_level: float
    model_id: str

    def __post_init__(self) -> None:
        if not all(isfinite(x) for x in (self.origin, self.target, self.mean, self.lower, self.upper, self.scale)):
            raise ValueError("forecast values must be finite")
        if self.scale <= 0 or not 0 < self.coverage_level < 1 or self.lower > self.upper:
            raise ValueError("invalid forecast interval")


@dataclass(frozen=True, slots=True)
class CalibrationReport:
    nominal_coverage: float
    empirical_coverage: float
    mean_interval_width: float
    mean_absolute_error: float
    interval_score: float
    n: int


class ProbabilisticForecastEngine:
    """Gaussian predictive baseline plus rolling residual conformal calibration."""

    @staticmethod
    def gaussian_interval(mean_value: float, scale: float, level: float) -> tuple[float, float]:
        if scale <= 0 or not 0 < level < 1:
            raise ValueError("scale must be positive and level in (0,1)")
        # Acklam-free approximation of the standard-normal inverse CDF.
        p = (1.0 + level) / 2.0
        z = ProbabilisticForecastEngine._normal_ppf(p)
        return mean_value - z * scale, mean_value + z * scale

    @staticmethod
    def _normal_ppf(p: float) -> float:
        if not 0 < p < 1:
            raise ValueError("p must be in (0,1)")
        # Peter John Acklam rational approximation.
        a = (-39.6968302866538, 220.946098424521, -275.928510446969, 138.357751867269,
             -30.6647980661472, 2.50662827745924)
        b = (-54.4760987982241, 161.585836858041, -155.698979859887, 66.8013118877197,
             -13.2806815528857)
        c = (-0.00778489400243029, -0.322396458041136, -2.40075827716184,
             -2.54973253934373, 4.37466414146497, 2.93816398269878)
        d = (0.00778469570904146, 0.32246712907004, 2.445134137143,
             3.75440866190742)
        if p < 0.02425:
            q = sqrt(-2 * log(p))
            return (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) /
                    ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1))
        if p > 1 - 0.02425:
            q = sqrt(-2 * log(1 - p))
            return -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) /
                     ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1))
        q = p - 0.5
        r = q * q
        return (((((a[0] * r + a[1]) * r + a[2]) * r + a[3]) * r + a[4]) * r + a[5]) * q /
                (((((b[0] * r + b[1]) * r + b[2]) * r + b[3]) * r + b[4]) * r + 1))

    @staticmethod
    def conformal_radius(residuals: Sequence[float], level: float) -> float:
        if not residuals or not 0 < level < 1:
            raise ValueError("residuals must be non-empty and level in (0,1)")
        values = sorted(abs(float(r)) for r in residuals)
        # Finite-sample split-conformal quantile: ceil((n+1)*(1-alpha))/n,
        # clipped to the largest observed nonconformity score.
        alpha = 1.0 - level
        rank = max(1, min(len(values), int((len(values) + 1) * (1.0 - alpha) + 0.999999)))
        return values[rank - 1]

    @classmethod
    def calibrated_forecast(cls, origin: float, target: float, mean_value: float,
                            residuals: Sequence[float], level: float, model_id: str) -> Forecast:
        radius = cls.conformal_radius(residuals, level)
        lower, upper = mean_value - radius, mean_value + radius
        scale = max(radius, 1e-12)
        return Forecast(origin, target, mean_value, lower, upper, scale, level, model_id)

    @staticmethod
    def interval_score(forecast: Forecast) -> float:
        alpha = 1.0 - forecast.coverage_level
        y, lo, hi = forecast.target, forecast.lower, forecast.upper
        penalty = (2.0 / alpha) * max(lo - y, 0.0) + (2.0 / alpha) * max(y - hi, 0.0)
        return (hi - lo) + penalty

    @staticmethod
    def crps_gaussian(observation: float, mean_value: float, scale: float) -> float:
        if scale <= 0:
            raise ValueError("scale must be positive")
        z = (observation - mean_value) / scale
        phi = exp(-0.5 * z * z) / sqrt(2 * pi)
        Phi = 0.5 * (1 + erf(z / sqrt(2)))
        return scale * (z * (2 * Phi - 1) + 2 * phi - 1 / sqrt(pi))

    @staticmethod
    def evaluate(forecasts: Sequence[Forecast]) -> CalibrationReport:
        if not forecasts:
            raise ValueError("at least one forecast is required")
        empirical = mean(f.lower <= f.target <= f.upper for f in forecasts)
        width = mean(f.upper - f.lower for f in forecasts)
        mae = mean(abs(f.target - f.mean) for f in forecasts)
        score = mean(ProbabilisticForecastEngine.interval_score(f) for f in forecasts)
        nominal = mean(f.coverage_level for f in forecasts)
        return CalibrationReport(nominal, empirical, width, mae, score, len(forecasts))


@dataclass(frozen=True, slots=True)
class RollingOriginResult:
    forecasts: tuple[Forecast, ...]
    calibration: CalibrationReport


class RollingOriginEvaluator:
    """Leakage-resistant temporal evaluation: each forecast uses only prior data."""

    @staticmethod
    def evaluate(values: Sequence[float], predictor: Callable[[Sequence[float]], float],
                 min_train: int, level: float, model_id: str) -> RollingOriginResult:
        if min_train < 2 or len(values) <= min_train:
            raise ValueError("insufficient temporal observations")
        forecasts: list[Forecast] = []
        residuals: list[float] = []
        for index in range(min_train, len(values)):
            history = tuple(float(v) for v in values[:index])
            prediction = float(predictor(history))
            if residuals:
                radius = ProbabilisticForecastEngine.conformal_radius(residuals, level)
            else:
                radius = max(1e-12, abs(values[index - 1] - prediction))
            forecast = Forecast(float(index - 1), float(index), prediction,
                                prediction - radius, prediction + radius, radius, level, model_id)
            forecasts.append(forecast)
            residuals.append(float(values[index] - prediction))
        return RollingOriginResult(tuple(forecasts), ProbabilisticForecastEngine.evaluate(forecasts))
