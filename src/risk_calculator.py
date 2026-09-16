"""
Calculadora de Riesgo Existencial
Fórmulas matemáticas trazables con intervalos de confianza.

The legacy score remains backward compatible. Rate-like quantities are now
explicitly tied to a dynamic denominator, and binomial rate uncertainty is
reported separately from the heuristic risk-score uncertainty.
"""

from __future__ import annotations

import hashlib
import json
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Dict, List, Tuple

import numpy as np

from backend.app.core.p0_contracts import EvidenceContract
from backend.app.core.epistemology_p0.epistemology.states import EpistemicStatus

from .config import SystemConfig
from .scientific_capability import DynamicDenominator, wilson_interval

logger = logging.getLogger(__name__)


@dataclass
class RiskResult:
    """Resultado del cálculo de riesgo con incertidumbre."""

    risk_score: float
    confidence_interval: Tuple[float, float]
    confidence_level: float
    standard_error: float
    sample_size: int
    component_scores: Dict[str, float]
    alert_level: str
    calculation_timestamp: str
    data_sources: List[str]
    audit_hash: str
    event_rate: float | None = None
    denominator_id: str | None = None
    event_rate_interval: Tuple[float, float] | None = None
    event_rate_confidence_level: float | None = None

    def to_dict(self) -> Dict:
        return {
            "risk_score": self.risk_score,
            "confidence_interval": self.confidence_interval,
            "confidence_level": self.confidence_level,
            "standard_error": self.standard_error,
            "sample_size": self.sample_size,
            "component_scores": self.component_scores,
            "alert_level": self.alert_level,
            "calculation_timestamp": self.calculation_timestamp,
            "data_sources": self.data_sources,
            "audit_hash": self.audit_hash,
            "event_rate": self.event_rate,
            "denominator_id": self.denominator_id,
            "event_rate_interval": self.event_rate_interval,
            "event_rate_confidence_level": self.event_rate_confidence_level,
        }


