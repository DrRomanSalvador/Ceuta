"""Learning memory for predictions, interventions and failed hypotheses."""
from dataclasses import dataclass
from ..errors import ContractViolation

@dataclass(frozen=True, slots=True)
class LearningRecord:
    learning_id: str
    source_id: str
    result: str
    model_id: str | None = None
    hypothesis_id: str | None = None
    update_required: bool = False
    def __post_init__(self):
        if not self.learning_id or not self.source_id or not self.result: raise ContractViolation("learning record fields required")

@dataclass(frozen=True, slots=True)
class ModelLifecycle:
    model_id: str
    status: str
    score: float | None = None
    challenger_id: str | None = None
    def __post_init__(self):
        if self.status not in {"CHAMPION","CHALLENGER","RETIRED","INVALID","SHADOW"}: raise ContractViolation("invalid model lifecycle status")

@dataclass(frozen=True, slots=True)
class LearningLedger:
    records: tuple[LearningRecord, ...]
    models: tuple[ModelLifecycle, ...]
