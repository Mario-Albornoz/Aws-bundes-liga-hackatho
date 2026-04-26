from events.models import MatchEvent
from events.loader import load_events
from datetime import datetime
from common.models import ServerMessageType, WSServerMessage
import asyncio

class EventSimulator:
    """
    Replays a DFL events XML file as a real-time stream.
 
    Attributes:
        speed: Playback speed multiplier.
               1.0 = real time, 60.0 = 1 match-minute per real second.
    """
    def __init__(self, speed: float = 1.0):
        self.speed = speed
        self._events: list[MatchEvent] = []
    
    def load(self) -> None:
        """
        Parse the XML file and cache the event list in memory.
        """
        self._events = load_events()

    async def stream(self):
        """
        Async generator that yields WSMessage instances.
 
        Timing: sleeps for (gap_between_events / speed) seconds before each yield,
        preserving the original intervals from the match.
 
        Yields:
            WSMessage with type=EVENT containing the MatchEvent payload.
        """
        if not self._events:
            self.load()
        
        match_id = self._events[0].match_id
        seq = 0
        prev_event_time: datetime | None = None     
        
        for event in self._events:
            seq += 1
            
            if prev_event_time is not None:
                gap_seconds = (
                    event.event_time - prev_event_time
                ).total_seconds()
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

    @property
    def event_count(self) -> int:
        return len(self._events)