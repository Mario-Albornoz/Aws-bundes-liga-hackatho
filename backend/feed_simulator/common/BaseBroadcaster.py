import asyncio
from collections import deque
from typing import Optional

from fastapi import WebSocket

from feed_simulator.common.BaseSimulator import BaseSimulator
from feed_simulator.common.models import WSServerMessage


class BaseBroadcaster:
    """
    Manages a single stream and broadcasts to all connected clients.

    One instance per match. A buffer keeps recent messages so reconnecting
    clients can catch up before joining the live stream.

    Live messages are placed into per-client asyncio queues. The router's
    consumer task is responsible for draining each queue and sending over
    the WebSocket.

    Subclasses override:
        BUFFER_SIZE            — replay buffer capacity
        QUEUE_SIZE             — per-client live-message queue capacity
        _on_stream_exhausted() — called when the simulator yields nothing more
    """

    BUFFER_SIZE: int
    QUEUE_SIZE: int

    def __init__(
        self, match_id: str, speed: float, simulator_class: BaseSimulator
    ) -> None:
        self.match_id: str = match_id
        self.speed: float = speed
        self._simulator: BaseSimulator = simulator_class(speed=speed)
        self._task: Optional[asyncio.Task] = None
        self._buffer: deque[WSServerMessage] = deque(maxlen=self.BUFFER_SIZE)
        self._clients: dict[str, asyncio.Queue] = {}
        self._lock = asyncio.Lock()

    async def start(self):
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run())

    async def stop(self):
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._clients.clear()

    async def connect(
        self, client_id: str, websocket: WebSocket, resume_seq: int = 0
    ) -> asyncio.Queue:
        """
        Register a client, replay missed messages, and return the client's queue.

        The caller (router) is responsible for consuming the returned queue
        and forwarding messages to the WebSocket.
        """
        queue: asyncio.Queue = asyncio.Queue(maxsize=self.QUEUE_SIZE)
        async with self._lock:
            self._clients[client_id] = queue
        await self._catchup(websocket, resume_seq)
        return queue

    async def disconnect(self, client_id: str):
        async with self._lock:
            self._clients.pop(client_id, None)

    async def _run(self):
        async for message in self._simulator.stream():
            self._buffer.append(message)
            await self._broadcast(message)
        await self._on_stream_exhausted()

    async def _broadcast(self, message: WSServerMessage) -> None:
        if not self._clients:
            return

        payload = message.model_dump_json()
        async with self._lock:
            clients = list(self._clients.items())

        for client_id, queue in clients:
            try:
                queue.put_nowait(payload)
            except asyncio.QueueFull:
                await self.disconnect(client_id)

    async def _catchup(self, websocket: WebSocket, resumed_seq: int):
        if websocket is None:
            return
        missed = [msg for msg in self._buffer if msg.seq > resumed_seq]
        for message in missed:
            try:
                await websocket.send_text(message.model_dump_json())
            except Exception:
                return

    async def _on_stream_exhausted(self) -> None:
        pass

    @property
    def client_count(self) -> int:
        return len(self._clients)
