import asyncio
from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = defaultdict(list)

    async def connect(self, room_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[room_id].append(websocket)

    def disconnect(self, room_id: int, websocket: WebSocket):
        self.active_connections[room_id].remove(websocket)

    async def broadcast(self, room_id: int, message: dict):
        await asyncio.gather(
            *[
                connection.send_json(message)
                for connection in self.active_connections[room_id]
            ],
            return_exceptions=True,
        )

    async def broadcast_all(self, message: dict):
        all_connections = [
            connection
            for connections in self.active_connections.values()
            for connection in connections
        ]
        await asyncio.gather(
            *[connection.send_json(message) for connection in all_connections],
            return_exceptions=True,
        )


connection_manager = ConnectionManager()
