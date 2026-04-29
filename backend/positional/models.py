from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class StatusOfPlay(str, Enum):
    InPlay = 1
    NotInPlay = 0


class Possession(str, Enum):
    HomeTeam = 1
    AwayTeam = 2


class PersonFrame(BaseModel):
    person_id: str
    team_id: str
    x: float
    y: float
    speed: float
    distance: float
    acceleration: float


class BallFrame(BaseModel):
    x: float
    y: float
    z: float
    speed: float
    distance: float
    acceleration: float
    status: StatusOfPlay
    possession: Possession


class PositionalFrame(BaseModel):
    frame_n: str
    timestamp: datetime
    game_section: str
    match_id: str
    players: list[PersonFrame]
    ball: BallFrame
