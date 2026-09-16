"""Finite scientific-limitation controls that are enforceable without prospective data.

These controls do not establish prospective validity. They make the remaining
scientific boundary explicit and testable: point-in-time feature eligibility,
frozen baseline identities, dependence-aware resampling, and calibration
statistics with proper scoring rules.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
import random
from statistics import mean
from typing import Iterable, Sequence


def _utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return value.astimezone(timezone.utc)


def _digest(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class FeatureDependency:
    dependency_id: str
    source_id: str
    source_version: str
    publication_time: datetime
    acquisition_time: datetime
    revision: int
    transformation_id: str
    derived_from_outcome: bool = False
    future_derived: bool = False

    def __post_init__(self) -> None:
        if not self.dependency_id or not self.source_id or not self.source_version or not self.transformation_id:
            raise ValueError("feature dependency identity is required")
        if self.revision < 0:
            raise ValueError("revision must be non-negative")
        object.__setattr__(self, "publication_time", _utc(self.publication_time))
        object.__setattr__(self, "acquisition_time", _utc(self.acquisition_time))

    def eligible_at(self, cutoff: datetime) -> bool:
        cutoff = _utc(cutoff)
        return (
            self.publication_time <= cutoff
            and self.acquisition_time <= cutoff
            and not self.derived_from_outcome
            and not self.future_derived
        )


@dataclass(frozen=True, slots=True)
class PITFeature:
    name: str
    value: float
    dependencies: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.name or not self.dependencies or not math.isfinite(self.value):
            raise ValueError("feature requires name, finite value and dependencies")


@dataclass(frozen=True, slots=True)
class PITManifest:
    forecast_origin: datetime
    information_cutoff: datetime
    dependencies: tuple[FeatureDependency, ...]
    features: tuple[PITFeature, ...]
    manifest_fingerprint: str
    feature_fingerprint: str

    @classmethod
    def build(
        cls,
        *,
        forecast_origin: datetime,
        information_cutoff: datetime,
        dependencies: Iterable[FeatureDependency],
        features: Iterable[PITFeature],
    ) -> "PITManifest":
        origin = _utc(forecast_origin)
        cutoff = _utc(information_cutoff)
        if cutoff > origin:
            raise ValueError("information cutoff cannot be after forecast origin")
        deps = tuple(sorted(dependencies, key=lambda item: item.dependency_id))
        feats = tuple(sorted(features, key=lambda item: item.name))
        by_id = {item.dependency_id: item for item in deps}
        if len(by_id) != len(deps):
            raise ValueError("dependency ids must be unique")
        for feature in feats:
            if any(dep_id not in by_id for dep_id in feature.dependencies):
                raise ValueError(f"feature {feature.name} references an unknown dependency")
            if any(not by_id[dep_id].eligible_at(cutoff) for dep_id in feature.dependencies):
                raise ValueError(f"feature {feature.name} has an ineligible point-in-time dependency")
        manifest_payload = {
            "forecast_origin": origin.isoformat(),
            "information_cutoff": cutoff.isoformat(),
            "dependencies": [
                {
                    "dependency_id": dep.dependency_id,
                    "source_id": dep.source_id,
                    "source_version": dep.source_version,
                    "publication_time": dep.publication_time.isoformat(),
                    "acquisition_time": dep.acquisition_time.isoformat(),
                    "revision": dep.revision,
                    "transformation_id": dep.transformation_id,
                    "derived_from_outcome": dep.derived_from_outcome,
                    "future_derived": dep.future_derived,
                }
                for dep in deps
            ],
            "features": [
                {"name": feature.name, "value": feature.value, "dependencies": feature.dependencies}
                for feature in feats
            ],
        }
        manifest_hash = _digest(manifest_payload)
        feature_hash = _digest({"manifest": manifest_hash, "features": [(f.name, f.value, f.dependencies) for f in feats]})
        return cls(origin, cutoff, deps, feats, manifest_hash, feature_hash)

    def verify(self, *, forecast_origin: datetime, information_cutoff: datetime) -> None:
        if _utc(forecast_origin) != self.forecast_origin:
            raise ValueError("forecast origin does not match PIT manifest")
        if _utc(information_cutoff) != self.information_cutoff:
            raise ValueError("information cutoff does not match PIT manifest")
        if any(not dep.eligible_at(self.information_cutoff) for dep in self.dependencies):
            raise ValueError("PIT manifest contains an ineligible dependency")


@dataclass(frozen=True, slots=True)
class BaselineSpec:
    baseline_id: str
    version: str
    definition: str
    population: str
    training_cutoff: datetime
    feature_cutoff: datetime

    @property
    def identity(self) -> str:
        return _digest({
            "baseline_id": self.baseline_id,
            "version": self.version,
            "definition": self.definition,
            "population": self.population,
            "training_cutoff": _utc(self.training_cutoff).isoformat(),
            "feature_cutoff": _utc(self.feature_cutoff).isoformat(),
        })


class FrozenBaselineRegistry:
    def __init__(self) -> None:
        self._specs: dict[str, BaselineSpec] = {}

    def register(self, spec: BaselineSpec) -> str:
        if spec.baseline_id in self._specs and self._specs[spec.baseline_id].identity != spec.identity:
            raise ValueError("baseline identity is immutable; create a new baseline id/version")
        self._specs[spec.baseline_id] = spec
        return spec.identity

    def get(self, baseline_id: str) -> BaselineSpec:
        try:
            return self._specs[baseline_id]
        except KeyError as exc:
            raise KeyError(f"unknown baseline: {baseline_id}") from exc

    def identity(self, baseline_id: str) -> str:
        return self.get(baseline_id).identity


@dataclass(frozen=True, slots=True)
class DependenceSummary:
    unit: str
    n_observations: int
    n_units: int
    estimate: float
    lower: float
    upper: float


def cluster_bootstrap_mean(
    values: Sequence[float],
    groups: Sequence[str],
    *,
    confidence: float = 0.95,
    resamples: int = 2000,
    seed: int = 17,
) -> DependenceSummary:
    if len(values) != len(groups) or not values:
        raise ValueError("values and groups must have equal non-zero length")
    if not 0.0 < confidence < 1.0 or resamples < 100:
        raise ValueError("invalid confidence or resample count")
    grouped: dict[str, list[float]] = {}
    for value, group in zip(values, groups):
        if not math.isfinite(float(value)):
            raise ValueError("values must be finite")
        grouped.setdefault(str(group), []).append(float(value))
    units = tuple(grouped.values())
    if len(units) < 2:
        raise ValueError("at least two independent clusters are required")
    estimate = mean(values)
    rng = random.Random(seed)
    boot: list[float] = []
    for _ in range(resamples):
        sample = [units[rng.randrange(len(units))] for _ in units]
        boot.append(mean(value for cluster in sample for value in cluster))
    boot.sort()
    alpha = (1.0 - confidence) / 2.0
    lo = boot[max(0, min(len(boot) - 1, int(alpha * len(boot))))]
    hi = boot[max(0, min(len(boot) - 1, int((1.0 - alpha) * len(boot)) - 1))]
    return DependenceSummary("cluster", len(values), len(units), estimate, lo, hi)


def binary_calibration(
    observed: Sequence[int],
    probabilities: Sequence[float],
    *,
    bins: int = 10,
) -> dict[str, float | int | str | None]:
    if len(observed) != len(probabilities) or not observed:
        raise ValueError("observed and probabilities must have equal non-zero length")
    if bins < 2:
        raise ValueError("at least two calibration bins are required")
    y = [int(v) for v in observed]
    p = [float(v) for v in probabilities]
    if any(v not in (0, 1) for v in y):
        raise ValueError("observed values must be binary")
    if any(not math.isfinite(v) or not 0.0 <= v <= 1.0 for v in p):
        raise ValueError("probabilities must be finite and in [0,1]")
    eps = 1e-12
    clipped = [min(1.0 - eps, max(eps, v)) for v in p]
    brier = mean((prob - obs) ** 2 for obs, prob in zip(y, p))
    log_loss = -mean(obs * math.log(prob) + (1 - obs) * math.log(1 - prob) for obs, prob in zip(y, clipped))
    observed_rate = mean(y)
    predicted_rate = mean(p)
    calibration_gap = predicted_rate - observed_rate
    ece = 0.0
    for index in range(bins):
        lo = index / bins
        hi = (index + 1) / bins
        members = [i for i, prob in enumerate(p) if (lo <= prob < hi) or (index == bins - 1 and prob == hi)]
        if members:
            ece += len(members) / len(p) * abs(mean(p[i] for i in members) - mean(y[i] for i in members))
    return {
        "n": len(y),
        "brier": brier,
        "log_loss": log_loss,
        "observed_rate": observed_rate,
        "predicted_rate": predicted_rate,
        "calibration_gap": calibration_gap,
        "expected_calibration_error": ece,
        "status": "empirical_calibration_diagnostic",
        "prospective_validity_status": "NOT_ESTABLISHED",
    }


__all__ = [
    "BaselineSpec",
    "DependenceSummary",
    "FeatureDependency",
    "FrozenBaselineRegistry",
    "PITFeature",
    "PITManifest",
    "binary_calibration",
    "cluster_bootstrap_mean",
]
