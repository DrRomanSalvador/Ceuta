"""Fail-closed safety gates for the longitudinal decision loop."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SafetyGate:
    allowed: bool
    reasons: tuple[str, ...]
    required_human_review: bool


class SafetyEngine:
    def evaluate(
        self,
        *,
        observable: bool,
        identifiable: bool,
        calibrated: bool,
        source_integrity: bool,
        model_valid: bool,
    ) -> SafetyGate:
        flags = (observable, identifiable, calibrated, source_integrity, model_valid)
        if any(not isinstance(flag, bool) for flag in flags):
            raise TypeError("safety gate state flags must be booleans")
        reasons = tuple(
            name
            for name, ok in (
                ("observability", observable),
                ("identifiability", identifiable),
                ("calibration", calibrated),
                ("source_integrity", source_integrity),
                ("model_validity", model_valid),
            )
            if not ok
        )
        return SafetyGate(not reasons, reasons, bool(reasons))
