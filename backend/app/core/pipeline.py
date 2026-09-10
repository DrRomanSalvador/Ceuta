from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from .audit import AuditChain
from .epistemic import (
    EpistemicEngine,
    EvidenceItem,
    EpistemicEvaluation,
    RiskEvaluation,
    calculate_risk,
)
from .policy import (
    PolicyEngine,
    PolicyRequest,
    PolicyResult,
)
from .review import ReviewGate, review_gate


@dataclass(slots=True)
class SafetyPipeline:

    policy: PolicyEngine
    epistemic: EpistemicEngine
    audit: AuditChain

    @classmethod
    def create(cls) -> "SafetyPipeline":
        return cls(
            policy=PolicyEngine(),
            epistemic=EpistemicEngine(),
            audit=AuditChain(),
        )

    def authorize(
        self,
        request: PolicyRequest,
        *,
        actor_id: str = "system",
    ) -> PolicyResult:

        result = self.policy.evaluate(request)

        self.audit.append(
            event_id=str(uuid4()),
            actor_id=actor_id,
            action="POLICY_EVALUATION",
            resource_type="policy_request",
            resource_id=None,
            decision=result.decision.value,
            payload={
                "purpose": request.purpose.value,
                "actor_role": request.actor_role,
                "target_is_individual":
                    request.target_is_individual,
                "target_is_group":
                    request.target_is_group,
                "data_classes": sorted(
                    x.value
                    for x in request.data_classes
                ),
                "sensitive_attributes": sorted(
                    x.value
                    for x in request.sensitive_attributes
                ),
            },
        )

        return result

    def evaluate_evidence(
        self,
        *,
        evidence: list[EvidenceItem],
        has_direct_observation: bool = False,
        is_explicit_source_assertion: bool = False,
        calibrated_probability: float | None = None,
        actor_id: str = "system",
    ) -> EpistemicEvaluation:

        result = self.epistemic.evaluate(
            evidence=evidence,
            has_direct_observation=has_direct_observation,
            is_explicit_source_assertion=
                is_explicit_source_assertion,
            calibrated_probability=
                calibrated_probability,
        )

        self.audit.append(
            event_id=str(uuid4()),
            actor_id=actor_id,
            action="EPISTEMIC_EVALUATION",
            resource_type="epistemic_evaluation",
            resource_id=None,
            decision=result.state.value,
            payload={
                "evidence_ids": [
                    e.evidence_id
                    for e in evidence
                ],
                "evidence_confidence":
                    result.evidence_confidence,
                "contradiction_ratio":
                    result.contradiction_ratio,
                "probability":
                    result.probability,
                "probability_status":
                    result.probability_status.value,
            },
        )

        return result

    @staticmethod
    def risk(
        *,
        evidence_confidence: float,
        impact: float,
        event_probability: float | None,
        uncertainty: float,
    ) -> RiskEvaluation:

        return calculate_risk(
            evidence_confidence=evidence_confidence,
            impact=impact,
            event_probability=event_probability,
            uncertainty=uncertainty,
        )

    @staticmethod
    def review(
        alert_level: str,
        *,
        rights_impact: bool = False,
    ) -> ReviewGate:

        return review_gate(
            alert_level,
            rights_impact=rights_impact,
        )