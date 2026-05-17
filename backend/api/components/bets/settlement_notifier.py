import asyncio
from collections import defaultdict

from fastapi import WebSocket


class BetSettlementNotifier:
    """Pushes bet settlement outcomes to clients subscribed by user_id."""

    def __init__(self) -> None:
        self._connections: dict[int, list[WebSocket]] = defaultdict(list)
        self._lock = asyncio.Lock()

    async def subscribe(self, user_id: int, websocket: WebSocket) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections[user_id].append(websocket)

    async def unsubscribe(self, user_id: int, websocket: WebSocket) -> None:
        async with self._lock:
            conns = self._connections.get(user_id)
            if not conns:
                return
            if websocket in conns:
                conns.remove(websocket)

    async def notify_user(self, user_id: int, message: dict) -> None:
        async with self._lock:
            targets = list(self._connections.get(user_id, []))
        if not targets:
            return
        await asyncio.gather(
            *[ws.send_json(message) for ws in targets],
            return_exceptions=True,
        )


bet_settlement_notifier = BetSettlementNotifier()
