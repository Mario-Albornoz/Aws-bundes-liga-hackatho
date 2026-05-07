from feed_simulator.events.models import MatchEvent


class MatchConsumer:
    def __init__(self, broadcaster, handlers):
        self._broadcaster = broadcaster
        self._handlers = handlers
        pass

    async def _handle_events(self, event: MatchEvent):
        for handler in self._handlers:
            await handler.handle(event)
