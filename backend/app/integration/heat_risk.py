"""Real-source ingestion and bounded epistemic integration for heat-health stress."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Mapping

import httpx

from app.core.epistemic import EpistemicEngine, EpistemicState, EvidenceItem

RISK_ID = "EXTREME_HEAT_HEALTH_STRESS"
SOURCE_ID = "open-meteo:forecast"
API_URL = "https://api.open-meteo.com/v1/forecast"
VARIABLES: tuple[str, ...] = (
    "temperature_2m", "apparent_temperature", "relative_humidity_2m",
    "dew_point_2m", "surface_pressure", "wind_speed_10m", "wind_gusts_10m",
    "precipitation", "rain", "cloud_cover", "shortwave_radiation",
    "direct_radiation", "uv_index", "visibility", "soil_temperature_0cm",
)


@dataclass(frozen=True, slots=True)
class Observation:
    variable: str
    value: float
    unit: str
    observed_at: datetime
    latitude: float
    longitude: float
    source_id: str
    source_url: str
    retrieval_id: str


@dataclass(frozen=True, slots=True)
class IngestionBatch:
    risk_id: str
    observations: tuple[Observation, ...]
    retrieved_at: datetime
    source_id: str
    source_url: str
    payload_digest: str
    missing_variables: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class IntegrationResult:
    risk_id: str
    epistemic_state: EpistemicState
    evidence_confidence: float
    uncertainty: float
    observations: tuple[Observation, ...]
    missing_variables: tuple[str, ...]
    provenance: Mapping[str, Any]
    serpiente_payload: Mapping[str, Any]


class OpenMeteoHeatAdapter:
    """Production HTTP adapter; callers can inject an HTTP client for tests."""

    def __init__(self, client: httpx.Client | None = None) -> None:
        self._client = client or httpx.Client(timeout=15.0)

    def ingest(self, *, latitude: float, longitude: float) -> IngestionBatch:
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ",".join(VARIABLES),
            "forecast_days": 1,
            "timezone": "UTC",
        }
        response = self._client.get(API_URL, params=params)
        response.raise_for_status()
        return self.parse(response.json(), latitude=latitude, longitude=longitude)

    @staticmethod
    def parse(
        payload: Mapping[str, Any], *, latitude: float, longitude: float
    ) -> IngestionBatch:
        hourly = payload.get("hourly")
        if not isinstance(hourly, Mapping):
            raise ValueError("Open-Meteo response lacks hourly observations")
        times = hourly.get("time")
        if not isinstance(times, list) or not times:
            raise ValueError("Open-Meteo response lacks hourly timestamps")
        units = payload.get("hourly_units", {})
        if not isinstance(units, Mapping):
            units = {}
        timestamp = datetime.fromisoformat(str(times[0]).replace("Z", "+00:00"))
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        retrieved_at = datetime.now(timezone.utc)
        raw = repr(sorted((str(k), str(v)) for k, v in payload.items())).encode()
        digest = sha256(raw).hexdigest()
        retrieval_id = f"{SOURCE_ID}:{digest[:16]}"
        observations: list[Observation] = []
        missing: list[str] = []
        for variable in VARIABLES:
            values = hourly.get(variable)
            if not isinstance(values, list) or not values or values[0] is None:
                missing.append(variable)
                continue
            try:
                value = float(values[0])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid numeric value for {variable}") from exc
            observations.append(
                Observation(
                    variable=variable,
                    value=value,
                    unit=str(units.get(variable, "unknown")),
                    observed_at=timestamp,
                    latitude=latitude,
                    longitude=longitude,
                    source_id=SOURCE_ID,
                    source_url=API_URL,
                    retrieval_id=retrieval_id,
                )
            )
        return IngestionBatch(
            risk_id=RISK_ID,
            observations=tuple(observations),
            retrieved_at=retrieved_at,
            source_id=SOURCE_ID,
            source_url=API_URL,
            payload_digest=digest,
            missing_variables=tuple(missing),
        )


def integrate_heat_batch(batch: IngestionBatch) -> IntegrationResult:
    """Expose observations to Serpiente without inventing probability or causality."""
    evidence = tuple(
        EvidenceItem(
            evidence_id=f"{obs.retrieval_id}:{obs.variable}",
            source_id=obs.source_id,
            independence_group=obs.source_id,
            supports=True,
            strength=1.0,
            reliability=0.5,
            directness=1.0,
            relevance=1.0,
        )
        for obs in batch.observations
    )
    evaluation = EpistemicEngine().evaluate(
        evidence=evidence,
        has_direct_observation=bool(batch.observations),
    )
    provenance = {
        "source_id": batch.source_id,
        "source_url": batch.source_url,
        "payload_digest": batch.payload_digest,
        "retrieved_at": batch.retrieved_at.isoformat(),
        "missing_variables": list(batch.missing_variables),
        "transformation": "open-meteo-hourly -> normalized-observations -> epistemic-evaluation",
    }
    payload = {
        "risk_id": batch.risk_id,
        "observations": [
            {"variable": o.variable, "value": o.value, "unit": o.unit,
             "observed_at": o.observed_at.isoformat(), "latitude": o.latitude,
             "longitude": o.longitude}
            for o in batch.observations
        ],
        "epistemic": {
            "state": evaluation.state.value,
            "evidence_confidence": evaluation.evidence_confidence,
            "uncertainty": evaluation.uncertainty,
            "probability": None,
            "probability_status": evaluation.probability_status.value,
        },
        "provenance": provenance,
    }
    return IntegrationResult(
        risk_id=batch.risk_id,
        epistemic_state=evaluation.state,
        evidence_confidence=evaluation.evidence_confidence,
        uncertainty=evaluation.uncertainty,
        observations=batch.observations,
        missing_variables=batch.missing_variables,
        provenance=provenance,
        serpiente_payload=payload,
    )
