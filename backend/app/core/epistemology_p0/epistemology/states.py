"""
CeutIA - Epistemic State Machine (P0)

Estados tipados y controlados. Transiciones válidas obligatorias.
Ningún estado se almacena como texto libre.
"""

from enum import Enum
from typing import Dict, Set, Optional, List
from dataclasses import dataclass, field
from datetime import datetime, timezone
import uuid


class EpistemicStatus(str, Enum):
    """Estados epistemológicos tipados y controlados."""
    OBSERVED_FACT = "OBSERVED_FACT"
    CORROBORATED_FACT = "CORROBORATED_FACT"
    ATTRIBUTED_CLAIM = "ATTRIBUTED_CLAIM"
    INFERENCE = "INFERENCE"
    HYPOTHESIS = "HYPOTHESIS"
    UNVERIFIED = "UNVERIFIED"
    CONTRADICTED = "CONTRADICTED"
    DISPROVEN = "DISPROVEN"
    UNKNOWN = "UNKNOWN"


# Transiciones válidas de la máquina de estados.
# Una afirmación de una única fuente SIEMPRE empieza como ATTRIBUTED_CLAIM.
# Solo puede pasar a CORROBORATED_FACT con evidencia independiente documentada.
VALID_TRANSITIONS: Dict[EpistemicStatus, Set[EpistemicStatus]] = {
    EpistemicStatus.ATTRIBUTED_CLAIM: {
        EpistemicStatus.CORROBORATED_FACT,
        EpistemicStatus.CONTRADICTED,
        EpistemicStatus.UNVERIFIED,
        EpistemicStatus.DISPROVEN,
        EpistemicStatus.INFERENCE,
        EpistemicStatus.HYPOTHESIS,
    },
    EpistemicStatus.UNVERIFIED: {
        EpistemicStatus.ATTRIBUTED_CLAIM,
        EpistemicStatus.CORROBORATED_FACT,
        EpistemicStatus.CONTRADICTED,
        EpistemicStatus.DISPROVEN,
        EpistemicStatus.HYPOTHESIS,
    },
    EpistemicStatus.CORROBORATED_FACT: {
        EpistemicStatus.CONTRADICTED,
        EpistemicStatus.DISPROVEN,
        EpistemicStatus.INFERENCE,
    },
    EpistemicStatus.CONTRADICTED: {
        EpistemicStatus.CORROBORATED_FACT,
        EpistemicStatus.DISPROVEN,
        EpistemicStatus.UNVERIFIED,
        EpistemicStatus.HYPOTHESIS,
    },
    EpistemicStatus.DISPROVEN: {
        EpistemicStatus.HYPOTHESIS,
    },
    EpistemicStatus.INFERENCE: {
        EpistemicStatus.HYPOTHESIS,
        EpistemicStatus.CORROBORATED_FACT,
        EpistemicStatus.CONTRADICTED,
        EpistemicStatus.DISPROVEN,
    },
    EpistemicStatus.HYPOTHESIS: {
        EpistemicStatus.INFERENCE,
        EpistemicStatus.ATTRIBUTED_CLAIM,
        EpistemicStatus.CORROBORATED_FACT,
        EpistemicStatus.CONTRADICTED,
        EpistemicStatus.DISPROVEN,
        EpistemicStatus.UNVERIFIED,
    },
    EpistemicStatus.OBSERVED_FACT: {
        EpistemicStatus.CORROBORATED_FACT,
        EpistemicStatus.CONTRADICTED,
        EpistemicStatus.DISPROVEN,
    },
    EpistemicStatus.UNKNOWN: {
        EpistemicStatus.ATTRIBUTED_CLAIM,
        EpistemicStatus.UNVERIFIED,
        EpistemicStatus.HYPOTHESIS,
    },
}


@dataclass(frozen=True)
class EpistemicTransition:
    """Registro inmutable de una transición de estado."""
    transition_id: str
    from_status: EpistemicStatus
    to_status: EpistemicStatus
    justification: str
    evidence_ids: tuple
    actor: str
    timestamp: datetime
    previous_version_id: Optional[str] = None

    def __post_init__(self):
        if self.to_status not in VALID_TRANSITIONS.get(self.from_status, set()):
            raise ValueError(
                f"Transición inválida: {self.from_status.value} → {self.to_status.value}. "
                f"Transiciones permitidas: {[s.value for s in VALID_TRANSITIONS.get(self.from_status, set())]}"
            )


class EpistemicStateMachine:
    """
    Máquina de estados epistemológicos.

    Reglas clave de la auditoría:
    - Una fuente que afirma X solo permite registrar ATTRIBUTED_CLAIM inicialmente.
    - No se convierte en CORROBORATED_FACT sin evidencia independiente documentada.
    - Las contradicciones no se resuelven artificialmente.
    - Una corrección NO sobrescribe el estado anterior: crea nueva versión.
    - No se declara desinformación solo por falsedad; se requiere evidencia de intención.
    """

    def __init__(self, initial_status: EpistemicStatus = EpistemicStatus.ATTRIBUTED_CLAIM):
        self.current_status = initial_status
        self.history: List[EpistemicTransition] = []
        self.version = 1
        self.entity_id = str(uuid.uuid4())

    def can_transition(self, to_status: EpistemicStatus) -> bool:
        return to_status in VALID_TRANSITIONS.get(self.current_status, set())

    def transition(
        self,
        to_status: EpistemicStatus,
        justification: str,
        evidence_ids: List[str],
        actor: str = "system",
        timestamp: Optional[datetime] = None,
    ) -> EpistemicTransition:
        if not self.can_transition(to_status):
            raise ValueError(
                f"Transición prohibida: {self.current_status.value} → {to_status.value}"
            )

        if not justification or not justification.strip():
            raise ValueError("Toda transición requiere justificación explícita")

        if to_status == EpistemicStatus.CORROBORATED_FACT and not evidence_ids:
            raise ValueError(
                "No se puede pasar a CORROBORATED_FACT sin evidence_ids de corroboración independiente"
            )

        ts = timestamp or datetime.now(timezone.utc)
        previous_version = self.entity_id

        transition = EpistemicTransition(
            transition_id=str(uuid.uuid4()),
            from_status=self.current_status,
            to_status=to_status,
            justification=justification,
            evidence_ids=tuple(evidence_ids),
            actor=actor,
            timestamp=ts,
            previous_version_id=previous_version,
        )

        self.history.append(transition)
        self.current_status = to_status
        self.version += 1
        self.entity_id = str(uuid.uuid4())

        return transition

    def get_lineage(self) -> List[dict]:
        """Devuelve el linaje completo de estados."""
        return [
            {
                "transition_id": t.transition_id,
                "from": t.from_status.value,
                "to": t.to_status.value,
                "justification": t.justification,
                "evidence_ids": list(t.evidence_ids),
                "actor": t.actor,
                "timestamp": t.timestamp.isoformat(),
                "previous_version_id": t.previous_version_id,
            }
            for t in self.history
        ]
