"""Operational distinction between information requests and formal VoI."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .value_of_information import ValueOfInformation


class InformationRequestStatus(StrEnum):
    PROPOSED = "proposed"
    EVALUATED = "evaluated"
    REJECTED = "rejected"


@dataclass(frozen=True, slots=True)
class InformationRequest:
    request_id: str
    signal: str
    decision_id: str
    status: InformationRequestStatus = InformationRequestStatus.PROPOSED

    def __post_init__(self) -> None:
        if not self.request_id or not self.signal or not self.decision_id:
            raise ValueError("request identity is incomplete")


@dataclass(frozen=True, slots=True)
class EvaluatedInformationRequest:
    request: InformationRequest
    voi: ValueOfInformation

    @property
    def decision_justified(self) -> bool:
        return self.voi.net_value > 0


__all__ = ["EvaluatedInformationRequest", "InformationRequest", "InformationRequestStatus"]
