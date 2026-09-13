from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SchemaDrift:
    source_id: str
    added: tuple[str, ...]
    removed: tuple[str, ...]
    changed: tuple[str, ...]

    @property
    def detected(self) -> bool:
        return bool(self.added or self.removed or self.changed)


class SchemaDriftDetector:
    def compare(self, source_id: str, expected: dict[str, str], observed: dict[str, str]) -> SchemaDrift:
        added = tuple(sorted(set(observed) - set(expected)))
        removed = tuple(sorted(set(expected) - set(observed)))
        changed = tuple(sorted(k for k in set(expected) & set(observed) if expected[k] != observed[k]))
        return SchemaDrift(source_id, added, removed, changed)
