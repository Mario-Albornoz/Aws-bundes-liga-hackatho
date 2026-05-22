from datetime import datetime, timezone
from uuid import uuid4
from api.components.communication.ConnectionManager import connection_manager
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from api.components.communication.ChatCache import chat_cache
import secrets
from api.components.communication.dto.ChatDtos import ChatMessage, JoinRoomRequest

router = APIRouter(prefix="/chat-room", tags=["chat"])


@router.post("/create")
async def create_chat_room(name: str, user_id: str):
    room_id = f"room_{uuid4()}"
    connection_string = secrets.token_urlsafe(16)

    room_info = chat_cache.create_chat_room(
        room_id=room_id, name=name, user_id=user_id, connection_string=connection_string
    )
    return JSONResponse(status_code=201, content=room_info.model_dump())


@router.post("/join")
async def join_chat_room(body: JoinRoomRequest):
    room_id = chat_cache.get_room_id_by_connection_string(body.connection_string)
    if not room_id:
        raise HTTPException(status_code=404, detail={"error": "Invalid join code"})

    chat_cache.add_user_to_chat_room(room_id=room_id, user_id=body.user_id)
    ws_token = chat_cache.create_ws_token(room_id=room_id, user_id=body.user_id)
    return {
        "room_id": room_id,
        "user_id": body.user_id,
        "ws_token": ws_token,
    }


@router.websocket("/stream")
async def chat_room_stream(websocket: WebSocket, room_id: str, ws_token: str):
    token = chat_cache.validate_and_consume_ws_token(ws_token)
    if not token or token["room_id"] != room_id:
        await websocket.accept()
        await websocket.close(code=4001)
        return
    user_id = token["user_id"]
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

    for message in chat_cache.get_chat_messages(room_id):
        await websocket.send_json(message.model_dump())

    try:
        while True:
            data = await websocket.receive_json()

            message = ChatMessage(
                id=str(uuid4()),
                room_id=room_id,
                sender_id=data.get("sender_id"),
                content=data.get("content"),
                timestamp=data.get("timestamp"),
            )

            await connection_manager.broadcast(room_id, message.model_dump())

            chat_cache.add_chat_message(room_id=room_id, message=message)

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
