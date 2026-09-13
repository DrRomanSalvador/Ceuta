"""Prospective model monitoring and champion/challenger lifecycle."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True, slots=True)
class PredictionOutcome:
    prediction_id:str; model_id:str; predicted:float; observed:float; as_of:Any; information_set_hash:str; loss:float

@dataclass(frozen=True, slots=True)
class ModelStatus:
    model_id:str; role:str; observations:int; cumulative_loss:float; valid:bool=True

class OnlineLearningEngine:
    def __init__(self): self._outcomes:list[PredictionOutcome]=[]
    def record(self,outcome:PredictionOutcome)->None:
        if not outcome.prediction_id or not outcome.model_id or not outcome.information_set_hash: raise ValueError("prediction outcome requires identifiers")
        if outcome.loss<0: raise ValueError("loss must be non-negative")
        if any(o.prediction_id==outcome.prediction_id for o in self._outcomes): raise ValueError("duplicate prediction outcome")
        self._outcomes.append(outcome)
    def status(self,model_ids:tuple[str,...])->tuple[ModelStatus,...]:
        if len(set(model_ids))!=len(model_ids): raise ValueError("model ids must be unique")
        means={m:sum(o.loss for o in self._outcomes if o.model_id==m)/sum(1 for o in self._outcomes if o.model_id==m) for m in model_ids if any(o.model_id==m for o in self._outcomes)}
        champion=min(means,key=means.get) if means else None
        return tuple(ModelStatus(m,"champion" if m==champion else "challenger",sum(o.model_id==m for o in self._outcomes),sum(o.loss for o in self._outcomes if o.model_id==m)) for m in model_ids)
