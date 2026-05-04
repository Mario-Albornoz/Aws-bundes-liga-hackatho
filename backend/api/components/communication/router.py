from datetime import datetime, timezone
from uuid import uuid4

from ConnectionManager import connection_manager
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

router = APIRouter(prefix="chat-room", tags=["chat"])


@router.websocket("/stream")
async def chat_room_stream(websocket: WebSocket, room_id: int):
    user_id = websocket.query_params.get("id")
    await connection_manager.connect(room_id=room_id, websocket=websocket)

    await connection_manager.broadcast(
        room_id,
        {
            "type": "user_joined",
            "room_id": room_id,
            "user_id": user_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        },
    )

    try:
        while True:
            data = await websocket.receive_json()

            message = {
                "type": "chat_message",
                "id": str(uuid4()),
                "room_id": room_id,
                "sender_id": user_id,
                "content": data.get("content"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

            await connection_manager.broadcast(room_id, message)

    except WebSocketDisconnect:
        connection_manager.disconnect(room_id=room_id, websocket=websocket)

        await connection_manager.broadcast(
            room_id,
            {
                "type": "user_left",
                "room_id": room_id,
                "user_id": user_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
