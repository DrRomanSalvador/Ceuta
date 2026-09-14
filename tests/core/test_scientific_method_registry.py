from app.core.scientific.scientific_method_registry import ScientificMethodRegistry, ScientificMethodRelease


def test_method_release_persists_preprocessing_assumptions_and_sources(tmp_path):
    registry = ScientificMethodRegistry(str(tmp_path / "methods.sqlite"))
    release = ScientificMethodRelease(
        "csd", "2", "critical_slowing_down",
        ("detrend:linear", "window:0.5"),
        ("stationary_noise", "adequate_sampling"),
        "prospective-window-2026",
        "supporting resilience diagnostic only",
        ("dakos-2012-csd-robustness", "dakos-2026-ews-overview"),
        "test-revision", "config-hash",
    )
    registry.register(release)
    assert len(release.fingerprint) == 64
    assert registry.verify_integrity()
