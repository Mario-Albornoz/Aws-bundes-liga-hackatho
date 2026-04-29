from events.loader import iter_events
from datetime import datetime
from common.models import ServerMessageType, WSServerMessage
import asyncio
from common.BaseSimulator import BaseSimulator


class EventSimulator(BaseSimulator):
    """
    Replays a DFL events XML file as a real-time stream.

    Attributes:
        speed: Playback speed multiplier.
               1.0 = real time, 60.0 = 1 match-minute per real second.
    """

    def __init__(self, speed: float = 1.0, path: str = "./data/Events_Anonym.xml"):
        super().__init__(path=path, speed=speed)

    async def stream(self):
        """
        Async generator that yields WSMessage instances.

        Timing: sleeps for (gap_between_events / speed) seconds before each yield,
        preserving the original intervals from the match.

        Yields:
            WSMessage with type=EVENT containing the MatchEvent payload.
        """
        seq = 0
        match_id = None
        prev_event_time: datetime | None = None

        loop = asyncio.get_running_loop()
        gen = iter_events(self.path)

        while True:
            chunk = await loop.run_in_executor(None, next, gen, None)
            if chunk is None:
                break
            for event in chunk:
                if match_id is None:
                    match_id = event.match_id

                seq += 1

                if prev_event_time is not None:
                    gap_seconds = (event.event_time - prev_event_time).total_seconds()
                    sleep_seconds = gap_seconds / self.speed
                    if sleep_seconds > 0:
                        await asyncio.sleep(sleep_seconds)

                prev_event_time = event.event_time

                yield WSServerMessage(
                    type=ServerMessageType.EVENT,
                    seq=seq,
                    match_id=match_id,
                    payload=event,
                )
