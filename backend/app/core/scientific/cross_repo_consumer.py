"""CeutIA-side consumer for the canonical SERPIENTE scientific contract."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .cross_repo_contract import ScientificPredictionMessage, validate_scientific_prediction_payload


@dataclass(frozen=True, slots=True)
class CrossRepoAcceptance:
    accepted: bool
    reason: str
    prediction: ScientificPredictionMessage | None


def consume_serpiente_prediction(payload: dict[str, Any]) -> CrossRepoAcceptance:
    """Reject scientifically unusable predictions without conflating prediction with causality."""
    try:
        prediction = validate_scientific_prediction_payload(payload)
    except (TypeError, ValueError, KeyError) as exc:
        return CrossRepoAcceptance(False, str(exc), None)
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
