"""Exact claim/evidence/citation trace contracts."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CitationTrace:
    claim_id: str
    source_id: str
    locator: str
    captured_text_hash: str
    captured_at: str

    def __post_init__(self) -> None:
        if not all(value.strip() for value in (self.claim_id, self.source_id, self.locator, self.captured_text_hash, self.captured_at)):
            raise ValueError("citation trace requires complete immutable locator metadata")


class CitationTraceRegistry:
    def __init__(self) -> None:
        self._traces: dict[str, list[CitationTrace]] = {}

    def add(self, trace: CitationTrace) -> None:
        traces = self._traces.setdefault(trace.claim_id, [])
        if trace not in traces:
            traces.append(trace)

    def traces(self, claim_id: str) -> tuple[CitationTrace, ...]:
        return tuple(self._traces.get(claim_id, ()))

    def traceable(self, claim_id: str) -> bool:
        return bool(self.traces(claim_id))


__all__ = ["CitationTrace", "CitationTraceRegistry"]
