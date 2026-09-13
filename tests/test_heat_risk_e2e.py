from datetime import datetime, timezone

import httpx
import pytest

from app.core.epistemic import EpistemicState
from app.integration.heat_risk import API_URL, RISK_ID, VARIABLES, OpenMeteoHeatAdapter, integrate_heat_batch


def payload(*, missing: str | None = None, invalid: str | None = None) -> dict:
    hourly = {"time": ["2026-09-13T10:00"]}
    units = {}
    for index, variable in enumerate(VARIABLES):
        hourly[variable] = [None if variable == missing else ("bad" if variable == invalid else float(index + 1))]
        units[variable] = "unit"
    return {"hourly": hourly, "hourly_units": units}


def test_real_adapter_parses_all_critical_variables() -> None:
    batch = OpenMeteoHeatAdapter.parse(payload(), latitude=35.8894, longitude=-5.3213)
    assert batch.risk_id == RISK_ID
    assert len(batch.observations) == 15
    assert batch.missing_variables == ()
    assert all(observed.observed_at.tzinfo is not None for observed in batch.observations)


def test_missing_variable_is_preserved_not_imputed() -> None:
    batch = OpenMeteoHeatAdapter.parse(payload(missing="uv_index"), latitude=35.8894, longitude=-5.3213)
    assert "uv_index" in batch.missing_variables
    result = integrate_heat_batch(batch)
    assert "uv_index" in result.provenance["missing_variables"]
    assert result.serpiente_payload["epistemic"]["probability"] is None


def test_schema_or_type_failure_is_rejected() -> None:
    with pytest.raises(ValueError, match="Invalid numeric value"):
        OpenMeteoHeatAdapter.parse(payload(invalid="temperature_2m"), latitude=35.8894, longitude=-5.3213)


def test_source_failure_propagates_without_fabricated_observation() -> None:
    transport = httpx.MockTransport(lambda request: httpx.Response(503, request=request, text="upstream unavailable"))
    with httpx.Client(transport=transport) as client:
        with pytest.raises(httpx.HTTPStatusError):
            OpenMeteoHeatAdapter(client).ingest(latitude=35.8894, longitude=-5.3213)


def test_duplicate_source_evidence_does_not_create_independence() -> None:
    result = integrate_heat_batch(OpenMeteoHeatAdapter.parse(payload(), latitude=35.8894, longitude=-5.3213))
    assert result.epistemic_state == EpistemicState.UNCERTAIN
    assert result.serpiente_payload["epistemic"]["probability"] is None
    assert result.serpiente_payload["provenance"]["source_id"] == "open-meteo:forecast"


def test_provenance_reconstructs_transformation() -> None:
    batch = OpenMeteoHeatAdapter.parse(payload(), latitude=35.8894, longitude=-5.3213)
    result = integrate_heat_batch(batch)
    assert result.provenance["source_url"] == API_URL
    assert result.provenance["payload_digest"] == batch.payload_digest
    assert result.provenance["transformation"]


def test_timestamp_is_aware_and_reproducible_from_source_payload() -> None:
    batch = OpenMeteoHeatAdapter.parse(payload(), latitude=35.8894, longitude=-5.3213)
    assert batch.observations[0].observed_at == datetime(2026, 9, 13, 10, tzinfo=timezone.utc)
