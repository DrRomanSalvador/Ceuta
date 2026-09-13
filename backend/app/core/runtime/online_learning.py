"""Prospective model monitoring and champion/challenger lifecycle."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping

@dataclass(frozen=True, slots=True)
class PredictionOutcome:
    prediction_id: str
    model_id: str
    predicted: float
    observed: float
    as_of: object
    information_set_hash: str
    loss: float

@dataclass(frozen=True, slots=True)
class ModelStatus:
    model_id: str
    role: str
    observations: int
    cumulative_loss: float
    valid: bool=True

class OnlineLearningEngine:
    def __init__(self): self._outcomes:list[PredictionOutcome]=[]
    def record(self,outcome:PredictionOutcome)->None:
        if any(o.prediction_id==outcome.prediction_id for o in self._outcomes): raise ValueError("duplicate prediction outcome")
        self._outcomes.append(outcome)
    def status(self, model_ids: tuple[str,...]) -> tuple[ModelStatus,...]:
        out=[]
        for mid in model_ids:
            rows=[o for o in self._outcomes if o.model_id==mid]
            out.append(ModelStatus(mid,"champion" if rows and sum(o.loss for o in rows)/len(rows)==min((sum(x.loss for x in self._outcomes if x.model_id=m)/len([x for x in self._outcomes if x.model_id==m]) for m in model_ids if any(x.model_id==m for x in self._outcomes)),default=float("inf")) else "challenger",len(rows),sum(o.loss for o in rows)))
        return tuple(out)
