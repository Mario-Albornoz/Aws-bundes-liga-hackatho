import asyncio
from typing import Optional

from feed_handler.consumers.handlers.AbstractHandler import AbstractHandler
from feed_handler.publishing_bets.BetNotifier import bet_notifier
from feed_handler.publishing_bets.BetRuleEngine import bet_rule_engine
from feed_simulator.common.BaseBroadcaster import BaseBroadcaster
from feed_simulator.common.models import ServerMessageType, WSServerMessage
from feed_simulator.events.models import MatchEvent


class FeedConsumer:
    def __init__(
        self,
        match_id: str,
        broadcaster: BaseBroadcaster,
        handlers: list,
    ):
        self.match_id = match_id
        self._broadcaster = broadcaster
        self._handlers: list[AbstractHandler] = handlers
        self._task: Optional[asyncio.Task] = None
        self._id = f"{match_id}:feed_consumer"

    async def start(self):
        queue = await self._broadcaster.connect(self._id, websocket=None)
        self._task = asyncio.create_task(self._run(queue))

    async def stop(self):
        await self._broadcaster.disconnect(self._id)
        if self._task:
            self._task.cancel()
            try:
                await self._task
                for handler in self._handlers:
                    await handler.complete()
            except asyncio.CancelledError:
                pass

    async def _run(self, queue: asyncio.Queue):
        try:
            while True:
                payload = await queue.get()
                message = WSServerMessage.model_validate_json(payload)
                if message.type != ServerMessageType.EVENT:
                    continue
                event = MatchEvent.model_validate(message.payload)
                for handler in self._handlers:
                    await handler.handle(event)
        except asyncio.CancelledError:
            raise
