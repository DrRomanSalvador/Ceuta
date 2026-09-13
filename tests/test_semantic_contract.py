from app.core.semantic_contract import MissingDataPolicy, SemanticContract


def contract(**overrides: object) -> SemanticContract:
    values: dict[str, object] = {
        "name": "metric_a",
        "canonical_name": "metric_a",
        "formula": "sum(x) / n",
        "input_domain": "finite numeric vector",
        "output_domain": "float in [0, 1]",
        "units": "ratio",
        "normalization": "n",
        "missing_data_policy": MissingDataPolicy.PRESERVE,
        "nan_policy": "reject",
        "zero_policy": "reject denominator zero",
        "error_policy": "raise ValueError",
        "temporal_semantics": "same observation window",
        "spatial_semantics": "local",
        "epistemic_role": "descriptive metric",
        "dependencies": (),
    }
    values.update(overrides)
    return SemanticContract(**values)  # type: ignore[arg-type]


def test_identical_contracts_are_compatible() -> None:
    left = contract()
    right = contract()
    assert left.compatibility_reasons(right) == ()
    assert left.is_semantically_compatible_with(right)


def test_normalization_difference_is_semantically_incompatible() -> None:
    left = contract(normalization="n")
    right = contract(normalization="n_minus_1")
    assert "normalization" in left.compatibility_reasons(right)
    assert not left.is_semantically_compatible_with(right)


def test_nan_policy_difference_is_semantically_incompatible() -> None:
    left = contract(nan_policy="reject")
    right = contract(nan_policy="omit")
    assert "nan_policy" in left.compatibility_reasons(right)
    assert not left.is_semantically_compatible_with(right)


def test_missing_data_policy_must_be_explicit() -> None:
    left = contract(missing_data_policy=MissingDataPolicy.PRESERVE)
    right = contract(missing_data_policy=MissingDataPolicy.EXPLICIT_IMPUTATION)
    assert "missing_data_policy" in left.compatibility_reasons(right)
    assert not left.is_semantically_compatible_with(right)


def test_epistemic_role_cannot_change_silently() -> None:
    left = contract(epistemic_role="evidence_quality")
    right = contract(epistemic_role="event_probability")
    assert "epistemic_role" in left.compatibility_reasons(right)
    assert not left.is_semantically_compatible_with(right)
