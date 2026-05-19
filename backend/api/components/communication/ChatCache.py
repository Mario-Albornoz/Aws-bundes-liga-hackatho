# make sure there is a singleton instace of this class across the server
from common.RedisClient import redis_client
from api.components.communication.dto.ChatDtos import ChatRoomInfo, ChatMessage
import json
import secrets


class ChatCache:
    def create_chat_room(
        self, room_id: str, name: str, user_id: str, connection_string: str
    ) -> ChatRoomInfo:
        cacheKey = f"chat:room:{room_id}"
        cached_room = redis_client.get(cacheKey)
        if cached_room:
            return ChatRoomInfo.model_validate_json(cached_room)

        new_room = ChatRoomInfo(
            room_id=room_id,
            name=name,
            connection_string=connection_string,
            created_by=user_id,
        )
        redis_client.set(cacheKey, new_room.model_dump_json())
        redis_client.set(f"chat:room:by_connection:{connection_string}", room_id)
        return new_room

    def get_room_id_by_connection_string(self, connection_string: str) -> str | None:
        result = redis_client.get(f"chat:room:by_connection:{connection_string}")
        return result.decode() if result else None

    def get_chat_room_info(self, room_id: str) -> ChatRoomInfo | None:
        cacheKey = f"chat:room:{room_id}"
        cached_info = redis_client.get(cacheKey)
        if cached_info:
            return ChatRoomInfo.model_validate_json(cached_info)
        return None

    def add_user_to_chat_room(self, room_id: str, user_id: str):
        cacheKey = f"chat:room:{room_id}:members"
        redis_client.sadd(cacheKey, user_id)

    def get_chat_messages(self, room_id: str) -> list[ChatMessage]:
        cacheKey = f"chat:room:{room_id}:messages"
        messages = redis_client.lrange(cacheKey, 0, -1)
        if messages:
            return [ChatMessage.model_validate_json(m) for m in messages]
        return []

    def add_chat_message(self, room_id: str, message: ChatMessage) -> None:
        cacheKey = f"chat:room:{room_id}:messages"
        redis_client.rpush(cacheKey, message.model_dump_json())

    def create_ws_token(self, room_id: str, user_id: str) -> str:
        token = secrets.token_urlsafe(16)
        token_key = f"chat:ws_token:{token}"
        token_data = json.dumps({"room_id": room_id, "user_id": user_id})
        redis_client.setex(token_key, 30, token_data)
        return token

    def validate_and_consume_ws_token(self, token: str) -> dict | None:
        token_key = f"chat:ws_token:{token}"
        token_data = redis_client.get(token_key)
        if token_data:
            redis_client.delete(token_key)
            return json.loads(token_data)
        return None


chat_cache = ChatCache()
