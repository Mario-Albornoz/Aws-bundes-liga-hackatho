from typing import Any
from enum import Enum
from pydantic import BaseModel


class ServerMessageType(str, Enum):
    EVENT = "event"
    POSITIONAL = "positional"
    MATCH_START = "match_start"
    MATCH_END = "match_end"
    HEARTBEAT = "heartbeat"
    ERROR = "error"


class ClientMessageType(str, Enum):
    PAUSE = "pause"
    RESUME = "resume"


class WSServerMessage(BaseModel):
    type: ServerMessageType
    seq: int
    match_id: str
    payload: Any


class WSClientMessage(BaseModel):
    type: ClientMessageType
