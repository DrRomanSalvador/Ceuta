"""Integrated territorial system representation and epistemic restraint layer."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from math import isfinite, log
from typing import Mapping, Sequence

import networkx as nx
import numpy as np


class EpistemicRelation(StrEnum):
    ASSOCIATION = "association"
    PREDICTION = "prediction"
    CAUSAL = "causal"
    MECHANISTIC = "mechanistic"
    OBSERVATION = "observation"
    UNKNOWN = "unknown"


class StateKind(StrEnum):
    OBSERVED = "observed"
    LATENT = "latent"
    PARTIALLY_OBSERVED = "partially_observed"
    ESTIMATED = "estimated"
    INFERRED = "inferred"
    COMPETING = "competing"
    UNKNOWN = "unknown"


class MissingnessMechanism(StrEnum):
    MCAR = "MCAR"
    MAR = "MAR"
    MNAR = "MNAR"
    UNKNOWN = "unknown"


class Scale(StrEnum):
    INDIVIDUAL = "individual"
    HOUSEHOLD = "household"
    SUBGROUP = "subgroup"
    NEIGHBOURHOOD = "neighbourhood"
    INSTITUTION = "institution"
    CITY = "city"
    REGIONAL = "regional"
    NATIONAL = "national"
    INTERNATIONAL = "international"


@dataclass(frozen=True, slots=True)
class ObservationProcess:
    process_id: str
    phenomenon: str
    measurement_method: str
    selection_mechanism: str
    reporting_mechanism: str
    aggregation_rule: str | None = None
    publication_delay_days: float | None = None
    revision_policy: str | None = None
    missingness: MissingnessMechanism = MissingnessMechanism.UNKNOWN
    coding_version: str | None = None

    def __post_init__(self) -> None:
        if not self.process_id or not self.phenomenon or not self.measurement_method:
            raise ValueError("observation process identity, phenomenon and method are required")
        if not self.selection_mechanism or not self.reporting_mechanism:
            raise ValueError("selection and reporting mechanisms are required")
        if self.publication_delay_days is not None and (
            not isfinite(self.publication_delay_days) or self.publication_delay_days < 0
        ):
            raise ValueError("publication delay must be finite and non-negative")


@dataclass(frozen=True, slots=True)
class Measurement:
    observation_id: str
    variable: str
    value: float | None
    observed_at: datetime
    available_at: datetime
    scale: Scale
    unit: str | None = None
    denominator: float | None = None
    process_id: str | None = None
    revision_id: str | None = None
    quality_flags: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.observation_id or not self.variable:
            raise ValueError("measurement identity is required")
        for timestamp in (self.observed_at, self.available_at):
            if timestamp.tzinfo is None or timestamp.utcoffset() is None:
                raise ValueError("measurement timestamps must be timezone-aware")
        if self.available_at < self.observed_at:
            raise ValueError("availability cannot precede observation time")
        if self.value is not None and not isfinite(float(self.value)):
            raise ValueError("measurement value must be finite")
        if self.denominator is not None and (not isfinite(self.denominator) or self.denominator <= 0):
            raise ValueError("denominator must be positive and finite")


@dataclass(frozen=True, slots=True)
class StateHypothesis:
    hypothesis_id: str
    state_vector: tuple[float, ...]
    covariance: tuple[tuple[float, ...], ...]
    kind: StateKind
    probability: float
    observation_refs: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.hypothesis_id or not self.state_vector:
            raise ValueError("state hypothesis requires identity and state vector")
        if not isfinite(float(self.probability)) or not 0.0 <= self.probability <= 1.0:
            raise ValueError("state hypothesis probability must be finite and in [0,1]")
        state = np.asarray(self.state_vector, dtype=float)
        if state.shape != (len(self.state_vector),) or not np.all(np.isfinite(state)):
            raise ValueError("state vector must be finite")
        matrix = np.asarray(self.covariance, dtype=float)
        if matrix.shape != (len(self.state_vector), len(self.state_vector)):
            raise ValueError("covariance shape must match state vector")
        if not np.all(np.isfinite(matrix)) or not np.allclose(matrix, matrix.T, atol=1e-10):
            raise ValueError("state covariance must be finite and symmetric")
        if np.any(np.linalg.eigvalsh(matrix) < -1e-9):
            raise ValueError("state covariance must be positive semidefinite")


@dataclass(frozen=True, slots=True)
class StateEstimate:
    estimate: tuple[float, ...]
    covariance: tuple[tuple[float, ...], ...]
    hypotheses: tuple[StateHypothesis, ...]
    identifiable: bool
    observable: bool
    uncertainty_note: str


@dataclass(frozen=True, slots=True)
class ObservabilityAssessment:
    observable: bool
    rank: int
    required_rank: int
    structural: bool
    reason: str
    competing_explanations: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class IdentifiabilityAssessment:
    identifiable: bool
    rank: int
    parameter_count: int
    structural: bool
    condition_number: float | None
    reason: str


@dataclass(frozen=True, slots=True)
class ScaleMapping:
    mapping_id: str
    source_scale: Scale
    target_scale: Scale
    source_ids: tuple[str, ...]
    target_ids: tuple[str, ...]
    operator: str
    weight: float
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.mapping_id or not self.source_ids or not self.target_ids or not self.operator:
            raise ValueError("scale mapping requires identity, endpoints and operator")
        if not isfinite(self.weight):
            raise ValueError("scale mapping weight must be finite")


@dataclass(frozen=True, slots=True)
class SpatialUnit:
    unit_id: str
    scale: Scale
    geometry_ref: str | None = None
    parent_id: str | None = None
    population: float | None = None
    area_km2: float | None = None

    def __post_init__(self) -> None:
        if not self.unit_id:
            raise ValueError("spatial unit requires identity")
        if self.population is not None and (not isfinite(self.population) or self.population < 0):
            raise ValueError("population must be finite and non-negative")
        if self.area_km2 is not None and (not isfinite(self.area_km2) or self.area_km2 <= 0):
            raise ValueError("area must be positive and finite")


@dataclass(frozen=True, slots=True)
class SpatialRelation:
    source_id: str
    target_id: str
    weight: float
    relation: str
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.source_id or not self.target_id or self.source_id == self.target_id:
            raise ValueError("spatial relation endpoints must be distinct")
        if not isfinite(self.weight) or self.weight < 0:
            raise ValueError("spatial relation weight must be finite and non-negative")


@dataclass(frozen=True, slots=True)
class MobilityFlow:
    flow_id: str
    origin: str
    destination: str
    time: datetime
    volume: float
    population_basis: float | None = None
    source_ref: str | None = None

    def __post_init__(self) -> None:
        if not self.flow_id or not self.origin or not self.destination:
            raise ValueError("mobility flow identity and endpoints are required")
        if self.time.tzinfo is None or self.time.utcoffset() is None:
            raise ValueError("mobility flow time must be timezone-aware")
        if not isfinite(self.volume) or self.volume < 0:
            raise ValueError("mobility volume must be finite and non-negative")
        if self.population_basis is not None and (not isfinite(self.population_basis) or self.population_basis <= 0):
            raise ValueError("population basis must be positive")


@dataclass(frozen=True, slots=True)
class DomainCoupling:
    coupling_id: str
    source_domain: str
    target_domain: str
    relation: EpistemicRelation
    strength: float
    lag_days: float = 0.0
    mechanism: str | None = None
    evidence_refs: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.coupling_id or not self.source_domain or not self.target_domain:
            raise ValueError("domain coupling identity is incomplete")
        if not isfinite(self.strength) or not isfinite(self.lag_days) or self.lag_days < 0:
            raise ValueError("coupling strength and lag must be finite; lag non-negative")
        if self.relation in {EpistemicRelation.CAUSAL, EpistemicRelation.MECHANISTIC} and not self.mechanism:
            raise ValueError("causal/mechanistic domain coupling requires a mechanism")


@dataclass(frozen=True, slots=True)
class Regime:
    regime_id: str
    label: str
    lower_bound: float | None = None
    upper_bound: float | None = None
    minimum_dwell: int = 1

    def __post_init__(self) -> None:
        if not self.regime_id or not self.label or self.minimum_dwell < 1:
            raise ValueError("regime identity and positive dwell are required")
        if self.lower_bound is not None and self.upper_bound is not None and self.lower_bound > self.upper_bound:
            raise ValueError("regime bounds are reversed")


@dataclass(frozen=True, slots=True)
class RegimeAssessment:
    regime_id: str
    changed: bool
    transition_allowed: bool
    confidence: float
    reason: str


@dataclass(frozen=True, slots=True)
class ForecastObject:
    forecast_id: str
    target: str
    issued_at: datetime
    horizon_end: datetime
    information_set: tuple[str, ...]
    model_id: str
    model_version: str
    parameters_ref: str
    probability: float | None = None
    interval: tuple[float, float] | None = None
    calibration_ref: str | None = None
    assumptions: tuple[str, ...] = ()
    outcome_definition: str = ""

    def __post_init__(self) -> None:
        if not self.forecast_id or not self.target or not self.model_id or not self.model_version or not self.outcome_definition:
            raise ValueError("forecast identity and outcome definition are required")
        for timestamp in (self.issued_at, self.horizon_end):
            if timestamp.tzinfo is None or timestamp.utcoffset() is None:
                raise ValueError("forecast timestamps must be timezone-aware")
        if self.horizon_end <= self.issued_at:
            raise ValueError("forecast horizon must follow issue time")
        if self.probability is not None and (not isfinite(float(self.probability)) or not 0 <= self.probability <= 1):
            raise ValueError("forecast probability must be finite and in [0,1]")
        if self.interval is not None:
            if len(self.interval) != 2 or not all(isfinite(float(x)) for x in self.interval) or self.interval[0] > self.interval[1]:
                raise ValueError("forecast interval must be finite and ordered")


@dataclass(frozen=True, slots=True)
class PredictabilityAssessment:
    predictable: bool
    confidence: float
    reasons: tuple[str, ...]
    abstain_recommended: bool

    def __post_init__(self) -> None:
        if not isfinite(float(self.confidence)) or not 0 <= self.confidence <= 1:
            raise ValueError("predictability confidence must be finite and in [0,1]")


@dataclass(frozen=True, slots=True)
class ModelAlternative:
    model_id: str
    version: str
    prediction: float
    uncertainty: float
    validity: str
    assumptions: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.model_id or not self.version or not isfinite(self.prediction) or not isfinite(self.uncertainty) or not 0 <= self.uncertainty <= 1:
            raise ValueError("model identity, prediction and uncertainty are invalid")


@dataclass(frozen=True, slots=True)
class ModelDisagreement:
    predictions: tuple[ModelAlternative, ...]
    spread: float
    material: bool
    reason: str

    def __post_init__(self) -> None:
        if not isfinite(float(self.spread)) or self.spread < 0:
            raise ValueError("model disagreement spread must be finite and non-negative")


@dataclass(frozen=True, slots=True)
class Intervention:
    intervention_id: str
    action: str
    start: datetime
    end: datetime | None
    target_domain: str
    resource_cost: float
    reversible: bool
    mechanism: str | None = None

    def __post_init__(self) -> None:
        if not self.intervention_id or not self.action or not self.target_domain:
            raise ValueError("intervention identity is incomplete")
        if self.start.tzinfo is None or self.start.utcoffset() is None:
            raise ValueError("intervention start must be timezone-aware")
        if self.end is not None and (self.end.tzinfo is None or self.end.utcoffset() is None or self.end < self.start):
            raise ValueError("intervention end is invalid")
        if not isfinite(self.resource_cost) or self.resource_cost < 0:
            raise ValueError("resource cost must be finite and non-negative")


@dataclass(frozen=True, slots=True)
class OutcomeRecord:
    decision_id: str
    intervention_id: str
    observed_at: datetime
    outcome: float
    expected: float | None = None
    attribution_status: str = "not_identified"

    def __post_init__(self) -> None:
        if self.observed_at.tzinfo is None or self.observed_at.utcoffset() is None:
            raise ValueError("outcome time must be timezone-aware")
        if not isfinite(self.outcome) or (self.expected is not None and not isfinite(self.expected)):
            raise ValueError("outcome values must be finite")


@dataclass(frozen=True, slots=True)
class InformationContribution:
    feature: str
    mutual_information: float
    conditional_information: float
    redundancy: float
    synergy: float

    def __post_init__(self) -> None:
        if not self.feature or any(not isfinite(x) or x < 0 for x in (self.mutual_information, self.conditional_information, self.redundancy, self.synergy)):
            raise ValueError("information measures must be finite and non-negative")


@dataclass(frozen=True, slots=True)
class SystemAssessment:
    observable: bool
    identifiable: bool
    predictability: PredictabilityAssessment
    model_disagreement: ModelDisagreement | None
    missing_data_risk: float
    measurement_process_risk: float
    spatial_dependency: bool
    network_dependency: bool
    regime_changed: bool
    abstain: bool
    reasons: tuple[str, ...]

    def __post_init__(self) -> None:
        for name, value in (("missing_data_risk", self.missing_data_risk), ("measurement_process_risk", self.measurement_process_risk)):
            if not isfinite(float(value)) or not 0 <= value <= 1:
                raise ValueError(f"{name} must be finite and in [0,1]")


class StateEstimator:
    @staticmethod
    def combine(hypotheses: Sequence[StateHypothesis]) -> StateEstimate:
        valid = tuple(item for item in hypotheses if item.probability > 0)
        if not valid:
            raise ValueError("at least one positive-probability state hypothesis is required")
        total = sum(item.probability for item in valid)
        if not isfinite(total) or total <= 0:
            raise ValueError("state hypothesis probabilities must have a finite positive sum")
        weights = np.asarray([item.probability / total for item in valid], dtype=float)
        vectors = np.asarray([item.state_vector for item in valid], dtype=float)
        mean = weights @ vectors
        covariance = np.zeros((vectors.shape[1], vectors.shape[1]), dtype=float)
        for weight, item, vector in zip(weights, valid, vectors):
            within = np.asarray(item.covariance, dtype=float)
            delta = (vector - mean).reshape(-1, 1)
            covariance += weight * (within + delta @ delta.T)
        if not np.all(np.isfinite(mean)) or not np.all(np.isfinite(covariance)):
            raise ValueError("combined state estimate must remain finite")
        competing = len(valid) > 1 or any(item.kind is StateKind.COMPETING for item in valid)
        return StateEstimate(tuple(mean.tolist()), tuple(map(tuple, covariance.tolist())), valid, not competing, True, "competing state hypotheses" if competing else "single state hypothesis")


class ObservabilityAnalyzer:
    @staticmethod
    def linear(A: Sequence[Sequence[float]], C: Sequence[Sequence[float]], *, tolerance: float = 1e-10) -> ObservabilityAssessment:
        a = np.asarray(A, dtype=float)
        c = np.asarray(C, dtype=float)
        if a.ndim != 2 or a.shape[0] != a.shape[1] or c.ndim != 2 or c.shape[1] != a.shape[0]:
            raise ValueError("A must be square and C must have compatible state dimension")
        if not np.all(np.isfinite(a)) or not np.all(np.isfinite(c)) or not isfinite(float(tolerance)) or tolerance <= 0:
            raise ValueError("observability inputs must be finite with positive tolerance")
        n = a.shape[0]
        blocks = [c]
        power = np.eye(n)
        for _ in range(1, n):
            power = power @ a
            blocks.append(c @ power)
        rank = int(np.linalg.matrix_rank(np.vstack(blocks), tol=tolerance))
        return ObservabilityAssessment(rank == n, rank, n, True, "observable" if rank == n else "observations cannot distinguish all state dimensions")


class IdentifiabilityAnalyzer:
    @staticmethod
    def from_sensitivity(sensitivity: Sequence[Sequence[float]], *, tolerance: float = 1e-10) -> IdentifiabilityAssessment:
        matrix = np.asarray(sensitivity, dtype=float)
        if matrix.ndim != 2 or matrix.size == 0 or not np.all(np.isfinite(matrix)) or not isfinite(float(tolerance)) or tolerance <= 0:
            raise ValueError("sensitivity matrix must be finite and non-empty with positive tolerance")
        rank = int(np.linalg.matrix_rank(matrix, tol=tolerance))
        parameters = matrix.shape[1]
        condition = None
        if rank == parameters:
            singular = np.linalg.svd(matrix, compute_uv=False)
            if singular[-1] > tolerance:
                condition = float(singular[0] / singular[-1])
        return IdentifiabilityAssessment(rank == parameters, rank, parameters, True, condition, "locally identifiable" if rank == parameters else "competing parameter explanations are not distinguishable")


class MissingnessAnalyzer:
    @staticmethod
    def risk(mechanisms: Sequence[MissingnessMechanism]) -> float:
        if not mechanisms:
            return 1.0
        weights = {MissingnessMechanism.MCAR: 0.05, MissingnessMechanism.MAR: 0.35, MissingnessMechanism.MNAR: 0.85, MissingnessMechanism.UNKNOWN: 0.65}
        return max(weights[item] for item in mechanisms)


class SpatialAnalyzer:
    @staticmethod
    def normalized_lag(values: Mapping[str, float], relations: Sequence[SpatialRelation]) -> float | None:
        if not relations:
            return None
        x = {key: float(value) for key, value in values.items() if isfinite(float(value))}
        if not x:
            return None
        mean = float(np.mean(list(x.values())))
        numerator = denominator = 0.0
        for relation in relations:
            if relation.source_id in x and relation.target_id in x:
                numerator += relation.weight * (x[relation.source_id] - mean) * (x[relation.target_id] - mean)
                denominator += relation.weight
        variance = float(np.mean([(value - mean) ** 2 for value in x.values()]))
        result = numerator / denominator / variance if denominator and variance > 0 else 0.0
        return result if isfinite(result) else None


class NetworkAnalyzer:
    @staticmethod
    def cascade(nodes: Sequence[str], edges: Sequence[tuple[str, str, float]], initial_active: Sequence[str], *, threshold: float = 0.5) -> tuple[str, ...]:
        if not isfinite(float(threshold)) or not 0 <= threshold <= 1:
            raise ValueError("threshold must be finite and in [0,1]")
        graph = nx.DiGraph()
        graph.add_nodes_from(nodes)
        for source, target, weight in edges:
            if not isfinite(weight) or weight < 0:
                raise ValueError("network weights must be finite and non-negative")
            graph.add_edge(source, target, weight=weight)
        active = set(initial_active)
        changed = True
        while changed:
            changed = False
            for node in graph.nodes:
                if node in active:
                    continue
                incoming = list(graph.in_edges(node, data="weight"))
                total = sum(float(weight) for _, _, weight in incoming)
                pressure = sum(float(weight) for source, _, weight in incoming if source in active)
                if total and pressure / total >= threshold:
                    active.add(node)
                    changed = True
        return tuple(sorted(active))

    @staticmethod
    def topology(nodes: Sequence[str], edges: Sequence[tuple[str, str, float]]) -> Mapping[str, float]:
        graph = nx.DiGraph()
        graph.add_nodes_from(nodes)
        for source, target, weight in edges:
            if not isfinite(float(weight)) or weight < 0:
                raise ValueError("network topology weights must be finite and non-negative")
            graph.add_edge(source, target, weight=weight)
        if len(graph) == 0:
            return {"density": 0.0, "largest_component": 0.0, "betweenness_max": 0.0}
        largest = max((len(component) for component in nx.connected_components(graph.to_undirected())), default=0)
        centrality = nx.betweenness_centrality(graph, weight="weight", normalized=True)
        result = {"density": float(nx.density(graph)), "largest_component": largest / len(graph), "betweenness_max": max(centrality.values(), default=0.0)}
        if not all(isfinite(float(value)) for value in result.values()):
            raise ValueError("network topology metrics must remain finite")
        return result


class InformationAnalyzer:
    @staticmethod
    def entropy(values: Sequence[int]) -> float:
        if not values:
            return 0.0
        counts = np.unique(np.asarray(values), return_counts=True)[1].astype(float)
        probabilities = counts / counts.sum()
        result = float(-sum(p * log(p) for p in probabilities if p > 0))
        if not isfinite(result):
            raise ValueError("entropy must remain finite")
        return result

    @staticmethod
    def mutual_information(x: Sequence[int], y: Sequence[int]) -> float:
        if len(x) != len(y) or not x:
            raise ValueError("information variables must have equal non-zero length")
        n = len(x)
        joint: dict[tuple[int, int], int] = {}
        x_counts: dict[int, int] = {}
        y_counts: dict[int, int] = {}
        for left, right in zip(x, y):
            joint[(left, right)] = joint.get((left, right), 0) + 1
            x_counts[left] = x_counts.get(left, 0) + 1
            y_counts[right] = y_counts.get(right, 0) + 1
        result = 0.0
        for (left, right), count in joint.items():
            pxy = count / n
            result += pxy * log(pxy / ((x_counts[left] / n) * (y_counts[right] / n)))
        result = max(0.0, float(result))
        if not isfinite(result):
            raise ValueError("mutual information must remain finite")
        return result


class RegimeDetector:
    @staticmethod
    def detect(value: float, current: Regime, candidate: Regime, *, dwell: int) -> RegimeAssessment:
        if not isfinite(value):
            raise ValueError("regime value must be finite")
        lower = candidate.lower_bound if candidate.lower_bound is not None else -np.inf
        upper = candidate.upper_bound if candidate.upper_bound is not None else np.inf
        inside = lower <= value <= upper
        allowed = inside and dwell >= candidate.minimum_dwell
        changed = candidate.regime_id != current.regime_id and allowed
        return RegimeAssessment(candidate.regime_id if changed else current.regime_id, changed, allowed, 1.0 if inside else 0.0, "candidate regime satisfies bounds and dwell" if changed else "transition not supported by current evidence")


class PredictabilityAnalyzer:
    @staticmethod
    def assess(errors: Sequence[float], *, model_spread: float = 0.0, mechanism_changed: bool = False, calibration_degraded: bool = False) -> PredictabilityAssessment:
        if not isfinite(float(model_spread)) or model_spread < 0:
            raise ValueError("model spread must be finite and non-negative")
        finite = [abs(float(error)) for error in errors if isfinite(float(error))]
        if not finite:
            return PredictabilityAssessment(False, 0.0, ("no evaluable forecast errors",), True)
        reasons: list[str] = []
        if mechanism_changed:
            reasons.append("mechanism change reduces forecastability")
        if calibration_degraded:
            reasons.append("calibration degradation reduces forecastability")
        if model_spread > 0:
            reasons.append("competing models disagree")
        confidence = 1.0 / (1.0 + float(np.mean(finite)) + model_spread)
        if not isfinite(confidence):
            raise ValueError("forecast confidence must remain finite")
        abstain = mechanism_changed or calibration_degraded or confidence < 0.35
        reasons.append("forecast confidence is below the operational abstention standard" if abstain else "no declared predictability limit was breached")
        return PredictabilityAssessment(not abstain, confidence, tuple(reasons), abstain)


class ModelDisagreementAnalyzer:
    @staticmethod
    def compare(models: Sequence[ModelAlternative], *, material_threshold: float = 0.2) -> ModelDisagreement | None:
        if not models:
            return None
        if not isfinite(float(material_threshold)) or material_threshold < 0:
            raise ValueError("material threshold must be finite and non-negative")
        predictions = [item.prediction for item in models]
        spread = float(max(predictions) - min(predictions))
        if not isfinite(spread):
            raise ValueError("model disagreement spread must remain finite")
        material = spread >= material_threshold
        return ModelDisagreement(tuple(models), spread, material, "material model disagreement" if material else "model disagreement below declared tolerance")


class SystemIntelligence:
    @staticmethod
    def assess(*, observability: ObservabilityAssessment, identifiability: IdentifiabilityAssessment, predictability: PredictabilityAssessment, missing_data_risk: float, measurement_process_risk: float, spatial_relations: Sequence[SpatialRelation] = (), network_edges: Sequence[tuple[str, str, float]] = (), regime_changed: bool = False, model_disagreement: ModelDisagreement | None = None) -> SystemAssessment:
        for name, value in (("missing_data_risk", missing_data_risk), ("measurement_process_risk", measurement_process_risk)):
            if not isfinite(float(value)) or not 0 <= value <= 1:
                raise ValueError(f"{name} must be finite and in [0,1]")
        reasons: list[str] = []
        if not observability.observable:
            reasons.append("insufficient observability")
        if not identifiability.identifiable:
            reasons.append("competing explanations are not identifiable")
        if predictability.abstain_recommended:
            reasons.extend(predictability.reasons)
        if measurement_process_risk >= 0.65:
            reasons.append("measurement/data-generating process may distort observed change")
        if missing_data_risk >= 0.65:
            reasons.append("missingness mechanism may bias inference")
        if model_disagreement and model_disagreement.material:
            reasons.append("material model disagreement")
        if regime_changed:
            reasons.append("regime transition detected; model validity may not transport")
        return SystemAssessment(observability.observable, identifiability.identifiable, predictability, model_disagreement, missing_data_risk, measurement_process_risk, bool(spatial_relations), bool(network_edges), regime_changed, bool(reasons), tuple(reasons))


__all__ = [
    "DomainCoupling", "EpistemicRelation", "ForecastObject", "IdentifiabilityAnalyzer", "IdentifiabilityAssessment",
    "InformationAnalyzer", "InformationContribution", "Intervention", "Measurement", "MissingnessAnalyzer",
    "MissingnessMechanism", "MobilityFlow", "ModelAlternative", "ModelDisagreement", "ModelDisagreementAnalyzer",
    "NetworkAnalyzer", "ObservationProcess", "ObservabilityAnalyzer", "ObservabilityAssessment", "OutcomeRecord",
    "PredictabilityAnalyzer", "PredictabilityAssessment", "Regime", "RegimeAssessment", "RegimeDetector", "Scale",
    "ScaleMapping", "SpatialAnalyzer", "SpatialRelation", "SpatialUnit", "StateEstimate", "StateEstimator",
    "StateHypothesis", "StateKind", "SystemAssessment", "SystemIntelligence",
]
