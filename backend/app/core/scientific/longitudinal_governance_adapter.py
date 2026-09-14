"""Bridge realized longitudinal mechanism state into scientific governance.

This adapter is deliberately explicit: longitudinal credibility, manipulation
flags, collusion flags and provenance-chain integrity are derived from the
persisted mechanism before a governance signal is emitted. It also repairs the
in-memory credibility accumulator after restart from durable settlements,
preventing restart-dependent governance decisions.

The adapter does not treat heuristic findings as proof of misconduct. Findings
remain flags and are converted to fail-closed governance only according to the
existing governance policy.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite

from app.core.scientific.governance_signals import GovernanceInput, GovernanceSignal, ScientificGovernance
from app.core.scientific.longitudinal_mechanism import LongitudinalIncentiveMechanism


@dataclass(frozen=True, slots=True)
class LongitudinalGovernanceState:
    supplier_id: str
    observations: int
    credibility: float
    mean_brier: float
    manipulation_flags: int
    collusion_flags: int
    provenance_chain_valid: bool
    report_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    provenance_refs: tuple[str, ...]


class LongitudinalGovernanceAdapter:
    """Make longitudinal mechanism state consumable by ScientificGovernance."""

    def __init__(self, mechanism: LongitudinalIncentiveMechanism) -> None:
        self.mechanism = mechanism
        self.rebuild_quality_state()

    def rebuild_quality_state(self) -> None:
        """Reconstruct the quality accumulator from durable settlements.

        ``LongitudinalIncentiveMechanism`` persists settlements but historically
        reconstructed reports/settlements without rebuilding ``_quality``.
        Rebuilding here makes credibility invariant to process restart while
        preserving the mechanism's existing public API and storage schema.
        """
        quality: dict[str, list[float]] = {}
        for settlement in self.mechanism._settlements.values():
            report = self.mechanism._reports.get(settlement.report_id)
            if report is None:
                raise ValueError(f"settlement references missing report: {settlement.report_id}")
            if not isfinite(settlement.brier_score) or not 0.0 <= settlement.brier_score <= 1.0:
                raise ValueError(f"invalid persisted Brier score: {settlement.report_id}")
            quality.setdefault(report.supplier_id, []).append(settlement.brier_score)
        self.mechanism._quality = quality

    def state(self, supplier_id: str) -> LongitudinalGovernanceState:
        self.rebuild_quality_state()
        credibility = self.mechanism.credibility(supplier_id)
        reports = [r for r in self.mechanism._reports.values() if r.supplier_id == supplier_id]
        settlements = [s for s in self.mechanism._settlements.values() if s.report_id in {r.report_id for r in reports}]
        findings = self.mechanism.findings()
        manipulation = sum(1 for f in findings if f.__class__.__name__ == "ManipulationFinding" and f.report_id in {r.report_id for r in reports})
        collusion = sum(1 for f in findings if f.__class__.__name__ == "CollusionFinding" and supplier_id in f.supplier_ids)
        evidence_refs = tuple(dict.fromkeys(e for r in reports for e in r.evidence_ids))
        provenance_refs = tuple(dict.fromkeys(r.evidence_fingerprint for r in reports if r.evidence_fingerprint))
        return LongitudinalGovernanceState(
            supplier_id=supplier_id,
            observations=credibility.observations,
            credibility=credibility.credibility,
            mean_brier=credibility.mean_brier,
            manipulation_flags=manipulation,
            collusion_flags=collusion,
            provenance_chain_valid=self.mechanism.audit_chain_valid(),
            report_refs=tuple(r.report_id for r in reports),
            evidence_refs=evidence_refs or tuple(r.report_id for r in reports),
            provenance_refs=provenance_refs or tuple(r.report_id for r in reports),
        )

    def governance_input(
        self,
        supplier_id: str,
        *,
        code_revision: str,
        configuration_hash: str,
        uncertainty: float = 0.0,
        mechanism_satisfied: bool = True,
        response_closure_complete: bool = True,
        model_conflict: bool = False,
    ) -> GovernanceInput:
        state = self.state(supplier_id)
        if not state.report_refs:
            raise ValueError("supplier has no longitudinal reports")
        if not 0.0 <= uncertainty <= 1.0:
            raise ValueError("uncertainty must be in [0,1]")
        return GovernanceInput(
            evidence_ids=state.evidence_refs,
            provenance_refs=state.provenance_refs,
            evidence_quality=max(0.0, min(1.0, 1.0 - state.mean_brier)) if state.observations else 0.0,
            independent_evidence_ratio=1.0,
            contradiction_ratio=0.0,
            credibility=state.credibility,
            mechanism_satisfied=mechanism_satisfied,
            manipulation_flags=state.manipulation_flags,
            collusion_flags=state.collusion_flags,
            provenance_valid=state.provenance_chain_valid,
            mechanism_integrity_valid=state.provenance_chain_valid,
            model_conflict=model_conflict,
            uncertainty=uncertainty,
            response_closure_complete=response_closure_complete,
            code_revision=code_revision,
            configuration_hash=configuration_hash,
            mechanism_ref=f"longitudinal:{supplier_id}",
        )

    def evaluate(
        self,
        governance: ScientificGovernance,
        decision_id: str,
        supplier_id: str,
        *,
        code_revision: str,
        configuration_hash: str,
        uncertainty: float = 0.0,
        mechanism_satisfied: bool = True,
        response_closure_complete: bool = True,
        model_conflict: bool = False,
    ) -> GovernanceSignal:
        value = self.governance_input(
            supplier_id,
            code_revision=code_revision,
            configuration_hash=configuration_hash,
            uncertainty=uncertainty,
            mechanism_satisfied=mechanism_satisfied,
            response_closure_complete=response_closure_complete,
            model_conflict=model_conflict,
        )
        return governance.evaluate(decision_id, value)


__all__ = ["LongitudinalGovernanceAdapter", "LongitudinalGovernanceState"]
