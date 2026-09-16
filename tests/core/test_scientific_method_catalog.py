from app.core.scientific.method_compatibility import CompatibilityStatus, DataCompatibilityContext, ScientificMethodCompatibility, ScientificMethodContract
from app.core.scientific.scientific_method_registry import ScientificMethodRegistry, register_core_method_releases


def test_core_method_releases_are_retrievable_and_provenanced(tmp_path):
    registry = ScientificMethodRegistry(str(tmp_path / "methods.sqlite"))
    register_core_method_releases(registry, code_revision="rev-1", configuration_hash="cfg-1")
    assert {item.method_id for item in registry.all()} >= {"csd", "rdm", "bma", "causal-identification", "metric-reactivity", "nonstationarity"}
    assert registry.get("csd", "1").source_ids
    assert registry.verify_integrity()


def test_schema_valid_is_not_scientific_compatibility(tmp_path):
    method = ScientificMethodContract("csd", "1", ("dakos-2012-csd-robustness",), "time-series:v1", ("x",), (("x", "mm"),), "daily", 30, "<=20%", ("stationary_noise",), "same_location", "independent_sources_required", (), "complex_systems", ("false_positive",), "csd-output:v1", "uncertainty:v1", ("prospective_transition_validation",), "rev", "cfg")
    data = DataCompatibilityContext("time-series:v1", ("x",), (("x", "m"),), "daily", 40, 0.0, "in_domain", "same_location", "independent", True, True)
    result = ScientificMethodCompatibility().evaluate(method, data)
    assert result.schema_valid
    assert result.status is CompatibilityStatus.ASSUMPTION_VIOLATION
    assert not result.scientifically_applicable
