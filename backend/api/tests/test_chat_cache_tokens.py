import json
from unittest.mock import patch

import pytest


def _make_cache():
    from api.components.communication.ChatCache import ChatCache

    return ChatCache()


def test_create_ws_token_calls_setex_with_30s_ttl():
    with patch("api.components.communication.ChatCache.redis_client") as mock_redis:
        cache = _make_cache()
        token = cache.create_ws_token(room_id="room_123", user_id="user_2")

        mock_redis.setex.assert_called_once()
        key, ttl, value = mock_redis.setex.call_args[0]
        assert key == f"chat:ws_token:{token}"
        assert ttl == 30
        assert json.loads(value) == {"room_id": "room_123", "user_id": "user_2"}


def test_validate_and_consume_returns_payload_on_valid_token():
    with patch("api.components.communication.ChatCache.redis_client") as mock_redis:
        payload = json.dumps({"room_id": "room_123", "user_id": "user_2"})
        mock_redis.get.return_value = payload

        cache = _make_cache()
        result = cache.validate_and_consume_ws_token("tok_abc")

        assert result == {"room_id": "room_123", "user_id": "user_2"}


def test_validate_and_consume_deletes_token_after_reading():
    with patch("api.components.communication.ChatCache.redis_client") as mock_redis:
        payload = json.dumps({"room_id": "room_123", "user_id": "user_2"})
        mock_redis.get.return_value = payload

        cache = _make_cache()
        cache.validate_and_consume_ws_token("tok_abc")

        mock_redis.get.assert_called_once_with("chat:ws_token:tok_abc")
        mock_redis.delete.assert_called_once_with("chat:ws_token:tok_abc")


def test_validate_and_consume_returns_none_for_unknown_token():
    with patch("api.components.communication.ChatCache.redis_client") as mock_redis:
        mock_redis.get.return_value = None

        cache = _make_cache()
        result = cache.validate_and_consume_ws_token("bad_token")

        assert result is None
        mock_redis.delete.assert_not_called()
