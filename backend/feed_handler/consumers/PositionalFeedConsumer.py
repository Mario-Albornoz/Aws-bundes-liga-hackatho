import asyncio
from typing import Optional

from feed_handler.consumers.handlers.AbstractHandler import AbstractHandler
from feed_simulator.common.BaseBroadcaster import BaseBroadcaster
from feed_simulator.common.models import ServerMessageType, WSServerMessage
from feed_simulator.positional.models import PositionalFrame


class PositionalFeedConsumer:
    def __init__(
        self,
        match_id: str,
        broadcaster: BaseBroadcaster,
        handlers: list[AbstractHandler[PositionalFrame]],
    ) -> None:
        self.match_id = match_id
        self._broadcaster = broadcaster
        self._handlers = handlers
        self._task: Optional[asyncio.Task] = None
        self._id = f"{match_id}:positional_feed_consumer"

    async def start(self) -> None:
        queue = await self._broadcaster.connect(self._id, websocket=None)
        self._task = asyncio.create_task(self._run(queue))

    async def stop(self) -> None:
        await self._broadcaster.disconnect(self._id)
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _run(self, queue: asyncio.Queue) -> None:
        try:
            while True:
                payload = await queue.get()
                message = WSServerMessage.model_validate_json(payload)
                if message.type == ServerMessageType.POSITIONAL:
                    frame = PositionalFrame.model_validate(message.payload)
                    for handler in self._handlers:
                        await handler.handle(frame)
                elif message.type == ServerMessageType.MATCH_END:
                    for handler in self._handlers:
                        await handler.complete()
                    break
        except asyncio.CancelledError:
            raise
