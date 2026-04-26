import asyncio
from collections import deque
from datetime import datetime, timezone
 
from fastapi import WebSocket
 
from common.models import ServerMessageType, WSServerMessage
from events.simulator import EventSimulator

class MatchBroadcaster:
    """
    Manages a single match stream and broadcast to all connected clients. 
    
    One instance per match. A buffer keeps recent messages so reconnecting clients
    can catch up before joining the live stream.
    """

    BUFFER_SIZE = 200
    
    def __init__(self, match_id: str, speed: float = 1.0):
        self.match_id = match_id
        self._simulator = EventSimulator(speed=speed)
        self._clients: dict[str, WebSocket] = {}  # client_id -> websocket
        self._buffer: deque[WSServerMessage] = deque(maxlen=self.BUFFER_SIZE)
        self._task: asyncio.Task | None = None
        self._lock = asyncio.Lock()

    async def start(self):
        """
        Load the XML file and start the simulator background task.
        """
        if self._task is None or self._task.done():
            self._simulator.load()
            self._task = asyncio.create_task(self._run())
        
    async def stop(self):
        """
        Cancel the simulator task and clear all connected clients.
 
        Called by BroadcastRegistry.shutdown() on application shutdown.
        """
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        self._clients.clear()
    
    async def connect(self, client_id: str, websocket: WebSocket, resume_seq: int = 0):
        """
        Register a client and replay any missed messages from the buffer.
 
        Args:
            client_id:  Unique identifier for this client connection (UUID).
            websocket:  The client's WebSocket connection.
            resume_seq: Last sequence number the client received. Messages
                        with seq > resume_seq are replayed before going live.
        """
        async with self._lock:
            self._clients[client_id] = websocket
        
        await self._catchup(websocket, resume_seq)
    
    async def disconnect(self, client_id: str):
        """
        Remove a client from the active recipient list.

        Args:
            client_id:  Unique identifier for this client connection (UUID).
        """
        async with self._lock:
            self._clients.pop(client_id, None)

    async def _run(self):
        """
        Background task body. Iterates the simulator and broadcasts each message.
        Sends MATCH_END to all clients when the simulator is done.
        """
        async for message in self._simulator.stream():
            self._buffer.append(message)
            await self._broadcast(message)
 
        # Match ended, notify all clients
        end_message = WSServerMessage(
            type=ServerMessageType.MATCH_END,
            seq=-1,
            match_id=self.match_id,
            server_ts=datetime.now(tz=timezone.utc),
            payload={"total_events": self._simulator.event_count},
        )
        await self._broadcast(end_message)
    

    async def _broadcast(self, message: WSServerMessage) -> None:
        """Send a message to all connected clients"""
        if not self._clients:
            return
 
        payload = message.model_dump_json()
        disconnected = []
 
        async with self._lock:
            for client_id, websocket in self._clients.items():
                try:
                    await websocket.send_text(payload)
                except Exception:
                    disconnected.append(client_id)
 
        for client_id in disconnected:
            await self.disconnect(client_id)
    
    async def _catchup(self, websocket: WebSocket, resumed_seq: int):
        """
        Replay buffered messages with seq > resume_seq to a single client.
 
        Called once per connect() call, before the client is added to the
        live recipient list. If the client's WebSocket fails during replay,
        the catch-up aborts and the client will reconnect again.

        Args:
            websocket:  The client's WebSocket connection.
            resume_seq: Last sequence number the client received. Messages
                        with seq > resume_seq are replayed before going live.
        """
        missed = [msg for msg in self._buffer if msg.seq > resumed_seq]
        for message in missed:
            try:
                await websocket.send_text(message.model_dump_json())
            except Exception:
                return
    
    @property
    def client_count(self) -> int:
        return len(self._clients)

class BroadcastRegistry:
    """
    Global registry of active MatchBroadcasters.
    One instance shared across the application.
    """
    def __init__(self) -> None:
        self._broadcasters: dict[str, MatchBroadcaster] = {}

    async def get_or_create(self, match_id: str, speed: float = 1.0) -> MatchBroadcaster:
        """Return existing broadcaster for a match, or create and start a new one."""
        if match_id not in self._broadcasters:
            broadcaster = MatchBroadcaster(match_id=match_id, speed=speed)
            await broadcaster.start()
            self._broadcasters[match_id] = broadcaster
        return self._broadcasters[match_id]
 
    async def shutdown(self) -> None:
        """Stop all active broadcasters. Called on app shutdown."""
        for broadcaster in self._broadcasters.values():
            await broadcaster.stop()
        self._broadcasters.clear()
