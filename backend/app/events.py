"""Tiny in-process pub/sub used by the Server-Sent Events endpoints.

The store publishes a full snapshot of the active-game list on every change,
and a per-game payload (the game, or ``None`` when it ends). Each SSE request
subscribes to an ``asyncio.Queue`` and unsubscribes when the client goes away.
"""

from __future__ import annotations

import asyncio
from typing import Any


class Broker:
    def __init__(self) -> None:
        self._subscribers: set[asyncio.Queue] = set()

    def subscribe(self) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._subscribers.add(queue)
        return queue

    def unsubscribe(self, queue: asyncio.Queue) -> None:
        self._subscribers.discard(queue)

    def publish(self, payload: Any) -> None:
        # Safe to call from sync code: put_nowait just appends. With no
        # subscribers (e.g. during seeding) this is a no-op.
        for queue in list(self._subscribers):
            queue.put_nowait(payload)


# Snapshot of the whole active-game list (list[dict]).
games_list_broker = Broker()

# Per-game updates published as (game_id, game_dict | None).
game_item_broker = Broker()
