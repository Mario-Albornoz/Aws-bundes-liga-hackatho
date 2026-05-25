import asyncio
import os
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from dotenv import load_dotenv
from api.components.replay.ReplayCache import replay_cache
from feed_simulator.common.models import (
    ClientMessageType,
    ServerMessageType,
    WSClientMessage,
    WSServerMessage,
)

load_dotenv()

router = APIRouter(prefix="/replay", tags=["replay"])

_FRAME_INTERVAL = float(os.getenv("REPLAY_FRAME_INTERVAL", "0.04"))
_IDLE_POLL_INTERVAL = float(os.getenv("REPLAY_IDLE_POLL_INTERVAL", "0.1"))
_IDLE_LIMIT = int(os.getenv("REPLAY_IDLE_LIMIT", "50"))


@router.get("/status")
async def replay_status():
    return await replay_cache.get_status()


@router.websocket("/stream")
async def replay_stream(
    websocket: WebSocket,
    from_chunk: int = Query(0, ge=0, description="Chunk index to start replay from"),
    speed: float = Query(1.0, gt=0, le=100, description="Playback speed multiplier"),
):
    await websocket.accept()

    match_id = os.getenv("MATCH_ID", "")
    stream_task: asyncio.Task | None = None

    async def _stream_follow(start_chunk: int) -> None:
        """
        Stream flushed chunks from start_chunk onward. When the client catches up to
        the current buffer tail, wait for newly recorded chunks.
        """
        next_idx = start_chunk
        idle_ticks = 0

        while True:
            total = await replay_cache.chunk_count()

            if next_idx < total:
                entry_id = await replay_cache.get_entry_id(next_idx)
                if entry_id is None:
                    idle_ticks += 1
                else:
                    idle_ticks = 0
                    frames = await replay_cache.get_chunk_by_entry_id(entry_id)
                    if frames:
                        for frame in frames:
                            frame_n = int(frame["frame_n"])
                            await websocket.send_text(
                                WSServerMessage(
                                    type=ServerMessageType.POSITIONAL,
                                    seq=frame_n,
                                    match_id=match_id,
                                    payload=frame,
                                ).model_dump_json()
                            )
                            await asyncio.sleep(_FRAME_INTERVAL / speed)
                    next_idx += 1
                    continue

            if replay_cache.pending_count() > 0:
                idle_ticks = 0
                await asyncio.sleep(_IDLE_POLL_INTERVAL)
                continue

            idle_ticks += 1
            if idle_ticks >= _IDLE_LIMIT:
                break
            await asyncio.sleep(_IDLE_POLL_INTERVAL)

        await websocket.send_text(
            WSServerMessage(
                type=ServerMessageType.MATCH_END,
                seq=-1,
                match_id=match_id,
                payload=None,
            ).model_dump_json()
        )

    stream_task = asyncio.create_task(_stream_follow(from_chunk))

    try:
        while True:
            raw = await websocket.receive_text()
            client_msg = WSClientMessage.model_validate_json(raw)

            if client_msg.type == ClientMessageType.PAUSE:
                if stream_task and not stream_task.done():
                    stream_task.cancel()

            elif client_msg.type == ClientMessageType.RESUME:
                if stream_task is None or stream_task.done():
                    stream_task = asyncio.create_task(_stream_follow(from_chunk))

    except WebSocketDisconnect:
        if stream_task:
            stream_task.cancel()
