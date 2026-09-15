"""CeutIA-side consumer for the canonical SERPIENTE scientific contract."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from .cross_repo_contract import ScientificPredictionMessage, validate_scientific_prediction_payload


@dataclass(frozen=True, slots=True)
class CrossRepoAcceptance:
    accepted: bool
    reason: str
    prediction: ScientificPredictionMessage | None


def consume_serpiente_prediction(payload: dict[str, Any], *, decision_time: datetime | None = None) -> CrossRepoAcceptance:
    """Reject scientifically unusable or point-in-time-ineligible predictions."""
    try:
        prediction = validate_scientific_prediction_payload(payload)
    except (TypeError, ValueError, KeyError) as exc:
        return CrossRepoAcceptance(False, str(exc), None)
    if decision_time is not None:
        if decision_time.tzinfo is None or decision_time.utcoffset() is None:
            return CrossRepoAcceptance(False, "temporally_ineligible:decision_time_not_timezone_aware", prediction)
        reference_time = decision_time.astimezone(timezone.utc)
        if prediction.origin_time.astimezone(timezone.utc) > reference_time:
            return CrossRepoAcceptance(False, "temporally_ineligible:prediction_origin_in_future", prediction)
        if prediction.available_at.astimezone(timezone.utc) > reference_time:
            return CrossRepoAcceptance(False, "temporally_ineligible:prediction_not_available", prediction)
    if prediction.ood_state == "OUT_OF_DISTRIBUTION":
        return CrossRepoAcceptance(False, "scientifically_incompatible:out_of_distribution", prediction)
    if prediction.ood_state == "UNKNOWN":
        return CrossRepoAcceptance(False, "scientifically_incompatible:ood_unknown", prediction)
    if prediction.calibration_status != "CALIBRATED":
        return CrossRepoAcceptance(False, "scientifically_incompatible:uncalibrated", prediction)
    if prediction.source_independence == "UNKNOWN":
        return CrossRepoAcceptance(False, "scientifically_incompatible:source_dependence_unknown", prediction)
    return CrossRepoAcceptance(True, "scientifically_compatible", prediction)


__all__ = ["CrossRepoAcceptance", "consume_serpiente_prediction"]
