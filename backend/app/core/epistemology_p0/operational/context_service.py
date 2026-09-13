"""
P1 — Servicio pull_context (Serpiente → CeutIA).

Cuando Serpiente detecta una anomalía, solicita contexto.
CeutIA responde con expediente de explicaciones e hipótesis rivales.
La alerta solo debería escalarse a revisión humana después de adjuntar este contexto.
"""

from __future__ import annotations
from typing import List, Optional, Callable
from datetime import datetime, timezone

from ..contracts.ceutia_serpiente import (
    PullContextRequest,
    ContextDossier,
    ContextExplanation,
)
from ..registry import ClaimRegistry
from ..evidence.models import Evidence


# Catálogo de tipos de explicación de la auditoría
EXPLANATION_TYPES = (
    "definition_change",
    "measurement_method_change",
    "ingestion_artifact",
    "publication_lag",
    "retrospective_revision",
    "coordinated_campaign",
    "excessive_source_dependence",
    "real_phenomenon_change",
    "other",
)


class ContextService:
    """Resuelve pull_context contra el ClaimRegistry."""

    def __init__(self, registry: ClaimRegistry):
        self.registry = registry

    def pull_context(self, request: PullContextRequest) -> ContextDossier:
        related: List[str] = []
        explanations: List[ContextExplanation] = []

        # Evidencias del registry asociadas a la variable (por claim statement / semantic)
        for claim_id, claim in self.registry.claims.items():
            for eid in claim.get("evidence_ids", []):
                ev = self.registry.evidences.get(eid)
                if ev is None:
                    continue
                related.append(eid)
                explanations.extend(self._hints_from_evidence(ev, request))

        # Hipótesis rivales: las del request + las inferidas
        rivals = list(request.competing_hypotheses)
        for et in ("definition_change", "ingestion_artifact", "real_phenomenon_change"):
            label = et.replace("_", " ")
            if label not in rivals and et not in rivals:
                rivals.append(et)

        if not explanations:
            explanations.append(
                ContextExplanation(
                    explanation_type="other",
                    description=(
                        f"No se encontró contexto documentado para '{request.variable}' "
                        f"en [{request.interval_start}, {request.interval_end}]. "
                        "Conservar hipótesis rivales y escalar a revisión humana si procede."
                    ),
                    confidence=0.3,
                    epistemic_status="HYPOTHESIS",
                )
            )

        return ContextDossier(
            request_id=request.request_id,
            variable=request.variable,
            explanations=explanations,
            rival_hypotheses=rivals,
            related_evidence_ids=list(dict.fromkeys(related)),
            notes=(
                "Alerta solo tras adjuntar este expediente. "
                "No resolver contradicciones artificialmente."
            ),
        )

    def _hints_from_evidence(
        self, ev: Evidence, request: PullContextRequest
    ) -> List[ContextExplanation]:
        out: List[ContextExplanation] = []
        if ev.unavailable_fields.get("event_time"):
            out.append(
                ContextExplanation(
                    explanation_type="ingestion_artifact",
                    description=f"Evidencia {ev.evidence_id} sin event_time: {ev.unavailable_fields['event_time']}",
                    supporting_evidence_ids=[ev.evidence_id],
                    confidence=0.6,
                )
            )
        if ev.contradictions:
            out.append(
                ContextExplanation(
                    explanation_type="other",
                    description=f"Evidencia {ev.evidence_id} tiene contradicciones abiertas",
                    supporting_evidence_ids=[ev.evidence_id],
                    confidence=0.7,
                    epistemic_status="CONTRADICTED",
                )
            )
        if ev.version > 1:
            out.append(
                ContextExplanation(
                    explanation_type="retrospective_revision",
                    description=f"Evidencia {ev.evidence_id} en versión {ev.version} (hubo revisión)",
                    supporting_evidence_ids=[ev.evidence_id],
                    confidence=0.65,
                )
            )
        if ev.corroboration:
            low_indep = [c for c in ev.corroboration if c.independence_score < 0.4]
            if low_indep:
                out.append(
                    ContextExplanation(
                        explanation_type="excessive_source_dependence",
                        description=(
                            f"Corroboraciones con baja independencia en {ev.evidence_id}"
                        ),
                        supporting_evidence_ids=[ev.evidence_id],
                        confidence=0.7,
                    )
                )
        return out
