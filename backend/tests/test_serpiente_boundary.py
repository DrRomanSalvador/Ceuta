from datetime import datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from app.core.serpiente_boundary import SerpientePredictionEnvelope


def envelope(origin_time: datetime) -> SerpientePredictionEnvelope:
    return SerpientePredictionEnvelope(schema_version="1.0", prediction_id="p1", origin_time=origin_time, horizon="24h", target="risk", probability=0.7, lower=0.4, upper=0.9, uncertainty={"epistemic":0.2,"aleatoric":0.1}, model_disagreement=0.1, regime="STABLE", provenance=["official:source"], point_in_time_fingerprint="a"*64)


def test_future_serpiente_prediction_is_rejected():
    now = datetime(2026, 9, 14, tzinfo=timezone.utc)
    with pytest.raises(ValueError, match="future"):
        envelope(now + timedelta(minutes=1)).validate_at(now)


def test_serpiente_nan_is_rejected_at_contract_boundary():
    with pytest.raises(ValidationError):
        SerpientePredictionEnvelope(schema_version="1.0", prediction_id="p1", origin_time=datetime(2026,9,14,tzinfo=timezone.utc), horizon="24h", target="risk", probability=float("nan"), lower=0.0, upper=1.0, uncertainty={"epistemic":0.2}, model_disagreement=0.1, regime="STABLE", provenance=["official"], point_in_time_fingerprint="a"*64)
