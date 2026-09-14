from app.core.evidence.change_attribution import ChangeAttribution, ChangeAttributionEngine


def test_process_change_blocks_phenomenon_claim() -> None:
    result = ChangeAttributionEngine().assess(process_evidence=("coding change",))
    assert result.attribution is ChangeAttribution.MEASUREMENT_PROCESS_SUPPORTED
    assert result.abstain_from_phenomenon_claim is True


def test_competing_process_and_phenomenon_explanations_remain_open() -> None:
    result = ChangeAttributionEngine().assess(phenomenon_evidence=("external indicator",), process_evidence=("surveillance change",))
    assert result.attribution is ChangeAttribution.BOTH_PLAUSIBLE
    assert result.abstain_from_phenomenon_claim is True
