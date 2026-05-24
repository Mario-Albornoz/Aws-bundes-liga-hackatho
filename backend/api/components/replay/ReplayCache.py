import os
import msgpack
from dotenv import load_dotenv
from common.RedisClient import async_redis_client
from feed_simulator.positional.models import PositionalFrame

load_dotenv()

_STREAM_TTL = int(os.getenv("REPLAY_STREAM_TTL", "14400"))


class ReplayCache:
    CHUNK_SIZE = int(os.getenv("REPLAY_CHUNK_SIZE", "25"))

    def __init__(self, match_id: str) -> None:
        self._stream_key = f"replay:{match_id}:frames"
        self._index_key = f"replay:{match_id}:index"
        self._pending: list[dict] = []
        self._ttl_set = False
        self._first_frame_n: int | None = None
        self._latest_frame_n: int | None = None

    async def add_frame(self, frame: PositionalFrame) -> None:
        frame_n = int(frame.frame_n)
        if self._first_frame_n is None:
            self._first_frame_n = frame_n
        self._latest_frame_n = frame_n
        self._pending.append(frame.model_dump(mode="json"))
        if len(self._pending) >= self.CHUNK_SIZE:
            await self._flush()

    async def _flush(self) -> None:
        if not self._pending:
            return
        packed = msgpack.packb(self._pending, use_bin_type=True)
        entry_id = await async_redis_client.xadd(self._stream_key, {"data": packed})
        await async_redis_client.rpush(self._index_key, entry_id)
        if not self._ttl_set:
            await async_redis_client.expire(self._stream_key, _STREAM_TTL)
            await async_redis_client.expire(self._index_key, _STREAM_TTL)
            self._ttl_set = True
        self._pending.clear()

    async def cleanup(self) -> None:
        await self._flush()
        await async_redis_client.delete(self._stream_key, self._index_key)
        self._pending.clear()
        self._ttl_set = False
        self._first_frame_n = None
        self._latest_frame_n = None

    def frame_n_to_chunk(self, frame_n: int) -> int:
        first = self._first_frame_n or frame_n
        return max(0, (frame_n - first) // self.CHUNK_SIZE)

    async def get_status(self) -> dict:
        chunk_count = await self.chunk_count()
        pending = len(self._pending)
        return {
            "available": chunk_count > 0 or pending > 0,
            "chunk_count": chunk_count,
            "pending_frames": pending,
            "live_edge_seq": self._latest_frame_n,
            "first_frame_n": self._first_frame_n,
            "frame_count": chunk_count * self.CHUNK_SIZE + pending,
        }

    def pending_count(self) -> int:
        return len(self._pending)

    async def chunk_count(self) -> int:
        return await async_redis_client.llen(self._index_key)

    async def get_entry_id(self, chunk_n: int) -> bytes | None:
        return await async_redis_client.lindex(self._index_key, chunk_n)

    async def get_entry_ids(self, start: int = 0) -> list[bytes]:
        return await async_redis_client.lrange(self._index_key, start, -1)

    async def get_chunk_by_entry_id(self, entry_id: bytes | str) -> list[dict] | None:
        entries = await async_redis_client.xrange(
            self._stream_key, min=entry_id, max=entry_id, count=1
        )
        if not entries:
            return None
        _, fields = entries[0]
        return msgpack.unpackb(fields[b"data"], raw=False)


replay_cache = ReplayCache(match_id=os.getenv("MATCH_ID", ""))
