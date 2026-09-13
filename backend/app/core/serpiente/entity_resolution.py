from __future__ import annotations

from dataclasses import dataclass
import re


@dataclass(frozen=True, slots=True)
class EntityCandidate:
    entity_id: str
    canonical_name: str
    aliases: tuple[str, ...] = ()


class EntityResolver:
    """Conservative deterministic resolver; ambiguity is returned, never silently collapsed."""

    @staticmethod
    def normalize(value: str) -> str:
        return re.sub(r"\s+", " ", value.casefold().strip())

    def resolve(self, mention: str, candidates: tuple[EntityCandidate, ...]) -> tuple[EntityCandidate, ...]:
        key = self.normalize(mention)
        exact = [c for c in candidates if key == self.normalize(c.canonical_name) or key in {self.normalize(a) for a in c.aliases}]
        return tuple(sorted(exact, key=lambda c: c.entity_id))
