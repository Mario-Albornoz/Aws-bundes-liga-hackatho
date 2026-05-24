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
    player_id: Optional[str] = None

    trigger_event_type: str = "Substitution"

    # Which team the user is betting on to win (match_result bets)
    team_id: Optional[str] = None
    # Home/away team IDs stored for result parsing during settlement
    team_left: Optional[str] = None
    team_right: Optional[str] = None


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
