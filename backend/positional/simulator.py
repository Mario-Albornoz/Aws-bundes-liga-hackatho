import asyncio
from common.models import ServerMessageType, WSServerMessage
from positional.loader import load_positional
from positional.models import PositionalFrame

_SOURCE_HZ = 25

class PositionalSimulator:
    """
    Replays a DFL positional XML file as a real-time stream.
 
    Attributes:
        speed: Playback speed multiplier.
               1.0 = real time, 60.0 = 1 match-minute per real second.
    """
    def __init__(self, speed: float = 1.0, path: str = "./data/Positions_Bayern_Hamburg.xml"):
        self.speed = speed
        self.path = path
        self._frames: list[PositionalFrame] = []
    
    def load(self):
        """
        Parse the XML file and cache the event list in memory.
        """
        self._frames = load_positional(self.path)
    
    async def load_async(self):
        """
        Non-blocking load
        """
        loop = asyncio.get_running_loop()
        self._frames = await loop.run_in_executor(None, load_positional)
    
    async def stream(self):
        """
        Async generator that yields WSMessage instances.
 
        Yields:
            WSMessage with type=POSITIONAL containing the MatchEvent payload.
        """
        if not self._frames:
            self.load()
        
        interval = 1 / (_SOURCE_HZ * self.speed)

        for frame in self._frames:
            yield WSServerMessage(
                type=ServerMessageType.POSITIONAL,
                seq=frame.frame_n,
                match_id=frame.match_id,
                payload=frame,
            )

            await asyncio.sleep(interval)
