from feed_handler.consumers.PositionalFeedConsumer import PositionalFeedConsumer
from feed_handler.consumers.handlers.ReplayHandler import ReplayHandler
from feed_simulator.common.BroadcastRegistry import BroadcastRegistry
from feed_simulator.positional.PositionalBroadcaster import PositionalBroadcaster


class PositionalBroadcastRegistry(BroadcastRegistry):
    def __init__(self) -> None:
        super().__init__()
        self._consumers: dict[str, PositionalFeedConsumer] = {}

    def _broadcaster_for(self, match_id: str, speed: float) -> PositionalBroadcaster:
        return PositionalBroadcaster(match_id=match_id, speed=speed)

    async def get_or_create(
        self, match_id: str, speed: float = 1.0
    ) -> PositionalBroadcaster:
        broadcaster = await super().get_or_create(match_id=match_id, speed=speed)
        if match_id not in self._consumers:
            consumer = PositionalFeedConsumer(
                match_id=match_id,
                broadcaster=broadcaster,
                handlers=[ReplayHandler()],
            )
            await consumer.start()
            self._consumers[match_id] = consumer
        return broadcaster

    async def shutdown(self) -> None:
        for consumer in self._consumers.values():
            await consumer.stop()
        self._consumers.clear()
        await super().shutdown()
