from common.BroadcastRegistry import BroadcastRegistry
from positional.PositionalBroadcaster import PositionalBroadcaster


class PositionalBroadcastRegistry(BroadcastRegistry):
    def _broadcaster_for(self, match_id: str, speed: float) -> PositionalBroadcaster:
        return PositionalBroadcaster(match_id=match_id, speed=speed)
