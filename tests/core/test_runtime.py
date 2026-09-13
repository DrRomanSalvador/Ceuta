from datetime import datetime, timezone

from app.core.epistemology_p0.advanced.runtime import run_demo_cycle


def test_runtime_cycle_is_executable_and_produces_forecasts() -> None:
    result = run_demo_cycle(as_of=datetime(2026, 9, 13, 12, 0, tzinfo=timezone.utc))

    assert result.state_id.startswith("state-")
    assert result.variables == ("health_pressure", "migration_pressure")
    assert len(result.forecast_ids) == 2
    assert all(item.startswith("forecast-") for item in result.forecast_ids)
    assert all(item.isoformat() == "2026-09-13T13:00:00+00:00" for item in result.forecast_targets)
