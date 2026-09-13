"""Deterministic event replay and forensic decision audit."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Sequence
from .sensing import RawSignal

@dataclass(frozen=True, slots=True)
class ReplayRecord:
    sequence: int
    payload_hash: str
    event_time: object
    decision_id: str
    output_hash: str

class DeterministicReplay:
    def replay(self, signals: Sequence[RawSignal], runner: Callable[[RawSignal], str]) -> tuple[ReplayRecord,...]:
        ordered=sorted(signals,key=lambda x:(x.event_time,x.available_at,x.payload_hash))
        records=[]
        for i,signal in enumerate(ordered):
            output=runner(signal)
            records.append(ReplayRecord(i+1,signal.payload_hash,signal.event_time,output,output))
        return tuple(records)
