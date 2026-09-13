"""Typed contracts enforcing the distinction between association and causation."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Sequence


class EpistemicLevel(str, Enum):
    OBSERVED = "observed"
    ASSOCIATIONAL = "associational"
    TEMPORALLY_COMPATIBLE = "temporally_compatible"
    CAUSALLY_PLAUSIBLE = "causally_plausible"
    CAUSALLY_IDENTIFIED = "causally_identified"
    INTERVENABLE = "intervenable"
    PROSPECTIVELY_VALIDATED = "prospectively_validated"


class CausalRelation(str, Enum):
    DIRECT = "direct"
    MEDIATED = "mediated"
    CONFOUNDED = "confounded"
    MODERATED = "moderated"
    FEEDBACK = "feedback"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class CausalEdge:
    cause: str
    effect: str
    relation: CausalRelation = CausalRelation.UNKNOWN
    lag: float | None = None
    mechanism: str | None = None
    confidence: float = 0.0
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.cause or not self.effect or self.cause == self.effect:
            raise ValueError("A causal edge requires distinct non-empty variables")
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Causal confidence must be in [0, 1]")
        if self.lag is not None and self.lag < 0:
            raise ValueError("Causal lag cannot be negative")


@dataclass(frozen=True)
class CausalHypothesis:
    hypothesis_id: str
    exposure: str
    outcome: str
    estimand: str
    assumed_confounders: tuple[str, ...] = ()
    mediators: tuple[str, ...] = ()
    moderators: tuple[str, ...] = ()
    negative_controls: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    epistemic_level: EpistemicLevel = EpistemicLevel.ASSOCIATIONAL

    def __post_init__(self) -> None:
        if not self.hypothesis_id or not self.exposure or not self.outcome:
            raise ValueError("Causal hypotheses require identifiers, exposure and outcome")
        if self.exposure == self.outcome:
            raise ValueError("Exposure and outcome must differ")


@dataclass(frozen=True)
class IdentificationAssessment:
    hypothesis_id: str
    identified: bool
    estimand: str
    adjustment_set: tuple[str, ...] = ()
    blockers: tuple[str, ...] = ()
    assumptions: tuple[str, ...] = ()
    falsification_tests: tuple[str, ...] = ()


@dataclass(frozen=True)
class CausalEvidence:
    evidence_id: str
    hypothesis_id: str
    level: EpistemicLevel
    strength: float
    source_ids: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    supports: bool = True

    def __post_init__(self) -> None:
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError("Evidence strength must be in [0, 1]")


@dataclass(frozen=True)
class CausalAssessment:
    hypothesis: CausalHypothesis
    identification: IdentificationAssessment
    evidence: tuple[CausalEvidence, ...] = ()
    competing_hypotheses: tuple[str, ...] = ()
    residual_uncertainty: tuple[str, ...] = ()
    interaction_terms: Mapping[str, str] = field(default_factory=dict)

    @property
    def causality_claim_allowed(self) -> bool:
        return self.identification.identified and any(
            e.supports and e.level in {
                EpistemicLevel.CAUSALLY_IDENTIFIED,
                EpistemicLevel.PROSPECTIVELY_VALIDATED,
            }
            for e in self.evidence
        )
