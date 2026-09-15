from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json

import pytest

from app.core.scientific.cross_repo_consumer import consume_serpiente_prediction
from app.core.scientific.cross_repo_contract import (
    CANONICAL_CONTRACT_HASH,
    CONTRACT_ID,
    CONTRACT_VERSION,
    ScientificPredictionMessage,
)


ORIGIN = datetime(2026, 9, 15, 5, 0, tzinfo=timezone.utc)


def _payload(**overrides):
    message = ScientificPredictionMessage(
        producer_repository="DrRomanSalvador/SERPIENTE",
        producer_component="LongitudinalForecaster",
        schema_version=CONTRACT_VERSION,
        prediction_id="prediction-1",
        origin_time=ORIGIN,
        available_at=ORIGIN,
        horizon="24h",
        target="risk",
        probability=0.7,
        lower=0.5,
        upper=0.9,
        uncertainty={"aleatoric": 0.1, "epistemic": 0.2},
        model_disagreement=0.1,
        model_id="longitudinal_ensemble",
        method_id="longitudinal_forecaster",
        method_version="1",
        training_window="2026-01-01/2026-09-01",
        reference_class="Ceuta",
        ood_state="IN_DOMAIN",
        causal_status="ABSTAIN",
        calibration_status="CALIBRATED",
        evidence_level="PREDICTIVE",
        source_independence="INDEPENDENT",
        provenance=("official:test",),
        configuration_hash="c" * 64,
        code_revision="r" * 40,
        point_in_time_fingerprint="p" * 64,
        integrity_hash="pending",
    )
    base = message.payload_without_integrity()
    integrity = sha256(json.dumps(base, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
    base["integrity_hash"] = integrity
    base.update(overrides)
    if "integrity_hash" not in overrides:
        # Recompute when an override changes signed content.
        unsigned = dict(base)
        unsigned.pop("integrity_hash", None)
        base["integrity_hash"] = sha256(json.dumps(unsigned, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
    base["contract_id"] = CONTRACT_ID
    base["contract_hash"] = CANONICAL_CONTRACT_HASH
    return base


def test_causal_abstention_does_not_invalidate_predictive_use():
    result = consume_serpiente_prediction(_payload())
    assert result.accepted is True
    assert result.prediction is not None
    assert result.prediction.causal_status == "ABSTAIN"


def test_future_available_at_is_rejected_by_temporal_consumer():
    payload = _payload(available_at=(ORIGIN + timedelta(hours=2)).isoformat())
    # The payload is intentionally re-signed after the temporal mutation.
    unsigned = dict(payload)
    unsigned.pop("integrity_hash")
    payload["integrity_hash"] = sha256(json.dumps(unsigned, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()
    result = consume_serpiente_prediction(payload, decision_time=ORIGIN + timedelta(hours=1))
    assert result.accepted is False
    assert result.reason == "temporally_ineligible:prediction_not_available"


def test_non_finite_interval_is_rejected_before_integrity_validation():
    with pytest.raises(ValueError, match="finite"):
        ScientificPredictionMessage(
            producer_repository="SERPIENTE",
            producer_component="test",
            schema_version=CONTRACT_VERSION,
            prediction_id="prediction-nan",
            origin_time=ORIGIN,
            available_at=ORIGIN,
            horizon="24h",
            target="risk",
            probability=0.5,
            lower=float("nan"),
            upper=0.9,
            uncertainty={"epistemic": 0.1},
            model_disagreement=0.1,
            model_id="m",
            method_id="method",
            method_version="1",
            training_window="window",
            reference_class="Ceuta",
            ood_state="IN_DOMAIN",
            causal_status="DESCRIPTIVE",
            calibration_status="CALIBRATED",
            evidence_level="PREDICTIVE",
            source_independence="INDEPENDENT",
            provenance=("source",),
            configuration_hash="c" * 64,
            code_revision="r" * 40,
            point_in_time_fingerprint="p" * 64,
            integrity_hash="x",
        )
