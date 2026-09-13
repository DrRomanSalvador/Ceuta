"""
CeutIA - Capa Epistemológica (P0)

Separación estricta de responsabilidades respecto a Serpiente.

CeutIA se encarga de:
- Ingestar y registrar fuentes y documentos
- Evaluar fiabilidad e independencia de fuentes
- Resolver entidades, lugares, unidades y definiciones semánticas
- Extraer claims
- Vincular afirmaciones con evidencias
- Normalizar tiempos, ubicaciones y conceptos
- Detectar contradicciones
- Mantener linaje completo
- Gestionar estados epistemológicos
- Proporcionar contexto ante anomalías detectadas por Serpiente

Serpiente NO decide si una fuente es creíble.
CeutIA NO convierte automáticamente una afirmación en predicción, causalidad o riesgo.
"""

from .epistemology import EpistemicStatus, EpistemicStateMachine
from .temporal import TemporalContext, TemporalFilter
from .sources import SourceIndependenceGraph, SourceNode, DependenceType
from .contracts import Observation, PullContextRequest, ContextDossier

__version__ = "0.1.0-p0"
__all__ = [
    "EpistemicStatus",
    "EpistemicStateMachine",
    "TemporalContext",
    "TemporalFilter",
    "SourceIndependenceGraph",
    "SourceNode",
    "DependenceType",
    "Observation",
    "PullContextRequest",
    "ContextDossier",
]
