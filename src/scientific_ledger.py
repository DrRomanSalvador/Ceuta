"""Durable scientific execution lineage on the canonical event log."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from mission.event_log import append_payload, load_jsonl, validate_chain

from .scientific_execution import ScientificExecutionRecord

SCIENTIFIC_EXECUTION_EVENT = "SCIENTIFIC_EXECUTION"


def _record_payload(record: ScientificExecutionRecord) -> dict[str, Any]:
    return {"record": record.model_dump(mode="json")}


def append_scientific_execution(
    path: Path,
    *,
    mission_id: str,
    actor: str,
    timestamp: str,
    record: ScientificExecutionRecord,
) -> dict[str, Any]:
    """Append one execution record, reusing an exact existing retry."""
    events = load_jsonl(path)
    validate_chain(events)
    payload = _record_payload(record)
    for event in events:
        if event.get("event_type") != SCIENTIFIC_EXECUTION_EVENT:
            continue
        existing = event.get("payload", {}).get("record", {})
        if existing.get("execution_id") != record.execution_id:
            continue
        if existing != payload["record"]:
            raise ValueError("execution_id already exists with different scientific record")
        return event
    return append_payload(
        path,
        event_type=SCIENTIFIC_EXECUTION_EVENT,
        mission_id=mission_id,
        actor=actor,
        timestamp=timestamp,
        payload=payload,
    )


def replay_scientific_executions(path: Path) -> tuple[ScientificExecutionRecord, ...]:
    """Validate the canonical chain and reconstruct scientific execution state."""
    events = load_jsonl(path)
    validate_chain(events)
    records: list[ScientificExecutionRecord] = []
    seen: set[str] = set()
    for event in events:
        if event.get("event_type") != SCIENTIFIC_EXECUTION_EVENT:
            continue
        raw = event.get("payload", {}).get("record")
        if not isinstance(raw, dict):
            raise ValueError("SCIENTIFIC_EXECUTION event has invalid record payload")
        record = ScientificExecutionRecord.model_validate(raw)
        if record.execution_id in seen:
            raise ValueError("duplicate scientific execution record")
        seen.add(record.execution_id)
        records.append(record)
    return tuple(records)
