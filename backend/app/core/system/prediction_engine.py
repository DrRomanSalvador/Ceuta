"""Probabilistic prediction contract with explicit calibration metadata."""
from dataclasses import dataclass
from ..errors import ContractViolation

@dataclass(frozen=True, slots=True)
class Prediction:
    prediction_id: str
    target: str
    horizon_seconds: float
    probability: float | None
    interval: tuple[float,float] | None = None
    nominal_coverage: float | None = None
    calibration_status: str = "UNASSESSED"
    model_id: str = ""
    def __post_init__(self):
        if not self.prediction_id or not self.target or self.horizon_seconds <= 0: raise ContractViolation("prediction identity/target/horizon invalid")
        if self.probability is not None and not 0 <= self.probability <= 1: raise ContractViolation("probability must be in [0,1]")
        if self.interval is not None and self.interval[1] < self.interval[0]: raise ContractViolation("invalid interval")
        if self.nominal_coverage is not None and not 0 < self.nominal_coverage < 1: raise ContractViolation("invalid nominal coverage")

@dataclass(frozen=True, slots=True)
class PredictionSet:
    predictions: tuple[Prediction, ...]
    distribution_shift: bool = False
    tail_risk_flag: bool = False
