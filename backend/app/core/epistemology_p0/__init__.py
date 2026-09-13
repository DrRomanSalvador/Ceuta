"""
CeutIA - Capa Epistemológica (P0)

Paquete aislado bajo backend/app/core/epistemology_p0/
No modifica epistemic.py, models.py ni metrics.py legacy.

Separación estricta respecto a Serpiente:
- CeutIA: procedencia, independencia, estados, evidencia, contexto
- Serpiente: anomalías, trayectorias, previsiones, riesgos
"""

from .epistemology.states import EpistemicStatus, EpistemicStateMachine
from .evidence.models import (
    Evidence,
    create_evidence,
    Uncertainty,
    UncertaintyType,
    Location,
)
from .temporal.multitemporal import TemporalContext, TemporalFilter
from .sources.independence import (
    SourceIndependenceGraph,
    SourceNode,
    DependenceType,
    DependenceEdge,
)
from .contracts.ceutia_serpiente import (
    Observation,
    PullContextRequest,
    ContextDossier,
    ContextExplanation,
)
from .registry import ClaimRegistry

__version__ = "0.1.0-p0"
__all__ = [
    "EpistemicStatus",
    "EpistemicStateMachine",
    "Evidence",
    "create_evidence",
    "Uncertainty",
    "UncertaintyType",
    "Location",
    "TemporalContext",
    "TemporalFilter",
    "SourceIndependenceGraph",
    "SourceNode",
    "DependenceType",
    "DependenceEdge",
    "Observation",
    "PullContextRequest",
    "ContextDossier",
    "ContextExplanation",
    "ClaimRegistry",
]
