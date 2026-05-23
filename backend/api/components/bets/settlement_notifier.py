import asyncio
from collections import defaultdict

from fastapi import WebSocket

from feed_handler.cache.BetCache import bet_cache


class BetSettlementNotifier:
    """Pushes bet settlement outcomes to clients subscribed by user_id. Thoruhg bet/stream ws"""

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
        await self.push_snapshot(user_id, targets)

    async def push_snapshot(
        self, user_id: int, targets: list | None = None
    ) -> None:
        """Send the user's current bet list. Fetches live targets if not provided."""
        if targets is None:
            async with self._lock:
                targets = list(self._connections.get(user_id, []))
        if not targets:
            return
        current_bets = await bet_cache.get_bets_by_user_id(user_id=user_id)
        snapshot = {
            "type": "bet_snapshot",
            "bets": [b.model_dump(mode="json") for b in current_bets],
        }
        await asyncio.gather(
            *[ws.send_json(snapshot) for ws in targets],
            return_exceptions=True,
        )


bet_settlement_notifier = BetSettlementNotifier()
