"""Versioned model/data/decision governance metadata."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True, slots=True)
class ModelGovernanceRecord:
    model_id: str
    version: str
    code_hash: str
    data_snapshot_hash: str
    assumptions: tuple[str,...]
    valid_from: datetime
    valid_to: datetime|None=None
    calibrated: bool=False

class ModelGovernance:
    def validate(self, record: ModelGovernanceRecord, at: datetime)->bool:
        return record.valid_from <= at and (record.valid_to is None or at < record.valid_to)
