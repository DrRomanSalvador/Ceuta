"""Canonical CeutIA<->SERPIENTE scientific contract.

CeutIA is the canonical owner of this contract. SERPIENTE emits the versioned
message and validates the canonical contract identity plus receiver-side
scientific semantics; it does not maintain a second schema definition.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from typing import Any

CONTRACT_ID = "ceutia-serpiente-scientific-prediction"
CONTRACT_VERSION = "1.1"
CONTRACT_FIELDS = (
    "producer_repository", "producer_component", "schema_version", "prediction_id",
    "origin_time", "available_at", "horizon", "target", "probability", "lower", "upper",
    "uncertainty", "model_disagreement", "model_id", "method_id", "method_version",
    "training_window", "reference_class", "ood_state", "causal_status", "calibration_status",
    "evidence_level", "source_independence", "provenance", "configuration_hash", "code_revision",
    "point_in_time_fingerprint", "integrity_hash",
)


def canonical_contract_hash() -> str:
    payload = {"contract_id": CONTRACT_ID, "version": CONTRACT_VERSION, "fields": CONTRACT_FIELDS}
    return sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


CANONICAL_CONTRACT_HASH = canonical_contract_hash()


@dataclass(frozen=True, slots=True)
class ScientificPredictionMessage:
    producer_repository: str
    producer_component: str
    schema_version: str
    prediction_id: str
    origin_time: datetime
    available_at: datetime
    horizon: str
    target: str
    probability: float
    lower: float
    upper: float
    uncertainty: dict[str, float]
    model_disagreement: float
    model_id: str
    method_id: str
    method_version: str
    training_window: str
    reference_class: str
    ood_state: str
    causal_status: str
    calibration_status: str
    evidence_level: str
    source_independence: str
    provenance: tuple[str, ...]
    configuration_hash: str
    code_revision: str
    point_in_time_fingerprint: str
    integrity_hash: str

    def __post_init__(self) -> None:
        for value, name in ((self.origin_time, "origin_time"), (self.available_at, "available_at")):
            if value.tzinfo is None or value.utcoffset() is None:
                raise ValueError(f"{name} must be timezone-aware")
        if self.available_at < self.origin_time:
            raise ValueError("available_at cannot precede origin_time")
        if not all(math.isfinite(value) for value in (self.probability, self.lower, self.upper, self.model_disagreement)):
            raise ValueError("prediction interval and disagreement values must be finite")
        if not 0 <= self.probability <= 1 or not 0 <= self.model_disagreement <= 1:
            raise ValueError("probability and disagreement must be in [0,1]")
        if self.lower > self.upper or not self.provenance or not self.point_in_time_fingerprint:
            raise ValueError("forecast interval, provenance and point-in-time fingerprint are required")
        if self.schema_version != CONTRACT_VERSION:
            raise ValueError("unsupported scientific contract version")
        if not self.model_id or not self.method_id or not self.method_version or not self.training_window or not self.reference_class:
            raise ValueError("scientific method identity is incomplete")
        if self.ood_state not in {"IN_DOMAIN", "NEAR_BOUNDARY", "OUT_OF_DISTRIBUTION", "UNKNOWN"}:
            raise ValueError("invalid OOD state")
        if self.causal_status not in {"DESCRIPTIVE", "CONDITIONAL", "IDENTIFIED", "ABSTAIN"}:
            raise ValueError("invalid causal status")
        if self.calibration_status not in {"CALIBRATED", "UNCALIBRATED", "UNKNOWN"}:
            raise ValueError("invalid calibration status")
        if self.source_independence not in {"INDEPENDENT", "DEPENDENT", "PARTIALLY_DEPENDENT", "UNKNOWN"}:
            raise ValueError("invalid source independence")
        if not self.integrity_hash:
            raise ValueError("integrity hash is required")

    def payload_without_integrity(self) -> dict[str, Any]:
        return {
            "contract_id": CONTRACT_ID, "contract_hash": CANONICAL_CONTRACT_HASH,
            "producer_repository": self.producer_repository, "producer_component": self.producer_component,
            "schema_version": self.schema_version, "prediction_id": self.prediction_id,
            "origin_time": self.origin_time.astimezone(timezone.utc).isoformat(), "available_at": self.available_at.astimezone(timezone.utc).isoformat(),
            "horizon": self.horizon, "target": self.target, "probability": self.probability, "lower": self.lower, "upper": self.upper,
            "uncertainty": self.uncertainty, "model_disagreement": self.model_disagreement, "model_id": self.model_id,
            "method_id": self.method_id, "method_version": self.method_version, "training_window": self.training_window,
            "reference_class": self.reference_class, "ood_state": self.ood_state, "causal_status": self.causal_status,
            "calibration_status": self.calibration_status, "evidence_level": self.evidence_level,
            "source_independence": self.source_independence, "provenance": self.provenance,
            "configuration_hash": self.configuration_hash, "code_revision": self.code_revision,
            "point_in_time_fingerprint": self.point_in_time_fingerprint,
        }

    def verify_integrity(self) -> bool:
        expected = sha256(json.dumps(self.payload_without_integrity(), sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
        return expected == self.integrity_hash


def validate_scientific_prediction_payload(payload: dict[str, Any]) -> ScientificPredictionMessage:
    if payload.get("contract_id") != CONTRACT_ID or payload.get("contract_hash") != CANONICAL_CONTRACT_HASH:
        raise ValueError("scientific contract identity mismatch")
    missing = [field for field in CONTRACT_FIELDS if field not in payload]
    if missing:
        raise ValueError(f"scientific contract missing fields: {','.join(missing)}")
    message = ScientificPredictionMessage(
        producer_repository=payload["producer_repository"], producer_component=payload["producer_component"], schema_version=payload["schema_version"],
        prediction_id=payload["prediction_id"], origin_time=datetime.fromisoformat(payload["origin_time"]), available_at=datetime.fromisoformat(payload["available_at"]),
        horizon=payload["horizon"], target=payload["target"], probability=float(payload["probability"]), lower=float(payload["lower"]), upper=float(payload["upper"]),
        uncertainty={str(k): float(v) for k, v in payload["uncertainty"].items()}, model_disagreement=float(payload["model_disagreement"]), model_id=payload["model_id"],
        method_id=payload["method_id"], method_version=payload["method_version"], training_window=payload["training_window"], reference_class=payload["reference_class"],
        ood_state=payload["ood_state"], causal_status=payload["causal_status"], calibration_status=payload["calibration_status"], evidence_level=payload["evidence_level"],
        source_independence=payload["source_independence"], provenance=tuple(payload["provenance"]), configuration_hash=payload["configuration_hash"], code_revision=payload["code_revision"],
        point_in_time_fingerprint=payload["point_in_time_fingerprint"], integrity_hash=payload["integrity_hash"],
    )
    if not message.verify_integrity():
        raise ValueError("scientific prediction integrity mismatch")
    if any(not math.isfinite(v) for v in message.uncertainty.values()):
        raise ValueError("uncertainty contains non-finite values")
    return message


@dataclass(frozen=True, slots=True)
class DecisionFeedbackMessage:
    decision_id: str
    decision_time: datetime
    action_id: str
    intervention_applied: bool
    outcome_id: str
    outcome_time: datetime
    provenance: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.decision_time.tzinfo is None or self.outcome_time.tzinfo is None or self.outcome_time < self.decision_time:
            raise ValueError("decision/outcome times must be ordered and timezone-aware")
        if not all((self.decision_id, self.action_id, self.outcome_id, self.provenance)):
            raise ValueError("feedback identity and provenance are required")


__all__ = ["CANONICAL_CONTRACT_HASH", "CONTRACT_ID", "CONTRACT_VERSION", "DecisionFeedbackMessage", "ScientificPredictionMessage", "validate_scientific_prediction_payload"]
