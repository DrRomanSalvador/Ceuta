from backend.app.core.decision.config_provenance import ConfigurationProvenance


def test_configuration_fingerprint_is_canonical():
    config = ConfigurationProvenance("runtime", "1", ("policy-source",), {"threshold_mode": "risk_class"})
    assert config.fingerprint() == ConfigurationProvenance("runtime", "1", ("policy-source",), {"threshold_mode": "risk_class"}).fingerprint()
