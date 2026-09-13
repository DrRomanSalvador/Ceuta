"""Small asynchronous event bus for the CeutIA pipeline.

The bus provides delivery isolation between pipeline stages. It is deliberately
in-process for the first implementation so the scientific contracts can be
validated before introducing external infrastructure.
"""

from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import DefaultDict

from .contracts import PipelineEvent


class EventBus:
    """Typed-event pub/sub bus with bounded subscriber queues.

    Publishing applies backpressure rather than dropping events. A subscriber
    can be removed explicitly, which is important for short-lived workers and
    tests. Event delivery preserves publication order per subscriber.
    """

    def __init__(self, *, queue_maxsize: int = 0) -> None:
        if queue_maxsize < 0:
            raise ValueError("queue_maxsize must be non-negative")
        self._queue_maxsize = queue_maxsize
        self._queues: DefaultDict[str, list[asyncio.Queue[PipelineEvent]]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def publish(self, event: PipelineEvent) -> int:
        """Publish an event and return the number of subscribers reached."""
        if not isinstance(event, PipelineEvent):
            raise TypeError("event must be a PipelineEvent")

        async with self._lock:
            queues = tuple(self._queues.get(event.event_type, ()))

        # Do not hold the subscription lock while applying queue backpressure.
        for queue in queues:
            await queue.put(event)
        return len(queues)

    async def subscribe(self, event_type: str) -> asyncio.Queue[PipelineEvent]:
        """Create and register a queue for one event type."""
        if not event_type:
            raise ValueError("event_type must not be empty")
        queue: asyncio.Queue[PipelineEvent] = asyncio.Queue(maxsize=self._queue_maxsize)
        async with self._lock:
            self._queues[event_type].append(queue)
        return queue

    async def unsubscribe(self, event_type: str, queue: asyncio.Queue[PipelineEvent]) -> bool:
        """Remove a previously registered queue; return whether it existed."""
        async with self._lock:
            queues = self._queues.get(event_type)
            if not queues:
                return False
            try:
                queues.remove(queue)
            except ValueError:
                return False
            if not queues:
                self._queues.pop(event_type, None)
            return True

    async def close(self) -> None:
        """Remove all subscriptions.

        Consumers remain responsible for cancelling their worker tasks. The
        bus never silently cancels application work.
        """
        async with self._lock:
            self._queues.clear()
