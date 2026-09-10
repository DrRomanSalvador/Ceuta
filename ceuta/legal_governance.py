"""
ceuta/legal_governance.py

Módulo de reducción de riesgo legal y de gobernanza para CeutIA.
Diseñado para minimizar exposición bajo AI Act (UE), RGPD y
responsabilidad por señales/alertas en contextos de alta sensibilidad territorial.

Principios:
- Nunca presentar hipótesis como hechos
- Nunca emitir señales de alto impacto sin aprobación humana explícita
- Trazabilidad completa de fuentes y transformaciones
- Kill-switch y registro inmutable de decisiones
- Separación estricta de capas epistemológicas
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class EpistemicLayer(str, Enum):
    DATA = "data"
    OBSERVATION = "observation"
    EVIDENCE = "evidence"
    CLAIM = "claim"
    HYPOTHESIS = "hypothesis"
    MODEL = "model"
    TRAJECTORY = "trajectory"
    SCENARIO = "scenario"
    SIGNAL = "signal"
    RECOMMENDATION = "recommendation"
    DECISION = "decision"


class ImpactLevel(str, Enum):
    LOW = "low"               # Informativo, sin acción pública
    MEDIUM = "medium"         # Puede influir en percepción, requiere revisión
    HIGH = "high"             # Puede inducir decisiones institucionales o públicas
    CRITICAL = "critical"     # Afecta seguridad, salud colectiva o orden público


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    SUPERSEDED = "superseded"


@dataclass
class SourceProvenance:
    source_id: str
    source_type: str                  # "official", "scientific", "audit", etc.
    url: Optional[str]
    retrieved_at: str                 # ISO-8601
    methodology_note: Optional[str] = None
    confidence: float = 0.0           # 0.0 - 1.0
    hash_content: Optional[str] = None


@dataclass
class EpistemicObject:
    """
    Todo output del sistema debe ser un EpistemicObject.
    Impide que una hipótesis se presente como hecho.
    """
    id: str
    layer: EpistemicLayer
    content: Dict[str, Any]
    created_at: str
    sources: List[SourceProvenance] = field(default_factory=list)
    parent_ids: List[str] = field(default_factory=list)
    assumptions: List[str] = field(default_factory=list)
    uncertainty_note: str = ""
    confidence_interval: Optional[Dict[str, float]] = None
    human_review_required: bool = True
    impact_level: ImpactLevel = ImpactLevel.MEDIUM
    legal_flags: Set[str] = field(default_factory=set)

    def to_public_dict(self) -> Dict[str, Any]:
        """Versión segura para exposición pública. Nunca eleva la capa."""
        return {
            "id": self.id,
            "layer": self.layer.value,
            "content": self.content,
            "created_at": self.created_at,
            "uncertainty_note": self.uncertainty_note,
            "confidence_interval": self.confidence_interval,
            "assumptions": self.assumptions,
            "human_review_required": self.human_review_required,
            "impact_level": self.impact_level.value,
            "disclaimer": self._disclaimer(),
        }

    def _disclaimer(self) -> str:
        if self.layer in {EpistemicLayer.HYPOTHESIS, EpistemicLayer.SCENARIO, EpistemicLayer.SIGNAL}:
            return (
                "Esto es una hipótesis/escenario/señal generada por modelo. "
                "No constituye un hecho establecido ni una predicción cierta. "
                "Requiere evaluación humana antes de cualquier uso operativo."
            )
        if self.layer == EpistemicLayer.RECOMMENDATION:
            return (
                "Recomendación condicionada. No es una orden ni una decisión vinculante. "
                "La responsabilidad de cualquier acción recae exclusivamente en el decisor humano."
            )
        return "Información sujeta a las limitaciones de las fuentes y del modelo."


@dataclass
class HumanApproval:
    approval_id: str
    object_id: str
    approver_id: str
    status: ApprovalStatus
    timestamp: str
    rationale: str
    scope: str                        # Qué exactamente se aprueba
    expires_at: Optional[str] = None


@dataclass
class DecisionRecord:
    """Registro inmutable de decisiones de alto impacto."""
    decision_id: str
    object_id: str
    approver_id: str
    action_taken: str
    timestamp: str
    legal_basis: str
    risk_acknowledged: List[str]
    hash_chain_prev: Optional[str] = None
    hash_self: Optional[str] = None


class LegalGovernanceEngine:
    """
    Motor central de contención legal.
    Toda salida de alto impacto debe pasar por aquí.
    """

    def __init__(self):
        self._approvals: Dict[str, HumanApproval] = {}
        self._decisions: List[DecisionRecord] = []
        self._killed: bool = False
        self._allowed_layers_for_public = {
            EpistemicLayer.DATA,
            EpistemicLayer.OBSERVATION,
            EpistemicLayer.EVIDENCE,
            EpistemicLayer.CLAIM,
        }

    # ------------------------------------------------------------------
    # Kill switch
    # ------------------------------------------------------------------
    def emergency_shutdown(self, reason: str, actor: str) -> None:
        self._killed = True
        self._log_decision(
            object_id="SYSTEM",
            approver_id=actor,
            action_taken=f"EMERGENCY_SHUTDOWN: {reason}",
            legal_basis="Principio de precaución + control humano efectivo",
            risks=["Pérdida temporal de capacidad analítica"],
        )

    def is_operational(self) -> bool:
        return not self._killed

    # ------------------------------------------------------------------
    # Creación controlada de objetos epistemológicos
    # ------------------------------------------------------------------
    def create_object(
        self,
        layer: EpistemicLayer,
        content: Dict[str, Any],
        sources: List[SourceProvenance],
        assumptions: List[str],
        uncertainty_note: str,
        impact_level: ImpactLevel = ImpactLevel.MEDIUM,
        parent_ids: Optional[List[str]] = None,
        confidence_interval: Optional[Dict[str, float]] = None,
    ) -> EpistemicObject:
        if self._killed:
            raise RuntimeError("Sistema en emergency shutdown. No se pueden crear nuevos objetos.")

        obj = EpistemicObject(
            id=str(uuid.uuid4()),
            layer=layer,
            content=content,
            created_at=datetime.now(timezone.utc).isoformat(),
            sources=sources,
            parent_ids=parent_ids or [],
            assumptions=assumptions,
            uncertainty_note=uncertainty_note,
            confidence_interval=confidence_interval,
            human_review_required=impact_level in {ImpactLevel.HIGH, ImpactLevel.CRITICAL},
            impact_level=impact_level,
        )

        # Flags legales automáticos
        if layer in {EpistemicLayer.SIGNAL, EpistemicLayer.RECOMMENDATION, EpistemicLayer.DECISION}:
            obj.legal_flags.add("HIGH_IMPACT_OUTPUT")
        if not sources:
            obj.legal_flags.add("NO_PROVENANCE")
        if impact_level == ImpactLevel.CRITICAL:
            obj.legal_flags.add("REQUIRES_EXPLICIT_HUMAN_APPROVAL")

        return obj

    # ------------------------------------------------------------------
    # Aprobación humana obligatoria
    # ------------------------------------------------------------------
    def request_approval(
        self,
        obj: EpistemicObject,
        approver_id: str,
        scope: str,
        expires_hours: int = 24,
    ) -> HumanApproval:
        if obj.impact_level not in {ImpactLevel.HIGH, ImpactLevel.CRITICAL}:
            raise ValueError("Solo objetos HIGH o CRITICAL requieren este flujo formal.")

        approval = HumanApproval(
            approval_id=str(uuid.uuid4()),
            object_id=obj.id,
            approver_id=approver_id,
            status=ApprovalStatus.PENDING,
            timestamp=datetime.now(timezone.utc).isoformat(),
            rationale="",
            scope=scope,
            expires_at=None,  # se puede calcular después
        )
        self._approvals[approval.approval_id] = approval
        return approval

    def resolve_approval(
        self,
        approval_id: str,
        status: ApprovalStatus,
        rationale: str,
        actor: str,
    ) -> HumanApproval:
        if approval_id not in self._approvals:
            raise KeyError("Approval no encontrada")
        appr = self._approvals[approval_id]
        if appr.approver_id != actor:
            raise PermissionError("Solo el aprobador designado puede resolver")
        appr.status = status
        appr.rationale = rationale
        appr.timestamp = datetime.now(timezone.utc).isoformat()
        return appr

    def can_release(self, obj: EpistemicObject) -> bool:
        """Decide si un objeto puede salir del sistema hacia el exterior."""
        if self._killed:
            return False
        if obj.impact_level in {ImpactLevel.HIGH, ImpactLevel.CRITICAL}:
            # Debe existir al menos una aprobación válida
            for appr in self._approvals.values():
                if (
                    appr.object_id == obj.id
                    and appr.status == ApprovalStatus.APPROVED
                ):
                    return True
            return False
        return True

    # ------------------------------------------------------------------
    # Registro de decisiones (cadena de hash simple)
    # ------------------------------------------------------------------
    def _log_decision(
        self,
        object_id: str,
        approver_id: str,
        action_taken: str,
        legal_basis: str,
        risks: List[str],
    ) -> DecisionRecord:
        prev_hash = self._decisions[-1].hash_self if self._decisions else None
        rec = DecisionRecord(
            decision_id=str(uuid.uuid4()),
            object_id=object_id,
            approver_id=approver_id,
            action_taken=action_taken,
            timestamp=datetime.now(timezone.utc).isoformat(),
            legal_basis=legal_basis,
            risk_acknowledged=risks,
            hash_chain_prev=prev_hash,
        )
        payload = json.dumps(asdict(rec), sort_keys=True, default=str)
        rec.hash_self = hashlib.sha256(payload.encode()).hexdigest()
        self._decisions.append(rec)
        return rec

    def record_high_impact_action(
        self,
        obj: EpistemicObject,
        approver_id: str,
        action_taken: str,
        legal_basis: str,
        risks: List[str],
    ) -> DecisionRecord:
        if not self.can_release(obj):
            raise PermissionError(
                "No se puede ejecutar acción de alto impacto sin aprobación humana válida."
            )
        return self._log_decision(
            object_id=obj.id,
            approver_id=approver_id,
            action_taken=action_taken,
            legal_basis=legal_basis,
            risks=risks,
        )

    # ------------------------------------------------------------------
    # Utilidades de cumplimiento
    # ------------------------------------------------------------------
    def public_safe_view(self, obj: EpistemicObject) -> Dict[str, Any]:
        """Vista que se puede mostrar públicamente sin elevar la capa epistemológica."""
        if not self.can_release(obj):
            return {
                "status": "restricted",
                "reason": "Pendiente de aprobación humana o sistema en shutdown",
                "layer": obj.layer.value,
            }
        return obj.to_public_dict()

    def export_audit_log(self) -> List[Dict[str, Any]]:
        return [asdict(d) for d in self._decisions]


# ------------------------------------------------------------------
# Ejemplo de uso mínimo (para tests y documentación)
# ------------------------------------------------------------------
if __name__ == "__main__":
    engine = LegalGovernanceEngine()

    src = SourceProvenance(
        source_id="INE-2026-Q2",
        source_type="official",
        url="https://www.ine.es/...",
        retrieved_at=datetime.now(timezone.utc).isoformat(),
        confidence=0.9,
    )

    hypothesis = engine.create_object(
        layer=EpistemicLayer.HYPOTHESIS,
        content={"statement": "Posible aceleración de presión en frontera sur"},
        sources=[src],
        assumptions=["Los datos de flujo son representativos", "No hay cambio brusco de política"],
        uncertainty_note="Intervalo amplio. Sensible a sesgos de reporte.",
        impact_level=ImpactLevel.HIGH,
    )

    print("Objeto creado:", hypothesis.id)
    print("¿Puede liberarse públicamente?", engine.can_release(hypothesis))
    print("Vista pública segura:", engine.public_safe_view(hypothesis))