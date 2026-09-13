from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RedTeamFinding:
    test_id: str
    passed: bool
    failure_mode: str | None


class RedTeamEngine:
    def evaluate(self, test_id: str, *, observed_failure: bool, failure_mode: str | None = None) -> RedTeamFinding:
        return RedTeamFinding(test_id, not observed_failure, failure_mode if observed_failure else None)
