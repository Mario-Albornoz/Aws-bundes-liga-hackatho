import asyncio
import uuid
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from feed_simulator.common.consume_queue import consume_queue
from feed_simulator.common.models import (
    ServerMessageType,
    ClientMessageType,
    WSClientMessage,
    WSServerMessage,
)
from feed_simulator.events.EventBroadcastRegistry import EventBroadcastRegistry
from dotenv import load_dotenv
import os

router = APIRouter(prefix="/events", tags=["events"])

load_dotenv()


@router.websocket("/stream")
async def event_stream(
    websocket: WebSocket,
    speed: float = Query(1.0, gt=0, le=600, description="Playback speed multiplier"),
    seq: int = Query(0, ge=0, description="Last received sequence number for catch-up"),
):
    await websocket.accept()

    match_id = os.getenv("MATCH_ID")

    registry: EventBroadcastRegistry = websocket.app.state.match_broadcast_registry
    broadcaster = await registry.get_or_create(match_id=match_id, speed=speed)

    client_id = str(uuid.uuid4())

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
