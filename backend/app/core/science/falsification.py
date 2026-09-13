"""Reproducible scientific red-team and falsification primitives."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FalsificationTarget:
    hypothesis_id: str
    prediction_id: str
    expected_observation: str
    falsifying_observation: str
    deadline: str
    evidence_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class RedTeamChallenge:
    challenge_id: str
    hypothesis_id: str
    alternative_explanation: str
    required_discriminator: str
    status: str = "OPEN"


@dataclass(frozen=True, slots=True)
class FalsificationOutcome:
    prediction_id: str
    status: str
    observed: str | None
    error: str | None
    evidence_ids: tuple[str, ...]


class ScientificRedTeam:
    """Keeps hypotheses falsifiable and alternatives explicit."""

    def challenge(self, target: FalsificationTarget, *, observed: str | None, evidence_ids: tuple[str, ...] = ()) -> FalsificationOutcome:
        if observed is None:
            return FalsificationOutcome(target.prediction_id, "UNRESOLVED", None, "outcome_not_observed", evidence_ids)
        if observed == target.falsifying_observation:
            return FalsificationOutcome(target.prediction_id, "FALSIFIED", observed, "falsifying_observation_observed", evidence_ids)
        if observed == target.expected_observation:
            return FalsificationOutcome(target.prediction_id, "SUPPORTED", observed, None, evidence_ids)
        return FalsificationOutcome(target.prediction_id, "INCONCLUSIVE", observed, "observation_matches_neither_declared_prediction", evidence_ids)

    @staticmethod
    def alternatives(hypothesis_id: str, alternatives: tuple[str, ...], discriminator: str) -> tuple[RedTeamChallenge, ...]:
        if not hypothesis_id or not discriminator:
            raise ValueError("hypothesis_id and discriminator are required")
        return tuple(
            RedTeamChallenge(
                challenge_id=f"{hypothesis_id}:alternative:{index}",
                hypothesis_id=hypothesis_id,
                alternative_explanation=alternative,
                required_discriminator=discriminator,
            )
            for index, alternative in enumerate(alternatives, start=1)
            if alternative
        )
