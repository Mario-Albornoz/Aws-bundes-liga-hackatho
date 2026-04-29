import asyncio
from common.models import ServerMessageType, WSServerMessage
from positional.loader import load_positional
from positional.models import PositionalFrame
from common.BaseSimulator import BaseSimulator
from dotenv import load_dotenv
import os

load_dotenv()

_SOURCE_HZ = int(os.getenv("SOURCE_HZ"))


class PositionalSimulator(BaseSimulator):
    """
    Replays a DFL positional XML file as a real-time stream.

    Attributes:
        speed: Playback speed multiplier.
               1.0 = real time, 60.0 = 1 match-minute per real second.
    """

    # "./data/Positions_Bayern_Hamburg.xml"
    def __init__(self, speed: float = 1.0, path: str = "./data/test_positional.xml"):
        super().__init__(path=path, speed=speed)
        self._frames: list[PositionalFrame] = []

    async def _load(self):
        """
        Non-blocking load
        """
        loop = asyncio.get_running_loop()
        self._frames = await loop.run_in_executor(None, load_positional, self.path)

    async def stream(self):
        """
        Async generator that yields WSMessage instances.

        Yields:
            WSMessage with type=POSITIONAL containing the MatchEvent payload.
        """
        if not self._frames:
            await self._load()

        interval = 1 / (_SOURCE_HZ * self.speed)

        for frame in self._frames:
            yield WSServerMessage(
                type=ServerMessageType.POSITIONAL,
                seq=frame.frame_n,
                match_id=frame.match_id,
                payload=frame,
            )

            await asyncio.sleep(interval)
