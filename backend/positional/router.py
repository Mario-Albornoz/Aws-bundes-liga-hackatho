import asyncio
from uuid import uuid4
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from common.consume_queue import consume_queue
from common.models import (
    ServerMessageType,
    ClientMessageType,
    WSClientMessage,
    WSServerMessage,
)
from positional.PositionalBroadcastRegistry import PositionalBroadcastRegistry

router = APIRouter(prefix="/positional", tags=["positional"])


@router.websocket("/stream")
async def positional_stream(
    websocket: WebSocket,
    match_id: str = Query(..., description="Match identifier"),
    speed: float = Query(1.0, gt=0, le=600, description="Playback speed multiplier"),
    seq: int = Query(0, ge=0, description="Last received sequence number for catch-up"),
):
    await websocket.accept()

    registry: PositionalBroadcastRegistry = (
        websocket.app.state.positional_broadcast_registry
    )
    broadcaster = await registry.get_or_create(match_id, speed=speed)

    client_id = str(uuid4())

    await websocket.send_text(
        WSServerMessage(
            type=ServerMessageType.MATCH_START,
            seq=0,
            match_id=match_id,
            payload={
                "speed": speed,
                "resume_from_seq": seq,
                "connected_clients": broadcaster.client_count + 1,
            },
        ).model_dump_json()
    )

    queue = await broadcaster.connect(
        client_id=client_id, websocket=websocket, resume_seq=seq
    )
    consumer_task = asyncio.create_task(consume_queue(queue, websocket))

    try:
        while True:
            raw = await websocket.receive_text()
            client_msg = WSClientMessage.model_validate_json(raw)

            if client_msg.type == ClientMessageType.PAUSE:
                consumer_task.cancel()
                await broadcaster.disconnect(client_id)

            elif client_msg.type == ClientMessageType.RESUME:
                queue = await broadcaster.connect(
                    client_id=client_id,
                    websocket=websocket,
                    resume_seq=seq,
                )
                consumer_task = asyncio.create_task(consume_queue(queue, websocket))
    except WebSocketDisconnect:
        consumer_task.cancel()
        await broadcaster.disconnect(client_id)
