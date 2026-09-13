"""Evidence-source dependency analysis.

Multiple documents may repeat one origin. This module prevents duplicated
reporting from being interpreted as independent corroboration.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SourceRecord:
    source_id: str
    origin_id: str
    parent_source_ids: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DependencyAnalysis:
    independent_source_count: int
    source_groups: tuple[tuple[str, tuple[str, ...]], ...]
    contaminated_evidence_ids: tuple[str, ...]


class SourceDependencyAnalyzer:
    def analyze(self, sources: tuple[SourceRecord, ...], evidence_sources: dict[str, tuple[str, ...]]) -> DependencyAnalysis:
        if not sources:
            raise ValueError("sources must not be empty")
        by_origin: dict[str, list[str]] = {}
        for source in sources:
            if not source.source_id or not source.origin_id:
                raise ValueError("source identity and origin are required")
            by_origin.setdefault(source.origin_id, []).append(source.source_id)

        groups = tuple(sorted((origin, tuple(sorted(ids))) for origin, ids in by_origin.items()))
        contaminated: list[str] = []
        for evidence_id, source_ids in evidence_sources.items():
            origins = {next((source.origin_id for source in sources if source.source_id == source_id), source_id) for source_id in source_ids}
            if len(origins) < len(set(source_ids)):
                contaminated.append(evidence_id)
        return DependencyAnalysis(
            independent_source_count=len(by_origin),
            source_groups=groups,
            contaminated_evidence_ids=tuple(sorted(contaminated)),
        )
