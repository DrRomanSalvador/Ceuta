"""Nested-system state aggregation with explicit scale provenance."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Mapping, Sequence

@dataclass(frozen=True, slots=True)
class ScaleState:
    scale_id: str
    parent_id: str | None
    values: Mapping[str, float]
    source_state_ids: tuple[str, ...]

class MultiscaleStateEngine:
    def aggregate(self, children: Sequence[ScaleState], parent_id: str, scale_id: str) -> ScaleState:
        if not children: raise ValueError("children cannot be empty")
        keys=set().union(*(item.values.keys() for item in children))
        values={key: sum(item.values[key] for item in children if key in item.values)/sum(key in item.values for item in children) for key in keys}
        ids=tuple(source for item in children for source in item.source_state_ids)
        return ScaleState(scale_id,parent_id,values,ids)
