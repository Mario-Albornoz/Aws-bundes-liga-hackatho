import uuid
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from common.models import (
    ServerMessageType,
    ClientMessageType,
    WSClientMessage,
    WSServerMessage,
)
from events.EventBroadcastRegistry import EventBroadcastRegistry

router = APIRouter(prefix="/events", tags=["events"])


@router.websocket("/stream")
async def event_stream(
    websocket: WebSocket,
    match_id: str = Query(..., description="Match identifier"),
    speed: float = Query(1.0, gt=0, le=600, description="Playback speed multiplier"),
    seq: int = Query(0, ge=0, description="Last received sequence number for catch-up"),
):
    await websocket.accept()

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

    await broadcaster.connect(client_id=client_id, websocket=websocket, resume_seq=seq)

    try:
        while True:
            raw = await websocket.receive_text()
            client_msg = WSClientMessage.model_validate_json(raw)

            if client_msg.type == ClientMessageType.PAUSE:
                await broadcaster.disconnect(client_id)

            elif client_msg.type == ClientMessageType.RESUME:
                await broadcaster.connect(
                    client_id=client_id,
                    websocket=websocket,
                    resume_seq=seq,
                )
    except WebSocketDisconnect:
        await broadcaster.disconnect(client_id)
