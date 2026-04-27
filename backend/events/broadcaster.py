from common.models import ServerMessageType, WSServerMessage
from events.simulator import EventSimulator
from common.broadcaster import BaseBroadcaster, BroadcastRegistry

class MatchBroadcaster(BaseBroadcaster):
    def __init__(self, match_id: str, speed: float = 1.0) -> None:
        super().__init__(match_id, speed, simulator_class=EventSimulator)

    async def _on_stream_exhausted(self) -> None:
        end_message = WSServerMessage(
            type=ServerMessageType.MATCH_END,
            seq=-1,
            match_id=self.match_id,
            payload={"total_events": self._simulator.event_count},
        )
        await self._broadcast(end_message)

class MatchBroadcastRegistry(BroadcastRegistry):
    def _broadcaster_for(self, match_id, speed):
        return MatchBroadcaster(match_id=match_id, speed=speed)
