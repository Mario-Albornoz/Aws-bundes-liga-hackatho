from positional.simulator import PositionalSimulator
from common.broadcaster import BaseBroadcaster, BroadcastRegistry
from common.models import ServerMessageType, WSServerMessage
import asyncio

class PositionalBroadcaster(BaseBroadcaster):
    BUFFER_SIZE = 1000
 
    def __init__(self, match_id: str, speed: float = 1.0) -> None:
        super().__init__(match_id, speed, simulator_class=PositionalSimulator)
    
    async def start(self):
        if self._task is None or self._task.done():
            # Non-blocking load
            await self._simulator.load_async()
            self._task = asyncio.create_task(self._run())
    
    async def _on_stream_exhausted(self) -> None:
        end_message = WSServerMessage(
            type=ServerMessageType.MATCH_END,
            seq=-1,
            match_id=self.match_id,
            payload=None,
        )
        await self._broadcast(end_message)
    
 
class PositionalBroadcastRegistry(BroadcastRegistry):
    def _broadcaster_for(self, match_id: str, speed: float) -> PositionalBroadcaster:
        return PositionalBroadcaster(match_id=match_id, speed=speed)
