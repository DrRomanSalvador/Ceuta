from backend.app.core.decision.failure_safety import SafetyDisposition, fail_closed


def test_invalid_data_blocks():
    assert fail_closed(dependencies_resolved=True, evidence_sufficient=True, data_valid=False, control_checks_passed=True) is SafetyDisposition.BLOCK


def test_unresolved_dependency_abstains():
    assert fail_closed(dependencies_resolved=False, evidence_sufficient=True, data_valid=True, control_checks_passed=True) is SafetyDisposition.ABSTAIN


def test_sufficient_valid_input_can_authorize():
    assert fail_closed(dependencies_resolved=True, evidence_sufficient=True, data_valid=True, control_checks_passed=True) is SafetyDisposition.AUTHORIZE
