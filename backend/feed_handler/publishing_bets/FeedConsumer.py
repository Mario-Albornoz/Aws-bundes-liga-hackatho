import asyncio
from typing import Optional
from feed_simulator.common.BaseBroadcaster import BaseBroadcaster
from feed_handler.publishing_bets.BetRuleEngine import bet_rule_engine
from feed_handler.publishing_bets.BetNotifier import bet_notifier
from feed_simulator.common.models import WSServerMessage, ServerMessageType
from feed_simulator.events.models import MatchEvent


class FeedConsumer:
    def __init__(
        self,
        match_id: str,
        broadcaster: BaseBroadcaster,
    ):
        self.match_id = match_id
        self._broadcaster = broadcaster
        self._task: Optional[asyncio.Task] = None
        self._id = "feed_consumer"

    async def start(self):
        queue = await self._broadcaster.connect(self._id, websocket=None)
        self._task = asyncio.create_task(self._run(queue))

    async def stop(self):
        self._broadcaster.disconnect(self._id)
        self._task.cancel()

    async def _run(self, queue: asyncio.Queue):
        while True:
            payload = await queue.get()
            message = WSServerMessage.model_validate_json(payload)
            if message.type != ServerMessageType.EVENT:
                continue
            event = MatchEvent.model_validate(message.payload)
            opportunity = bet_rule_engine.evaluate(event)
            if opportunity:
                await bet_notifier.notify(opportunity)
