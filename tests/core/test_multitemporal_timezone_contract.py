from datetime import datetime, timezone

import pytest

from app.core.epistemology_p0.temporal.multitemporal import TemporalContext, TemporalFilter


def test_temporal_context_point_in_time_rejects_naive_cutoff():
    context = TemporalContext(event_time=datetime(2026, 9, 15, 12, 0))
    with pytest.raises(ValueError, match="timezone-aware"):
        context.is_valid_at(datetime(2026, 9, 15, 13, 0))


def test_temporal_filter_rejects_naive_simulation_time():
    context = TemporalContext(ingestion_time=datetime(2026, 9, 15, 12, 0, tzinfo=timezone.utc))
    with pytest.raises(ValueError, match="timezone-aware"):
        TemporalFilter.filter_by_available_at([context], datetime(2026, 9, 15, 13, 0))
