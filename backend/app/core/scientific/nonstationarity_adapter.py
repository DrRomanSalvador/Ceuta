"""Governance adapter for non-stationarity and support-boundary findings."""
from __future__ import annotations

from .governance_signals import GovernanceInput
from .nonstationarity import NonStationarityAssessment


class NonStationarityGovernanceAdapter:
    """Turns regime/support findings into existing fail-closed governance inputs."""

    def __init__(self, *, code_revision: str, configuration_hash: str) -> None:
        if not code_revision or not configuration_hash:
            raise ValueError("code_revision and configuration_hash are required")
        self.code_revision = code_revision
        self.configuration_hash = configuration_hash

    def to_input(
        self,
        assessment: NonStationarityAssessment,
        *,
        evidence_ids: tuple[str, ...],
        provenance_refs: tuple[str, ...],
        evidence_quality: float = 1.0,
        independent_evidence_ratio: float = 1.0,
        contradiction_ratio: float = 0.0,
    ) -> GovernanceInput:
        if not evidence_ids or not provenance_refs:
            raise ValueError("evidence_ids and provenance_refs are required")
        return GovernanceInput(
            evidence_ids=evidence_ids,
            provenance_refs=provenance_refs,
            evidence_quality=evidence_quality,
            independent_evidence_ratio=independent_evidence_ratio,
            contradiction_ratio=contradiction_ratio,
            mechanism_satisfied=assessment.state != "abstain",
            model_conflict=assessment.regime_change,
            uncertainty=max(assessment.uncertainty, 0.95 if assessment.extrapolation else 0.0),
            code_revision=self.code_revision,
            configuration_hash=self.configuration_hash,
            mechanism_ref="nonstationarity-v1",
        )
