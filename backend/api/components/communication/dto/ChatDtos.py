from pydantic import BaseModel


class ChatRoomInfo(BaseModel):
    room_id: str
    name: str
    connection_string: str
    created_by: str


class JoinRoomRequest(BaseModel):
    user_id: str
    connection_string: str


class ChatMessage(BaseModel):
    id: str
    room_id: str
    sender_id: str
    content: str
    timestamp: str
