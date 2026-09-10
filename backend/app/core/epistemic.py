from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from math import isfinite
from typing import Iterable


class EpistemicState(str, Enum):
    FACT_DOCUMENTED = "FACT_DOCUMENTED"
    SOURCE_ASSERTION = "SOURCE_ASSERTION"
    EVIDENCE_SUPPORTED = "EVIDENCE_SUPPORTED"
    EVIDENCE_CONTRADICTED = "EVIDENCE_CONTRADICTED"
    INFERENCE = "INFERENCE"
    HYPOTHESIS = "HYPOTHESIS"
    ALTERNATIVE_HYPOTHESIS = "ALTERNATIVE_HYPOTHESIS"
    UNCERTAIN = "UNCERTAIN"
    DISPROVEN = "DISPROVEN"
    RETRACTED = "RETRACTED"


class ProbabilityStatus(str, Enum):
    NOT_CALIBRATED = "NOT_CALIBRATED"
    CALIBRATED = "CALIBRATED"
    NOT_APPLICABLE = "NOT_APPLICABLE"


@dataclass(frozen=True, slots=True)
class EvidenceItem:
    evidence_id: str
    source_id: str
    independence_group: str | None
    supports: bool
    strength: float
    reliability: float
    directness: float
    relevance: float
    contradictory: bool = False

    def __post_init__(self) -> None:
        for name in (
            "strength",
            "reliability",
            "directness",
            "relevance",
        ):
            value = getattr(self, name)

            if not isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError(
                    f"{name} must be finite and between 0 and 1"
                )


@dataclass(frozen=True, slots=True)
class EpistemicEvaluation:
    state: EpistemicState
    evidence_confidence: float
    contradiction_ratio: float
    independent_support_groups: int
    independent_opposition_groups: int
    probability: float | None
    probability_status: ProbabilityStatus
    uncertainty: float
    explanation: str


class EpistemicEngine:
    """
    Deterministic epistemic layer.

    LLM output is never trusted as an epistemic score.
    """

    def evaluate(
        self,
        *,
        evidence: Iterable[EvidenceItem],
        has_direct_observation: bool = False,
        is_explicit_source_assertion: bool = False,
        calibrated_probability: float | None = None,
    ) -> EpistemicEvaluation:

        items = tuple(evidence)

        if not items:
            return EpistemicEvaluation(
                EpistemicState.UNCERTAIN,
                0.0,
                1.0,
                0,
                0,
                None,
                ProbabilityStatus.NOT_CALIBRATED,
                1.0,
                "No evidence available.",
            )

        support = [
            e for e in items
            if e.supports and not e.contradictory
        ]

        opposition = [
            e for e in items
            if (not e.supports) or e.contradictory
        ]

        support_groups = {
            e.independence_group
            or f"source:{e.source_id}"
            for e in support
        }

        opposition_groups = {
            e.independence_group
            or f"source:{e.source_id}"
            for e in opposition
        }

        support_score = self._aggregate_independent(support)
        opposition_score = self._aggregate_independent(opposition)

        total = support_score + opposition_score

        contradiction_ratio = (
            opposition_score / total
            if total
            else 1.0
        )

        evidence_confidence = max(
            0.0,
            min(
                1.0,
                support_score
                * (1.0 - 0.5 * contradiction_ratio),
            ),
        )

        uncertainty = max(
            0.0,
            min(1.0, 1.0 - evidence_confidence),
        )

        if calibrated_probability is not None:
            if (
                not isfinite(calibrated_probability)
                or not 0 <= calibrated_probability <= 1
            ):
                raise ValueError(
                    "calibrated_probability must be between 0 and 1"
                )

            probability = calibrated_probability
            probability_status = ProbabilityStatus.CALIBRATED

        else:
            probability = None
            probability_status = ProbabilityStatus.NOT_CALIBRATED

        if (
            opposition_score > support_score
            and opposition_score > 0.65
        ):
            state = EpistemicState.EVIDENCE_CONTRADICTED

        elif (
            has_direct_observation
            and support_score >= 0.75
        ):
            state = EpistemicState.FACT_DOCUMENTED

        elif (
            is_explicit_source_assertion
            and support_score < 0.75
        ):
            state = EpistemicState.SOURCE_ASSERTION

        elif (
            support_score >= 0.65
            and len(support_groups) >= 2
        ):
            state = EpistemicState.EVIDENCE_SUPPORTED

        else:
            state = EpistemicState.UNCERTAIN

        return EpistemicEvaluation(
            state=state,
            evidence_confidence=round(
                evidence_confidence,
                6,
            ),
            contradiction_ratio=round(
                contradiction_ratio,
                6,
            ),
            independent_support_groups=len(
                support_groups
            ),
            independent_opposition_groups=len(
                opposition_groups
            ),
            probability=probability,
            probability_status=probability_status,
            uncertainty=round(uncertainty, 6),
            explanation=(
                "Confidence describes evidence quality/support; "
                "it is not event probability. Probability is emitted "
                "only when supplied by a separately calibrated model."
            ),
        )

    @staticmethod
    def _aggregate_independent(
        items: Iterable[EvidenceItem],
    ) -> float:
        best_by_group: dict[str, float] = {}

        for item in items:
            group = (
                item.independence_group
                or f"source:{item.source_id}"
            )

            quality = (
                item.strength
                * item.reliability
                * item.directness
                * item.relevance
            )

            best_by_group[group] = max(
                best_by_group.get(group, 0.0),
                quality,
            )

        if not best_by_group:
            return 0.0

        remaining = 1.0

        for value in best_by_group.values():
            remaining *= (
                1.0
                - max(
                    0.0,
                    min(1.0, value),
                )
            )

        return 1.0 - remaining


@dataclass(frozen=True, slots=True)
class RiskEvaluation:
    evidence_confidence: float
    event_probability: float | None
    impact: float
    risk_score: float
    uncertainty: float
    probability_status: ProbabilityStatus


def calculate_risk(
    *,
    evidence_confidence: float,
    impact: float,
    event_probability: float | None,
    uncertainty: float,
) -> RiskEvaluation:

    for name, value in (
        ("evidence_confidence", evidence_confidence),
        ("impact", impact),
        ("uncertainty", uncertainty),
    ):
        if (
            not isfinite(value)
            or not 0 <= value <= 1
        ):
            raise ValueError(
                f"{name} must be between 0 and 1"
            )

    if (
        event_probability is not None
        and (
            not isfinite(event_probability)
            or not 0 <= event_probability <= 1
        )
    ):
        raise ValueError(
            "event_probability must be between 0 and 1"
        )

    if event_probability is None:
        risk_score = (
            evidence_confidence
            * impact
            * (1.0 - uncertainty)
        )

        status = ProbabilityStatus.NOT_CALIBRATED

    else:
        risk_score = (
            event_probability
            * impact
            * evidence_confidence
            * (1.0 - uncertainty)
        )

        status = ProbabilityStatus.CALIBRATED

    return RiskEvaluation(
        evidence_confidence=evidence_confidence,
        event_probability=event_probability,
        impact=impact,
        risk_score=round(
            max(
                0.0,
                min(1.0, risk_score),
            ),
            6,
        ),
        uncertainty=uncertainty,
        probability_status=status,
    )