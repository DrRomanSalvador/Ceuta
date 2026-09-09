import importlib


def test_models_importable():
    module = importlib.import_module("app.core.models")
    assert module is not None


def test_metrics_importable():
    module = importlib.import_module("app.core.metrics")
    assert module is not None


def test_epistemic_validation_importable():
    module = importlib.import_module(
        "app.core.epistemic_validation"
    )
    assert module is not None


def test_evidence_policy_importable():
    module = importlib.import_module(
        "app.core.evidence_policy"
    )
    assert module is not None


def test_adversarial_validation_importable():
    module = importlib.import_module(
        "app.core.adversarial_validation"
    )
    assert module is not None
    def test_risk_is_not_probability_by_default():
    from app.core.models import RiskAssessment

    assessment = RiskAssessment(
        risk_id="TEST-001",
        hazard="synthetic",
        horizon="24h",
        state_pressure=0.8,
        trajectory_pressure=0.7,
        reserve_margin=0.2,
        sensitivity=0.6,
        coupling=0.7,
        propagation=0.6,
        threshold_proximity=0.8,
        recovery_capacity=0.3,
        epistemic_confidence=0.8,
        probability=None,
        calibration_status="UNCALIBRATED",
        operational_urgency="REVIEW",
    )

    assert assessment.probability is None
    assert assessment.calibrated is False
    def test_signal_cannot_become_fact_automatically():
    from app.core.evidence_policy import (
        SourceClass,
        assess_source_for_claim,
    )

    source = assess_source_for_claim(
        source_id="social-001",
        source_class=SourceClass.SOCIAL_MEDIA,
        provenance_verified=True,
        freshness_verified=True,
        independence_assessed=False,
    )

    assert source.admissible_as_signal is True
    assert source.admissible_for_factual_claim is False