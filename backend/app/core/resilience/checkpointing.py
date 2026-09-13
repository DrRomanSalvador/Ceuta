from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Checkpoint:
    checkpoint_id: str
    sequence: int
    state_hash: str


class CheckpointStore:
    def __init__(self) -> None:
        self._items: list[Checkpoint] = []

    def save(self, checkpoint: Checkpoint) -> None:
        if self._items and checkpoint.sequence <= self._items[-1].sequence:
            raise ValueError("checkpoint sequence must be strictly increasing")
        self._items.append(checkpoint)

    @property
    def latest(self) -> Checkpoint | None:
        return self._items[-1] if self._items else None
