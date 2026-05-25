from api.components.replay.ReplayCache import replay_cache
from feed_handler.consumers.handlers.AbstractHandler import AbstractHandler
from feed_simulator.positional.models import PositionalFrame


class ReplayHandler(AbstractHandler[PositionalFrame]):
    async def handle(self, event: PositionalFrame) -> None:
        await replay_cache.add_frame(event)

    async def complete(self) -> None:
        await replay_cache.cleanup()
