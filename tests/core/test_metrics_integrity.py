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