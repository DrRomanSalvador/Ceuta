"""Falsification and adversarial checks for causal hypotheses."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from .contracts import CausalEvidence, CausalHypothesis, EpistemicLevel


@dataclass(frozen=True)
class FalsificationResult:
    hypothesis_id: str
    passed: bool
    failed_tests: tuple[str, ...]
    unresolved_tests: tuple[str, ...]


class FalsificationEngine:
    def evaluate(
        self,
        hypothesis: CausalHypothesis,
        evidence: Iterable[CausalEvidence],
    ) -> FalsificationResult:
        evidence_by_id = {item.evidence_id: item for item in evidence}
        failed: list[str] = []
        unresolved: list[str] = []
        for control in hypothesis.negative_controls:
            matches = [e for e in evidence_by_id.values() if control in e.source_ids]
            if not matches:
                unresolved.append(f"negative_control:{control}")
            elif any(e.supports and e.level in {EpistemicLevel.CAUSALLY_IDENTIFIED, EpistemicLevel.PROSPECTIVELY_VALIDATED} for e in matches):
                failed.append(f"negative_control:{control}")
        return FalsificationResult(
            hypothesis_id=hypothesis.hypothesis_id,
            passed=not failed,
            failed_tests=tuple(failed),
            unresolved_tests=tuple(unresolved),
        )
