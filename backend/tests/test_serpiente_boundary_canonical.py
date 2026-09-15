from datetime import datetime, timezone

from app.core.serpiente_boundary import SerpientePredictionEnvelope


def _envelope() -> SerpientePredictionEnvelope:
    return SerpientePredictionEnvelope(
        schema_version="1.0",
        prediction_id="prediction-1",
        origin_time=datetime(2026, 9, 15, 5, 0, tzinfo=timezone.utc),
        horizon="24h",
        target="risk",
        probability=0.7,
        lower=0.5,
        upper=0.9,
        uncertainty={"aleatoric": 0.1, "epistemic": 0.2},
        model_disagreement=0.1,
        regime="STABLE",
        provenance=["official:source-1"],
        point_in_time_fingerprint="b" * 64,
    )


def test_serpiente_envelope_has_deterministic_canonical_identity():
    first = _envelope()
    second = SerpientePredictionEnvelope.model_validate(first.model_dump(mode="json"))
    assert first.canonical_hash() == second.canonical_hash()
    assert len(first.canonical_hash()) == 64


def test_serpiente_envelope_canonical_identity_changes_with_prediction_content():
    first = _envelope()
    changed = first.model_copy(update={"probability": 0.71})
    assert first.canonical_hash() != changed.canonical_hash()
