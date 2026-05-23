from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from feed_handler.consumers.handlers.dto.BetTypes import BetTypes


class BetStatus(str, Enum):
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class BetParticipant(BaseModel):
    user_id: int = Field(..., gt=0)
    bet_amount: int = Field(..., gt=0)
    position: bool


class BetSpecifications(BaseModel):
    player_id: str

    trigger_event_type: str = "Substitution"

    team_id: Optional[str] = None


class BetInfo(BaseModel):
    bet_id: str
    bet_type: BetTypes
    duration: int = Field(..., gt=0)
    match_id: str
    bet_specs: BetSpecifications


class BetSubscription(BaseModel):
    participant: BetParticipant


class BetCreateRequest(BaseModel):
    bet_info: BetInfo
    bet_subscription: BetSubscription


# TODO refactor so that it works with other bets not only the substition type
class Bet(BaseModel):
    bet_info: BetInfo
    participants: list[BetParticipant] = []

    bet_status: BetStatus = BetStatus.PENDING

    triggered: bool = False

    scored: bool = False
