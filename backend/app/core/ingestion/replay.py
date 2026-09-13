from __future__ import annotations

from app.core.pipeline.contracts import ObservationRecord


class IngestionReplay:
    def replay(self, observations: tuple[ObservationRecord, ...], *, cutoff) -> tuple[ObservationRecord, ...]:
        if cutoff.tzinfo is None or cutoff.utcoffset() is None:
            raise ValueError("cutoff must be timezone-aware")
        return tuple(o for o in observations if o.available_at <= cutoff)
