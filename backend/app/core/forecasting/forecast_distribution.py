from __future__ import annotations

from dataclasses import dataclass
from math import sqrt


@dataclass(frozen=True, slots=True)
class ForecastDistribution:
    mean: float
    standard_deviation: float
    lower: float
    upper: float
    interval_kind: str
    nominal_coverage: float | None = None


class ForecastDistributionEngine:
    """Build descriptive sample summaries without falsely claiming calibration."""

    def build(self, samples: tuple[float, ...], *, z: float = 1.96) -> ForecastDistribution:
        if not samples:
            raise ValueError("samples must not be empty")
        mean = sum(samples) / len(samples)
        variance = sum((x - mean) ** 2 for x in samples) / max(1, len(samples) - 1)
        sd = sqrt(variance)
        margin = z * sd / sqrt(len(samples))
        return ForecastDistribution(
            mean=mean,
            standard_deviation=sd,
            lower=mean - margin,
            upper=mean + margin,
            interval_kind="mean_confidence_interval",
            nominal_coverage=None,
        )

    def predictive_from_samples(
        self,
        samples: tuple[float, ...],
        *,
        lower_quantile: float = 0.025,
        upper_quantile: float = 0.975,
    ) -> ForecastDistribution:
        if not samples:
            raise ValueError("samples must not be empty")
        if not 0.0 <= lower_quantile < upper_quantile <= 1.0:
            raise ValueError("invalid quantiles")
        ordered = sorted(samples)

        def quantile(q: float) -> float:
            position = (len(ordered) - 1) * q
            left = int(position)
            right = min(left + 1, len(ordered) - 1)
            fraction = position - left
            return ordered[left] + fraction * (ordered[right] - ordered[left])

        mean = sum(ordered) / len(ordered)
        variance = sum((x - mean) ** 2 for x in ordered) / max(1, len(ordered) - 1)
        coverage = upper_quantile - lower_quantile
        return ForecastDistribution(
            mean=mean,
            standard_deviation=sqrt(variance),
            lower=quantile(lower_quantile),
            upper=quantile(upper_quantile),
            interval_kind="empirical_predictive_interval",
            nominal_coverage=coverage,
        )
