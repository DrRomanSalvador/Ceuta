"""Versioned model/data/decision governance metadata."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json


@dataclass(frozen=True, slots=True)
class ModelGovernanceRecord:
    model_id: str
    version: str
    code_hash: str
    data_snapshot_hash: str
    assumptions: tuple[str, ...]
    valid_from: datetime
    valid_to: datetime | None = None
    calibrated: bool = False
    validation_ref: str = ""
    calibration_ref: str = ""
    approval_ref: str = ""
    release_hash: str = ""

    def __post_init__(self) -> None:
        if not self.model_id or not self.version or not self.code_hash or not self.data_snapshot_hash:
            raise ValueError("model governance identity and provenance are required")
        for value in (self.valid_from, self.valid_to):
            if value is not None and (value.tzinfo is None or value.utcoffset() is None):
                raise ValueError("model validity timestamps must be timezone-aware")
        if self.valid_to is not None and self.valid_to <= self.valid_from:
            raise ValueError("model validity interval must be ordered")
        if self.calibrated and not self.calibration_ref:
            raise ValueError("calibrated models require a calibration reference")
        if self.calibrated and not self.validation_ref:
            raise ValueError("calibrated models require a validation reference")
        if self.release_hash:
            expected = self.fingerprint()
            if self.release_hash != expected:
                raise ValueError("release_hash does not match model governance payload")

    def payload(self) -> dict[str, object]:
        return {
            "model_id": self.model_id,
            "version": self.version,
            "code_hash": self.code_hash,
            "data_snapshot_hash": self.data_snapshot_hash,
            "assumptions": self.assumptions,
            "valid_from": self.valid_from.isoformat(),
            "valid_to": self.valid_to.isoformat() if self.valid_to else None,
            "calibrated": self.calibrated,
            "validation_ref": self.validation_ref,
            "calibration_ref": self.calibration_ref,
            "approval_ref": self.approval_ref,
        }

    def fingerprint(self) -> str:
        canonical = json.dumps(self.payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return sha256(canonical.encode("utf-8")).hexdigest()


class ModelGovernance:
    def validate(self, record: ModelGovernanceRecord, at: datetime) -> bool:
        if at.tzinfo is None or at.utcoffset() is None:
            raise ValueError("model validation requires timezone-aware timestamp")
        if record.valid_from > at or (record.valid_to is not None and at >= record.valid_to):
            return False
        if not record.calibrated or not record.validation_ref or not record.calibration_ref:
            return False
        return bool(record.approval_ref and record.release_hash == record.fingerprint())


__all__ = ["ModelGovernance", "ModelGovernanceRecord"]
