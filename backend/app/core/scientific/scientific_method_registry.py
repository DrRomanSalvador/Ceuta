"""Versioned scientific method/preprocessing registry and compatibility metadata."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import sqlite3


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


@dataclass(frozen=True, slots=True)
class ScientificMethodRelease:
    method_id: str
    version: str
    method_family: str
    preprocessing: tuple[str, ...]
    assumptions: tuple[str, ...]
    validation_window: str
    applicability_boundary: str
    source_ids: tuple[str, ...]
    code_revision: str
    configuration_hash: str

    def __post_init__(self) -> None:
        if not all((self.method_id, self.version, self.method_family, self.validation_window, self.applicability_boundary, self.code_revision, self.configuration_hash)):
            raise ValueError("scientific method release metadata is incomplete")
        if not self.source_ids:
            raise ValueError("scientific method release requires source provenance")
        if not self.assumptions:
            raise ValueError("scientific method release requires assumptions")

    @property
    def fingerprint(self) -> str:
        return sha256(_canonical(asdict(self)).encode()).hexdigest()


class ScientificMethodRegistry:
    def __init__(self, storage_path: str) -> None:
        if not storage_path:
            raise ValueError("storage_path is required")
        self.storage_path = storage_path
        with sqlite3.connect(storage_path) as db:
            db.execute("""CREATE TABLE IF NOT EXISTS scientific_method_releases(
                method_id TEXT NOT NULL, version TEXT NOT NULL, payload TEXT NOT NULL,
                fingerprint TEXT NOT NULL, PRIMARY KEY(method_id, version)
            )""")

    def register(self, release: ScientificMethodRelease) -> None:
        payload = _canonical(asdict(release))
        fingerprint = sha256(payload.encode()).hexdigest()
        with sqlite3.connect(self.storage_path) as db:
            if db.execute("SELECT 1 FROM scientific_method_releases WHERE method_id=? AND version=?", (release.method_id, release.version)).fetchone():
                raise ValueError("method release already exists")
            db.execute("INSERT INTO scientific_method_releases VALUES(?,?,?,?)", (release.method_id, release.version, payload, fingerprint))

    def get(self, method_id: str, version: str) -> ScientificMethodRelease:
        with sqlite3.connect(self.storage_path) as db:
            row = db.execute("SELECT payload FROM scientific_method_releases WHERE method_id=? AND version=?", (method_id, version)).fetchone()
        if not row:
            raise KeyError((method_id, version))
        data = json.loads(row[0])
        data["preprocessing"] = tuple(data["preprocessing"]); data["assumptions"] = tuple(data["assumptions"]); data["source_ids"] = tuple(data["source_ids"])
        return ScientificMethodRelease(**data)

    def all(self) -> tuple[ScientificMethodRelease, ...]:
        with sqlite3.connect(self.storage_path) as db:
            rows = db.execute("SELECT payload FROM scientific_method_releases ORDER BY method_id,version").fetchall()
        result = []
        for (payload,) in rows:
            data = json.loads(payload)
            for key in ("preprocessing", "assumptions", "source_ids"):
                data[key] = tuple(data[key])
            result.append(ScientificMethodRelease(**data))
        return tuple(result)

    def verify_integrity(self) -> bool:
        with sqlite3.connect(self.storage_path) as db:
            rows = db.execute("SELECT payload,fingerprint FROM scientific_method_releases").fetchall()
        return all(sha256(payload.encode()).hexdigest() == fingerprint for payload, fingerprint in rows)


def register_core_method_releases(registry: ScientificMethodRegistry, *, code_revision: str, configuration_hash: str) -> None:
    """Register only methods whose scientific identity is already present in the corpus.

    This is a release catalogue, not a claim of prospective validity. Callers must
    still run ScientificMethodCompatibility against their actual data contract.
    """
    releases = (
        ScientificMethodRelease("csd", "1", "critical_slowing_down", ("lag1_autocorrelation", "variance", "minimum_observations"), ("adequate_sampling", "domain_specific_dynamics", "noise_not_dominant"), "prospective-required", "early_warning_supporting_diagnostic", ("dakos-2012-csd-robustness", "dakos-2026-ews-overview", "false-positives-2019-ews"), code_revision, configuration_hash),
        ScientificMethodRelease("rdm", "1", "robust_decision_making", ("plausible_future_enumeration", "satisficing", "regret"), ("explicit_strategy_performance", "declared_thresholds"), "prospective-required", "deep_uncertainty_decision_support", ("dmdu-rdm-pandemic-2023", "dmdu-rand-robust-decision-making"), code_revision, configuration_hash),
        ScientificMethodRelease("bma", "1", "bayesian_model_averaging", ("validation_log_predictive_score", "weight_normalization"), ("comparable_target_horizon", "point_in_time_validation"), "prospective-required", "probabilistic_forecast_aggregation", ("ensemble-bayesian-model-averaging",), code_revision, configuration_hash),
        ScientificMethodRelease("causal-identification", "1", "causal_identification", ("estimand_specification", "assumption_audit"), ("consistency", "conditional_exchangeability", "positivity"), "prospective-required", "identified_causal_effects_only", ("pearl-2009-causality", "causal-generalizability-bareinboim"), code_revision, configuration_hash),
        ScientificMethodRelease("metric-reactivity", "1", "reflexive_measurement", ("exposure_tracking", "outcome_decoupling", "source_divergence"), ("indicator_exposure_observable", "independent_outcome_measurement"), "prospective-required", "incentive_exposed_indicators", ("bevan-hood-2006-target-gaming", "mannion-braithwaite-2012-unintended-consequences"), code_revision, configuration_hash),
        ScientificMethodRelease("nonstationarity", "1", "regime_change_detection", ("rolling_mean_shift", "variance_ratio", "support_check"), ("ordered_observations", "reference_support_declared"), "prospective-required", "time_series_with_declared_support", ("dakos-2026-ews-overview", "wolpert-macready-1997-no-free-lunch"), code_revision, configuration_hash),
    )
    for release in releases:
        try:
            registry.register(release)
        except ValueError as exc:
            if "already exists" not in str(exc):
                raise


__all__ = ["ScientificMethodRegistry", "ScientificMethodRelease", "register_core_method_releases"]
