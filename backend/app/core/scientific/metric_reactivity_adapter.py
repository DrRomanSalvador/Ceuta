"""Governance adapter for endogenous-indicator risk.

Indicator corruption is treated as a first-class strategic manipulation signal,
while preserving the epistemic distinction between anomaly and proven gaming.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.core.scientific.governance_signals import GovernanceInput
from app.core.scientific.metric_reactivity import GamingDiagnostics


@dataclass(frozen=True, slots=True)
class MetricReactivityGovernanceAdapter:
    code_revision: str
    configuration_hash: str

    def to_input(
        self,
        diagnostics: GamingDiagnostics,
        *,
        evidence_ids: tuple[str, ...],
        provenance_refs: tuple[str, ...],
        evidence_quality: float,
        independent_evidence_ratio: float,
        contradiction_ratio: float,
        response_closure_complete: bool = True,
        mechanism_ref: str = "scientific:metric-reactivity-v1",
    ) -> GovernanceInput:
        if not evidence_ids or not provenance_refs:
            raise ValueError("metric-reactivity governance requires evidence and provenance")
        compromised = "indicator_validity_compromised" in diagnostics.flags
        uncertainty = min(1.0, diagnostics.corruption_score + (0.15 if diagnostics.requires_review else 0.0))
        return GovernanceInput(
            evidence_ids=evidence_ids,
            provenance_refs=provenance_refs,
            evidence_quality=evidence_quality,
            independent_evidence_ratio=independent_evidence_ratio,
            contradiction_ratio=contradiction_ratio,
            mechanism_satisfied=not compromised,
            manipulation_flags=1 if diagnostics.requires_review else 0,
            provenance_valid=True,
            mechanism_integrity_valid=not compromised,
            model_conflict=False,
            uncertainty=uncertainty,
            response_closure_complete=response_closure_complete,
            code_revision=self.code_revision,
            configuration_hash=self.configuration_hash,
            mechanism_ref=mechanism_ref,
        )


__all__ = ["MetricReactivityGovernanceAdapter"]
