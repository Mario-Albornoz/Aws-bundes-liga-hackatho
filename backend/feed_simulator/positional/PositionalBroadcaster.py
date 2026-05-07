from feed_simulator.positional.PositionalSimulator import PositionalSimulator
from feed_simulator.common.BaseBroadcaster import BaseBroadcaster
from feed_simulator.common.models import ServerMessageType, WSServerMessage
from dotenv import load_dotenv
import os

load_dotenv()


class PositionalBroadcaster(BaseBroadcaster):
    BUFFER_SIZE = int(os.getenv("POSITIONAL_BUFFER", "256"))
    QUEUE_SIZE = int(os.getenv("POSITIONAL_QUEUE_SIZE", "32"))

    def __init__(self, match_id: str, speed: float = 1.0) -> None:
        super().__init__(match_id, speed, simulator_class=PositionalSimulator)

    async def _on_stream_exhausted(self) -> None:
        end_message = WSServerMessage(
            type=ServerMessageType.MATCH_END,
            seq=-1,
            match_id=self.match_id,
            payload=None,
        )
        await self._broadcast(end_message)
