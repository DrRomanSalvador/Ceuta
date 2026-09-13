from backend.app.core.decision.value_of_information import ValueOfInformation
from backend.app.core.decision.voi_contract import EvaluatedInformationRequest, InformationRequest


def test_information_request_requires_formal_voi_evaluation():
    request = InformationRequest("r1", "signal", "d1")
    voi = ValueOfInformation(10.0, 7.0, 3.0, 1.0, 2.0, "expected_value_of_sample_information")
    evaluated = EvaluatedInformationRequest(request, voi)
    assert evaluated.decision_justified
