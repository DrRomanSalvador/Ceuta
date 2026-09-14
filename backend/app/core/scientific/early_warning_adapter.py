"""Adapter from early-warning diagnostics to CeutIA scientific governance.

The adapter deliberately requires the caller to supply the underlying evidence
quality and provenance contract. Early-warning diagnostics modify release
eligibility; they do not manufacture evidence quality or causal identification.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.core.scientific.early_warning_governance import EarlyWarningAssessment
from app.core.scientific.governance_signals import GovernanceInput


@dataclass(frozen=True, slots=True)
class EarlyWarningGovernanceAdapter:
    code_revision: str
    configuration_hash: str

    def to_input(
        self,
        assessment: EarlyWarningAssessment,
        *,
        evidence_ids: tuple[str, ...],
        provenance_refs: tuple[str, ...],
        evidence_quality: float,
        independent_evidence_ratio: float,
        contradiction_ratio: float,
        mechanism_ref: str = "scientific:early-warning-v1",
    ) -> GovernanceInput:
        if not evidence_ids or not provenance_refs:
            raise ValueError("early-warning governance requires evidence and provenance")
        # Insufficient CSD data is treated as uncertainty, not as evidence that
        # a tipping point exists. Cry-wolf abstention is a hard mechanism gate.
        uncertainty = 0.95 if "critical_slowing_down_insufficient_data" in assessment.reasons else 0.0
        if "critical_slowing_down_confounders_present" in assessment.reasons:
            uncertainty = max(uncertainty, 0.8)
        mechanism_satisfied = assessment.cry_wolf_disposition != "abstain" and assessment.alert_allowed
        return GovernanceInput(
            evidence_ids=evidence_ids,
            provenance_refs=provenance_refs,
            evidence_quality=evidence_quality,
            independent_evidence_ratio=independent_evidence_ratio,
            contradiction_ratio=contradiction_ratio,
            mechanism_satisfied=mechanism_satisfied,
            provenance_valid=True,
            mechanism_integrity_valid=True,
            uncertainty=uncertainty,
            response_closure_complete=True,
            code_revision=self.code_revision,
            configuration_hash=self.configuration_hash,
            mechanism_ref=mechanism_ref,
        )


__all__ = ["EarlyWarningGovernanceAdapter"]