class RiskCalculator:
    """Calculate risk only from epistemically admissible evidence."""

    ADMISSIBLE_STATUSES = {
        EpistemicStatus.OBSERVED_FACT,
        EpistemicStatus.CORROBORATED_FACT,
    }

    def __init__(self, config: SystemConfig = None):
        self.config = config or SystemConfig()
        self.thresholds = self.config.THRESHOLDS

    def calculate_risk(
        self,
        evidence_data: List[EvidenceContract],
        *,
        event_count: float | None = None,
        denominator: DynamicDenominator | None = None,
    ) -> RiskResult:
        """Calculate heuristic risk and, optionally, denominator-bound event rate.

        ``event_count`` and ``denominator`` must be supplied together. The
        event-rate interval is a Wilson interval and applies to a binomial
        event proportion, not to the heuristic weighted risk score.
        """
        if not evidence_data:
            raise ValueError("Risk calculation requires at least one evidence record")
        if (event_count is None) != (denominator is None):
            raise ValueError("event_count and denominator must be supplied together")
        if event_count is not None and denominator is not None:
            if event_count < 0 or event_count > denominator.population_at_risk:
                raise ValueError("event_count must satisfy 0 <= event_count <= population_at_risk")

        inadmissible = [
            evidence.evidence_id
            for evidence in evidence_data
            if evidence.epistemic_status not in self.ADMISSIBLE_STATUSES
        ]
        if inadmissible:
            raise ValueError(f"Evidence is not admissible for risk calculation: {inadmissible}")

        indicators = self._extract_indicators(evidence_data)
        normalized = self._normalize_indicators(indicators)
        raw_score = self._calculate_raw_score(normalized)
        risk_score = self._sigmoid(raw_score)
        ci_low, ci_high, se = self._calculate_confidence_interval(risk_score, len(evidence_data))
        alert_level = self._determine_alert_level(risk_score)

        component_scores = {
            "capability_growth": normalized.get("capability_growth", 0.5),
            "incident_count": normalized.get("incident_count", 0.5),
            "governance_gap": normalized.get("governance_gap", 0.5),
            "awareness_level": normalized.get("awareness_level", 0.5),
            "international_cooperation": normalized.get("international_cooperation", 0.5),
        }
        event_rate = denominator.rate(event_count) if denominator is not None and event_count is not None else None
        event_rate_interval = (
            self._event_rate_interval(event_count, denominator.population_at_risk)
            if denominator is not None and event_count is not None
            else None
        )

        audit_content = (
            f"{risk_score}{ci_low}{ci_high}{self._dict_to_str(component_scores)}"
            f"{event_rate}{event_rate_interval}{denominator.denominator_id if denominator else None}"
        )
        audit_hash = hashlib.sha256(audit_content.encode()).hexdigest()[:16]

        result = RiskResult(
            risk_score=round(risk_score, 4),
            confidence_interval=(round(ci_low, 4), round(ci_high, 4)),
            confidence_level=self.config.CONFIDENCE_LEVEL,
            standard_error=round(se, 4),
            sample_size=len(evidence_data),
            component_scores=component_scores,
            alert_level=alert_level,
            calculation_timestamp=datetime.now(UTC).isoformat(),
            data_sources=[evidence.source_id for evidence in evidence_data],
            audit_hash=audit_hash,
            event_rate=round(event_rate, 8) if event_rate is not None else None,
            denominator_id=denominator.denominator_id if denominator is not None else None,
            event_rate_interval=(
                (round(event_rate_interval[0], 8), round(event_rate_interval[1], 8))
                if event_rate_interval is not None
                else None
            ),
            event_rate_confidence_level=self.config.CONFIDENCE_LEVEL if event_rate is not None else None,
        )
        logger.info("Riesgo calculado: %.4f (nivel: %s)", result.risk_score, result.alert_level)
        return result

    def _event_rate_interval(self, event_count: float, population_at_risk: float) -> Tuple[float, float]:
        if not float(event_count).is_integer() or not float(population_at_risk).is_integer():
            raise ValueError("Wilson event-rate interval requires integer event and population counts")
        return wilson_interval(int(event_count), int(population_at_risk), z=self.config.Z_SCORE)

    def _extract_indicators(self, evidence_data: List[EvidenceContract]) -> Dict[str, float]:
        indicators = {
            "capability_growth": 0.5,
            "incident_count": 0.3,
            "governance_gap": 0.6,
            "awareness_level": 0.4,
            "international_cooperation": 0.3,
        }
        for evidence in evidence_data:
            source = evidence.source_id
            try:
                value = json.loads(evidence.claim)
            except (TypeError, json.JSONDecodeError):
                value = None
            if "UN" in source and isinstance(value, dict) and isinstance(value.get("incidents"), (int, float)):
                indicators["incident_count"] = min(value["incidents"] / 10.0, 1.0)
            if "Reuters" in source:
                indicators["international_cooperation"] = 0.5
        return indicators

    def _normalize_indicators(self, indicators: Dict[str, float]) -> Dict[str, float]:
        normalized = {}
        for key, value in indicators.items():
            min_val = 0.0
            max_val = 1.0
            normalized[key] = 0.5 if max_val == min_val else max(0.0, min(1.0, (value - min_val) / (max_val - min_val)))
        return normalized

    def _calculate_raw_score(self, normalized: Dict[str, float]) -> float:
        return sum(weight * normalized.get(indicator, 0.5) for indicator, weight in self.config.MODEL_WEIGHTS.items())

    def _sigmoid(self, x: float) -> float:
        return 1.0 / (1.0 + np.exp(-x))

    def _calculate_confidence_interval(self, risk_score: float, n: int) -> Tuple[float, float, float]:
        if n < 2:
            return (0.0, 1.0, 0.5)
        se = np.sqrt(risk_score * (1 - risk_score) / n)
        z = self.config.Z_SCORE
        ci_low = max(0.0, risk_score - z * se)
        ci_high = min(1.0, risk_score + z * se)
        return ci_low, ci_high, se

    def _determine_alert_level(self, risk_score: float) -> str:
        if risk_score < self.thresholds.green_max:
            return "GREEN"
        if risk_score < self.thresholds.yellow_max:
            return "YELLOW"
        if risk_score < self.thresholds.orange_max:
            return "ORANGE"
        return "RED"

    def _dict_to_str(self, values: Dict) -> str:
        return ",".join(f"{key}:{value}" for key, value in sorted(values.items()))
