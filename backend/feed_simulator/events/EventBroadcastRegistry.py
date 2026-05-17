from feed_handler.consumers.handlers.BetProcessingHandler import BetProcessingHandler
from feed_handler.consumers.handlers.BetPublishingHandler import BetPublishingHandler
from feed_handler.consumers.handlers.dto.BetTypes import BetTypes
from feed_handler.publishing_bets.BetNotifier import bet_notifier
from feed_handler.publishing_bets.BetRuleEngine import bet_rule_engine
from feed_handler.publishing_bets.FeedConsumer import FeedConsumer
from feed_simulator.common.BroadcastRegistry import BroadcastRegistry
from feed_simulator.events.EventBroadcaster import EventBroadcaster


class EventBroadcastRegistry(BroadcastRegistry):
    def __init__(self) -> None:
        super().__init__()
        self._consumers: dict[str, FeedConsumer] = {}

    def _broadcaster_for(self, match_id: str, speed: float):
        return EventBroadcaster(match_id=match_id, speed=speed)

    async def get_or_create(
        self, match_id: str, speed: float = 1.0
    ) -> EventBroadcaster:
        broadcaster = await super().get_or_create(match_id=match_id, speed=speed)
        if match_id not in self._consumers:

            consumer = FeedConsumer(
                match_id=match_id,
                broadcaster=broadcaster,
                # assing handlers here, all new processing or publishing handlers should be attached to this handlers list
                handlers=[
                    BetProcessingHandler(BetTypes.SUBSTITUTION.value),
                    BetPublishingHandler(),
                ],
            )
            await consumer.start()
            self._consumers[match_id] = consumer
        return broadcaster

    async def shutdown(self) -> None:
        for consumer in self._consumers.values():
            await consumer.stop()
        self._consumers.clear()
        await super().shutdown()
