from feed_simulator.common.BroadcastRegistry import BroadcastRegistry
from feed_simulator.events.EventBroadcaster import EventBroadcaster


class EventBroadcastRegistry(BroadcastRegistry):
    def _broadcaster_for(self, match_id: str, speed: float):
        return EventBroadcaster(match_id=match_id, speed=speed)
