import asyncio
import sqlite3
from datetime import datetime
from feed_simulator.common.models import ServerMessageType, WSServerMessage
from feed_simulator.positional.loader import load_positional_to_db, iter_frame_ns, get_frame
from feed_simulator.common.BaseSimulator import BaseSimulator


class PositionalSimulator(BaseSimulator):
    """
    Replays a DFL positional XML file as a real-time stream.

    Attributes:
        speed: Playback speed multiplier.
               1.0 = real time, 60.0 = 1 match-minute per real second.
    """

    def __init__(
        self, speed: float = 1.0, path: str = "./data/Positions_Bayern_Hamburg.xml"
    ):
        super().__init__(path=path, speed=speed)

    async def stream(self):
        loop = asyncio.get_running_loop()
        conn: sqlite3.Connection = await loop.run_in_executor(
            None, load_positional_to_db, self.path
        )

        prev_timestamp: datetime | None = None

        try:
            for frame_n in iter_frame_ns(conn):
                frame = get_frame(conn, frame_n)

                if prev_timestamp is not None:
                    gap_seconds = (frame.timestamp - prev_timestamp).total_seconds()
                    sleep_seconds = gap_seconds / self.speed
                    if sleep_seconds > 0:
                        await asyncio.sleep(sleep_seconds)

                yield WSServerMessage(
                    type=ServerMessageType.POSITIONAL,
                    seq=frame.frame_n,
                    match_id=frame.match_id,
                    payload=frame,
                )

                prev_timestamp = frame.timestamp
        finally:
            conn.close()
