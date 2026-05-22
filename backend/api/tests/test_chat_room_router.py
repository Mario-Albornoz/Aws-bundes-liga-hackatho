import pytest
from unittest.mock import patch
from fastapi import FastAPI
from starlette.testclient import TestClient
from starlette.websockets import WebSocketDisconnect

from api.components.communication.router import router as chat_router
from api.components.communication.models import ChatRoomInfo


def _app() -> FastAPI:
    app = FastAPI()
    app.include_router(chat_router)
    return app


def _room_info(connection_string: str = "secret") -> ChatRoomInfo:
    return ChatRoomInfo(
        room_id="room_123",
        name="Test Room",
        connection_string=connection_string,
        created_by="user_1",
    )


@pytest.fixture(autouse=True)
def clear_connection_manager():
    from api.components.communication.ConnectionManager import connection_manager

    connection_manager.active_connections.clear()
    yield
    connection_manager.active_connections.clear()


def test_join_returns_ws_token_on_success():
    with patch("api.components.communication.router.chat_cache") as mock_cache:
        mock_cache.get_chat_room_info.return_value = _room_info("secret")
        mock_cache.create_ws_token.return_value = "tok_abc"

        with TestClient(_app()) as client:
            r = client.post(
                "/chat-room/join",
                json={
                    "room_id": "room_123",
                    "user_id": "user_2",
                    "connection_string": "secret",
                },
            )

        assert r.status_code == 200
        data = r.json()
        assert data["ws_token"] == "tok_abc"
        assert data["room_id"] == "room_123"
        assert data["user_id"] == "user_2"
        mock_cache.add_user_to_chat_room.assert_called_once_with(
            room_id="room_123", user_id="user_2"
        )
        mock_cache.create_ws_token.assert_called_once_with(
            room_id="room_123", user_id="user_2"
        )


def test_join_returns_404_when_room_not_found():
    with patch("api.components.communication.router.chat_cache") as mock_cache:
        mock_cache.get_chat_room_info.return_value = None

        with TestClient(_app()) as client:
            r = client.post(
                "/chat-room/join",
                json={
                    "room_id": "room_999",
                    "user_id": "user_2",
                    "connection_string": "secret",
                },
            )

        assert r.status_code == 404
        mock_cache.add_user_to_chat_room.assert_not_called()
        mock_cache.create_ws_token.assert_not_called()


def test_join_returns_400_on_wrong_connection_string():
    with patch("api.components.communication.router.chat_cache") as mock_cache:
        mock_cache.get_chat_room_info.return_value = _room_info("correct_secret")

        with TestClient(_app()) as client:
            r = client.post(
                "/chat-room/join",
                json={
                    "room_id": "room_123",
                    "user_id": "user_2",
                    "connection_string": "wrong_secret",
                },
            )

        assert r.status_code == 400
        mock_cache.add_user_to_chat_room.assert_not_called()
        mock_cache.create_ws_token.assert_not_called()


def test_stream_sends_user_joined_on_connect():
    with patch("api.components.communication.router.chat_cache") as mock_cache:
        mock_cache.validate_and_consume_ws_token.return_value = {
            "room_id": "room_123",
            "user_id": "user_2",
        }

        with TestClient(_app()) as client:
            with client.websocket_connect(
                "/chat-room/stream?room_id=room_123&ws_token=tok_abc"
            ) as ws:
                msg = ws.receive_json()

        assert msg["type"] == "user_joined"
        assert msg["user_id"] == "user_2"
        assert msg["room_id"] == "room_123"
        assert "timestamp" in msg


def test_stream_rejected_with_invalid_token():
    with patch("api.components.communication.router.chat_cache") as mock_cache:
        mock_cache.validate_and_consume_ws_token.return_value = None

        with TestClient(_app()) as client:
            with pytest.raises(WebSocketDisconnect) as exc_info:
                with client.websocket_connect(
                    "/chat-room/stream?room_id=room_123&ws_token=bad_token"
                ) as ws:
                    ws.receive_json()

        assert exc_info.value.code == 4001


def test_stream_rejected_when_token_room_mismatches():
    with patch("api.components.communication.router.chat_cache") as mock_cache:
        # ticket was issued for room_123 but client connects to room_999
        mock_cache.validate_and_consume_ws_token.return_value = {
            "room_id": "room_123",
            "user_id": "user_2",
        }

        with TestClient(_app()) as client:
            with pytest.raises(WebSocketDisconnect) as exc_info:
                with client.websocket_connect(
                    "/chat-room/stream?room_id=room_999&ws_token=tok_abc"
                ) as ws:
                    ws.receive_json()

        assert exc_info.value.code == 4001


def test_stream_token_is_one_time_use():
    consumed = {"used": False}

    def consume_ticket(_token):
        if consumed["used"]:
            return None
        consumed["used"] = True
        return {"room_id": "room_123", "user_id": "user_2"}

    with patch("api.components.communication.router.chat_cache") as mock_cache:
        mock_cache.validate_and_consume_ws_token.side_effect = consume_ticket

        with TestClient(_app()) as client:
            with client.websocket_connect(
                "/chat-room/stream?room_id=room_123&ws_token=tok_abc"
            ) as ws:
                ws.receive_json()

            with pytest.raises(WebSocketDisconnect) as exc_info:
                with client.websocket_connect(
                    "/chat-room/stream?room_id=room_123&ws_token=tok_abc"
                ) as ws:
                    ws.receive_json()

        assert exc_info.value.code == 4001


def test_stream_echoes_chat_message_back_to_sender():
    with patch("api.components.communication.router.chat_cache") as mock_cache:
        mock_cache.validate_and_consume_ws_token.return_value = {
            "room_id": "room_123",
            "user_id": "user_2",
        }

        with TestClient(_app()) as client:
            with client.websocket_connect(
                "/chat-room/stream?room_id=room_123&ws_token=tok_abc"
            ) as ws:
                ws.receive_json()  # user_joined
                ws.send_json({"content": "hello"})
                msg = ws.receive_json()

        assert msg["content"] == "hello"
        assert msg["sender_id"] == "user_2"
        assert msg["room_id"] == "room_123"
        assert "id" in msg
        assert "timestamp" in msg
        mock_cache.add_chat_message.assert_called_once()


def test_connection_manager_broadcasts_to_all_sockets_in_room():
    import asyncio
    from unittest.mock import AsyncMock
    from api.components.communication.ConnectionManager import ConnectionManager

    async def _run():
        manager = ConnectionManager()
        ws1, ws2 = AsyncMock(), AsyncMock()
        manager.active_connections["room_123"] = [ws1, ws2]

        await manager.broadcast("room_123", {"content": "hello"})

        ws1.send_json.assert_awaited_once_with({"content": "hello"})
        ws2.send_json.assert_awaited_once_with({"content": "hello"})

    asyncio.run(_run())


def test_connection_manager_broadcast_does_not_leak_to_other_rooms():
    import asyncio
    from unittest.mock import AsyncMock
    from api.components.communication.ConnectionManager import ConnectionManager

    async def _run():
        manager = ConnectionManager()
        ws_target, ws_other = AsyncMock(), AsyncMock()
        manager.active_connections["room_123"] = [ws_target]
        manager.active_connections["room_999"] = [ws_other]

        await manager.broadcast("room_123", {"content": "hello"})

        ws_target.send_json.assert_awaited_once()
        ws_other.send_json.assert_not_awaited()

    asyncio.run(_run())
