from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Mapping


@dataclass(frozen=True, slots=True)
class AuditEvent:
    event_id: str
    timestamp: str
    actor_id: str
    action: str
    resource_type: str
    resource_id: str | None
    decision: str | None
    payload_hash: str
    previous_hash: str
    event_hash: str


def canonical_json(
    value: Mapping[str, Any],
) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_text(value: str) -> str:
    return hashlib.sha256(
        value.encode("utf-8")
    ).hexdigest()


class AuditChain:
    def __init__(self) -> None:
        self._previous_hash = "0" * 64
        self._events: list[AuditEvent] = []

    @property
    def events(self) -> tuple[AuditEvent, ...]:
        return tuple(self._events)

    def append(
        self,
        *,
        event_id: str,
        actor_id: str,
        action: str,
        resource_type: str,
        resource_id: str | None,
        decision: str | None,
        payload: Mapping[str, Any],
    ) -> AuditEvent:

        timestamp = datetime.now(
            timezone.utc
        ).isoformat()

        payload_hash = sha256_text(
            canonical_json(payload)
        )

        unsigned = {
            "event_id": event_id,
            "timestamp": timestamp,
            "actor_id": actor_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "decision": decision,
            "payload_hash": payload_hash,
            "previous_hash": self._previous_hash,
        }

        event_hash = sha256_text(
            canonical_json(unsigned)
        )

        event = AuditEvent(
            **unsigned,
            event_hash=event_hash,
        )

        self._events.append(event)
        self._previous_hash = event_hash

        return event

    def verify(self) -> bool:
        previous = "0" * 64

        for event in self._events:
            unsigned = asdict(event)
            unsigned.pop("event_hash")

            if event.previous_hash != previous:
                return False

            if (
                sha256_text(
                    canonical_json(unsigned)
                )
                != event.event_hash
            ):
                return False

            previous = event.event_hash

        return True