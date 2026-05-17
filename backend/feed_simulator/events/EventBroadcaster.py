from feed_simulator.common.models import ServerMessageType, WSServerMessage
from feed_simulator.events.EventSimulator import EventSimulator
from feed_simulator.common.BaseBroadcaster import BaseBroadcaster
from dotenv import load_dotenv
import os

load_dotenv()


class EventBroadcaster(BaseBroadcaster):
    BUFFER_SIZE = int(os.getenv("EVENT_BUFFER", "256"))
    QUEUE_SIZE = int(os.getenv("EVENT_QUEUE_SIZE", "32"))

    def __init__(self, match_id: str, speed: float = 1.0) -> None:
        super().__init__(match_id, speed, simulator_class=EventSimulator)

    async def _on_stream_exhausted(self) -> None:
        end_message = WSServerMessage(
            type=ServerMessageType.MATCH_END,
            seq=-1,
            match_id=self.match_id,
            payload=None,
        )
        await self._broadcast(end_message)
