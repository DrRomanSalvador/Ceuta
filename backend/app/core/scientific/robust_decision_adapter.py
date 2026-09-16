"""Adapter from DMDU/BMA/causal state into the canonical governance mechanism."""
from __future__ import annotations

from .governance_signals import GovernanceInput
from .robust_decision import CausalIdentificationContract, EnsembleForecast, RobustnessProfile


class RobustDecisionGovernanceAdapter:
    """Preserve caller provenance while translating scientific state to governance."""

    def __init__(self, *, code_revision: str, configuration_hash: str, mechanism_ref: str = "dmdu") -> None:
        if not code_revision or not configuration_hash:
            raise ValueError("code revision and configuration hash are required")
        self.code_revision = code_revision
        self.configuration_hash = configuration_hash
        self.mechanism_ref = mechanism_ref

    def to_input(
        self,
        *,
        evidence_ids: tuple[str, ...],
        provenance_refs: tuple[str, ...],
        evidence_quality: float,
        independent_evidence_ratio: float,
        contradiction_ratio: float,
        robustness: RobustnessProfile,
        ensemble: EnsembleForecast | None = None,
        causal: CausalIdentificationContract | None = None,
    ) -> GovernanceInput:
        if not evidence_ids or not provenance_refs:
            raise ValueError("evidence and provenance references are required")
        uncertainty = 1.0 - robustness.robustness_score
        model_conflict = False
        if ensemble is not None:
            model_conflict = ensemble.disagreement >= 0.2
            uncertainty = max(uncertainty, min(1.0, ensemble.disagreement))
        causal_identified = True if causal is None else causal.identifiable
        return GovernanceInput(
            evidence_ids=evidence_ids,
            provenance_refs=provenance_refs,
            evidence_quality=evidence_quality,
            independent_evidence_ratio=independent_evidence_ratio,
            contradiction_ratio=contradiction_ratio,
            credibility=robustness.satisficing_rate,
            mechanism_satisfied=causal_identified and robustness.satisficing_rate > 0,
            manipulation_flags=0,
            collusion_flags=0,
            provenance_valid=True,
            mechanism_integrity_valid=True,
            model_conflict=model_conflict,
            uncertainty=uncertainty,
            response_closure_complete=True,
            code_revision=self.code_revision,
            configuration_hash=self.configuration_hash,
            mechanism_ref=self.mechanism_ref,
        )


__all__ = ["RobustDecisionGovernanceAdapter"]
